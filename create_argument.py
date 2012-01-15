from tornado import Server
server = Server()
def create_page(response):
 response.write( '''<html>
  		<head>
  			<title>New Argument</title>
  		</head>
  		
  		<body>
  		<textarea>Title of your argument here:
  			</textarea>
  			<textarea>Please write your statement here:
  			</textarea>
  			<input type = "submit"
  			please write your statement here:="save">
  		
  		</body>
	</html>''')
	
server.register("/argument/create",create_page)
server.run()
