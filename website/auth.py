import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from website.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Views Requiring Provisioning and Authentication

# Register User: Students register right away, Librarian or Admin requests an existing admin
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        role = request.form['role']
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not role:
            error = 'Role is required.'
        elif not first_name:
            error = 'First name is required'
        elif not last_name:
            error = 'Last name is required'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO users (first_name, last_name, username, password) VALUES (?, ?, ?, ?)",
                    (first_name, last_name, username, generate_password_hash(password)),
                )
                if role == 'student':
                    db.execute(
                        'INSERT INTO roles (username, role_name, approval) VALUES (?, ?, ?)',
                        (username, 'student', 1),
                    )
                elif role == 'librarian' or role == 'admin':
                    db.execute(
                        'INSERT INTO roles (username, role_name, approval) VALUES (?, ?, ?)',
                        (username, role, 0),
                    )
                    flash("Registration must be approved before login")
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

# Login
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone() 
        role = db.execute(
            'SELECT * FROM roles WHERE username = ?', (username,)
        ).fetchone() # fetchone returns one row from query, fetchall returns a list of all results


        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        else:
            approval = role['approval']
            if approval == 0:
                error = 'Account must be verified. Contact your administrator.'

        if error is None:
            session.clear()
            session['user_id'] = user['username']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

# Load User Data if logged in
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE username = ?', (user_id,)
        ).fetchone()
        g.user_role = get_db().execute(
            'SELECT * FROM roles WHERE username = ?', (user_id,)
        ).fetchone()

# Logout User
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

def check_auth(role):
    if g.user_role['role_name'] == role:
        return True
    else:
        return False