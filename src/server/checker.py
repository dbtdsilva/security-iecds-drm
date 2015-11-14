import cherrypy
import json
from database.storage_api import storage
import datetime

SESSION_USERID = 'userid'
SESSION_DEVICE = 'device_key'
SESSION_PLAYER = 'player_key'

REQUEST_PARAMETER = 'parameters'

def check_parameters(*args, **kwargs):
    conditions = cherrypy.request.config.get('parameters', None)
    if conditions is not None:
        for condition in conditions:
            (valid, error) = condition()
            if not valid:
                raise error

def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable."""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if REQUEST_PARAMETER not in f._cp_config:
            f._cp_config[REQUEST_PARAMETER] = []
        f._cp_config[REQUEST_PARAMETER].extend(conditions)
        return f
    return decorate

def logged():
    def check():
        userid = cherrypy.session.get(SESSION_USERID)
        if userid != None:
            return (True, None)
        return (False, cherrypy.HTTPError(401, "Requires authentication"))
    return check

def device_key():
    def check():
        devkey = cherrypy.session.get(SESSION_DEVICE)
        if devkey != None and storage.exists_device_key(devkey):
            return (True, None)
        return (False, cherrypy.HTTPError(400, "Device key wasn't provided"))
    return check

def is_player():
    def check():
        playerkey = cherrypy.session.get(SESSION_PLAYER)
        if playerkey != None and storage.exists_player_key(playerkey):
            return (True, None)
        return (False, cherrypy.HTTPError(400, "Player certificate isn't valid, re-download the player"))
    return check

def check_policies_and_refresh(userid, fileid, devicekey, user_agent, remote_addr):
    now = datetime.datetime.today().time().isoformat()
    return (True, None)

def jsonify_error(status, message, traceback, version):
    response = cherrypy.response
    response.headers['Content-Type'] = 'application/json'
    return json.dumps({'status': status, 'message': message})

cherrypy.tools.checker = cherrypy.Tool('before_handler', check_parameters)