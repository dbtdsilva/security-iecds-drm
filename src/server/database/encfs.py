import subprocess
import shutil
import os
from Crypto.Hash import SHA256, SHA512

media_dir = "../files"
mount_dir = "mount"
store_dir = "store"

def insert_encrypted_file(file, master_password):
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

    print store_f
    if os.path.exists(store_f):
        return

    if not os.path.exists(mount_f):
        os.makedirs(mount_f)
    if not os.path.exists(store_f):
        os.makedirs(store_f)

    subprocess.call(["expect", "encfs.exp", encfs_password, os.path.abspath(mount_f), os.path.abspath(store_f)],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.call(["fusermount","-z","-u", os.path.abspath(mount_f)])
    subprocess.call(["/bin/sh", "-c", 'echo '+encfs_password+' | encfs -S -o allow_root --idle=1 '+os.path.abspath(store_f)+' '+os.path.abspath(mount_f)])
    shutil.copyfile("../media/" + filename, mount_f + os.path.sep + filename)
    #subprocess.call(["fusermount","-u", os.path.abspath(mount_f)])
