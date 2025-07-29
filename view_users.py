# view_users.py
import sqlite3

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("SELECT id, username, password, role FROM users")
rows = cursor.fetchall()

print("🧑‍💻 Registered Users:\n")
for row in rows:
    print(f"ID: {row[0]}, Username: {row[1]}, Password: {row[2]}, Role: {row[3]}")

conn.close()
