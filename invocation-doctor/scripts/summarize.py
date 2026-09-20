#!/usr/bin/env python3
import argparse,json
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('before',type=Path);ap.add_argument('after',type=Path);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--demo',action='store_true');a=ap.parse_args();b=json.loads(a.before.read_text());c=json.loads(a.after.read_text())
def rate(x):
 if 'accuracy' in x:return float(x['accuracy'])
 tp=x.get('tp',0);tn=x.get('tn',0);fp=x.get('fp',0);fn=x.get('fn',0);return (tp+tn)/max(1,tp+tn+fp+fn)
r={'demo':a.demo,'before_accuracy':rate(b),'after_accuracy':rate(c),'delta':rate(c)-rate(b),'before':b,'after':c};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2))

