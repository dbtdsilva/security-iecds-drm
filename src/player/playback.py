import subprocess
from cipherops import Cipherops
from Crypto.Cipher import AES

class Playback:
    def __init__(self, filename, FileKey):
        encFile = open("./videos/" + filename, "r")

        try:
            #cmdline = ['vlc', '-'] #default demux is broken, use below instead
            cmdline = ['vlc', '--demux', 'avformat', '-']

            player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
    
            aes = AES.new(FileKey, AES.MODE_ECB)
            encData = encFile.read(32)
    
            while len(encData) != 0:
                data = aes.decrypt(encData)
                #data = op.decryptBlock(encData, FileKey)
                player.stdin.write(data)
                encData = encFile.read(32)

        finally:
            encFile.close()
            player.terminate()
