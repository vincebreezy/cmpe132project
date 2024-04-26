from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from website.auth import login_required, check_auth
from website.db import get_db

bp = Blueprint('books', __name__, url_prefix='/books')

# Books--------------------------------------------------------------------------------------------------
@bp.route('/book_inventory', methods=('GET', 'POST'))
@login_required
def book_inventory():
    db = get_db()
    books = db.execute(
        "SELECT * FROM books ORDER BY title" 
    ).fetchall()
    return render_template('books/book_inventory.html', books=books)

@bp.route('/search', methods=('GET', 'POST'))
@login_required
def search():
    if request.method == 'POST':
        query = request.form['search']
        db = get_db()
        search_made = True

        results = db.execute(
            'SELECT * FROM books WHERE title LIKE ?', ('%' + query + '%',)
        ).fetchall()

        # Check if there are no results
        if not results:
            error = 'No results found.'
            flash(error)
        return render_template('books/book_inventory.html', books=results, search_made=search_made)
        
    return render_template('books/book_inventory.html', books=[], search_made=search_made)


@bp.route('/<isbn>/book_info', methods=('GET', 'POST'))
@login_required
def book_info(isbn):
    db = get_db()
    book = db.execute(
        'SELECT * FROM books WHERE isbn = ?', (isbn,)
    ).fetchone()
    return render_template('books/book_info.html', book=book)

@bp.route('/my_books', methods=('GET', 'POST'))
@login_required
def my_books():
    # Only Students have access because only students can borrow books
    if check_auth('student') == False:
        flash('You do not have permision to view this page.')
        return redirect(url_for('index'))
    
    db = get_db()
    my_books = db.execute(
        'SELECT bor.isbn, bor.username, b.title, b.author '
        'FROM borrowed_by bor JOIN books b ON bor.isbn = b.isbn '
        'WHERE bor.username = ?', (g.user['username'],)
    ).fetchall()
    return render_template('books/my_books.html', my_books=my_books)

@bp.route('/<isbn>/borrow', methods=('POST',))
@login_required
def borrow(isbn):
    db = get_db()
    quantity = db.execute(
        'SELECT quantity FROM books WHERE isbn = ?', (isbn,)
    ).fetchone()
    book_check = db.execute(
        'SELECT COUNT(*) FROM borrowed_by WHERE isbn = ? AND username = ?',
        (isbn, g.user['username'])
    ).fetchone()
    # Checks if book is already borrowed by student
    if book_check[0] == 0:
        if quantity['quantity'] > 0:
            db.execute(
                'INSERT INTO borrowed_by (isbn, username) ' 
                'VALUES (?, ?)', (isbn, g.user['username'])
            )
            db.execute(
                'UPDATE books SET quantity = quantity - 1 '
                'WHERE isbn = ?', (isbn,)
            )
            db.commit()
        else:
            flash('Book is not available.')
    else:
        flash('You are already borrowing this book.')
    return redirect(url_for('books.my_books'))

@bp.route('/<isbn>/return_book', methods=('POST',))
@login_required
def return_book(isbn):
    db = get_db()
    db.execute(
        'DELETE FROM borrowed_by WHERE isbn = ? AND username = ?',
        (isbn, g.user['username'])
    )
    db.execute(
        'UPDATE books SET quantity = quantity + 1 '
        'WHERE isbn = ?', (isbn,)
    )
    db.commit()
    flash('Book successfully returned.')

    return redirect(url_for('books.my_books'))

@bp.route('/add_book', methods=('GET', 'POST'))
@login_required
def add_book():
    # Adding books is only for librarians and admins
    if check_auth('student') == True:
        flash('You do not have permision to view this page.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        quantity = request.form['quantity']
        db = get_db()
        error = None

        if not title:
            error = 'Book Title is required.'
        elif not author:
            error = 'Author is required.'
        elif not isbn:
            error = 'ISBN is required.'
        elif not quantity:
            error = 'Quantity is required'

        if error is None:
            try:
                db.execute(
                    'INSERT INTO books (title, author, isbn, quantity) '
                    'VALUES (?, ?, ?, ?)', (title, author, isbn, quantity)
                )
                db.commit()
                flash('Book successfully added.')
            except db.IntegrityError:
                # If ISBN is already in the database
                flash('Book is already in the library.')
        else:
            flash('Adding book was unsuccessful')
            return redirect(url_for("index"))

        if error is not None: flash(error)

    return render_template('books/add_book.html')

@bp.route('/<isbn>/update_book', methods=('GET', 'POST'))
@login_required
def update_book(isbn):
    # Only librarians and admins have access
    if check_auth('student') == True:
        flash('You do not have permision to view this page.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        qty = request.form.get('quantity')
        db = get_db()
        error = None
        book = db.execute(
                'SELECT * FROM books WHERE isbn = ?', (isbn,)
            ).fetchone()

        if not qty:
            error = 'Quantity required.'
        elif not title:
            error = 'Title required.'
        elif not author:
            error = 'Author required.'

        if error is None:
            qty = int(qty)
            currently_borrowed = db.execute(
            'SELECT COUNT(*) FROM borrowed_by WHERE isbn = ?', (isbn,)
            ).fetchone()
            
            if qty <= 0 and currently_borrowed[0] <= 0:
                # If the new proposed amount is 0 or below, just remove the book.
                db.execute(
                    'DELETE FROM books WHERE isbn = ?', (isbn,)
                )
                db.commit()
                flash('Book successfully deleted.')
                return redirect(url_for('books.book_inventory'))
            elif qty > 0 and currently_borrowed[0] <= qty:
                db.execute(
                    'UPDATE books SET title = ?, author = ?, quantity = ? '
                    'WHERE isbn = ?', (title, author, qty, isbn)
                )
                db.commit()
                flash('Book was successfully updated.')
                return redirect(url_for('books.book_inventory'))
            elif currently_borrowed[0] > qty:
                flash(f'This book is currently borrowed by {currently_borrowed[0]} '
                'students and cannot be removed from the system.')
                return redirect(url_for('books.book_inventory')) 
            
    return render_template('books/update_book.html', book=book)

@bp.route('/<isbn>/remove_book', methods=('POST',))
@login_required
def remove_book(isbn):
    # Only librarians and admins have access
    if check_auth('student') == True:
        flash('You do not have permision to view this page.')
        return redirect(url_for('index'))

    db = get_db()
    currently_borrowed = db.execute(
        'SELECT COUNT(*) FROM borrowed_by WHERE isbn = ?', (isbn,)
    ).fetchone()

    # If the book is currently being borrowed, you cannot remove the book from the system
    if currently_borrowed[0] > 0:
        flash(f'This book is currently borrowed by {currently_borrowed[0]} '
               'students and cannot be removed from the system.')
        return redirect(url_for('books.book_inventory'))

    db.execute(
        'DELETE FROM books WHERE isbn = ?', (isbn,)
    )
    db.commit()
    flash('Book successfully deleted.')
    return redirect(url_for('books.book_inventory'))