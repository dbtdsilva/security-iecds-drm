from binascii import hexlify, unhexlify
#import bcrypt
from hashlib import sha512
from Crypto import Random
from OpenSSL import crypto as openCrypto
import OpenSSL
from OpenSSL._util import lib as openCryptolib

class Cipher:
    BLOCK_SIZE = 32
    PLAYER_HASH_LEN = 64
    def __init__(self):
        pass

    def generatePlayerHash(self, pkey):
        h = sha512()
        h.update(pkey)
        return h.digest()

    def generateUserKey(self):
        return Random.new().read(self.BLOCK_SIZE)

    def convert_certificate_to_PEM(self, file_string, file_type=OpenSSL.crypto.FILETYPE_ASN1):
        if file_type != OpenSSL.crypto.FILETYPE_ASN1 and \
            file_type != OpenSSL.crypto.FILETYPE_PEM:
            return None
        if file_type == OpenSSL.crypto.FILETYPE_PEM:
            return file_string
        x509 = OpenSSL.crypto.load_certificate(file_type, file_string)
        return OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, x509)