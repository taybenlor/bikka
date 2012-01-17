from pg8000 import sqlite
import os.path
import os
import urlparse
import inverse_index

url = urlparse.urlparse(os.environ['DATABASE_URL'])
config = {
    'NAME':     url.path[1:],
    'USER':     url.username,
    'PASSWORD': url.password,
    'HOST':     url.hostname,
    'PORT':     url.port
}

conn = DBAPI.connect(host=config['HOST'], user=config['USER'], password=config['PASSWORD'], database=config["NAME"])

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
);'''
cur.execute('''
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
