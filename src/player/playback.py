import subprocess
from Crypto.Cipher import AES

BLOCK_SIZE = 32

class Playback:
    def __init__(self, path, FileKey):
        print path
        encFile = open(path, "r")

        #cmdline = ['cvlc', '--autoscale', '-'] #default demux is broken, use below instead
        cmdline = ['cvlc', '--autoscale', '--play-and-exit', '--demux', 'avformat', '-']

        player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
    
        aes = AES.new(FileKey, AES.MODE_ECB)
        FileKey = None
        del FileKey
        encData = encFile.read(BLOCK_SIZE)
    
        while len(encData) != 0:
            if len(encData) < BLOCK_SIZE:
                raise Exception("Invalid block size or it wasn't correctly ciphered")
            data = aes.decrypt(encData)
            encData = encFile.read(BLOCK_SIZE)
            if len(encData) == 0:
                data = data[:-bytearray(data)[-1]]
            player.stdin.write(data)

        encFile.close()
        player.terminate()
