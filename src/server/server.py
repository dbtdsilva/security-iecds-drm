#encoding=utf-8
from Crypto import Random
from Crypto.Cipher import AES
import os.path
import cherrypy
from cherrypy.lib import jsontools as json

BLOCK_SIZE = 32
current_dir = os.path.dirname(os.path.abspath(__file__))

class User(object):
	exposed = True

	@cherrypy.tools.json_out()
	def GET(self, dsid=None):
		return []

class Titles(object):
	exposed = True

	@cherrypy.tools.json_out()
	def GET(self, dsid=None):
		return []

	@cherrypy.tools.json_in()
	def POST(self, login=False):
		pass

class Title(object):
	exposed = True

	def GET(self, *vpath):
		item = vpath[0]
		#IV = Random.new().read(BLOCK_SIZE)
		CryptoHeader = '12345678901234567890123456789012'	#Random.new().read(BLOCK_SIZE)

		UserKey = '12345678901234567890123456789012'
		DeviceKey = '12345678901234567890123456789012'
		PlayerKey = '12345678901234567890123456789012'

		aes = AES.new(CryptoHeader, AES.MODE_ECB)
		CrypDevKey = aes.encrypt(DeviceKey)
		aes = AES.new(CrypDevKey, AES.MODE_ECB)
		CrypDevUserKey = aes.encrypt(UserKey)
		aes = AES.new(CrypDevUserKey, AES.MODE_ECB)
		FileKey = aes.encrypt(PlayerKey)

		aes = AES.new(FileKey, AES.MODE_ECB)

		print FileKey
		f = open('media/news_interview.wmv', 'r')

		dataEncrypted = ""
		data = f.read(BLOCK_SIZE)
		while data:
			if len(data) < BLOCK_SIZE:
				dataEncrypted += data
			else:
				dataEncrypted += aes.encrypt(data)
			data = f.read(BLOCK_SIZE)
		return dataEncrypted

class Root(object):
	pass
#	@cherrypy.expose
#	def index(self):
#		return "Hello"

if __name__ == '__main__':
	RESTopts = {
        #'tools.SASessionTool.on': True,
        #'tools.SASessionTool.engine': model.engine,
        #'tools.SASessionTool.scoped_session': model.DBSession,
        #'tools.authenticate.on': True,
        #'tools.is_authorized.on': True,
        #'tools.authorize_admin.on': True,
        'tools.json_out.handler': json.json_handler,
        'tools.json_in.processor': json.json_processor,
        'request.dispatch': cherrypy.dispatch.MethodDispatcher()
    }

	cherrypy.server.socket_port = 8080
	cherrypy.server.socket_host = "0.0.0.0"
	cherrypy.tree.mount(Titles(), "/api/titles", {'/': RESTopts})
	cherrypy.tree.mount(Title(), "/api/title", {'/': RESTopts})
	cherrypy.tree.mount(Root(), "/", "app.config")
	cherrypy.engine.start()
	cherrypy.engine.block()
