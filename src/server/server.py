#encoding=utf-8
import cherrypy

class Root(object):
	pass
#	@cherrypy.expose
#	def index(self):
#		return "Hello"

if __name__ == '__main__':
	cherrypy.server.socket_port = 8080
	cherrypy.server.socket_host = "0.0.0.0"
	cherrypy.tree.mount(Root(), "/", "app.config")
	cherrypy.engine.start()
	cherrypy.engine.block()
