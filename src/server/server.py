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

# -> API DETAILS
# POST /api/user/login username=user
# Details: Creates a session

# POST /api/user/logout
# Details: Logout the current user

# GET  /api/title/all
# Details: Gets all titles available to be bought

# GET  /api/title/user                              # Requires login
# Details: Gets all titles that the user bought

# POST  /api/title/<pk>                             # Requires login
# Details: Buys a specific title

# GET  /api/title/<pk>                              # Requires login
# Details: Downloads a specific title encrypted (must have been bought
# before)

# POST /api/title/validate/<pk> key=current_result  # Requires login
# Details: Sends the current cipher result key to the server to process
# with user key

class API(object):
    def __init__(self):
        self.user = User()
        self.title = Title()

class User(object):
    def __init__(self):
        self.login = UserLogin()
        self.logout = UserLogout()

class UserLogin(object):
    exposed = True
    @cherrypy.tools.json_out()
    def POST(self):
        content_length = cherrypy.request.headers['Content-Length']
        raw_body = cherrypy.request.body.read(int(content_length))
        body = json.loads(raw_body)

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

class Title(object):
    exposed = True
    def __init__(self):
        self.all = TitleAll()
        self.user = TitleUser()
        self.validate = TitleValidate()

    @cherrypy.tools.json_out()
    def GET(self, title):
        pass

    @cherrypy.tools.json_out()
    def POST(self, title):
        pass

class TitleValidate(object):
    exposed = True

    @cherrypy.tools.json_out()
    def GET(self, title):
        if cherrypy.session.get(SESSION_KEY) == None:
            cherrypy.response.status = 400
            return {"detail": "Requires authentication"}
        username = cherrypy.session.get(SESSION_KEY)
        userid = storage.get_user_id(username)

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

class TitleUser(object):
    exposed = True

    @cherrypy.tools.json_out()
    def GET(self):
        if cherrypy.session.get(SESSION_KEY) == None:
            cherrypy.response.status = 400
            return {"detail": "Requires authentication"}
        username = cherrypy.session.get(SESSION_KEY)
        userid = storage.get_user_id(username)
        lrelations = storage.get_user_file_list(userid)
        print lrelations
        flist = []
        for (ufile, filet) in lrelations:
            tmp = filet.to_dict()
            tmp['boughtdate'] = str(ufile.boughtdate)
            flist += [ tmp ]
        return flist

class TitleAll(object):
    exposed = True

    @cherrypy.tools.json_out()
    def GET(self):
        return [ a.to_dict() for a in storage.get_file_list() ]

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
