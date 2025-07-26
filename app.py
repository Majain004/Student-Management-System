from flask import Flask, render_template, request, send_file, redirect, url_for, session
import sqlite3
import csv
import subprocess
from flask_mail import Mail, Message
import random
import os



from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# -------- Flask-Login Setup --------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# -------- User Setup --------
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)



# -------- Login Route --------
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('students.db')
        cur = conn.cursor()
        cur.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            # Login the user using Flask-Login
            login_user(User(username))  # create User object with username
            session['role'] = user[1]   # save role in session if needed
            return redirect(url_for('index'))
        else:
            msg = '❌ Invalid credentials'

    return render_template('login.html', message=msg)


# -------- Guest Login --------
@app.route('/guest-login', methods=['POST'])
def guest_login():
    guest_user = User('guest')
    login_user(guest_user)
    session['role'] = 'guest'
    return redirect(url_for('index'))



# -------- Register --------
import random
import smtplib
from email.mime.text import MIMEText

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm', '').strip()

        if not username or not email or not password or not confirm:
            msg = "❌ All fields required!"
        elif password != confirm:
            msg = "❌ Passwords do not match!"
        else:
            otp = str(random.randint(100000, 999999))
            session['temp_user'] = {'username': username, 'email': email, 'password': password, 'otp': otp}

            # Send OTP
            sender_email = 'jainma004@gmail.com'
            app_password = 'siynfxqmpksxzhia'

            message = MIMEText(f'Your OTP for registration is: {otp}')
            message['Subject'] = 'Student Management Registration OTP'
            message['From'] = sender_email
            message['To'] = email

            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(sender_email, app_password)
                    server.sendmail(sender_email, email, message.as_string())
                return redirect(url_for('verify_otp'))
            except Exception as e:
                msg = f"❌ Failed to send OTP: {e}"

    return render_template('register.html', message=msg)

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    msg = ''
    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()
        actual_otp = session.get('temp_user', {}).get('otp', '')

        if entered_otp == actual_otp:
            user = session['temp_user']
            conn = sqlite3.connect('students.db')
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                            (user['username'], user['password'], 'user'))
                conn.commit()
                msg = "✅ Registered successfully!"
                session.pop('temp_user', None)
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                msg = "❌ Username already exists!"
            finally:
                conn.close()
        else:
            msg = "❌ Incorrect OTP. Try again."

    return render_template('verify_otp.html', message=msg)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'jainma004@gmail.com'
app.config['MAIL_PASSWORD'] = 'aqrxsdflnzbnsfoa'

app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# -------- Logout --------
@app.route('/logout')
def logout():
    logout_user()           # ✅ properly logs out the Flask-Login user
    session.clear()
    return redirect(url_for('login'))



# -------- Index (Add Student) --------
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():

    msg = ''
    if request.method == 'POST':
        id = request.form.get('id', '').strip()
        name = request.form.get('name', '').strip()
        course = request.form.get('course', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        if not id.isdigit():
            msg = "❌ ID must be a number!"
        elif not name or not course:
            msg = "❌ All fields are required!"
        else:
            try:
                subprocess.run(['insert.exe', id, name, course, phone, address], check=True)
                msg = "✅ Student added successfully!"
            except Exception as e:
                msg = f"❌ Error: {e}"

    return render_template('index.html', message=msg)


# -------- View Students --------
@app.route('/students')
@login_required
def view_students():
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    cur.execute("SELECT roll, name, course, phone, address FROM students")
    students = cur.fetchall()
    conn.close()
    return render_template('students.html', students=students)


# -------- Edit --------
@app.route('/edit/<int:roll>', methods=['GET', 'POST'])
@login_required
def edit_student(roll):
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        course = request.form['course']
        phone = request.form['phone']
        address = request.form['address']
        cur.execute("UPDATE students SET name=?, course=?, phone=?, address=? WHERE roll=?", 
                    (name, course, phone, address, roll))
        conn.commit()
        conn.close()
        return redirect(url_for('view_students'))

    cur.execute("SELECT roll, name, course, phone, address FROM students WHERE roll=?", (roll,))
    student = cur.fetchone()
    conn.close()
    return render_template('edit.html', student=student)


# -------- Delete --------
@app.route('/delete/<int:roll>', methods=['POST'])
@login_required
def delete_student(roll):
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE roll = ?", (roll,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_students'))



# -------- Search --------
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    results = []
    query = ''
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        conn = sqlite3.connect('students.db')
        cur = conn.cursor()
        cur.execute("SELECT roll, name, course, phone, address FROM students WHERE name LIKE ? OR course LIKE ? OR roll LIKE ?",
                    (f"%{query}%", f"%{query}%", f"%{query}%"))
        results = cur.fetchall()
        conn.close()
    return render_template('search.html', results=results, query=query)


# -------- Export --------
@app.route('/export')
@login_required
def export():
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    cur.execute("SELECT roll, name, course, phone, address FROM students")
    data = cur.fetchall()
    conn.close()

    with open('students.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Roll No', 'Name', 'Course', 'Phone', 'Address'])
        writer.writerows(data)

    return send_file('students.csv', as_attachment=True)


# -------- Run --------
if __name__ == '__main__':
    app.run(debug=True)
