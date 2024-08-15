#
# upload_extra_script.py
# set the output_port
#  if target_filename is found then that drive is used
#  else if target_drive is found then that drive is used
#
from __future__ import print_function

import pioutil
if pioutil.is_pio_build():

	target_filename = "FIRMWARE.CUR"
	target_drive = "REARM"

	import os,getpass,platform

	current_OS = platform.system()
	Import("env")

	def print_error(e):
		print('\nUnable to find destination disk (%s)\n' \
			  'Please select it in platformio.ini using the upload_port keyword ' \
			  '(https://docs.platformio.org/en/latest/projectconf/section_env_upload.html) ' \
			  'or copy the firmware (.pio/build/%s/firmware.bin) manually to the appropriate disk\n' \
			  %(e, env.get('PIOENV')))
import os
import getpass
import string
import subprocess
from ctypes import windll

def get_windows_drives():
    """Returns a list of available drives on Windows."""
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter + ':\\')
        bitmask >>= 1
    return drives

def find_windows_disk(target_drive, target_filename):
    """Find the disk on Windows containing the target drive or file."""
    for drive in get_windows_drives():
        try:
            volume_info = str(subprocess.check_output('cmd /C dir ' + drive, stderr=subprocess.STDOUT))
        except Exception as e:
            print(f'Error accessing {drive}: {e}')
            continue
        if target_drive in volume_info:
            return drive, True
        if target_filename in volume_info:
            return drive, False
    return None, None

def find_linux_disk(target_drive, target_filename):
    """Find the disk on Linux containing the target drive or file."""
    user_media_path = os.path.join(os.sep, 'media', getpass.getuser())
    drives = os.listdir(user_media_path)
    
    if target_drive in drives:
        return os.path.join(user_media_path, target_drive) + os.sep, True
    
    for drive in drives:
        try:
            files = os.listdir(os.path.join(user_media_path, drive))
        except:
            continue
        if target_filename in files:
            return os.path.join(user_media_path, drive) + os.sep, False
    return None, None

def find_darwin_disk(target_drive, target_filename):
    """Find the disk on MacOS containing the target drive or file."""
    drives = os.listdir('/Volumes')
    
    if target_drive in drives:
        return '/Volumes/' + target_drive + '/', True
    
    for drive in drives:
        try:
            filenames = os.listdir('/Volumes/' + drive + '/')
        except:
            continue
        if target_filename in filenames:
            return '/Volumes/' + drive + '/', False
    return None, None

def before_upload(source, target, env):
    """Main function to determine the upload disk based on the current OS."""
    upload_disk = None
    target_file_found = False
    target_drive_found = False

    if current_OS == 'Windows':
        upload_disk, target_drive_found = find_windows_disk(target_drive, target_filename)
    elif current_OS == 'Linux':
        upload_disk, target_drive_found = find_linux_disk(target_drive, target_filename)
    elif current_OS == 'Darwin':
        upload_disk, target_drive_found = find_darwin_disk(target_drive, target_filename)

    if upload_disk:
        if current_OS == 'Linux' and (target_file_found or target_drive_found):
            env.Replace(UPLOAD_FLAGS="-P$UPLOAD_PORT")
        return upload_disk
    else:
        print("Disk not found")
        return None


			#
			# Set upload_port to drive if found
			#
			if target_file_found or target_drive_found:
				env.Replace(UPLOAD_PORT=upload_disk)
				print('\nUpload disk: ', upload_disk, '\n')
			else:
				print_error('Autodetect Error')

		except Exception as e:
			print_error(str(e))

	env.AddPreAction("upload", before_upload)
