"""
seed.py - Initialize the database with tables and seed data.
Run this once before starting the application:
    python seed.py
"""

import os
import csv
import sys

# Make sure we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Book, BorrowTransaction, Reservation
from werkzeug.security import generate_password_hash

app = create_app()

def seed():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()

        # Seed default users if not present
        if not User.query.filter_by(username='librarian').first():
            librarian = User(
                username='librarian',
                email='admin@libflow.com',
                role='librarian'
            )
            librarian.set_password('admin123')
            db.session.add(librarian)
            print("Created librarian user (username: librarian, password: admin123)")

        if not User.query.filter_by(username='student1').first():
            student1 = User(
                username='student1',
                email='student1@libflow.com',
                role='student'
            )
            student1.set_password('student123')
            db.session.add(student1)
            print("Created student user (username: student1, password: student123)")

        if not User.query.filter_by(username='student2').first():
            student2 = User(
                username='student2',
                email='student2@libflow.com',
                role='student'
            )
            student2.set_password('student123')
            db.session.add(student2)

        db.session.commit()

        # Seed books from cleaned CSV
        if Book.query.count() == 0:
            csv_path = os.path.join(os.path.dirname(__file__), 'data', 'cleaned_books.csv')
            if not os.path.exists(csv_path):
                # Try same directory
                csv_path = os.path.join(os.path.dirname(__file__), 'cleaned_books.csv')

            if os.path.exists(csv_path):
                print(f"Seeding books from {csv_path}...")
                count = 0
                with open(csv_path, encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    batch = []
                    for row in reader:
                        try:
                            year = int(row.get('publication_year', 0) or 0)
                        except (ValueError, TypeError):
                            year = 0

                        try:
                            total = int(row.get('total_copies', 5) or 5)
                            avail = int(row.get('available_copies', 5) or 5)
                        except (ValueError, TypeError):
                            total = 5
                            avail = 5

                        book = Book(
                            isbn=row['isbn'],
                            title=row['title'] or 'Unknown Title',
                            author=row['author'] or 'Unknown Author',
                            publisher=row.get('publisher') or 'Unknown Publisher',
                            publication_year=year if year > 0 else None,
                            total_copies=total,
                            available_copies=avail
                        )
                        batch.append(book)
                        count += 1

                        if count % 500 == 0:
                            db.session.bulk_save_objects(batch)
                            db.session.commit()
                            batch = []
                            print(f"  {count} books seeded...")

                    if batch:
                        db.session.bulk_save_objects(batch)
                        db.session.commit()

                print(f"Done! {count} books seeded successfully.")
            else:
                print(f"WARNING: cleaned_books.csv not found at {csv_path}")
                print("Please place cleaned_books.csv in the data/ folder and re-run seed.py")
        else:
            print(f"Books already in database ({Book.query.count()} records). Skipping book seed.")

        print("\nDatabase ready!")
        print(f"  Users: {User.query.count()}")
        print(f"  Books: {Book.query.count()}")

if __name__ == '__main__':
    seed()
