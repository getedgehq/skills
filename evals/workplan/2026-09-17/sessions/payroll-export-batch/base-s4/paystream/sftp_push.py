"""Upload bank files to finance SFTP."""
import paramiko
import os


def upload(local_path, host, keyfile):
    """Upload a file to the finance SFTP server.
    
    Args:
        local_path: Path to the local file to upload
        host: SFTP hostname
        keyfile: Path to SSH private key file
    """
    # Parse host if it contains username
    if "@" in host:
        username, hostname = host.split("@", 1)
    else:
        username = "paystream"
        hostname = host
    
    # Load the private key
    key = paramiko.RSAKey.from_private_key_file(keyfile)
    
    # Connect and upload
    transport = paramiko.Transport((hostname, 22))
    try:
        transport.connect(username=username, pkey=key)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        # Upload to the remote path (same filename)
        remote_path = os.path.basename(local_path)
        sftp.put(local_path, remote_path)
        
        sftp.close()
    finally:
        transport.close()
