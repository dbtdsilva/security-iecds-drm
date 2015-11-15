import subprocess
from Crypto.Cipher import AES
BLOCK_SIZE = 32

class Playback:
    def __init__(self, path, FileKey, stream=None):

        if stream is None:
            handle = open(path, "r")
        else:
            handle = open(path, 'w')

        cmdline = ['bash','-c', 'cvlc --autoscale --play-and-exit --demux avformat -']
        player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
        print "process"

        if stream is not None:
            cryptoHeader = stream.raw.read(BLOCK_SIZE)
        aes = AES.new(FileKey, AES.MODE_ECB)
        FileKey = None
        del FileKey

        channelFragmentation = BLOCK_SIZE * 1500
        if stream is None:
            encData = handle.read(channelFragmentation)
        else:
            encData = stream.raw.read(channelFragmentation)
            handle.write(encData)

        while len(encData) != 0:
            data = aes.decrypt(encData)
            if stream is None:
                encData = handle.read(channelFragmentation)
            else:
                encData = stream.raw.read(channelFragmentation)
                handle.write(encData)

            if len(encData) == 0:
                data = data[:-bytearray(data)[-1]]
            player.stdin.write(data)


        handle.close()
        player.terminate()
