from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.books import books
from app.models import Book
from app import db


@books.route('/')
@login_required
def index():
    search = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Book.query
    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                Book.title.ilike(like),
                Book.author.ilike(like),
                Book.isbn.ilike(like),
                Book.publisher.ilike(like)
            )
        )

    pagination = query.order_by(Book.title).paginate(page=page, per_page=20, error_out=False)
    return render_template('books/index.html', books=pagination, search=search)


@books.route('/<isbn>')
@login_required
def detail(isbn):
    book = Book.query.get_or_404(isbn)
    from app.models import BorrowTransaction, Reservation
    user_has_active_borrow = BorrowTransaction.query.filter_by(
        user_id=current_user.user_id, isbn=isbn).filter(
        BorrowTransaction.status.in_(['active', 'overdue'])).first()
    user_has_reservation = Reservation.query.filter_by(
        user_id=current_user.user_id, isbn=isbn, status='active').first()
    return render_template('books/detail.html',
                           book=book,
                           user_has_active_borrow=user_has_active_borrow,
                           user_has_reservation=user_has_reservation)


@books.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if not current_user.is_librarian():
        flash('Access denied.', 'danger')
        return redirect(url_for('books.index'))

    if request.method == 'POST':
        isbn = request.form.get('isbn', '').strip()
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        publisher = request.form.get('publisher', '').strip()
        year = request.form.get('publication_year', '').strip()
        copies = request.form.get('total_copies', 1, type=int)

        if not isbn or not title or not author:
            flash('ISBN, title, and author are required.', 'danger')
            return render_template('books/add.html')

        if Book.query.get(isbn):
            flash('A book with this ISBN already exists.', 'danger')
            return render_template('books/add.html')

        try:
            year_int = int(year) if year else None
        except ValueError:
            year_int = None

        book = Book(isbn=isbn, title=title, author=author,
                    publisher=publisher or None,
                    publication_year=year_int,
                    total_copies=copies,
                    available_copies=copies)
        db.session.add(book)
        db.session.commit()
        flash(f'Book "{title}" added successfully.', 'success')
        return redirect(url_for('books.detail', isbn=isbn))

    return render_template('books/add.html')
