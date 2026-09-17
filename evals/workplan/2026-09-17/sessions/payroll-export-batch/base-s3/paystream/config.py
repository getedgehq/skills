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
    return settings
