#encoding=utf-8
from Crypto import Random
from Crypto.Cipher import AES
import os.path
import cherrypy.wsgiserver.ssl_builtin
import json
from cherrypy.lib import jsontools
from database.storage_api import storage
import binascii
from checker import require, logged, device_key, SESSION_DEVICE, SESSION_USERID, jsonify_error

BLOCK_SIZE = 32
current_dir = os.path.dirname(os.path.abspath(__file__))

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

    # POST /api/user/login {username=user, key=dkey}
    # Details: Creates a session
    @cherrypy.tools.json_out()
    def POST(self):
        try:
            content_length = cherrypy.request.headers['Content-Length']
            raw_body = cherrypy.request.body.read(int(content_length))
            body = json.loads(raw_body)
        except Exception:
            raise cherrypy.HTTPError(400, "Wrong format")

        if 'username' in body and not storage.is_user_valid(body['username']):
            raise cherrypy.HTTPError(400, "Provided bad credentials")
        if 'key' in body:
            if len(body['key']) != BLOCK_SIZE * 2:
                raise cherrypy.HTTPError(400, "Key is not valid")
            cherrypy.session[SESSION_DEVICE] = binascii.unhexlify(body['key'])
            username = cherrypy.session.get(SESSION_USERID)
            user_id = storage.get_user_id(username)
            storage.associate_device_to_user(user_id, cherrypy.session.get(SESSION_DEVICE))
        cherrypy.session[SESSION_USERID] = storage.get_user_id(body['username'])
        cherrypy.response.status = 200
        return {"detail": "Login successfully"}
        

class UserLogout(object):
    exposed = True

    # POST /api/user/logout
    # Details: Logout the current user
    @cherrypy.tools.json_out()
    @require(logged())
    def POST(self):
        cherrypy.response.status = 200
        cherrypy.session[SESSION_USERID] = None
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
    @require(logged(), device_key())
    def GET(self, title, seed_only = False):
        if seed_only == '1' or seed_only == 'True' or seed_only == 'true':
            seed_only = True
        user_id = cherrypy.session.get(SESSION_USERID)
        if not storage.user_has_title(user_id, title):
            raise cherrypy.HTTPError(400, "Current user didn't buy this title")

        file_key = storage.get_file_key(user_id, title)
        user_key = storage.get_user_details(user_id).userkey
        device_key = cherrypy.session.get(SESSION_DEVICE)
        player_key = '\xb8\x8b\xa6Q)c\xd6\x14/\x9dpxc]\xff\x81L\xd2o&\xc2\xd1\x94l\xbf\xa6\x1d\x8fA\xdee\x9c'

        if file_key == None:
            # first time that a file was requested, must generate seed
            seed = Random.new().read(BLOCK_SIZE)
            seed_dev_key = AES.new(device_key, AES.MODE_ECB).encrypt(seed)
            seed_dev_user_key = AES.new(user_key, AES.MODE_ECB).encrypt(seed_dev_key)
            # Player key is hardcoded for now, but we want to share it using the certificate
            file_key = AES.new(player_key, AES.MODE_ECB).encrypt(seed_dev_user_key)
            file_key = storage.update_file_key(file_key, title, user_id)
        else:
            seed_dev_user_key = AES.new(player_key, AES.MODE_ECB).decrypt(file_key)
            seed_dev_key = AES.new(user_key, AES.MODE_ECB).decrypt(seed_dev_user_key)
            seed = AES.new(device_key, AES.MODE_ECB).decrypt(seed_dev_key)

        print "Player key", binascii.hexlify(player_key)
        print "User key: ", binascii.hexlify(user_key)
        print "Device key: ", binascii.hexlify(device_key)
        print "File Key: ", binascii.hexlify(file_key)
        print "Seed: ", binascii.hexlify(seed)
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
    @require(logged())
    def POST(self, title):
        storage.buy_file(cherrypy.session.get(SESSION_USERID), title)
        return {"detail": "Title was successfully purchased"}

class TitleValidate(object):
    exposed = True

    # POST /api/title/validate/<pk> key=current_result  
    # Requires login
    # Details: Sends the current cipher result key to the server to process
    # with user key
    @require(logged())
    def POST(self, title):
        user_id = cherrypy.session.get(SESSION_USERID)
        if not storage.user_has_title(user_id, title):
            raise cherrypy.HTTPError(400, "Current user didn't buy this title")

        try:
            content_length = cherrypy.request.headers['Content-Length']
            raw_body = cherrypy.request.body.read(int(content_length))
            body = json.loads(raw_body)
            if 'key' not in body:
                raise Exception()
            key_val = body['key']
        except Exception:
            raise cherrypy.HTTPError(400, "Current key wasn't provided")

        user_key = storage.get_user_details(user_id).userkey
        next_key = AES.new(user_key, AES.MODE_ECB).encrypt(binascii.unhexlify(key_val))
        return next_key

class TitleUser(object):
    exposed = True
    def __init__(self):
        self.all = TitleUserAll()

    # GET  /api/title/user                              
    # Requires login
    # Details: Gets all titles that the user bought
    @cherrypy.tools.json_out()
    @require(logged())
    def GET(self):
        return storage.get_user_file_list(cherrypy.session.get(SESSION_USERID))

class TitleUserAll(object):
    exposed = True

    # GET  /api/title/user
    # Requires login
    # Details: Gets all titles that the user bought
    @cherrypy.tools.json_out()
    @require(logged())
    def GET(self):
        return storage.get_user_file_list(cherrypy.session.get(SESSION_USERID), True)

class TitleAll(object):
    exposed = True

    # GET  /api/title/all
    # Details: Gets all titles available to be bought
    @cherrypy.tools.json_out()
    def GET(self):
        return [ a.to_dict() for a in storage.get_file_list() ]

class Root(object):
    pass

if __name__ == '__main__':
    RESTopts = {
        'tools.sessions.on': True,
        'tools.checker.on': True,
        'error_page.default': jsonify_error,
        'tools.json_out.handler': jsontools.json_handler,
        'tools.json_in.processor': jsontools.json_processor,
        'request.dispatch': cherrypy.dispatch.MethodDispatcher()
    }

    key = "certificates/Security_P3G1_SSL_key.pem"
    cert = "certificates/Security_P3G1_SSL.crt"
    root = "certificates/Security_P3G1_Root.crt"


    from OpenSSL.SSL import *
    import OpenSSL
    from cherrypy import wsgiserver
    from cherrypy.wsgiserver import ssl_builtin, ssl_pyopenssl
    def client_callback(conn, x509, error_num, error_depth, ret_code):
        print('client_callback({}, {}, {}, {}, {})'.format(conn, x509, error_num, error_depth, ret_code))
        return ret_code

    context = Context(SSLv23_METHOD)
    context.use_privatekey_file(key)
    context.use_certificate_file(cert)
    supported_ciphers = ('DHE-RSA-AES256-SHA',
      'AES256-SHA',
      'DHE-RSA-AES128-SHA',
      'AES128-SHA',
      'EDH-RSA-DES-CBC3-SHA',
      'DHE-RSA-AES256-SHA',
      'AES256-SHA',
      'DHE-RSA-AES128-SHA',
      'AES128-SHA',
      'EDH-RSA-DES-CBC3-SHA',
      'DES-CBC3-SHA',
      'RC4-SHA'
    )

    context.set_cipher_list(':'.join(supported_ciphers))
    context.set_options(OpenSSL.SSL.OP_NO_SSLv2 | OpenSSL.SSL.OP_NO_SSLv3)
    context.load_client_ca(root)
    context.load_verify_locations(root, "Security_P3G1_SSL_chain.pem")
    context.set_verify(VERIFY_PEER, client_callback)

    #cherrypy.server = wsgiserver.CherryPyWSGIServer(("0.0.0.0", int(443)), API)
    cherrypy.server.ssl_module = 'pyopenssl'
    #cherrypy.server.ssl_context = context
    #cherrypy.server.ssl_certificate = cert
    #cherrypy.server.ssl_private_key = key
    #cherrypy.server.ssl_ca_certificate = root
    cherrypy.server.thread_pool = 30
    #cherrypy.server.ssl_adapter = pyOpenSSLAdapter(cert, key, root)
    #cherrypy.server.ssl_adapter.context = ctx
    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.server.socket_port = 8000

    #cherrypy.tree.graft(app
    cherrypy.tree.mount(API(), "/api/", {'/': RESTopts})
    cherrypy.tree.mount(Root(), "/", "app.config")
    cherrypy.engine.start()
    cherrypy.engine.block()
