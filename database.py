import sqlite3
import os.path

if not os.path.exists('database.sqlitedb'):

    conn = sqlite3.connect('database.sqlitedb')
    cur = conn.cursor()

    cur.executescript (file('db.sql').read())
    conn.commit()
