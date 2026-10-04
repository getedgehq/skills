#!/usr/bin/env python3
"""Local structural validation of this Agent Skills package."""
import argparse,re,json,sys
from pathlib import Path
import yaml

def main():
 p=argparse.ArgumentParser();p.add_argument('skill',type=Path);a=p.parse_args();root=a.skill.resolve();errors=[]
 text=(root/'SKILL.md').read_text();m=re.match(r'^---\n(.*?)\n---\n',text,re.S)
 if not m:errors.append('Missing YAML frontmatter');meta={}
 else:meta=yaml.safe_load(m.group(1))
 name=meta.get('name','')
 if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',name) or len(name)>64:errors.append('Invalid skill name')
 if root.name!=name:errors.append('Directory name must match skill name')
 if not isinstance(meta.get('description'),str) or not 1<=len(meta['description'])<=1024:errors.append('Invalid description')
 for target in re.findall(r'\]\(([^)]+)\)',text):
  if '://' not in target and not (root/target).is_file():errors.append('Broken reference: '+target)
 for f in root.rglob('*'):
  if f.is_file() and f.suffix.lower() in {'.ttf','.otf','.woff','.woff2','.eot','.ttc'}:errors.append('Font binary: '+str(f.relative_to(root)))
 if len(text.splitlines())>=500:errors.append('SKILL.md exceeds progressive-disclosure target')
 print(json.dumps({'ok':not errors,'errors':errors,'name':name,'skill_lines':len(text.splitlines())},indent=2));return bool(errors)
if __name__=='__main__':sys.exit(main())
