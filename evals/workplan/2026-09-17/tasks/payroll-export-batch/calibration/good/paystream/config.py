"""Runtime settings, read from paystream.ini with defaults."""
import configparser
import os

DEFAULTS = {
    "rounding_minutes": 15,
    "overtime_weekly_minutes": 2400,
}

# The ini has always been written [payroll]; config.py was reading [paystream], so nothing
# in the file was ever applied. [paystream] stays accepted so an older ini still works.
SECTIONS = ("payroll", "paystream")

INI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "paystream.ini")


def load(path=None):
    cfg = configparser.ConfigParser()
    cfg.read(path or INI)
    settings = dict(DEFAULTS)
    for section in SECTIONS:
        if cfg.has_section(section):
            for key in DEFAULTS:
                if cfg.has_option(section, key):
                    settings[key] = cfg.getint(section, key)
    return settings
