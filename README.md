# LibFlow - Library Management System

A full-featured web-based Library Management System built with Python (Flask) and SQLite, containerized with Docker.

## Features

- **User Registration & Login** — Students and librarians register with role-based access
- **Book Browsing & Search** — Search 10,000+ books by title, author, ISBN, or publisher
- **Borrow Books** — Students borrow books with a 14-day loan period
- **Return Books** — Books returned via dashboard or book detail page
- **Reserve Books** — Reserve unavailable books; reservation fulfilled automatically on return
- **Transaction History** — Full history of borrows and reservations per user (all users for librarians)
- **Librarian Dashboard** — System-wide stats: total books, users, overdue count, pending reservations
- **Overdue Tracking** — Automatically marks overdue borrows
- **Dataset** — Seeded with 10,000 books from the [Kaggle Books Dataset](https://www.kaggle.com/datasets/saurabhbagchi/books-dataset)

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 + Flask 3.0 |
| Database | SQLite via Flask-SQLAlchemy |
| Auth | Flask-Login + Werkzeug password hashing |
| Frontend | Bootstrap 5 + Bootstrap Icons |
| Container | Docker + Docker Compose |

## Project Structure

```
.
├── app/
│   ├── __init__.py         # App factory
│   ├── models.py           # User, Book, BorrowTransaction, Reservation
│   ├── auth/               # Login, register, logout routes
│   ├── main/               # Dashboard and history routes
│   ├── books/              # Book listing, search, detail, add
│   ├── borrow/             # Checkout, return, reserve, cancel
│   └── templates/          # Jinja2 HTML templates
├── data/
│   └── cleaned_books.csv   # Cleaned Kaggle dataset (10,000 books)
├── clean_books.py          # Kaggle dataset cleaning script
├── seed.py                 # Database initialization and seeding
├── run.py                  # Application entry point
├── config.py               # Flask configuration
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Quick Start

### Option 1: Run with Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/230206902/230206902-ostimteknik.edu.tr.git
cd 230206902-ostimteknik.edu.tr

# 2. Copy the cleaned dataset into the data folder
#    (cleaned_books.csv is included in the repo)

# 3. Build and run
docker-compose up --build

# 4. Open in browser
# http://localhost:3000
```

### Option 2: Run Locally

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create data directory and add cleaned CSV
mkdir -p data
cp cleaned_books.csv data/

# 4. Seed the database
python seed.py

# 5. Run the app
python run.py

# 6. Open in browser
# http://localhost:3000
```

## Default Login Credentials

| Role | Username | Password |
|---|---|---|
| Librarian | `librarian` | `admin123` |
| Student | `student1` | `student123` |
| Student | `student2` | `student123` |

## Dataset

The initial book inventory uses the [Books Dataset from Kaggle](https://www.kaggle.com/datasets/saurabhbagchi/books-dataset), containing books with ISBN, title, author, publisher, and publication year. The raw CSV is cleaned using `clean_books.py`, which:

- Parses the semicolon-separated, Latin-1 encoded file
- Deduplicates by ISBN
- Validates and normalizes publication years
- Outputs a clean UTF-8 CSV with 10,000 records

## Database Schema

- **Users** — user_id, username, email, password_hash, role, created_at
- **Books** — isbn, title, author, publisher, publication_year, total_copies, available_copies
- **BorrowTransactions** — transaction_id, user_id, isbn, borrow_date, due_date, return_date, status
- **Reservations** — reservation_id, user_id, isbn, reservation_date, status

## IYD 328 - İŞ YERİ DENEYİMİ 2025-2026 Spring Semester
