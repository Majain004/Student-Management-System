import sqlite3

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.executescript("""
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS users;

CREATE TABLE students (
    roll INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    course TEXT NOT NULL,
    phone TEXT,
    address TEXT
);
""")

conn.commit()
conn.close()

print("✅ Tables dropped and recreated successfully.")
