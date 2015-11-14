#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from cherrypy.wsgiserver.ssl_builtin import BuiltinSSLAdapter
if sys.version_info < (3, 0):
  from cherrypy.wsgiserver.wsgiserver2 import ssl_adapters
else:
  from cherrypy.wsgiserver.wsgiserver3 import ssl_adapters

try:
    import ssl
except ImportError:
    ssl = None

try:
    from _pyio import DEFAULT_BUFFER_SIZE
except ImportError:
    try:
        from io import DEFAULT_BUFFER_SIZE
    except ImportError:
        DEFAULT_BUFFER_SIZE = -1

import sys

from cherrypy import wsgiserver

class BuiltinSsl(BuiltinSSLAdapter):
    """ Wrapper based on Builtinssl socket """

    def __init__(self, certificate, private_key, certificate_chain=None):
        if ssl is None:
            raise ImportError("You must install the ssl module to use HTTPS.")
        self.certificate = certificate
        self.private_key = private_key
        self.certificate_chain = certificate_chain

    def wrap(self, sock):
        """Wrap and return the given socket, plus WSGI environ entries."""
        try:
            s = ssl.wrap_socket(sock, do_handshake_on_connect=True,
                                server_side=True, certfile=self.certificate,
                                cert_reqs=ssl.CERT_OPTIONAL,
                                ca_certs=self.certificate_chain,
                                keyfile=self.private_key,
                                ssl_version=ssl.PROTOCOL_SSLv23)
        except ssl.SSLError:
            e = sys.exc_info()[1]
            if e.errno == ssl.SSL_ERROR_EOF:
                # This is almost certainly due to the cherrypy engine
                # 'pinging' the socket to assert it's connectable;
                # the 'ping' isn't SSL.
                return None, {}
            elif e.errno == ssl.SSL_ERROR_SSL:
                if e.args[1].endswith('http request'):
                    # The client is speaking HTTP to an HTTPS server.
                    raise wsgiserver.NoSSLError
                elif e.args[1].endswith('unknown protocol'):
                    # The client is speaking some non-HTTP protocol.
                    # Drop the conn.
                    return None, {}
            raise
        return s, self.get_environ(s)

ssl_adapters['custom-ssl'] = BuiltinSsl