import sqlite3

# Connect to database
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")

# Check if books table has data
if ('books',) in tables:
    cursor.execute("SELECT COUNT(*) FROM books")
    book_count = cursor.fetchone()[0]
    print(f"\nBooks in database: {book_count}")

conn.close()

