"""Push a finished bank file to the finance SFTP drop.

UNTESTED. There is no host, user or key available outside the ops vault, so this path has
never been executed end to end. Credentials are read from the environment at call time and
are never written into the repo.
"""
import os

ENV = ("PAYSTREAM_SFTP_HOST", "PAYSTREAM_SFTP_USER", "PAYSTREAM_SFTP_KEY")


class MissingCredentials(RuntimeError):
    pass


def push(path):
    missing = [k for k in ENV if not os.environ.get(k)]
    if missing:
        raise MissingCredentials(
            "cannot upload %s: %s not set. Pull them from the ops vault before the run."
            % (path, ", ".join(missing)))
    raise NotImplementedError(
        "transport not wired up: needs an sftp client and one successful dry run against the "
        "finance drop before it can be trusted with a real payroll file")
