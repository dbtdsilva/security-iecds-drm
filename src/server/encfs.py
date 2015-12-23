import subprocess
import shutil
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
mount_dir = "/opt/iedcs-mount"
store_dir = "/opt/iedcs-store"

# --- Manage directories (all files in media folder) ---

#if not os.path.exists(mount_dir):
#    os.makedirs(mount_dir)

#if not os.path.exists(store_dir):
#    os.makedirs(store_dir)

#encfs_password = "abcdefgh12345"

#for f in os.listdir(current_dir + os.path.sep + "media"):
#    if not os.path.exists(mount_dir + os.path.sep + f):
#        os.mkdir(mount_dir + os.path.sep + f)
#    if not os.path.exists(store_dir + os.path.sep + f):
#        os.mkdir(store_dir + os.path.sep + f)
       
#    mount_f = mount_dir + os.path.sep + f
#    store_f = store_dir + os.path.sep + f
#    subprocess.call(["expect", "encfs.exp", encfs_password, mount_f, store_f])
       
#    shutil.copyfile(current_dir + os.path.sep + "media" + os.path.sep + f, mount_f + os.path.sep + f)

#    subprocess.call(["umount", "-l", mount_f + os.path.sep + f])


# --- Manage directory (when adding new file) ---
file_path = "./media/sample2.mkv"
title = "sample2.mkv"
encfs_password = "abcdefgh12345"

if not os.path.exists(mount_dir):
    os.makedirs(mount_dir)
if not os.path.exists(store_dir):
    os.makedirs(store_dir)

if not os.path.exists(mount_dir + os.path.sep + title):
    os.mkdir(mount_dir + os.path.sep + title)
if not os.path.exists(store_dir + os.path.sep + title):
    os.mkdir(store_dir + os.path.sep + title)

mount_f = mount_dir + os.path.sep + title
store_f = store_dir + os.path.sep + title
subprocess.call(["expect", "encfs.exp", encfs_password, mount_f, store_f])
subprocess.call(["/bin/sh", "-c", 'echo '+encfs_password+' | encfs -S /opt/iedcs-store/sample2.mkv/ /opt/iedcs-mount/sample2.mkv/'])

shutil.copyfile(file_path, mount_f + os.path.sep + title)

subprocess.call(["fusermount", "-u", mount_f])

