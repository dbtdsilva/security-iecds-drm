#encoding=utf-8
from Crypto import Random
from Crypto.Cipher import AES
import os.path
import cherrypy
import json
from cherrypy.lib import jsontools
from database.storage_api import storage

BLOCK_SIZE = 32
current_dir = os.path.dirname(os.path.abspath(__file__))

SESSION_KEY = 'username'

class API(object):
    def __init__(self):
        self.user = User()
        self.titles = Titles()

class User(object):
    def __init__(self):
        self.login = UserLogin()
        self.logout = UserLogout()

class UserLogin(object):
    exposed = True
    @cherrypy.tools.json_out()
    def POST(self):
        content_length = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(content_length))
        body = json.loads(rawbody)

        if 'username' in body and not storage.is_user_valid(body['username']):
            cherrypy.response.status = 400
            return {"detail": "Provided bad credentials"}
        cherrypy.response.status = 200
        cherrypy.session[SESSION_KEY] = body['username']
        return {"detail": "Login successfully"}
        

class UserLogout(object):
    exposed = True
    @cherrypy.tools.json_out()
    def POST(self):
        if cherrypy.session.get(SESSION_KEY) == None:
            cherrypy.response.status = 400
            return {"detail": "No user was logged in."}
        cherrypy.response.status = 200
        cherrypy.session[SESSION_KEY] = None
        return {"detail": "User logged out."}

class Titles(object):
    exposed = True

    @cherrypy.tools.json_out()
    def GET(self, *vpath):
        if len(vpath) == 0:
            return [ a.to_dict() for a in storage.get_file_list() ]
        userid = vpath[0]
        lrelations = storage.get_user_file_list(userid)
        print lrelations
        flist = []
        for (ufile, filet) in lrelations:
            tmp = filet.to_dict()
            tmp['boughtdate'] = str(ufile.boughtdate)
            flist += [ tmp ] 
        return flist

    @cherrypy.tools.json_in()
    def POST(self, login=False):
        pass

    #def all(sel)f

class Title(object):
    exposed = True

    def GET(self, *vpath):
        item = vpath[0]
        #IV = Random.new().read(BLOCK_SIZE)
        CryptoHeader = '12345678901234567890123456789012'
                #Random.new().read(BLOCK_SIZE)

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

if __name__ == '__main__':
    RESTopts = {
        #'tools.SASessionTool.on': True,
        #'tools.SASessionTool.engine': model.engine,
        #'tools.SASessionTool.scoped_session': model.DBSession,
        #'tools.authenticate.on': True,
        #'tools.is_authorized.on': True,
        #'tools.authorize_admin.on': True,
        'tools.sessions.on': True,
        'tools.json_out.handler': jsontools.json_handler,
        'tools.json_in.processor': jsontools.json_processor,
        'request.dispatch': cherrypy.dispatch.MethodDispatcher()
    }

    cherrypy.server.socket_port = 8080
    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.tree.mount(API(), "/api/", {'/': RESTopts})
    #cherrypy.tree.mount(Root(), "/", "app.config")
    cherrypy.engine.start()
    cherrypy.engine.block()
