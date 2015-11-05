import subprocess
from cipherops import Cipherops

encFile = open("/home/security/Desktop/test/videos/enc.avi", "r")

try:
    #cmdline = ['vlc', '-'] #default demux is broken, use below instead
    cmdline = ['vlc', '--demux', 'avformat', '-']

    player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
    
    cryptoHeader = '12345678901234567890123456789012'
    UserKey = '12345678901234567890123456789012'
    DeviceKey = '12345678901234567890123456789012'
    PlayerKey = '12345678901234567890123456789012'

    op = Cipherops(cryptoHeader, UserKey, DeviceKey, PlayerKey)
    FileKey = op.getFileKey()

    encData = encFile.read(32)
    
    while len(encData) != 0:
        data = op.decryptBlock(encData, FileKey)
        player.stdin.write(data)
        encData = encFile.read(32)

finally:
    encFile.close()
    player.terminate()
