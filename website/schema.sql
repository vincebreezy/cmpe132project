DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS borrowed_by;
DROP TABLE IF EXISTS reserve_room;

CREATE TABLE users(
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    PRIMARY KEY (username)
);

CREATE TABLE roles(
    role_name TEXT NOT NULL CHECK (role_name IN ('admin', 'librarian', 'student')),
    username INTEGER NOT NULL,
    approval INTEGER(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (username) REFERENCES user (username),
    PRIMARY KEY (username, role_name)
);

CREATE TABLE books(
    isbn TEXT(17) NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    PRIMARY KEY (isbn)
);

CREATE TABLE rooms(
    room_num INTEGER NOT NULL,
    listed INTEGER(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (room_num)
);

CREATE TABLE borrowed_by(
    isbn TEXT(17) NOT NULL,
    username TEXT NOT NULL,
    FOREIGN KEY (isbn) REFERENCES books (isbn),
    FOREIGN KEY (username) REFERENCES users (username),
    PRIMARY KEY (isbn, username)
);

CREATE TABLE reserve_room(
    room_num TEXT(17) NOT NULL,
    date_time TEXT NOT NULL,
    username TEXT NOT NULL,
    FOREIGN KEY (room_num) REFERENCES rooms (room_num),
    FOREIGN KEY (username) REFERENCES users (username),
    PRIMARY KEY (room_num, date_time, username)
);