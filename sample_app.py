from tornado import Server

from lib import template

def index(response):
	data = {'name': 'Ben', 'arguments': ['Is banana bread cake or bread?', 'another argument']}
	output = template.render_file('sample/test.html', data)
	response.write(output)

def login(response):
	name = response.get_field('name')
	data = {'name': name}
	output = template.render_file('sample/login.html', data)
	response.write(output)

server = Server()
server.register('/', index)
server.register('/login', login)
server.run()

