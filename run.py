from app import create_app, db
from app.models import User, Book, BorrowTransaction, Reservation

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Book': Book,
        'BorrowTransaction': BorrowTransaction,
        'Reservation': Reservation
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)
