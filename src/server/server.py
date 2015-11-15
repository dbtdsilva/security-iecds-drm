#encoding=utf-8
from Crypto import Random
from Crypto.Cipher import AES
import os.path
import cherrypy.wsgiserver.ssl_builtin
import json
from cherrypy.lib import jsontools
from database.storage_api import storage
import binascii
from checker import require, logged, device_key, SESSION_DEVICE, \
    SESSION_USERID, jsonify_error, SESSION_PLAYER, is_player, check_policies_and_refresh, \
    SESSION_PLAYER_SALT, player_salt, SESSION_PLAYER_INTEGRITY, player_integrity
import custom_adapter
from cipher import Cipher
import time

BLOCK_SIZE = 32
cipherLib = Cipher()
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
        self.valplayer = ValidatePlayer()
        self.stream = Stream()

class Stream(object):
    def __init__(self):
        self.validate = StreamValidate()
    exposed = True

    def GET(self):
        print "begin"
        yield "asdasd"
        print "what"
        time.sleep(3)
        yield "wwwww"
        print "end"
        time.sleep(3)
        yield "wwwww"
        print "end"
    GET._cp_config = {'response.stream': True}
class StreamValidate(object):
    exposed = True
    def POST(self):
        try:
            content_length = cherrypy.request.headers['Content-Length']
            raw_body = cherrypy.request.body.read(int(content_length))
            body = json.loads(raw_body)
        except Exception:
            raise cherrypy.HTTPError(400, "Wrong format")

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
        if cherrypy.session.get(SESSION_PLAYER) is None and hasattr(cherrypy.request.rfile, 'rfile'):
            der_player = cherrypy.request.rfile.rfile._sock.getpeercert(binary_form=True)
            if der_player != None:
                DER = cherrypy.request.rfile.rfile._sock.getpeercert(binary_form=True)
                pkey = cipherLib.convert_certificate_to_PEM(DER)
                player_key = storage.get_player_key(cipherLib.generatePlayerHash(pkey))
                if player_key == None:
                    raise cherrypy.HTTPError(400, "Certificate expired, re-download the player.")
                cherrypy.session[SESSION_PLAYER] = player_key
        cherrypy.session[SESSION_USERID] = storage.get_user_id(body['username'])
        cherrypy.response.status = 200
        return {"status": 200, "message": "Login successfully"}
        

class UserLogout(object):
    exposed = True

    # POST /api/user/logout
    # Details: Logout the current user
    @cherrypy.tools.json_out()
    @require(logged())
    def POST(self):
        cherrypy.response.status = 200
        cherrypy.session[SESSION_USERID] = None
        return {"status": 200, "message": "User logged out."}

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
    @require(logged(), device_key(), is_player(), player_integrity())
    def GET(self, title, seed_only = False):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        if seed_only == '1' or seed_only == 'True' or seed_only == 'true':
            seed_only = True
        user_id = cherrypy.session.get(SESSION_USERID)
        if not storage.user_has_title(user_id, title):
            raise cherrypy.HTTPError(400, "Current user didn't buy this title")
        file_key = storage.get_file_key(user_id, title)
        user_key = storage.get_user_details(user_id).userkey
        device_key = cherrypy.session.get(SESSION_DEVICE)
        player_key = '\xb8\x8b\xa6Q)c\xd6\x14/\x9dpxc]\xff\x81L\xd2o&\xc2\xd1\x94l\xbf\xa6\x1d\x8fA\xdee\x9c'

        # Beyond this point user have bought the title, lets check the policies
        (valid, message) = check_policies_and_refresh(user_id, title, device_key,
                                   cherrypy.request.headers['User-Agent'],
                                   cherrypy.request.headers['Remote-Addr'])
        if not valid:
            raise cherrypy.HTTPError(400, message)
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

        #print "Player key", binascii.hexlify(player_key)
        #print "User key: ", binascii.hexlify(user_key)
        #print "Device key: ", binascii.hexlify(device_key)
        #print "File Key: ", binascii.hexlify(file_key)
        #print "Seed: ", binascii.hexlify(seed)
        def content():
            if seed_only:
                yield seed
                return

            print storage.get_tile_details(title).path
            f = open("media/" + storage.get_tile_details(title).path, 'r')
            aes = AES.new(file_key, AES.MODE_ECB)

            yield seed

            channel_fragmentation = BLOCK_SIZE * 1500
            data = f.read(channel_fragmentation)
            print "starting"
            while data:
                if len(data) < channel_fragmentation:
                    data = cipherLib.pkcs7_encode(data, BLOCK_SIZE)
                    dataEncrypted = aes.encrypt(data)
                    yield dataEncrypted
                dataEncrypted = aes.encrypt(data)
                yield dataEncrypted
                data = f.read(channel_fragmentation)
        return content()
    GET._cp_config = {'response.stream': True}

    # POST  /api/title/<pk>                             
    # Requires login
    # Details: Buys a specific title
    @cherrypy.tools.json_out()
    @require(logged())
    def POST(self, title):
        storage.buy_file(cherrypy.session.get(SESSION_USERID), title)
        return {"status": 200, "message": "Title was successfully purchased"}

class TitleValidate(object):
    exposed = True

    # POST /api/title/validate/<pk> key=current_result  
    # Requires login
    # Details: Sends the current cipher result key to the server to process
    # with user key
    @require(logged(), is_player(), device_key(), player_integrity())
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
        a = cherrypy
        return [ a.to_dict() for a in storage.get_file_list() ]

class ValidatePlayer(object):
    exposed = True

    def GET(self):
        if cherrypy.session.get(SESSION_PLAYER) is None and hasattr(cherrypy.request.rfile, 'rfile'):
            der_player = cherrypy.request.rfile.rfile._sock.getpeercert(binary_form=True)
            if der_player != None:
                DER = cherrypy.request.rfile.rfile._sock.getpeercert(binary_form=True)
                pkey = cipherLib.convert_certificate_to_PEM(DER)
                player_key = storage.get_player_key(cipherLib.generatePlayerHash(pkey))
                if player_key == None:
                    raise cherrypy.HTTPError(400, "Certificate expired, re-download the player.")
                cherrypy.session[SESSION_PLAYER] = player_key
        if cherrypy.session.get(SESSION_PLAYER) is None:
            raise cherrypy.HTTPError(400, "Player certificate must be provided.")

        salt = Random.new().read(32)
        cherrypy.session[SESSION_PLAYER_SALT] = salt
        return salt

    @cherrypy.tools.json_out()
    @require(player_salt(), is_player())
    def POST(self, hash):
        salt = cherrypy.session.get(SESSION_PLAYER_SALT)
        cherrypy.session[SESSION_PLAYER_SALT] = None
        player_filelist = storage.get_player(cherrypy.session[SESSION_PLAYER]).filelist_integrity.split(",")
        if cipherLib.getPlayerIntegrityHash(player_filelist, salt) == hash:
            cherrypy.session[SESSION_PLAYER_INTEGRITY] = True
            cherrypy.response.status = 200
            return {"status": 200, "message": "Player integrity validated."}
        else:
            raise cherrypy.HTTPError(400, "Player integrity isn't valid.")

class Root(object):
    @cherrypy.expose()
    def thing(self):
        self._cp_config = {'response.stream': True}
        print "begin"
        yield "asdasd"
        print "what"
        time.sleep(3)
        yield "wwwww"
        print "end"
    #thing._cp_config = {'response.stream': True}

if __name__ == '__main__':
    RESTopts = {
        'tools.sessions.on': True,
        'tools.checker.on': True,
        'error_page.default': jsonify_error,
        'tools.json_out.handler': jsontools.json_handler,
        'tools.json_in.processor': jsontools.json_processor,
        'request.dispatch': cherrypy.dispatch.MethodDispatcher()
    }

    key = "certificates/ssl/Security_P3G1_SSL_key.pem"
    cert = "certificates/ssl/Security_P3G1_SSL.crt"
    root = "certificates/rootCA/Security_P3G1_Root.crt"

    cherrypy.server.ssl_module = 'custom-ssl'
    cherrypy.server.ssl_certificate = cert
    cherrypy.server.ssl_private_key = key
    cherrypy.server.thread_pool = 100
    #cherrypy.server.ssl_ca_certificate = root
    cherrypy.server.ssl_certificate_chain = root
    cherrypy.server.socket_host = "0.0.0.0"
    if os.getenv('DEBUG_MODE') == 'dev':
        cherrypy.server.socket_port = 4433
    else:
        cherrypy.server.socket_port = 443

    cherrypy.tree.mount(API(), "/api/", {'/': RESTopts})
    cherrypy.tree.mount(Root(), "/", "app.config")
    cherrypy.engine.start()
    cherrypy.engine.block()
