import os
import paramiko

def sync_dir(sftp, local_dir, remote_dir):
    if not remote_dir.endswith('/'):
        remote_dir += '/'
    if not local_dir.endswith('/'):
        local_dir += '/'
    try:  # Ensure remote directory exists
        sftp.stat(remote_dir)
        print(f"Remote directory exists: {remote_dir}")
    except FileNotFoundError:
        print(f"Remote directory does not exist: {remote_dir}")
        sftp.mkdir(remote_dir)
    except Exception as e:
        print(f"Error checking remote directory: {e}")
        return
    local_files = os.listdir(local_dir)  # Compare local and remote directories
    print(f"Local files: {local_files}")
    try:
        remote_files = sftp.listdir(remote_dir)
        print(f"Remote files: {remote_files}")
    except Exception as e:
        print(f"Error listing remote directory: {e}")
        return
    for file in local_files:  # Upload new and modified files
        local_path = os.path.join(local_dir, file)
        remote_path = remote_dir + file
        if os.path.isdir(local_path):
            sync_dir(sftp, local_path, remote_path)
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
                print(f"Error removing remote file or directory {remote_path}: {e}")

def upload():
    os.chdir("/savit/www.weigu")
    url = "tux.lu"
    login = ""
    password = ""
    sport = 222
    destination = "/home/guy/www.weigu"
    src = "/savit/www.weigu"
    dst = destination
    print(f"Connecting to {url} with username {login}")
    text = "Please wait while uploading\n"
    print(text)
    try:
        transport = paramiko.Transport((url, sport))  # Connect to the server
        transport.connect(username=login, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sync_dir(sftp, src, dst)
        sftp.close()
        transport.close()
        text = "Upload done!\n"
        print(text)
    except Exception as e:
        print(f"Error during upload: {e}")

upload()
