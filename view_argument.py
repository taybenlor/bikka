from tornado import Server
import sqlite3
from lib import template
server = Server()
conn = sqlite3.connect('database.sqlitedb')
cur = conn.cursor()


def argument_page(response):
  id = response.get_field("id")
  response.write(template.render_file("viewarg.html" ,"rU"))
  cur.execute("""insert into comments ("post_id","user_id", "description", agree) values(
   '%s',null,"comment",1)""" % id)
  
def comment(response):
  comment = get_field("comment_textbox")	
	

server.register("/argument/view",argument_page)
server.register("/argument/comment",comment)
server.run()
