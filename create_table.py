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

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user'
);
""")

conn.commit()
conn.close()

print("✅ Tables dropped and recreated successfully.")
