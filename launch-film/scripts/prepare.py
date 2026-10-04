#!/usr/bin/env python3
"""Copy the reusable starter into a fresh, editable project. Never overwrites."""
import argparse,shutil
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('destination',type=Path);a=p.parse_args()
 root=Path(__file__).resolve().parents[1];dest=a.destination.resolve()
 if dest.exists():p.error('Destination already exists. Choose a fresh directory; existing work is not overwritten.')
 shutil.copytree(root/'templates'/'film',dest)
 shutil.copytree(root/'assets'/'brand',dest/'assets'/'brand',dirs_exist_ok=True)
 for name in ['audio','qa','renders']:(dest/name).mkdir(exist_ok=True)
 print('Prepared:',dest)
 print('Next: edit brief.json and brief.js, then generate the audio and render.')
if __name__=='__main__':main()
