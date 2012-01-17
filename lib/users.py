#users.py

from pg8000 import DBAPI as sqlite3

import os, urlparse

def currentuser(response): # returns user object
  url = urlparse.urlparse(os.environ['DATABASE_URL'])
  config = {
      'NAME':     url.path[1:],
      'USER':     url.username,
      'PASSWORD': url.password,
      'HOST':     url.hostname,
      'PORT':     url.port
  }

  conn = sqlite3.connect(host=config['HOST'], user=config['USER'], password=config['PASSWORD'], database=config["NAME"])
  
  cur = conn.cursor()
  username = response.get_cookie('username') 
  cur.execute("select password from users where username = '%s';" % username)
  password = cur.fetchone()
  cur.execute("select id from users where username = ?;", (username,))
  n = cur.fetchone()
  n = n[0] if n else None
  cur.execute("select email from users where username = '%s';" % username)
  email = cur.fetchone()
  cur.execute("select bio from users where username = '%s';" % username)
  bio = cur.fetchone()
  return User({'username':username, 'password':password, 'n':n, 'email':email, 'bio':bio})


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
    self.bio = data["bio"]

  def get_id(self):
    return self.id

def getmessage(response):
  if response.get_field('message')==None:
    message = ""
  else:
    message = response.get_field('message').replace('+', ' ')
  return message

secret = "you got snailed"
