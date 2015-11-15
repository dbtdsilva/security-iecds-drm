import subprocess
from Crypto.Cipher import AES
BLOCK_SIZE = 32
import threading

class Playback:
    def read_stdout(self, stdout, player):
        while True:
            line = stdout.readline()
            if line == '':
                break
            if "xcb_window window error: X server failure" in line.rstrip():
                self.running = False
                player.terminate()
            print "Player: ", line.rstrip()

    def __init__(self, path, FileKey, iv, stream=None):
        self.running = True

        if stream is None:
            handle = open(path, "r")
        else:
            handle = open(path, 'w')

        cmdline = ['cvlc','--autoscale','--play-and-exit','--demux','avformat','-']
        player = subprocess.Popen(cmdline, bufsize = 0, stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        thread = threading.Thread(target=self.read_stdout, args=(player.stdout, player))
        thread.start()

        if stream is not None:
            cryptoHeader = stream.raw.read(BLOCK_SIZE + AES.block_size)
            seed = cryptoHeader[:BLOCK_SIZE]
            iv = cryptoHeader[BLOCK_SIZE:]
        aes = AES.new(FileKey, AES.MODE_CBC, iv)
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
            try:
                player.stdin.write(data)
            except:
                print "VLC was closed."
                break


        handle.close()
        player.terminate()
