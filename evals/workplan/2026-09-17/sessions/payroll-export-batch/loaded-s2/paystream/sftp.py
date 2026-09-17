"""SFTP upload for bank files to finance server."""
import sys


def upload_to_finance(local_path, remote_name=None, config=None):
    """Upload a file to the finance SFTP server.
    
    Args:
        local_path: Path to the local file to upload
        remote_name: Optional remote filename (defaults to basename of local_path)
        config: Dict with 'host', 'username', 'key_path', 'remote_dir'
        
    Returns:
        True on success, False on failure
        
    Raises:
        ValueError if config is missing required keys
        ImportError if paramiko is not installed
    """
    if config is None:
        raise ValueError("SFTP config required. Expected dict with keys: host, username, key_path, remote_dir")
    
    required = ["host", "username", "key_path", "remote_dir"]
    missing = [k for k in required if k not in config]
    if missing:
        raise ValueError("SFTP config missing keys: %s" % ", ".join(missing))
    
    try:
        import paramiko
    except ImportError:
        print("ERROR: paramiko not installed. Install with: pip install paramiko", file=sys.stderr)
        return False
    
    import os
    
    if remote_name is None:
        remote_name = os.path.basename(local_path)
    
    remote_path = config["remote_dir"].rstrip("/") + "/" + remote_name
    
    try:
        # Connect to SFTP server
        key = paramiko.RSAKey.from_private_key_file(config["key_path"])
        transport = paramiko.Transport((config["host"], config.get("port", 22)))
        transport.connect(username=config["username"], pkey=key)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        # Upload file
        sftp.put(local_path, remote_path)
        
        # Clean up
        sftp.close()
        transport.close()
        
        return True
        
    except Exception as e:
        print("ERROR: SFTP upload failed: %s" % e, file=sys.stderr)
        return False
