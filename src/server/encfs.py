import subprocess
import shutil
import os
import binascii
import threading

media_dir = "files"
mount_dir = "mount"
store_dir = "store"

class EncryptedFileSystemMedia:
    def __init__(self):
        self.requests = {}
        self.access = threading.Lock()

    def mount_encrypted_file(self, filename, encfs_password):
        self.access.acquire()
        try:
            title = binascii.hexlify(filename)
            mount_f = media_dir + os.path.sep + mount_dir + os.path.sep + title
            store_f = media_dir + os.path.sep + store_dir + os.path.sep + title

            if not os.path.exists(mount_f + os.path.sep + filename):
                subprocess.call(["/bin/sh", "-c", 'echo '+encfs_password+' | encfs -S '+
                                 os.path.abspath(store_f)+' '+os.path.abspath(mount_f)])
            f = open(mount_f + os.path.sep + filename)
            return f
        except Exception:
            return None
        finally:
            if filename not in self.requests:
                self.requests[filename] = 0
            else:
                self.requests[filename] += 1
            self.access.release()

    def unmount_encrypted_file(self, filename):
        self.access.acquire()

        try:
            title = binascii.hexlify(filename)
            mount_f = media_dir + os.path.sep + mount_dir + os.path.sep + title
            if filename in self.requests:
                self.requests[filename] -= 1
                if self.requests[filename] == 0:
                    subprocess.call(["fusermount", "-u", os.path.abspath(mount_f)])
        finally:
            self.access.release()
