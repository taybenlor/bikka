#!/usr/bin/env python

from os import path, environ
from tornado import Server
from lib import template
import ranker
import database
import re
import sqlite3
import hashlib
import Cookie
from lib.users import *
from lib.search import *
import sys

conn = sqlite3.connect('database.sqlitedb')
cur = conn.cursor()

def index(response):
  arguments = ranker.rankerTime() #rankByAll doubles up all the posts
  data = {'arguments': arguments, 'message':getmessage(response), 'isloggedin':isloggedin(response), "username": currentuser(response).username}
  response.write(template.render_file('templates/feed/index.html', data))

def login(response):
  if requirenouser(response):
    data = {'message':getmessage(response), 'isloggedin':isloggedin(response), "username": currentuser(response).username}
    response.write(template.render_file('templates/user/login.html', data))

def addargument(response):
  data = {'message':getmessage(response),'isloggedin':isloggedin(response), "username": currentuser(response).username}
  title = response.get_field("arg_title")
  statement = response.get_field("statement")
  userid = currentuser(response).get_id() if isloggedin(response) else 0
  cur.execute('insert into posts (title, description, time, user_id) values (?, ?, datetime(), ?)', (title, statement, userid))
  conn.commit()
  response.redirect('/?message=Argument+created.')

  # add to the index
  cur.execute('select id from posts order by id desc limit 1')
  post_id = int(cur.fetchone()[0])
  add_text(post_id, statement, 'posts')

def view_argument(response, argument_id):
  cur.execute('select * from posts where id=?', (argument_id,))
  argument = cur.fetchone()
  response.write(template.render_file('templates/viewarg.html', {'argument': argument, 'message': getmessage(response), 'isloggedin': isloggedin(response)}))

def register(response):
  newusername = response.get_field('newusername')
  newpassword = response.get_field('newpassword')
  confpassword = response.get_field('confpassword')
  email = response.get_field('email')
  print "Data received."
  if newusername == None or newpassword == None or confpassword == None or email == None:
    print 'Registration failed: Blank field'
    message = 'You+must+fill+in+all+fields!'
    failure = True
  elif confpassword != newpassword:
    print 'Registration failed: Confirm password does not match'
    message = 'Passwords+do+not+match!'
    failure = True
  elif cur.execute("select count(*) from users where username = '%s'" % newusername).fetchone()[0]:
    print "Registration failed: Username already exists."
    message = 'Username+already+in+use!'
    failure = True
  elif cur.execute("select count(*) from users where email = '%s'" % email).fetchone()[0]:
    print 'Registration failed: Email already exists'
    message = 'Email+already+in+use!'
    failure = True
  elif not re.match(r'[^@]+@[^@]+\.[^@]', email):
    print 'Registration failed: Email not valid'
    message = 'Email+not+valid!'
    failure = True
  else:
    message = 'Thankyou+for+registering.'
    failure = False
  if failure == False:
    response.redirect('/?message='+message)
    # user => database
    hashpw = hashlib.md5(newpassword).hexdigest()
    print "Password hashed."
    cur.execute('''insert into users (username,password,email)values('%s','%s','%s')''' %(newusername,hashpw,email))
    conn.commit()
  else:
    response.redirect('/login?message='+message)

def dologin(response):
  data = {'message' : getmessage(response)}
  username = response.get_field('username')
  password = response.get_field('password')
  if username == None or password == None:
    print 'Registration failed: Blank field'
    response.redirect('/login?message=You+must+fill+in+all+fields!')
  else:
    hashpwd = hashlib.md5(password).hexdigest()
    if cur.execute("select count(*) from users where username = '%s' and password = '%s'" % (username,hashpwd)).fetchone()[0]:
      # add a cookie!
      response.set_cookie("username", username, path='/')
      response.set_cookie("userhash", hashlib.md5(username+secret).hexdigest(), path="/")
      u = response.get_cookie("username")
      response.redirect('/?message=Login+successful.')
    else:
      response.redirect('/login?message=Incorrect+username/password+combination!')

def logout(response):
  response.clear_cookie('username', path='/')
  response.clear_cookie('userhash', path='/')
  response.redirect('/?message=You+have+been+logged+out.')


def create_page(response):
  data = {'message':getmessage(response), 'isloggedin':isloggedin(response), "username": currentuser(response).username }
  response.write(template.render_file('templates/addargument.html', data))

def save_comments(response):

    if agree:
        agreeordis = True
    else:
        agreeordis = False

    post_id = response.get_field('post_id')

    with sqlite3.connect('database.sqlitedb') as conn:
        no_comments= conn.execute("""
                select comments from post where user_id = ?
                """, currentuser().get_id())
    no_comment += 1

    with sqlite3.connect('database.sqlitedb') as conn:
        no_comments= conn.execute("""
                supadate comments
                """)

    with sqlite3.connect('database.sqlitedb') as conn:
        user = conn.execute("""
                select id from users where username = ?
                """, currentuser().get_id())

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

    # add to the index
    cur.execute('select id from comments order by id desc limit 1')
    post_id = int(cur.fetchone()[0])
    add_text(post_id, remark, 'comments')

def custom404(response, page_name):
    response.set_status(404)
    response.write(template.render_file("static/404.html", {'isloggedin': isloggedin(response)}))

def profile(response, view):
    view = response.get_field("view")
    cur.execute("select dp from users where username = '%s'" % view)
    dp = cur.fetchone()
    if dp == None:
      dp = "/static/placeholderdp.png"
    cur.execute("select bio from users where username = '%s'" % view)
    bio = cur.fetchone()
    data = {'message':getmessage(response), 'isloggedin':isloggedin(response), "view":view, "username":currentuser(response).username, "dp":dp, "bio":bio}
    response.write(template.render_file("templates/user/profiles.html", data))

def search_handler(response):
    query = response.get_field('query')
    data = {'isloggedin': isloggedin(response), 'results': search(query)}
    response.write(template.render_file("templates/search_result.html", data))

if len(sys.argv) == 2:
    port_s = sys.argv[1]
    if not port_s.isdigit():
        print 'ERROR: Port must be a number'
        quit()
    server = Server(port=int(port_s))
else:
    server = Server()


server.register('/', index)
server.register('/login', login)
server.register('/register', register)
server.register('/dologin', dologin)
server.register('/logout', logout)
server.register("/argument/create",create_page)
server.register("/argument/docreate",addargument)
server.register("/search",search_handler)
server.register("/argument/(\d+)", view_argument)
server.register("/profile?(.*)", profile)
server.register("/(.*)", custom404)
server.run()
