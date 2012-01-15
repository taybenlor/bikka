import sqlite3

def rankerComment():
    with open_db() as conn:
        cur = conn.execute("""
            select id, title, time, comments
            from posts
            order by comments desc
            limit 10
            """)
        return cur.fetchall()
    
def rankerTime():
    with open_db() as conn:
        cur = conn.execute("""
            select id, title, time, comments
            from posts
            order by time desc
            limit 10
            """)
        return cur.fetchall()

def rankByAll():
    return rankerTime() + rankerComment()
    

def open_db():
    return sqlite3.connect('database.sqlitedb')

def test():
    with open_db() as conn:
        cur = conn.execute("""
        create table if not exists arguments (
        arg_name text not null default '',
        no_comments integer not null default 0,
        time_posted integer not null default 01012000120000) 
        """)
        cur = conn.execute("""
        insert into arguments values ('One', 13, 021219990300)
        """)
        cur = conn.execute("""
        insert into arguments values ('Two', 18, 021219990300)
        """)

if __name__ == "__main__":
    test()