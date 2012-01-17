#!/usr/bin/env python

from os import path, environ
from tornado import Server
from lib import template
import ranker
import database
import re
from pg8000 import DBAPI as sqlite3
import hashlib
import urllib
import Cookie
from lib.users import *
from lib.search import *
import sys
from PIL import Image
import cStringIO
import datetime
import os, urlparse


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

def index(response):
  arguments = ranker.rankerTime() #rankByAll doubles up all the posts

  def percentages(argument_id):
    cur.execute("SELECT COUNT(*)  FROM comments WHERE post_id = ?", (str(argument_id),))
    no_of_comments=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) from comments where post_id = ? and agree = 'False'", (str(argument_id),))
    no_of_true = cur.fetchone()[0]
    no_of_false = no_of_comments - no_of_true
    try:
      percentage_false = float(no_of_false)/no_of_comments*100
      percentage_true = 100-percentage_false
    except:
      percentage_false, percentage_true = 0,0
    return percentage_true, percentage_false

  arguments = [argument + percentages(argument[0]) for argument in arguments]

  data = {'arguments': arguments, 'message':getmessage(response), 'isloggedin':isloggedin(response), "username": currentuser(response).username,
          'fix_date': (lambda old: (datetime.datetime.strptime(old, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(11.0/24.0)).strftime('%Y-%m-%d %H:%M:%S'))}
  response.write(template.render_file('templates/feed/index.html', data))

def login(response):
  if requirenouser(response):
    data = {'message':getmessage(response), 'isloggedin':isloggedin(response), "username": currentuser(response).username}
    response.write(template.render_file('templates/user/login.html', data))

import time
history = {}
TIMER = 2000

def addargument(response):
  requireuser(response)
  data = {'message':getmessage(response),'isloggedin':isloggedin(response), "username": currentuser(response).username}
  title = response.get_field("arg_title")
  statement = response.get_field("statement")
  userid = currentuser(response).id if isloggedin(response) else 0
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
  cur.execute('select c.post_id, c.description, c.agree, u.username from comments c, users u where post_id=? and c.user_id = u.id', (argument_id,))
  comments = cur.fetchall()
  cur.execute("SELECT COUNT(*)  FROM comments WHERE post_id = ?", (argument_id,))
  no_of_comments=cur.fetchone()[0]
  cur.execute("SELECT COUNT(*) from comments where post_id = ? and agree = 'False'", (argument_id,))
  no_of_true = cur.fetchone()[0]
  no_of_false = no_of_comments - no_of_true
  #percentage_true = round(float(no_of_true)/float(no_of_comments)*100)
  #percentage_false = 100-percentage_true
  try:
	percentage_false = float(no_of_false)/no_of_comments*100
	percentage_true = 100-percentage_false
  except:
	percentage_false, percentage_true = 0,0
  response.write(template.render_file('templates/viewarg.html', {
  	  'argument': argument,
	  'comments': comments,
  	  'message': getmessage(response), 
  	  'isloggedin': isloggedin(response), 
  	  'username':currentuser(response).username,
	  'score':(percentage_true,percentage_false)}))


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
  elif cur.execute("select count(*) from users where username = ?", (newusername,)).fetchone()[0]:
    print "Registration failed: Username already exists."
    message = 'Username+already+in+use!'
    failure = True
  elif cur.execute("select count(*) from users where email = ?", (email,)).fetchone()[0]:
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
    # response.redirect('/?message='+message)
    # user => database
    hashpw = hashlib.md5(newpassword).hexdigest()
    print "Password hashed."
    cur.execute('''insert into users (username,password,email)values(?,?,?)''', (newusername,hashpw,email))
    conn.commit()
    setcookie(response,newusername)
    response.redirect('/?message='+message)
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
    if cur.execute("select count(*) from users where username = ? and password = ?", (username,hashpwd)).fetchone()[0]:
      # add a cookie!
      setcookie(response,username)
      u = response.get_cookie("username")
      response.redirect('/?message=Login+successful.')
    else:
      response.redirect('/login?message=Incorrect+username/password+combination!')

def logout(response):
  response.clear_cookie('username', path='/')
  response.clear_cookie('userhash', path='/')
  response.redirect('/?message=You+have+been+logged+out.')


def create_page(response):
  requireuser(response)
  data = {'message':getmessage(response), 'isloggedin':isloggedin(response), "username": currentuser(response).username }
  response.write(template.render_file('templates/addargument.html', data))

def save_comments(response):
    agree = response.get_field('agree') == "Yay"
    post_id = response.get_field('post_id')
    user_id = currentuser(response).get_id()
    comment = response.get_field('comment')
    print user_id
    cur.execute("""insert into comments (post_id, user_id, description, agree) values (?, ?, ?, ?)""", (post_id,str(user_id),comment,str(agree)))
    conn.commit()
    cur.execute("update posts set comments = comments + 1 where id = ?", (post_id,))
    conn.commit()
    response.redirect("/argument/" + post_id)

    # add to the index
    cur.execute('select id from comments order by id desc limit 1')
    comment_id = int(cur.fetchone()[0])
    add_text(comment_id, comment, 'comments')

def custom404(response, page_name):
    response.set_status(404)
    response.write(template.render_file("static/404.html", {'isloggedin': isloggedin(response), "username": currentuser(response).username}))

def profile(response, view):
    if cur.execute("select count(*) from users where username = ?", (view,)).fetchone()[0]:
      cur.execute("select dp from users where username = ?", (view,))
      dp = cur.fetchone()[0]
      if dp == None:
        dp = "/static/placeholderdp.png"
      cur.execute("select bio from users where username = ?", (view,))
      bio = cur.fetchone()[0]

      follower = is_follower(response, view)
      data = {'message':getmessage(response), 'isloggedin':isloggedin(response), "view":view, "username":currentuser(response).username, "dp":dp, "bio":bio, "is_follower":follower}
      response.write(template.render_file("templates/user/profiles.html", data))
    else:
      response.redirect("/?message=No+such+user!")

def follow(response):
    view = response.get_field('other_name')
    to_follow = eval(response.get_field('to_follow'))
    current_user = currentuser(response).username

    if to_follow == True:
        cur.execute("INSERT INTO followers VALUES (?, ?)", (current_user, view))
    else:
    	cur.execute("DELETE FROM followers WHERE follower_id = ? AND followee_id = ?", (current_user, view))
    conn.commit()
    response.redirect('/profile/' + view)

def is_follower(response, view):
    current_user = currentuser(response).username
    cur.execute("SELECT * FROM followers WHERE follower_id = ? AND followee_id = ?", (current_user, view))
    matches = cur.fetchall()
    if len(matches) > 0:
    	return True
    return False

def search_handler(response):
    query = response.get_field('query')
    data = {'isloggedin': isloggedin(response), 'results': search(query), 'query':query, 'username': currentuser(response).username}
    response.write(template.render_file("templates/search_result.html", data))

if len(sys.argv) == 2:
    port_s = sys.argv[1]
    if not port_s.isdigit():
        print 'ERROR: Port must be a number'
        quit()
    server = Server(port=int(port_s))
else:
    server = Server()

def editprofile(response):
  data = {'message':getmessage(response), 'isloggedin':isloggedin(response), "username":currentuser(response).username, "bio":currentuser(response).bio[0]}
  response.write(template.render_file("templates/user/editprofile.html", data))

def editprofile_cont(response):
  username = currentuser(response).username
  newbio = response.get_field('editbio')
  newdp = response.get_field('dpurl')
  try:
    imgfile = urllib.urlopen(newdp)
    im = cStringIO.StringIO(imgfile.read())
  except:
    pass
    
  width, height = (0, 0)
  
  if newbio == None and newdp == None:
    response.redirect("/editprofile?message=You+must+fill+in+some+fields!")
  elif newdp == None:
    # update bio
    cur.execute("update users set bio = ? where username = ?", (newbio, username))
    response.redirect("/profile/"+username)
  elif width > 200 or height > 300:
    response.redirect("/editprofile?message=Maximum+image+size+is+200x300px.")
  elif newbio == None:
    # update dp
    cur.execute("update users set dp = ? where username = ?", (newdp, username))
    response.redirect("/profile/"+username)
  else:
    # update all
    cur.execute("update users set bio = ? where username = ?", (newbio, username))
    cur.execute("update users set dp = ? where username = ?", (newdp, username))
    response.redirect("/profile/"+username)

def setcookie(response, username):
  response.set_cookie("username", username, path='/')
  response.set_cookie("userhash", hashlib.md5(username+secret).hexdigest(), path="/")
  print "Baking cookies for ?.", username
    

#create_index()
server.register('/', index)
server.register('/login', login)
server.register('/register', register)
server.register('/dologin', dologin)
server.register('/logout', logout)
server.register("/argument/create",create_page)
server.register("/argument/docreate",addargument)
server.register("/comment/add",save_comments)
server.register("/search",search_handler)
server.register("/argument/(\d+)", view_argument)
server.register("/profile/(.*)", profile)
server.register("/follow", follow)
server.register("/editprofile", editprofile)
server.register("/editprofile_cont", editprofile_cont)
server.register("/(.*)", custom404)
server.run()
