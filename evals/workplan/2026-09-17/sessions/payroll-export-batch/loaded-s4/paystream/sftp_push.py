"""SFTP push to finance server."""
import os
import sys

# Placeholder - credentials should be provided via config
# TODO: Get from ops vault
SFTP_CONFIG = {
    "host": os.environ.get("PAYSTREAM_SFTP_HOST", ""),
    "port": int(os.environ.get("PAYSTREAM_SFTP_PORT", "22")),
    "username": os.environ.get("PAYSTREAM_SFTP_USER", ""),
    "key_path": os.environ.get("PAYSTREAM_SFTP_KEY", ""),
    "remote_dir": os.environ.get("PAYSTREAM_SFTP_DIR", "/incoming"),
}


def push(local_path, settings):
    """Push file to finance SFTP server.
    
    Requires environment variables:
    - PAYSTREAM_SFTP_HOST: SFTP server hostname
    - PAYSTREAM_SFTP_USER: SFTP username
    - PAYSTREAM_SFTP_KEY: Path to SSH private key file
    - PAYSTREAM_SFTP_PORT: (optional, default 22)
    - PAYSTREAM_SFTP_DIR: (optional, default /incoming)
    """
    if not SFTP_CONFIG["host"]:
        raise ValueError("SFTP host not configured. Set PAYSTREAM_SFTP_HOST environment variable.")
    if not SFTP_CONFIG["username"]:
        raise ValueError("SFTP username not configured. Set PAYSTREAM_SFTP_USER environment variable.")
    if not SFTP_CONFIG["key_path"]:
        raise ValueError("SFTP key path not configured. Set PAYSTREAM_SFTP_KEY environment variable.")
    
    try:
        import paramiko
    except ImportError:
        raise ImportError("paramiko not installed. Install with: pip install paramiko")
    
    # Load the private key
    key = paramiko.RSAKey.from_private_key_file(SFTP_CONFIG["key_path"])
    
    # Connect to SFTP server
    transport = paramiko.Transport((SFTP_CONFIG["host"], SFTP_CONFIG["port"]))
    transport.connect(username=SFTP_CONFIG["username"], pkey=key)
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    try:
        # Upload the file
        remote_path = os.path.join(SFTP_CONFIG["remote_dir"], os.path.basename(local_path))
        sftp.put(local_path, remote_path)
    finally:
        sftp.close()
        transport.close()
