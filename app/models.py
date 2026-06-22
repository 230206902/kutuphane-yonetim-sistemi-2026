from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'Users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    borrows = db.relationship('BorrowTransaction', backref='user', lazy='dynamic')
    reservations = db.relationship('Reservation', backref='user', lazy='dynamic')

    def get_id(self):
        return str(self.user_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_librarian(self):
        return self.role == 'librarian'

    def __repr__(self):
        return f'<User {self.username}>'


class Book(db.Model):
    __tablename__ = 'Books'

    isbn = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.Text, nullable=False)
    author = db.Column(db.Text, nullable=False)
    publisher = db.Column(db.Text)
    publication_year = db.Column(db.Integer)
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)

    borrows = db.relationship('BorrowTransaction', backref='book', lazy='dynamic')
    reservations = db.relationship('Reservation', backref='book', lazy='dynamic')

    def is_available(self):
        return self.available_copies > 0

    def __repr__(self):
        return f'<Book {self.title}>'


class BorrowTransaction(db.Model):
    __tablename__ = 'BorrowTransactions'

    transaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    isbn = db.Column(db.String(20), db.ForeignKey('Books.isbn'), nullable=False)
    borrow_date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')  # active, returned, overdue

    def __init__(self, user_id, isbn, days=14):
        self.user_id = user_id
        self.isbn = isbn
        self.borrow_date = date.today()
        self.due_date = date.today() + timedelta(days=days)
        self.status = 'active'

    def is_overdue(self):
        if self.status == 'active' and date.today() > self.due_date:
            return True
        return False

    def days_remaining(self):
        if self.status == 'returned':
            return None
        delta = self.due_date - date.today()
        return delta.days

    def __repr__(self):
        return f'<BorrowTransaction {self.transaction_id}>'


class Reservation(db.Model):
    __tablename__ = 'Reservations'

    reservation_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    isbn = db.Column(db.String(20), db.ForeignKey('Books.isbn'), nullable=False)
    reservation_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, fulfilled, cancelled

    def __repr__(self):
        return f'<Reservation {self.reservation_id}>'
