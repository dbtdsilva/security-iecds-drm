import subprocess
import shutil
import os
import binascii

media_dir = "../files"
mount_dir = "mount"
store_dir = "store"

def insert_encrypted_file(self, filename, encfs_password):
    title = binascii.hexlify(filename)

    mount_f = media_dir + os.path.sep + mount_dir + os.path.sep + title
    store_f = media_dir + os.path.sep + store_dir + os.path.sep + title

    if not os.path.exists(mount_f):
        os.makedirs(mount_f)
    if not os.path.exists(store_f):
        os.makedirs(store_f)

    subprocess.call(["expect", "encfs.exp", encfs_password, os.path.abspath(mount_f), os.path.abspath(store_f)])
    subprocess.call(["/bin/sh", "-c", 'echo '+encfs_password+' | encfs -S '+os.path.abspath(store_f)+' '+os.path.abspath(mount_f)])
    shutil.copyfile(filename, mount_f + os.path.sep + filename)
    subprocess.call(["fusermount", "-u", os.path.abspath(mount_f)])
