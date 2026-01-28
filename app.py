from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
import os
from models import authenticate_user

app = Flask(__name__)
app.secret_key = 'change-this-to-something-random'  # For session management

# Simple auth decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        password = request.form.get('password')

        if authenticate_user(first_name, password):
            session['logged_in'] = True
            session['first_name'] = first_name
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('first_name', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Run on all network interfaces so other devices can access
    app.run(host='0.0.0.0', port=5000, debug=True)
