# SFTP Configuration - TODO

This file needs to be populated with credentials from the ops vault.

## Required Information

The following needs to be retrieved from the ops vault:

1. **SFTP Host:** `finance.sftp.example.com` (placeholder)
2. **Username:** `paystream_upload` (placeholder)
3. **SSH Private Key Path:** `/path/to/private/key` (placeholder)
4. **Remote Directory:** `/uploads/paystream/` (placeholder)

## How to Configure

### Option 1: Add to paystream.ini

Add a new `[sftp]` section to `paystream.ini`:

```ini
[sftp]
host = finance.sftp.example.com
username = paystream_upload
key_path = /path/to/private/key
remote_path = /uploads/paystream/
```

Then update `paystream/config.py` to read these settings.

### Option 2: Environment Variables

Set environment variables:
```bash
export PAYSTREAM_SFTP_HOST=finance.sftp.example.com
export PAYSTREAM_SFTP_USER=paystream_upload
export PAYSTREAM_SFTP_KEY=/path/to/private/key
export PAYSTREAM_SFTP_PATH=/uploads/paystream/
```

Then update `paystream/sftp.py` to read from environment.

### Option 3: Command Line Arguments

Add CLI flags:
```bash
python3 -m paystream --input data.csv --out bank.csv \
  --sftp-push \
  --sftp-host finance.sftp.example.com \
  --sftp-user paystream_upload \
  --sftp-key /path/to/private/key \
  --sftp-path /uploads/paystream/
```

## Dependencies

The SFTP implementation will require the `paramiko` library:

```bash
pip install paramiko
```

## Security Notes

- The SSH private key should have restricted permissions (chmod 600)
- Never commit the private key or credentials to git
- Consider using SSH agent for key management
- The ops vault should be the single source of truth for these credentials
