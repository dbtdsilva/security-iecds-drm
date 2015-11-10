from binascii import hexlify, unhexlify
#import bcrypt
from hashlib import sha512
from Crypto import Random

class Cipher:
    BLOCK_SIZE = 32
    PLAYER_HASH_LEN = 64
    def __init__(self):
        pass

    def generatePlayerHash(self, pw_binary):
        h = sha512()
        h.update(pw_binary)
        return h.digest()

    def generateUserKey(self):
        return Random.new().read(self.BLOCK_SIZE)