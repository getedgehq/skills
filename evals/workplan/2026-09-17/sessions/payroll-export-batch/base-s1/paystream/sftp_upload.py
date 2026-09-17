"""SFTP upload to finance server."""
import os
import paramiko


def upload(local_path, host, username, key_path):
    """Upload a file to the finance SFTP server.
    
    Args:
        local_path: Path to the local file to upload
        host: SFTP hostname
        username: SFTP username
        key_path: Path to the private key file
    """
    # Load the private key
    key = paramiko.RSAKey.from_private_key_file(key_path)
    
    # Connect via SFTP
    transport = paramiko.Transport((host, 22))
    transport.connect(username=username, pkey=key)
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    # Upload to the remote directory (finance expects files in /incoming)
    remote_filename = os.path.basename(local_path)
    remote_path = f"/incoming/{remote_filename}"
    
    sftp.put(local_path, remote_path)
    
    sftp.close()
    transport.close()
