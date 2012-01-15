import sqlite3
import os.path
import inverse_index

conn = sqlite3.connect('database.db')
cur = conn.cursor()

#    cur.execute("DROP TABLE posts")
#    cur.execute("DROP TABLE comments")

cur.executescript ('''
create table posts(
    id integer not null,
    title text not null,
    description text,
    primary key (id),
    unique (title)
);

create table comments(
    id integer not null,
    title text not null,
    description text,
    primary key (id)
);''')

posts = [(0, 'Banana Bread', 'the cat mat maths sat crap comic sans maty database man'),
(1, 'Comic Sans', 'is comic sans a good font?'),
(2, 'Bag Carrying', 'do you carry or wear a backpack?'),
(3, 'Spaces or Tabs?', 'SPACES REIGN SUPREME'),
(4, 'Vim or Emacs?', 'vim is all-powerful')]

comments = [(0, 'Cake', 'Omnomnomnom'),
(3, 'Spaces!', '           '),
(4, 'VIIIIIIIIIIM', 'emacs is an os. it sucks.')]

for a,b,c in posts:
	cur.execute("INSERT INTO posts VALUES (?, ?, ?)", (a,b,c))
	inverse_index.add_text(a, c, 'posts')

for a,b,c in comments:
	cur.execute("INSERT INTO comments VALUES (?, ?, ?)", (a,b,c))
	inverse_index.add_text(a, c, 'comments')

conn.commit()
conn.close()
