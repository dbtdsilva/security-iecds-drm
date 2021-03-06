import cherrypy
import json
from database.storage_api import storage
import datetime
from OpenSSL import crypto
from cipher import Cipher
import binascii
from copy import deepcopy

SESSION_USERID = 'userid'
SESSION_DEVICE = 'device_key'
SESSION_PLAYER = 'player_key'
SESSION_PLAYER_SALT = 'p_salt'
SESSION_PLAYER_INTEGRITY = 'p_integrity'
SESSION_CHALLENGE_SALT = 'p_challenge_salt'
SESSION_CHALLENGE_VALID = 'p_challenge_valid'

REQUEST_PARAMETER = 'parameters'

cipherLib = Cipher()

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

def has_player_certificate():
    def check():
        if 'Ssl-Client-Cert' in cherrypy.request.headers:
            if Cipher().validatePlayerCertificate(
                    cipherLib.cleanReceivedPEM(cherrypy.request.headers['Ssl-Client-Cert'])):
                return (True, None)
            return (False, "Chain of certificates provided isn't valid")
        return (False, cherrypy.HTTPError(400, "Certificate wasn't provided"))
    return check

def challenge_salt_exists():
    def check():
        if cherrypy.session.get(SESSION_CHALLENGE_SALT) is not None:
            return (True, None)
        return (False, cherrypy.HTTPError("Must generate a challenge before validate"))
    return check

def has_cc_certificate():
    def check():
        if 'Ssl-Client-Cert' in cherrypy.request.headers and \
                'Ssl-Client-S-Dn-Cn' in cherrypy.request.headers and \
                'Ssl-Client-Cert-Chain-0' in cherrypy.request.headers and \
                'Ssl-Client-I-Dn-Cn' in cherrypy.request.headers:
            ec_de_autenticacao = crypto.load_certificate(
                    crypto.FILETYPE_PEM,
                    cipherLib.cleanReceivedPEM(cherrypy.request.headers['Ssl-Client-Cert-Chain-0']))
            if Cipher().validateCertificate(cipherLib.cleanReceivedPEM(cherrypy.request.headers['Ssl-Client-Cert']),
                                    ec_de_autenticacao.get_issuer().commonName,
                                    cherrypy.request.headers['Ssl-Client-I-Dn-Cn']):
                return (True, None)
            return (False, cherrypy.HTTPError(400, "Chain of certificates provided isn't valid"))
        if 'Ssl-Client-Cert' in cherrypy.request.headers:
            return (False, cherrypy.HTTPError(400, "Certificate provided isn't complete"))
        return (False, cherrypy.HTTPError(400, "Certificate wasn't provided"))
    return check

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

def player_salt():
    def check():
        psalt = cherrypy.session.get(SESSION_PLAYER_SALT)
        if psalt != None:
            return (True, None)
        return (False, cherrypy.HTTPError(400, "You must generate a salt before you begin validation"))
    return check

def player_integrity():
    def check():
        integrity = cherrypy.session.get(SESSION_PLAYER_INTEGRITY)
        if integrity != None and integrity == True:
            return (True, None)
        return (False, cherrypy.HTTPError(400, "Player must validate his integrity"))
    return check

def is_player():
    def check():
        playerkey = cherrypy.session.get(SESSION_PLAYER)
        if playerkey != None and storage.exists_player_key(playerkey):
            return (True, None)
        return (False, cherrypy.HTTPError(400, "Player certificate isn't valid, re-download the player"))
    return check

def check_policies_and_refresh(userid, fileid, devicekey, user_agent, remote_addr):
    if not storage.policy_is_playable_on_device(fileid, userid, devicekey):
        return (False, "Reached maximum number of devices for this file!")
    if not storage.policy_is_valid_policy_region(fileid, remote_addr):
        return (False, "You're not in a valid region to play this file")
    if not storage.policy_is_valid_time(fileid, datetime.datetime.today().time()):
        return (False, "Current time is restricted to play the file")
    if not storage.policy_is_valid_policy_system(fileid, user_agent):
        return (False, "Your OS isn't allowed to reproduce the file")
    if not storage.policy_has_valid_plays(fileid, userid):
        return (False, "You've reached the maximum number of times that you're allowed to play this file")

    return (True, None)

def jsonify_error(status, message, traceback, version):
    response = cherrypy.response
    response.headers['Content-Type'] = 'application/json'
    return json.dumps({'status': status, 'message': message})

cherrypy.tools.checker = cherrypy.Tool('before_handler', check_parameters)