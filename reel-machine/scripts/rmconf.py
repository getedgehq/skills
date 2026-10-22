"""Shared config for reel-machine scripts.

Values come from the environment first, then from the config file at
$REEL_CONFIG (default: ~/.config/reel-machine/config.env), then from the
defaults below. The config file is plain KEY=value lines. Keep secrets
(ELEVENLABS_API_KEY, BUFFER_TOKEN*) in the environment, injected by your
secrets manager for the one process that needs them, never in the file.
"""
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG_FILE = Path(os.path.expanduser(os.environ.get("REEL_CONFIG", "~/.config/reel-machine/config.env")))

DEFAULTS = {
    "REEL_WORK": "~/reel-machine",          # clips/, transcripts/, bundles/, renders/
    "REEL_HANDLE": "@yourhandle",           # closer text on the last frame
    "REEL_LANGUAGE": "en",                  # Scribe language code; empty = auto-detect
    "REEL_HOOK_FONT": "",                   # default: $REEL_WORK/fonts/FunnelDisplay.ttf
    "REEL_CAPTION_FONT": "",                # default: Helvetica Neue Bold on macOS, else the hook font
    "REEL_CAPTION_FONT_INDEX": "",          # face index inside a .ttc (Helvetica Neue Bold = 1)
    "REEL_SPEED": "1.1",
    "REEL_GRADE": "eq=contrast=1.05:saturation=1.14:gamma=1.02,colorbalance=rm=-0.015:bm=0.015",
    "REEL_REMOTE": "",                      # optional ssh host for remote_render.sh
    "REEL_REVIEW_CMD": "",                  # second model for caption review, prompt on stdin
    "REEL_BANNED_WORDS": "",                # comma list the caption check rejects (e.g. a word your brand avoids)
    "REEL_PUBLIC_BASE_URL": "",             # https base where rendered mp4s are publicly reachable
    "REEL_UPLOAD_CMD": "",                  # e.g. "rsync -q {file} user@host:/var/www/reels/" ({file} is replaced)
    "BUFFER_INSTAGRAM_CHANNEL": "",         # Buffer channel id or handle
    "BUFFER_TIKTOK_CHANNEL": "",
    "BUFFER_YOUTUBE_CHANNEL": "",
    "BUFFER_IG_COLLAB": "",                 # optional Instagram collaborator username(s), comma list
    "YOUTUBE_CATEGORY_ID": "28",            # 28 = Science & Technology
}


def _file_values():
    vals = {}
    if CONFIG_FILE.exists():
        for line in CONFIG_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip().strip('"').strip("'")
    return vals


_FILE = _file_values()


def get(key, default=None):
    if os.environ.get(key):
        return os.environ[key]
    if _FILE.get(key):
        return _FILE[key]
    if default is not None:
        return default
    return DEFAULTS.get(key, "")


def work():
    p = Path(os.path.expanduser(get("REEL_WORK")))
    p.mkdir(parents=True, exist_ok=True)
    return p


def hook_font():
    f = get("REEL_HOOK_FONT") or str(work() / "fonts" / "FunnelDisplay.ttf")
    if not Path(os.path.expanduser(f)).exists():
        raise SystemExit(f"hook font not found: {f} (run scripts/setup.sh or set REEL_HOOK_FONT)")
    return os.path.expanduser(f)


def caption_font():
    """(path, index) for the caption face."""
    f = get("REEL_CAPTION_FONT")
    idx = get("REEL_CAPTION_FONT_INDEX")
    if not f:
        mac = "/System/Library/Fonts/HelveticaNeue.ttc"
        if Path(mac).exists():
            return mac, int(idx or 1)
        return hook_font(), 0
    return os.path.expanduser(f), int(idx or 0)


def bold(font):
    """Variable fonts (Funnel Display) need the Bold instance selected."""
    try:
        font.set_variation_by_name("Bold")
    except Exception:
        pass
    return font
