from binascii import hexlify, unhexlify
from Crypto.Cipher import AES
from hashlib import sha512, pbkdf2_hmac
from Crypto import Random
import OpenSSL

class Cipher:
    BLOCK_SIZE = 32
    PLAYER_HASH_LEN = 64
    USER_HASH_LEN = 64
    def __init__(self):
        pass

    def generatePlayerHash(self, pkey):
        h = sha512()
        h.update(pkey)
        return h.digest()

    def generateUserHash(self, user_pem):
        h = sha512()
        h.update(user_pem)
        return h.digest()

    def generateIV(self):
        return Random.new().read(AES.block_size)

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

    def getPlayerIntegrityHash(self, player_filelist, salt):
        hash = ""
        for file in player_filelist:
            hash += pbkdf2_hmac('sha512', open(file, 'r').read(), salt, 1000)
        return hexlify(pbkdf2_hmac('sha512', hash, salt, 1000))

    def pkcs7_decode(self, data, block_size):
        return data[:-bytearray(data)[-1]]

    def pkcs7_encode(self, data, block_size):
        char_to_pad = block_size - (len(data) % block_size)
        return data + str(bytearray([ char_to_pad for c in range(char_to_pad) ]))