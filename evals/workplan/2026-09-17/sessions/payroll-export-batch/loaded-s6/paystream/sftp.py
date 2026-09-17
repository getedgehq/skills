"""SFTP upload to finance server."""
import sys


def push_to_finance(local_path, sftp_config):
    """Upload bank file to finance SFTP server.
    
    Args:
        local_path: Path to the bank file to upload
        sftp_config: Dict with 'host', 'username', 'key_path', 'remote_dir'
    
    Returns:
        True if upload succeeded, False otherwise
    """
    try:
        import paramiko
    except ImportError:
        print("ERROR: paramiko not installed. Run: pip install paramiko", file=sys.stderr)
        return False
    
    try:
        # Load private key
        key = paramiko.RSAKey.from_private_key_file(sftp_config['key_path'])
        
        # Connect
        transport = paramiko.Transport((sftp_config['host'], 22))
        transport.connect(username=sftp_config['username'], pkey=key)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        # Upload
        remote_filename = local_path.split('/')[-1]
        remote_path = f"{sftp_config['remote_dir']}/{remote_filename}"
        sftp.put(local_path, remote_path)
        
        # Cleanup
        sftp.close()
        transport.close()
        
        print(f"Uploaded {local_path} to {sftp_config['host']}:{remote_path}")
        return True
        
    except Exception as e:
        print(f"ERROR: SFTP upload failed: {e}", file=sys.stderr)
        return False


def load_sftp_config():
    """Load SFTP configuration from ops vault or environment.
    
    Expected config:
    - FINANCE_SFTP_HOST
    - FINANCE_SFTP_USER
    - FINANCE_SFTP_KEY_PATH
    - FINANCE_SFTP_REMOTE_DIR (optional, defaults to /incoming)
    
    Returns:
        Dict with SFTP config, or None if not configured
    """
    import os
    
    host = os.environ.get('FINANCE_SFTP_HOST')
    user = os.environ.get('FINANCE_SFTP_USER')
    key_path = os.environ.get('FINANCE_SFTP_KEY_PATH')
    remote_dir = os.environ.get('FINANCE_SFTP_REMOTE_DIR', '/incoming')
    
    if not all([host, user, key_path]):
        return None
    
    return {
        'host': host,
        'username': user,
        'key_path': key_path,
        'remote_dir': remote_dir
    }
