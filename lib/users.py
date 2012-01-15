#users.py

import sqlite3

def currentuser(response): # returns user object
  conn = sqlite3.connect('database.sqlitedb')
  cur = conn.cursor()
  username = response.get_cookie('username')
  password = cur.execute("select password from users where username = '%s'" % username)
  n = cur.execute("select id from users where username = '%s'" % username)
  email = cur.execute("select email from users where username = '%s'" % username)
  return User({'username':username, 'password':password, 'n':n, 'email':email})


def isloggedin(response): # returns true if logged in, else false
  if response.get_cookie('username') == None:
    return False
  else:
    return True

def requireuser(response): # returns true if logged in, else redirects to login
  if isloggedin(response):
    return True
  else:
    response.redirect('/login')
    return False

def requirenouser(response): # opposite of requireuser
  if not isloggedin(response):
    return True
  else:
    response.redirect('/')
    return False

class User(object):
  def __init__(self, data):
    self.username = data["username"]
    self.id = data["n"]
    self.email = data["email"]
    self.password = data["password"]

  def get_id(self):
    return self.id

def getmessage(response):
  if response.get_field('message')==None:
    message = ""
  else:
    message = response.get_field('message').replace('+', ' ')
  return message

secret = "you got snailed"
