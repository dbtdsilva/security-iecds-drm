#encoding=utf-8
from Crypto import Random
from Crypto.Cipher import AES
import os.path
import cherrypy
import json
from cherrypy.lib import jsontools
from database.storage_api import storage
import binascii

BLOCK_SIZE = 32
current_dir = os.path.dirname(os.path.abspath(__file__))

SESSION_KEY = 'username'
SESSION_DEVICE = 'device_key'

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

    # POST /api/user/login username=user
    # Details: Creates a session
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
        if 'key' in body:
            if len(body['key']) != BLOCK_SIZE * 2:
                cherrypy.response.status = 400
                return {"detail": "Key is not valid"}
            cherrypy.session[SESSION_DEVICE] = binascii.unhexlify(body['key'])
            username = cherrypy.session.get(SESSION_KEY)
            user_id = storage.get_user_id(username)
            storage.associate_device_to_user(user_id, cherrypy.session.get(SESSION_DEVICE))
        return {"detail": "Login successfully"}
        

class UserLogout(object):
    exposed = True

    # POST /api/user/logout
    # Details: Logout the current user
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

    # GET  /api/title/<pk>                              
    # Requires login
    # Details: Downloads a specific title encrypted (must have been bought
    # before)
    def GET(self, title):
        if cherrypy.session.get(SESSION_KEY) == None:
            cherrypy.response.status = 400
            return {"detail": "Requires authentication"}
        username = cherrypy.session.get(SESSION_KEY)
        user_id = storage.get_user_id(username)
        if not storage.user_has_title(user_id, title):
            cherrypy.response.status = 400
            return {"detail": "Current user didn't buy this title"}
        content_length = cherrypy.request.headers['Content-Length']
        raw_body = cherrypy.request.body.read(int(content_length))
        body = json.loads(raw_body)

        seed_only = False
        if 'seed_only' in body and (body['seed_only'] == '1' or 
                                    body['seed_only'] == 'true' or
                                    body['seed_only'] == 'True'):
            seed_only = True

        file_key = storage.get_file_key(user_id, title)
        user_key = storage.get_user_details(user_id).userkey
        device_key = cherrypy.session.get(SESSION_DEVICE)
        player_key = '\xb8\x8b\xa6Q)c\xd6\x14/\x9dpxc]\xff\x81L\xd2o&\xc2\xd1\x94l\xbf\xa6\x1d\x8fA\xdee\x9c'

        if file_key == None:
            # first time that a file was requested, must generate seed
            seed = Random.new().read(BLOCK_SIZE)

            if device_key == None:
                cherrypy.response.status = 400
                return {"detail": "Player used to download didn't report the device."}
            seed_dev_key = AES.new(device_key, AES.MODE_ECB).encrypt(seed)
            seed_dev_user_key = AES.new(user_key, AES.MODE_ECB).encrypt(seed_dev_key)
            # Player key is hardcoded for now, but we want to share it using the certificate
            file_key = AES.new(player_key, AES.MODE_ECB).encrypt(seed_dev_user_key)
            file_key = storage.update_file_key(file_key, title, user_id)
        else:
            seed_dev_user_key = AES.new(player_key, AES.MODE_ECB).decrypt(file_key)
            seed_dev_key = AES.new(user_key, AES.MODE_ECB).decrypt(seed_dev_user_key)
            seed = AES.new(device_key, AES.MODE_ECB).decrypt(seed_dev_key)
        
        if seed_only:
            return seed
            
        f = open("media/" + storage.get_tile_details(title).path, 'r')
        aes = AES.new(file_key, AES.MODE_ECB)

        dataEncrypted = seed
        data = f.read(BLOCK_SIZE)
        while data:
            if len(data) < BLOCK_SIZE:
                # TODO with PCKS#7
                dataEncrypted += data
            else:
                dataEncrypted += aes.encrypt(data)
            data = f.read(BLOCK_SIZE)
        return dataEncrypted

    # POST  /api/title/<pk>                             
    # Requires login
    # Details: Buys a specific title
    @cherrypy.tools.json_out()
    def POST(self, title):
        if cherrypy.session.get(SESSION_KEY) == None:
            cherrypy.response.status = 400
            return {"detail": "Requires authentication"}
        username = cherrypy.session.get(SESSION_KEY)
        user_id = storage.get_user_id(username)

        storage.buy_file(user_id, title)
        return {"detail": "Title was successfully purchased"}

class TitleValidate(object):
    exposed = True

    # POST /api/title/validate/<pk> key=current_result  
    # Requires login
    # Details: Sends the current cipher result key to the server to process
    # with user key
    def POST(self, title):
        if cherrypy.session.get(SESSION_KEY) == None:
            cherrypy.response.status = 400
            return {"detail": "Requires authentication"}
        username = cherrypy.session.get(SESSION_KEY)
        user_id = storage.get_user_id(username)
        if not storage.user_has_title(user_id, title):
            cherrypy.response.status = 400
            return {"detail": "Current user didn't buy this title"}

        content_length = cherrypy.request.headers['Content-Length']
        raw_body = cherrypy.request.body.read(int(content_length))
        body = json.loads(raw_body)
        if 'key' not in body:
            cherrypy.response.status = 400
            return {"detail": "You must provide your current key"}

        user_key = storage.get_user_details(user_id).userkey
        next_key = AES.new(user_key, AES.MODE_ECB).encrypt(body['key'])
        return next_key

class TitleUser(object):
    exposed = True

    # GET  /api/title/user                              
    # Requires login
    # Details: Gets all titles that the user bought
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

    # GET  /api/title/all
    # Details: Gets all titles available to be bought
    @cherrypy.tools.json_out()
    def GET(self):
        abc = cherrypy
        return [ a.to_dict() for a in storage.get_file_list() ]

class Root(object):
    pass

if __name__ == '__main__':
    RESTopts = {
        'tools.sessions.on': True,
        'tools.json_out.handler': jsontools.json_handler,
        'tools.json_in.processor': jsontools.json_processor,
        'request.dispatch': cherrypy.dispatch.MethodDispatcher()
    }

    cherrypy.server.socket_port = 443
    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.server.ssl_module = 'pyopenssl'
    cherrypy.server.ssl_certificate = 'certificates/Security_P3G1_SSL.crt'
    cherrypy.server.ssl_private_key = 'certificates/Security_P3G1_SSL_key.pem'
    cherrypy.tree.mount(API(), "/api/", {'/': RESTopts})
    cherrypy.tree.mount(Root(), "/", "app.config")
    cherrypy.engine.start()
    cherrypy.engine.block()
