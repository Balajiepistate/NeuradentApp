from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'secret123'  # Replace with a secure key in production

DB = 'users.db'

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']

        conn = get_db_connection()
        conn.execute('INSERT INTO users (name, email, mobile, password) VALUES (?, ?, ?, ?)',
                     (name, email, mobile, password))
        conn.commit()
        conn.close()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_mobile = request.form['email_or_mobile']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE (email = ? OR mobile = ?) AND password = ?',
            (email_or_mobile, email_or_mobile, password)
        ).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid login credentials.', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return "Welcome to your dashboard! <a href='/logout'>Logout</a>"

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/export')
def export():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()

    export_path = 'users_export.xlsx'
    df.to_excel(export_path, index=False)

    return f"User data exported to {export_path}"

if __name__ == '__main__':
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        conn.execute('''CREATE TABLE users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            email TEXT,
                            mobile TEXT,
                            password TEXT NOT NULL
                        )''')
        conn.commit()
        conn.close()

    app.run(debug=True)

