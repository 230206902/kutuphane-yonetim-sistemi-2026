from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.borrow import borrow
from app.models import Book, BorrowTransaction, Reservation
from app import db
from datetime import date


@borrow.route('/checkout/<isbn>', methods=['POST'])
@login_required
def checkout(isbn):
    book = Book.query.get_or_404(isbn)

    # Check if user already has this book borrowed
    existing = BorrowTransaction.query.filter_by(
        user_id=current_user.user_id, isbn=isbn).filter(
        BorrowTransaction.status.in_(['active', 'overdue'])).first()
    if existing:
        flash('You already have this book borrowed.', 'warning')
        return redirect(url_for('books.detail', isbn=isbn))

    if book.available_copies <= 0:
        flash('No copies available. You can reserve it instead.', 'warning')
        return redirect(url_for('books.detail', isbn=isbn))

    # Create borrow transaction
    transaction = BorrowTransaction(user_id=current_user.user_id, isbn=isbn, days=14)
    book.available_copies -= 1
    db.session.add(transaction)
    db.session.commit()

    flash(f'You have successfully borrowed "{book.title}". Due date: {transaction.due_date}', 'success')
    return redirect(url_for('main.dashboard'))


@borrow.route('/return/<int:transaction_id>', methods=['POST'])
@login_required
def return_book(transaction_id):
    transaction = BorrowTransaction.query.get_or_404(transaction_id)

    # Only the borrower or a librarian can return
    if transaction.user_id != current_user.user_id and not current_user.is_librarian():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))

    if transaction.status == 'returned':
        flash('This book has already been returned.', 'info')
        return redirect(url_for('main.dashboard'))

    book = Book.query.get(transaction.isbn)
    transaction.status = 'returned'
    transaction.return_date = date.today()
    book.available_copies += 1

    # Fulfil oldest reservation if any
    reservation = Reservation.query.filter_by(isbn=transaction.isbn, status='active').order_by(
        Reservation.reservation_date).first()
    if reservation:
        reservation.status = 'fulfilled'
        flash(f'Book returned and reservation for user {reservation.user_id} fulfilled.', 'info')

    db.session.commit()
    flash(f'"{book.title}" has been returned successfully.', 'success')
    return redirect(url_for('main.dashboard'))


@borrow.route('/reserve/<isbn>', methods=['POST'])
@login_required
def reserve(isbn):
    book = Book.query.get_or_404(isbn)

    # Check already reserved
    existing_res = Reservation.query.filter_by(
        user_id=current_user.user_id, isbn=isbn, status='active').first()
    if existing_res:
        flash('You already have an active reservation for this book.', 'warning')
        return redirect(url_for('books.detail', isbn=isbn))

    # Check already borrowed
    existing_borrow = BorrowTransaction.query.filter_by(
        user_id=current_user.user_id, isbn=isbn).filter(
        BorrowTransaction.status.in_(['active', 'overdue'])).first()
    if existing_borrow:
        flash('You already have this book borrowed.', 'warning')
        return redirect(url_for('books.detail', isbn=isbn))

    # If book is available, just borrow it
    if book.available_copies > 0:
        flash('This book is available! You can borrow it directly.', 'info')
        return redirect(url_for('books.detail', isbn=isbn))

    reservation = Reservation(user_id=current_user.user_id, isbn=isbn)
    db.session.add(reservation)
    db.session.commit()
    flash(f'Reservation placed for "{book.title}". You will be notified when it becomes available.', 'success')
    return redirect(url_for('main.dashboard'))


@borrow.route('/cancel-reservation/<int:reservation_id>', methods=['POST'])
@login_required
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.user_id != current_user.user_id and not current_user.is_librarian():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))

    reservation.status = 'cancelled'
    db.session.commit()
    flash('Reservation cancelled.', 'info')
    return redirect(url_for('main.dashboard'))
