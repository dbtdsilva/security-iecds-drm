import subprocess
import os
from Crypto.Hash import SHA256, SHA512

media_dir = "files"
mount_dir = "mount"
store_dir = "store"

class EncryptedFileSystemMedia:
    def mount_encrypted_file(self, file, master_password):
        filename = file.path
        obj = SHA256.new()
        obj.update(file.author)
        obj.update(filename)
        obj.update(file.title)
        title = obj.hexdigest()

        obj_pass = SHA512.new()
        obj_pass.update(file.author)
        obj_pass.update(master_password)
        obj_pass.update(file.title)
        encfs_password = obj_pass.hexdigest()

        mount_f = media_dir + os.path.sep + mount_dir + os.path.sep + title
        store_f = media_dir + os.path.sep + store_dir + os.path.sep + title

        if not os.path.exists(mount_f + os.path.sep + filename):
            subprocess.call(["/bin/sh", "-c", 'echo '+encfs_password+' | encfs -S --idle=1 '+
                                 os.path.abspath(store_f)+' '+os.path.abspath(mount_f)])
        f = open(mount_f + os.path.sep + filename)
        return f