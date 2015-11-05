import sys
from Crypto.Cipher import AES

class Cipherops:
    userKey = ''
    deviceKey = ''
    playerKey = ''
    seed = ''

    def __init__(self, seed, UserKey, DeviceKey, PlayerKey):
        self.userKey = UserKey
        self.deviceKey = DeviceKey
        self.playerKey = PlayerKey
        self.seed = seed

    def getFileKey(self):
        aes = AES.new(self.seed, AES.MODE_ECB)
        cryptoDevKey = aes.encrypt(self.deviceKey)
        aes = AES.new(cryptoDevKey, AES.MODE_ECB)
        cryptoDevUserKey = aes.encrypt(self.userKey)
        aes = AES.new(cryptoDevKey, AES.MODE_ECB)
        FileKey = aes.encrypt(self.playerKey)

        return FileKey

    def decryptBlock(self, block, key):
        aes = AES.new(key, AES.MODE_ECB)
        data = aes.decrypt(block)
        return data

    def encryptBlock(self, block, key):
        aes = AES.new(key, AES.MODE_ECB)
        data = aes.encrypt(block)
        return data

#encrypt file
#fin = open("/home/security/Desktop/test/videos/drop.avi", "r")
#fout = open("/home/security/Desktop/test/videos/enc.avi", "w")

#cryptoHeader = '12345678901234567890123456789012'
#UserKey = '12345678901234567890123456789012'
#DeviceKey = '12345678901234567890123456789012'
#PlayerKey = '12345678901234567890123456789012'

#op = Cipherops(cryptoHeader, UserKey, DeviceKey, PlayerKey)
#fkey = op.getFileKey()

#data = fin.read(32)

#while len(data) != 0:
    #if len(encData) < 32:
        #decData = encData
#    if len(data) % 16 != 0:
#        data += ' ' * (16 - len(data) % 16)
    #else:
#    encData = op.encryptBlock(data, fkey)

#    fout.write(encData)

#    data = fin.read(32)

#fin.close()
#fout.close()

#decrypt file
#fin = open("/home/security/Desktop/test/videos/enc.avi", "r")
#fout = open("/home/security/Desktop/test/videos/dec.avi", "w")

#cryptoHeader = '12345678901234567890123456789012'
#UserKey = '12345678901234567890123456789012'
#DeviceKey = '12345678901234567890123456789012'
#PlayerKey = '12345678901234567890123456789012'

#op = Cipherops(cryptoHeader, UserKey, DeviceKey, PlayerKey)
#fkey = op.getFileKey()

#encData = fin.read(32)

#while len(encData) != 0:
    #if len(encData) < 32:
        #decData = encData
    #if len(encData) % 16 != 0:
        #encData += ' ' * (16 - len(encData) % 16)
    #else:
#    decData = op.decryptBlock(encData, fkey)

 #   fout.write(decData)

  #  encData = fin.read(32)

#fin.close()
#fout.close()
