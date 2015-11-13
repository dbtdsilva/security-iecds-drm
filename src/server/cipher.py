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

    def get_certificate_pubkey(self, file_string, file_type=OpenSSL.crypto.FILETYPE_ASN1):
        if file_type != OpenSSL.crypto.FILETYPE_ASN1 and \
            file_type != OpenSSL.crypto.FILETYPE_PEM:
            return None
        certificate = OpenSSL.crypto.load_certificate(file_type, file_string)
        bio = openCrypto._new_mem_buf()
        openCryptolib.PEM_write_bio_PUBKEY(bio, certificate.get_pubkey()._pkey)
        return openCrypto._bio_to_string(bio)