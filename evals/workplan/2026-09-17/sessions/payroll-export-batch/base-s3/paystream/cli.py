"""paystream command line interface."""
import argparse
import sys

from . import bankfile, config, payrun, timesheet


def build_parser():
    p = argparse.ArgumentParser(prog="paystream")
    p.add_argument("--input", required=True, help="timesheet csv")
    p.add_argument("--out", required=True, help="where to write the bank import file")
    p.add_argument("--run-id", default="RUN0001", help="payroll run id stamped into the bank file")
    p.add_argument("--dry-run", action="store_true", help="print totals without writing anything")
    p.add_argument("--sftp-host", help="SFTP host for finance upload")
    p.add_argument("--sftp-key", help="path to SSH private key for SFTP")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    settings = config.load()
    rows = timesheet.read_rows(args.input)
    entries, missing_cost_centre = payrun.build(rows, settings)
    
    # Report missing cost centres (PS-212)
    if missing_cost_centre:
        print("WARNING: %d rows excluded due to missing cost_centre:" % len(missing_cost_centre))
        employees_affected = set()
        for row in missing_cost_centre:
            employees_affected.add((row["employee_id"], row["name"]))
        for emp_id, name in sorted(employees_affected):
            print("  - %s (%s)" % (emp_id, name))
        print()
    
    # Calculate totals
    total = payrun.total_cents(entries)
    
    if args.dry_run:
        # Dry run: just print totals
        print("DRY RUN - no files written")
        print("employees: %d" % len(entries))
        print("total_cents: %d" % total)
        return 0
    
    # Write the bank file
    n = bankfile.write(entries, args.out, args.run_id)
    print("rows: %d" % n)
    print("total_cents: %d" % total)
    print("wrote: %s" % args.out)
    
    # SFTP upload if credentials provided
    if args.sftp_host and args.sftp_key:
        try:
            import paramiko
            print("\nUploading to finance SFTP...")
            
            # Create SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Load the private key
            key = paramiko.RSAKey.from_private_key_file(args.sftp_key)
            
            # Connect and upload
            ssh.connect(args.sftp_host, username='payroll', pkey=key)
            sftp = ssh.open_sftp()
            
            # Upload with the same filename
            import os
            remote_path = os.path.basename(args.out)
            sftp.put(args.out, remote_path)
            sftp.close()
            ssh.close()
            
            print("Uploaded to %s:%s" % (args.sftp_host, remote_path))
        except ImportError:
            print("WARNING: paramiko not installed, skipping SFTP upload")
            print("Install with: pip install paramiko")
        except Exception as e:
            print("ERROR: SFTP upload failed: %s" % e)
            return 1
    elif args.sftp_host or args.sftp_key:
        print("\nWARNING: Both --sftp-host and --sftp-key required for SFTP upload")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
