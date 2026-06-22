from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.main import main
from app.models import BorrowTransaction, Reservation, Book
from app import db
from datetime import date


@main.route('/')
def index():
    from flask_login import current_user
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main.route('/dashboard')
@login_required
def dashboard():
    # Update overdue status
    active_borrows = BorrowTransaction.query.filter_by(status='active').all()
    for b in active_borrows:
        if b.is_overdue():
            b.status = 'overdue'
    db.session.commit()

    if current_user.is_librarian():
        # Librarian sees system overview
        total_books = Book.query.count()
        total_users = __import__('app.models', fromlist=['User']).User.query.count()
        active_borrows_count = BorrowTransaction.query.filter(
            BorrowTransaction.status.in_(['active', 'overdue'])).count()
        overdue_count = BorrowTransaction.query.filter_by(status='overdue').count()
        pending_reservations = Reservation.query.filter_by(status='active').count()
        recent_borrows = BorrowTransaction.query.order_by(
            BorrowTransaction.transaction_id.desc()).limit(10).all()
        return render_template('main/librarian_dashboard.html',
                               total_books=total_books,
                               total_users=total_users,
                               active_borrows_count=active_borrows_count,
                               overdue_count=overdue_count,
                               pending_reservations=pending_reservations,
                               recent_borrows=recent_borrows)
    else:
        # Student sees their own info
        my_borrows = BorrowTransaction.query.filter_by(
            user_id=current_user.user_id).filter(
            BorrowTransaction.status.in_(['active', 'overdue'])).all()
        my_reservations = Reservation.query.filter_by(
            user_id=current_user.user_id, status='active').all()
        return render_template('main/student_dashboard.html',
                               my_borrows=my_borrows,
                               my_reservations=my_reservations)


@main.route('/history')
@login_required
def history():
    if current_user.is_librarian():
        borrows = BorrowTransaction.query.order_by(
            BorrowTransaction.transaction_id.desc()).all()
        reservations = Reservation.query.order_by(
            Reservation.reservation_id.desc()).all()
    else:
        borrows = BorrowTransaction.query.filter_by(
            user_id=current_user.user_id).order_by(
            BorrowTransaction.transaction_id.desc()).all()
        reservations = Reservation.query.filter_by(
            user_id=current_user.user_id).order_by(
            Reservation.reservation_id.desc()).all()

    return render_template('main/history.html', borrows=borrows, reservations=reservations)
