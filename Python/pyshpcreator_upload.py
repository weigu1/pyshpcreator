#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Upload homepage directory to server

import os
import sys
import paramiko

class Upload:
    """ Upload homepage directory to server """
    def __init__(self, hp_dir_name, dst, url, login, password, sport):
        self.src = hp_dir_name # source
        self.dst = dst
        self.url = url
        self.login = login
        self.password = password
        self.sport = sport  # SFTP port number

    def sync_dir(self, sftp, local_dir, remote_dir):
        """ Synchronize a local directory with a remote directory using SFTP.
            Upload new and modified files, remove files if only in the remote directory.
            Directories are created if they do not exist. Needed by upload() """
        if not remote_dir.endswith('/'):
            remote_dir += '/'
        if not local_dir.endswith('/'):
            local_dir += '/'
        try:  # Ensure remote directory exists
            sftp.stat(remote_dir)
            text = f"Remote directory exists: {remote_dir}"
            print(text)
        except FileNotFoundError:
            text = f"Remote directory does not exist: {remote_dir}. Creating the directory"
            print(text)
            sftp.mkdir(remote_dir)
        except Exception as e:
            text = f"Error checking remote directory: {e}"
            print(text)
            return text
        local_files = os.listdir(local_dir)  # Compare local and remote directories
        print(f"Local files: {local_files}")
        try:
            remote_files = sftp.listdir(remote_dir)
            print(f"Remote files: {remote_files}")
        except Exception as e:
            text2 = f"Error listing remote directory: {e}"
            print(text2)
            return text2
        for file in local_files:  # Upload new and modified files
            local_path = os.path.join(local_dir, file)
            remote_path = remote_dir + file
            if os.path.isdir(local_path):
                self.sync_dir(sftp, local_path, remote_path)
            else:
                try:
                    upload_file = False
                    if file not in remote_files:
                        upload_file = True
                    else:
                        local_stat = os.stat(local_path)
                        remote_stat = sftp.stat(remote_path)
                        if local_stat.st_size != remote_stat.st_size or local_stat.st_mtime > remote_stat.st_mtime:
                            upload_file = True
                    if upload_file:
                        print(f"Uploading file: {local_path} to {remote_path}")
                        sftp.put(local_path, remote_path)
                except Exception as e:
                    print(f"Error uploading file {local_path} to {remote_path}: {e}")
        for file in remote_files:  # Remove files if only in the remote directory
            remote_path = remote_dir + file
            local_path = os.path.join(local_dir, file)
            if file not in local_files:
                try:
                    if sftp.stat(remote_path).st_mode & 0o40000:  # Check if it's a directory
                        print(f"Removing remote directory: {remote_path}")
                        sftp.rmdir(remote_path)
                    else:
                        print(f"Removing remote file: {remote_path}")
                        sftp.remove(remote_path)
                except Exception as e:
                    text3 = f"Error removing remote file or directory {remote_path}: {e}"
                    print(text3)
                    return text3
        return text + "\nSynchronization done!"

    def upload(self):
        """ Upload a local directory to a remote directory using SFTP."""
        if self.src[:-1] != '/':
            self.src += '/'
        os.chdir(self.src)
        text = f"Connecting to {self.url} with username {self.login}\n" \
                "Please wait while uploading\nThis will take some time!"
        print(text)
        try:
            transport = paramiko.Transport((self.url, int(self.sport)))  # Connect to the server
            transport.connect(username = self.login, password = self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            text = text + self.sync_dir(sftp, self.src, self.dst)
            sftp.close()
            transport.close()
            text = "Upload done!\n"
            print(text)
        except Exception as e:
            text = f"Error during upload: {e}"
        return text

### main ####
def main():
    """setup and start mainloop"""
    print ('Argument list: ', sys.argv)
    hp_dir_name = "/savit/www.test/"
    dst = "/home/guy/www.test"
    url = "pitti.lu"
    login = ""
    password = ""
    sport = "22"
    if len(sys.argv) == 7:
        hp_dir_name = sys.argv[1]
        dst = sys.argv[2]
        url = sys.argv[3]
        login = sys.argv[4]
        password = sys.argv[5]
        sport = sys.argv[6]

    up = Upload(hp_dir_name, dst, url, login, password, sport)
    text = up.upload()
    print(text)

if __name__ == '__main__':
    main()