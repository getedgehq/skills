"""paystream command line interface."""
import argparse
import sys
import os

from . import bankfile, config, payrun, timesheet


def build_parser():
    p = argparse.ArgumentParser(prog="paystream")
    p.add_argument("--input", required=True, help="timesheet csv")
    p.add_argument("--out", required=True, help="where to write the bank import file")
    p.add_argument("--run-id", default="RUN0001", help="payroll run id stamped into the bank file")
    p.add_argument("--dry-run", action="store_true", help="print totals without writing files")
    p.add_argument("--sftp-upload", action="store_true", help="upload to finance SFTP after writing")
    p.add_argument("--sftp-host", help="SFTP host (or set PAYSTREAM_SFTP_HOST)")
    p.add_argument("--sftp-key", help="path to SSH private key (or set PAYSTREAM_SFTP_KEY)")
    return p


def upload_to_sftp(local_path, host, key_path):
    """Upload file to finance SFTP server.
    
    Returns: True on success, False on failure
    """
    try:
        import paramiko
    except ImportError:
        print("ERROR: paramiko not installed. Run: pip install paramiko")
        return False
    
    try:
        # Parse host (may include username and path)
        if "@" in host:
            username, host_part = host.split("@", 1)
        else:
            username = "paystream"
            host_part = host
            
        if ":" in host_part:
            hostname, remote_path = host_part.split(":", 1)
        else:
            hostname = host_part
            remote_path = "/incoming/"
        
        # Connect
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, key_filename=key_path)
        
        sftp = client.open_sftp()
        remote_file = os.path.join(remote_path, os.path.basename(local_path))
        sftp.put(local_path, remote_file)
        sftp.close()
        client.close()
        
        print("uploaded to SFTP: %s" % remote_file)
        return True
        
    except Exception as e:
        print("ERROR: SFTP upload failed: %s" % e)
        return False


def main(argv=None):
    args = build_parser().parse_args(argv)
    settings = config.load()
    rows = timesheet.read_rows(args.input)
    entries, filtered = payrun.build(rows, settings)
    
    # PS-212: Report filtered rows with missing cost_centre
    if filtered:
        print("WARNING: %d rows excluded due to missing cost_centre:" % len(filtered))
        for r in filtered:
            print("  %s (%s) - %s, day %s, %d minutes" % (
                r["employee_id"], r["name"], r["week"], r["day"], r["minutes"]))
        print()
    
    total = payrun.total_cents(entries)
    
    if args.dry_run:
        print("DRY RUN - no files written")
        print("rows: %d" % len(entries))
        print("total_cents: %d" % total)
        return 0
    
    n = bankfile.write(entries, args.out, args.run_id)
    print("rows: %d" % n)
    print("total_cents: %d" % total)
    print("wrote: %s" % args.out)
    
    # SFTP upload if requested
    if args.sftp_upload:
        host = args.sftp_host or os.environ.get("PAYSTREAM_SFTP_HOST")
        key = args.sftp_key or os.environ.get("PAYSTREAM_SFTP_KEY")
        
        if not host or not key:
            print("ERROR: SFTP upload requested but credentials not provided")
            print("  Set --sftp-host and --sftp-key, or PAYSTREAM_SFTP_HOST and PAYSTREAM_SFTP_KEY")
            return 1
        
        if not upload_to_sftp(args.out, host, key):
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
