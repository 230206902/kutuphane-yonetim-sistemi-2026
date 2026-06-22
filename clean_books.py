"""
clean_books.py - Clean the raw Kaggle Books dataset and output a usable CSV.

Usage:
    python clean_books.py

Input:  data/books_raw.csv  (download from https://www.kaggle.com/datasets/saurabhbagchi/books-dataset)
Output: data/cleaned_books.csv
"""

import csv
import os


def clean_books(input_file='data/books_raw.csv', output_file='data/cleaned_books.csv'):
    if not os.path.exists(input_file):
        print(f"ERROR: Input file '{input_file}' not found.")
        print("Please download the Books dataset from Kaggle and place it at data/books_raw.csv")
        return

    cleaned_data = []
    seen_isbns = set()
    skipped = 0

    print(f"Reading {input_file}...")

    with open(input_file, mode='r', encoding='latin-1') as f:
        for i, line in enumerate(f):
            if i == 0:
                continue  # Skip header

            line = line.strip().rstrip(',')
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1]

            parts = line.split(';')
            if len(parts) < 5:
                skipped += 1
                continue

            isbn = parts[0].strip('"').strip()
            title = parts[1].strip('"').strip()
            author = parts[2].strip('"').strip()
            year = parts[3].strip('"').strip()
            publisher = parts[4].strip('"').strip()

            # Skip blank ISBN
            if not isbn or isbn in seen_isbns:
                skipped += 1
                continue

            seen_isbns.add(isbn)

            # Validate and clean year
            try:
                y = int(year)
                if not (1000 < y <= 2026):
                    y = 0
            except (ValueError, TypeError):
                y = 0

            cleaned_data.append({
                'isbn': isbn,
                'title': title or 'Unknown Title',
                'author': author or 'Unknown Author',
                'publication_year': y,
                'publisher': publisher or 'Unknown Publisher',
                'total_copies': 5,
                'available_copies': 5
            })

            if len(cleaned_data) >= 10000:
                break

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, mode='w', encoding='utf-8', newline='') as f:
        fieldnames = ['isbn', 'title', 'author', 'publication_year', 'publisher', 'total_copies', 'available_copies']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_data)

    print(f"Done! Cleaned {len(cleaned_data)} books -> {output_file}")
    print(f"Skipped {skipped} invalid rows.")


if __name__ == '__main__':
    clean_books()
