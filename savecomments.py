from pg8000 import DBAPI as sqlite3

def save_comments(response):
    #description = comment_textbox
    #agree ==> put a 1 in the database, else put a 0
    #find out post id of this arguement (should be in table)
    #find out user id ...

    #also need to update the posts database to add a count to number of commments

    if agree:
        agreeordis = True
    else:
        agreeordis = False

    post_id = response.get_field('post_id')

    with sqlite3.connect('database.sqlitedb') as conn:
        user = conn.execute("""
                select id from users where username = ?
                """, get_logged_in_user()) # TODO
    
    with sqlite3.connect('database.sqlitedb') as conn:
       post = conn.execute("""
                select post_id from posts where username = ?
                """, post_id)

    with sqlite3.connect('database.sqlitedb') as conn:
        cur = conn.execute("""
                insert into comments
                values (post_id = ?, user_id = ?, description = ?,
                agree = ?)
                """, (post,user,remark,agreeordis))
