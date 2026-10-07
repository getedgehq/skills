#!/usr/bin/env python3
"""Pack a manifest {entity_id: local_image_path} into one sprite; missing images keep monograms."""
import argparse, json, math, pathlib
from PIL import Image, ImageOps
p=argparse.ArgumentParser();p.add_argument('data');p.add_argument('manifest');p.add_argument('--cols',type=int,default=16);p.add_argument('--size',type=int,default=64);a=p.parse_args()
if not 1<=a.cols<=64 or not 16<=a.size<=256:p.error('cols 1..64 and size 16..256')
path=pathlib.Path(a.data);data=json.loads(path.read_text());manifest=json.loads(pathlib.Path(a.manifest).read_text());images=[];indices={}
for e in data['entities']:
 file=manifest.get(e['id'])
 if not file:continue
 try:
  with Image.open(file) as im:
   if min(im.size)<16:continue
   im=ImageOps.contain(im.convert('RGBA'),(a.size-8,a.size-8));tile=Image.new('RGBA',(a.size,a.size));tile.alpha_composite(im,((a.size-im.width)//2,(a.size-im.height)//2))
 except (OSError,ValueError):continue
 if file not in indices:indices[file]=len(images);images.append(tile)
 e['sprite']=indices[file]
if images:
 sprite=Image.new('RGBA',(a.cols*a.size,math.ceil(len(images)/a.cols)*a.size))
 for i,im in enumerate(images):sprite.alpha_composite(im,((i%a.cols)*a.size,(i//a.cols)*a.size))
 sprite.save(path.parent/'logos.webp','WEBP');data['meta']['sprite']={'cols':a.cols,'size':a.size,'url':'logos.webp','count':len(images)}
 path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
print('Packed',len(images),'unique logos; all others use monograms')
