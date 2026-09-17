"""Runtime settings, read from paystream.ini with defaults."""
import configparser
import os

DEFAULTS = {
    "rounding_minutes": 15,
    "overtime_weekly_minutes": 2400,
}

INI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "paystream.ini")


def load(path=None):
    cfg = configparser.ConfigParser()
    cfg.read(path or INI)
    settings = dict(DEFAULTS)
    if cfg.has_section("payroll"):
        for key in DEFAULTS:
            if cfg.has_option("payroll", key):
                settings[key] = cfg.getint("payroll", key)
    
    # Load SFTP config if present
    if cfg.has_section("sftp"):
        settings["sftp"] = {
            "host": cfg.get("sftp", "host") if cfg.has_option("sftp", "host") else None,
            "username": cfg.get("sftp", "username") if cfg.has_option("sftp", "username") else None,
            "key_path": cfg.get("sftp", "key_path") if cfg.has_option("sftp", "key_path") else None,
            "remote_dir": cfg.get("sftp", "remote_dir") if cfg.has_option("sftp", "remote_dir") else None,
            "port": cfg.getint("sftp", "port") if cfg.has_option("sftp", "port") else 22,
        }
    
    return settings
