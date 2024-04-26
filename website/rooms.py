from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from datetime import datetime, timedelta

from website.auth import login_required, check_auth
from website.db import get_db

bp = Blueprint('rooms', __name__, url_prefix='/rooms')

# Rooms--------------------------------------------------------------------------------------------------
@bp.route('/my_reservations', methods=('GET', 'POST'))
@login_required
def my_reservations():
    # Everyone has access to reserving rooms
    
    db = get_db()
    my_reservations = db.execute(
        'SELECT * FROM reserve_room WHERE username = ? '
        'ORDER BY date_time', (g.user['username'],)
    ).fetchall()
    # Format Date using helper function
    formatted_reservations = [
            {'room_num': room_num, 'date_time': format_datetime(datetime.strptime(date_time, "%Y-%m-%dT%H:%M")),
             'username': username}
            for room_num, date_time, username in my_reservations
        ]
    return render_template('rooms/my_reservations.html', my_res=zip(formatted_reservations,my_reservations))

# This view shows every reservation by all users
@bp.route('/all_reservations', methods=('GET', 'POST'))
@login_required
def all_reservations():
    # Page only for librarians and admins
    if check_auth('student') == True:
        flash('You do not have permision to view this page.')
        return redirect(url_for('index'))
    
    db = get_db()
    all_reservations = db.execute(
        'SELECT * FROM reserve_room '
        'ORDER BY date_time',
    ).fetchall()
    # Format Date using helper function
    formatted_reservations = [
            {'room_num': room_num, 'date_time': format_datetime(datetime.strptime(date_time, "%Y-%m-%dT%H:%M")),
             'username': username}
            for room_num, date_time, username in all_reservations
        ]
    return render_template('rooms/all_reservations.html', my_res=zip(formatted_reservations,all_reservations))

# Written with the help of ChatGPT. PDF will explain and link to chat
@bp.route('/reserve_room', methods=('GET', 'POST'))
@login_required
def reserve_room():
    if request.method == 'POST':
        room_num = request.form['room_num']
        date_time = request.form['date_time']
        username = g.user['username']
        db = get_db()

        # Convert input of date_time string to datetime object
        selected_datetime = datetime.strptime(date_time, "%Y-%m-%dT%H:%M")
        
        # Find existing reservations
        existing_res = db.execute(
            'SELECT date_time FROM reserve_room '
            'WHERE room_num = ? AND date_time >= ? AND date_time < ?',
            (room_num, selected_datetime, datetime.strftime(selected_datetime + timedelta(hours=2), "Y-%m-%dT%H:%M"))
        ).fetchall()

        #Check if the room is available at the day and time
        if not existing_res:
            db.execute(
                'INSERT INTO reserve_room (room_num, date_time, username) '
                'VALUES (?, ?, ?)', (room_num, date_time, username)
            )
            db.commit()
            flash('Room reserved successfully.')
            return redirect(url_for('rooms.my_reservations'))
        else:
            flash('Room already reserved for a 2-hour block at the selected date and time.')
    # Fetch list of available rooms for the html page
    avail_rooms = get_available_rooms()

    return render_template('rooms/reserve_room.html', avail_rooms=avail_rooms)

# This function uses a different method compared to the update and delete functions of users and books
# Uses hidden input forms instead of passing variables via url link (needed two variables here)
@bp.route('/cancel_reservation', methods=('GET', 'POST'))
@login_required
def cancel_reservation():
    if request.method == 'POST':
        room_num = request.form['room_num']
        date_time = request.form['date_time']
        db = get_db()

        db.execute(
            'DELETE FROM reserve_room WHERE room_num = ? AND date_time = ?',
            (room_num, date_time)
        )
        db.commit()
        flash('Reservation cancelled sucessfully.')
        return redirect(url_for('index'))

@bp.route('/manage_rooms', methods=('GET', 'POST'))
@login_required
def manage_rooms():
    # Page only for librarians and admins
    if check_auth('student') == True:
        flash('You do not have permision to view this page.')
        return redirect(url_for('index'))
    
    db = get_db()
    rooms = db.execute('SELECT * FROM rooms')

    return render_template('rooms/manage_rooms.html', rooms=rooms)

@bp.route('/add_room', methods=('GET', 'POST'))
@login_required
def add_room():
    # Page only for librarians and admins
    if check_auth('student') == True:
        flash('You do not have permision to view this page.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        room_num = request.form.get('room_num')
        db = get_db()
        error = None

        if not room_num:
            error = 'Room Number required.'
        
        if error is None:
            try:
                db.execute(
                    'INSERT INTO rooms (room_num) '
                    'VALUES (?)', (room_num,)
                )
                db.commit()
            except db.IntegrityError:
                error = f"Room {room_num} is already available." 
        else:
            flash('Adding room was unsuccessful.')
            return redirect(url_for('index'))
        
        if error is not None: flash(error)
        return redirect(url_for('rooms.manage_rooms'))

@bp.route('/remove_room', methods=('GET', 'POST'))
@login_required
def remove_room():
    # Page only for librarians and admins
    if check_auth('student') == True:
        flash('You do not have permision to view this page.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        room_num = request.form.get('room_num')
        db = get_db()
        error = None

        if not room_num:
            error = 'Room Number required.'
        
        if error is None:
            try:
                db.execute(
                    'DELETE FROM rooms WHERE room_num = ?',
                    (room_num,)
                )
                # Cancel all reservations when room is deleted
                db.execute(
                    'DELETE FROM reserve_room WHERE room_num = ?',
                    (room_num,)
                )
                db.commit()
                flash('Room successfully removed. All existing reservations have been cancelled.')
            except db.IntegrityError:
                error = f"Room {room_num} is not in the system." 
        else:
            flash('Removing room was unsuccessful.')
            return redirect(url_for('index'))
        
        if error is not None: flash(error)
        return redirect(url_for('rooms.manage_rooms'))

@bp.route('/list_room', methods=('GET', 'POST'))
@login_required
def list_room():
    # Page only for librarians and admins
    if check_auth('student') == True:
        flash('You do not have permision to view this page.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        room_num = request.form.get('room_num')
        db = get_db()
        room = db.execute(
            'SELECT * FROM rooms WHERE room_num = ?',
            (room_num,)
        ).fetchone()

        if (room['listed'] == 1): #if room is listed, unlist room
            db.execute(
                'UPDATE rooms SET listed = 0 WHERE room_num = ?',
                (room_num,)
            )
            db.commit()
            flash('Room successfully unlisted.')
            return redirect(url_for('rooms.manage_rooms'))
        elif (room['listed'] == 0): #if room is unlisted, list room
            db.execute(
                'UPDATE rooms SET listed = 1 WHERE room_num = ?',
                (room_num,)
            )
            db.commit()
            flash('Room successfully listed.')
            return redirect(url_for('rooms.manage_rooms'))


# Helper Functions with the help of ChatGPT
def get_available_rooms():
    db = get_db()
    all_rooms = db.execute('SELECT room_num FROM rooms WHERE listed == 1').fetchall()

    next_hours = datetime.now() + timedelta(hours=2)
    existing_res = db.execute(
        'SELECT room_num FROM reserve_room '
        'WHERE date_time >= ? AND date_time < ?',
        (datetime.now(), next_hours)
    ).fetchall()

    avail_rooms = [room[0] for room in all_rooms if room not in existing_res]
    return avail_rooms

def format_datetime(reservation_datetime):
    # Custom function to format the reservation datetime
    day = reservation_datetime.day
    suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    formatted_datetime = reservation_datetime.strftime(f"%A %B {day}{suffix}, %Y at %I:%M%p")
    return formatted_datetime

def is_within_operating_hours(time_slot):
    # Operating Hours
    op_start = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)
    op_end = datetime.now().replace(hour=23, minute=0, second=0, microsecond=0)

    if (op_start <= time_slot <= op_end):
        return True
    else:
        return False