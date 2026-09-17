"""SFTP push to finance server.

TODO: This requires credentials from the ops vault.
Host and SSH key need to be configured before this will work.

Expected configuration (not present):
- SFTP host
- SFTP username  
- SFTP path
- SSH private key

Once credentials are available, update this module with the actual connection details.
"""


def push_to_finance(local_path):
    """Push the bank file to the finance SFTP server.
    
    Args:
        local_path: Path to the local bank file to upload
        
    Raises:
        NotImplementedError: Credentials not yet configured
    """
    raise NotImplementedError(
        "SFTP push requires credentials from ops vault. "
        "Please configure host, username, path, and SSH key in this module."
    )


# Example implementation once credentials are available:
"""
import paramiko
import os

SFTP_HOST = "finance.example.com"  # From ops vault
SFTP_PORT = 22
SFTP_USER = "paystream_upload"     # From ops vault
SFTP_PATH = "/incoming/payroll"     # From ops vault
SSH_KEY_PATH = os.path.expanduser("~/.ssh/finance_deploy_key")  # From ops vault


def push_to_finance(local_path):
    import paramiko
    
    # Load the SSH key
    private_key = paramiko.RSAKey.from_private_key_file(SSH_KEY_PATH)
    
    # Connect to SFTP
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USER, pkey=private_key)
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    try:
        # Upload the file
        remote_filename = os.path.basename(local_path)
        remote_path = os.path.join(SFTP_PATH, remote_filename)
        sftp.put(local_path, remote_path)
    finally:
        sftp.close()
        transport.close()
"""
