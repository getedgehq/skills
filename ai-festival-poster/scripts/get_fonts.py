#!/usr/bin/env python3
"""Download the three open-source (SIL OFL) fonts the poster uses into scripts/fonts/."""
import os, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
FILES = {"Anton-Regular.ttf": "anton/Anton-Regular.ttf",
         "ArchivoNarrow[wght].ttf": "archivonarrow/ArchivoNarrow%5Bwght%5D.ttf",
         "Inter[opsz,wght].ttf": "inter/Inter%5Bopsz,wght%5D.ttf"}
os.makedirs(os.path.join(HERE, "fonts"), exist_ok=True)
for name, path in FILES.items():
    dst = os.path.join(HERE, "fonts", name)
    if not os.path.exists(dst):
        urllib.request.urlretrieve(BASE + path, dst)
    print("ok", name)
