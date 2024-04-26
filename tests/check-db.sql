.mode json
.header on
.output ./tests/results.json
.open ./instance/website.sqlite
.tables
SELECT * FROM users;
SELECT * FROM roles;
SELECT * FROM books;
SELECT * FROM rooms;
SELECT * FROM borrowed_by;
SELECT * FROM reserve_room;