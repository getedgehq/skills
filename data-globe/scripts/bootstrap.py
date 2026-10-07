#!/usr/bin/env python3
"""Copy the starter into a new directory and freeze the free MapLibre runtime locally."""
import argparse, pathlib, shutil, urllib.request
p=argparse.ArgumentParser(); p.add_argument('out'); a=p.parse_args()
out=pathlib.Path(a.out)
if out.exists() and any(out.iterdir()): p.error('output must be empty; existing projects are never overwritten')
shutil.copytree(pathlib.Path(__file__).resolve().parents[1]/'template',out,dirs_exist_ok=True)
(out/'vendor').mkdir(exist_ok=True)
for remote,local in [('dist/maplibre-gl.js','maplibre-gl.js'),('dist/maplibre-gl.css','maplibre-gl.css'),('LICENSE.txt','maplibre-LICENSE.txt')]:
 urllib.request.urlretrieve('https://unpkg.com/maplibre-gl@5.24.0/'+remote,out/'vendor'/local)
print('Starter ready:',out,'— serve with python3 -m http.server --bind 127.0.0.1 --directory',out,'0')
