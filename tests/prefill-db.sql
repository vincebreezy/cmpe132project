.mode json
.header on
.output ./tests/results.json
.open ./instance/website.sqlite

INSERT INTO users (first_name, last_name, username, password)
VALUES ('Happy', 'Pancakes', '1hp', 'scrypt:32768:8:1$ESqrRwiTqHn72iPD$eef7c3a3af7a9c1be8d7c688bfacf96439b32dd45eaf93cb3f80e6e6a7980e3d93f5dccff5cf52eb41be3b03991518a01e2a0a39966df4ae40b5cbd587da422c'),
       ('iayze', 'iayze', 'iayze', 'scrypt:32768:8:1$Fh9Bada1Tkc9wyBw$fcd9aeb4cb1222a94e2c7690cebf524dfd3b16ec89ea2f99e218a8838645a189776151543dedfc62a93a832cb0ef86dd28c1b3076a8346a697048af9c321425e'),
       ('Ken', 'Carson', 'user00xman', 'scrypt:32768:8:1$J8t5fX5Y7kp2w4kB$e281a0cdca21283d08f54e4474e44109ab8e8e317f90f3856b600321f0491ec6ddf56cfaf0394c0b5b13a3c5b3b25ba5d5d95fd0ac1888bdc574fd70828218d5'),
       ('summrs', 'rino', 'summrsxo', 'scrypt:32768:8:1$vKyTB3XwQdt9qySm$0779c643921ba529b7dc009243ef89e0a1959e1e04258b2461d1cacb56acdac7ddc98a4953f84463ccf5e52966a17340374d6d0e74c93c65781d38df3fd3067e');

INSERT INTO roles (role_name, username, approval)
VALUES ('student', '1hp', 1),
       ('librarian', 'iayze', 0),
       ('admin', 'user00xman', 1),
       ('librarian', 'patrick', 1);

INSERT INTO books (isbn, title, author, quantity)
VALUES
    ('000-0-000-00000-1', 'Diary of a Wimpy Kid', 'Jeff Kinney', 5),
    ('000-0-000-00000-2', 'Diary of a Wimpy Kid: Dog Days', 'Jeff Kinney', 3),
    ('000-0-000-00000-3', 'Diary of a Wimpy Kid: Cabin Fever', 'Jeff Kinney', 2),
    ('000-0-000-00000-4', 'Diary of a Wimpy Kid: Do it Yourself', 'Jeff Kinney', 8),
    ('000-0-000-00000-5', 'Diary of a Wimpy Kid: Rodrick Rules', 'Jeff Kinney', 1),
    ('000-0-000-00000-6', 'Diary of a Wimpy Kid: The Third Wheel', 'Jeff Kinney', 4),
    ('000-0-000-00000-7', 'Green Eggs and Ham', 'Dr. Seuss', 6),
    ('000-0-000-00000-8', 'Captain Underpants', 'Dav Pilkey', 10),
    ('000-0-000-00000-9', 'Magic Tree House', 'Mary Pope Osbourne', 7),
    ('000-0-000-00000-0', 'Harry Potter', 'J.K. Rowling', 2),
    ('100-0-000-00000-1', 'Wocket in my Pocket', 'Dr. Seuss', 3),
    ('100-0-000-00000-2', 'Introduction to C++', 'Wiley', 5),
    ('100-0-000-00000-3', 'Girlfriend on Mars', 'Deborah Willis', 1),
    ('100-0-000-00000-4', 'Of Mice and Men', 'John Steinback', 4),
    ('100-0-000-00000-5', 'Introduction to Orchestra', 'Hans Zimmer', 6),
    ('100-0-000-00000-6', 'How to Kickflip', 'Rodney Mullen', 9),
    ('100-0-000-00000-7', 'Thrasher Magazine', 'Thrasher Skate', 2),
    ('100-0-000-00000-8', 'Project X', 'Ken Carson', 3),
    ('100-0-000-00000-9', 'Self Titled', 'Playboi Carti', 7),
    ('100-0-000-00000-0', 'NOSTYLIST', 'Destroy Lonely', 4);

INSERT INTO rooms (room_num) 
VALUES
    (101),
    (102),
    (103),
    (104),
    (105),
    (201),
    (202),
    (203),
    (204),
    (205),
    (301),
    (302),
    (303),
    (304),
    (305),
    (401),
    (402),
    (403),
    (404),
    (405);


SELECT * FROM users;
SELECT * FROM roles;
SELECT * FROM books;
SELECT * FROM rooms;