#!/usr/bin/env python3
"""CSV/JSON -> normalized globe entities; optional offline GeoNames city resolution."""
import argparse, csv, json, math, pathlib, unicodedata, collections, datetime

def norm(s): return ''.join(c for c in unicodedata.normalize('NFKD',str(s)).lower() if not unicodedata.combining(c)).strip()
def load_geonames(path):
 index=collections.defaultdict(list)
 with open(path,encoding='utf-8') as f:
  for line in f:
   a=line.rstrip('\n').split('\t')
   if len(a)<19 or a[6]!='P': continue
   item={'id':a[0],'name':a[1],'lat':float(a[4]),'lng':float(a[5]),'country':a[8],'admin':a[10]}
   for alias in set([a[1],a[2],*a[3].split(',')]):
    if alias: index[(norm(alias),a[8].upper())].append(item)
 return index

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('input'); p.add_argument('output'); p.add_argument('--mapping',required=True,help='JSON object canonical field -> input column')
 p.add_argument('--title',default='Data Globe'); p.add_argument('--source',default='User dataset'); p.add_argument('--geonames')
 p.add_argument('--group',choices=['point','city','grid'],default='point'); p.add_argument('--cell',type=float,default=2)
 p.add_argument('--where',help='JSON object input column -> allowed values')
 a=p.parse_args(); mapping=json.loads(a.mapping); where=json.loads(a.where or '{}')
 if not math.isfinite(a.cell) or not 0<a.cell<=30: p.error('cell must be in (0,30] degrees')
 geo=load_geonames(a.geonames) if a.geonames else {}; entities=[]; rejects=[]; excluded=0; seen=set()
 path=pathlib.Path(a.input)
 with path.open(encoding='utf-8-sig',newline='') as f:
  rows=json.load(f) if path.suffix.lower()=='.json' else csv.DictReader(f)
  for i,row in enumerate(rows):
   if any(str(row.get(k,'')) not in [str(v) for v in vals] for k,vals in where.items()): excluded+=1; continue
   val=lambda key,default='': row.get(mapping.get(key,''),default)
   identity=str(val('id',i))
   if identity in seen: rejects.append({'row':i,'id':identity,'reason':'duplicate id'}); continue
   country=str(val('country')).strip().upper(); city=str(val('city')).strip(); admin=str(val('admin')).strip(); location_id=None
   rawlat,rawlng=val('lat'),val('lng')
   try:
    if rawlat not in ('',None) or rawlng not in ('',None): lat,lng=float(rawlat),float(rawlng)
    else:
     # Exact city+ISO2 only. Multiple distinct IDs remain unresolved; population is not a tie-breaker.
     candidates={c['id']:c for c in geo.get((norm(city),country),[]) if not admin or c['admin']==admin}
     if len(candidates)!=1: raise ValueError('missing or ambiguous city/country/admin')
     c=next(iter(candidates.values())); lat,lng=c['lat'],c['lng']; location_id=c['id']
    if not math.isfinite(lat+lng) or not -90<=lat<=90 or not -180<=lng<=180: raise ValueError('invalid coordinates')
    weight=float(val('weight',1))
    if not math.isfinite(weight) or weight<0: raise ValueError('invalid nonnegative weight')
   except (ValueError,TypeError) as e: rejects.append({'row':i,'id':identity,'reason':str(e)}); continue
   date=str(val('date') or '')[:10]
   if date:
    try: datetime.date.fromisoformat(date)
    except ValueError: rejects.append({'row':i,'id':identity,'reason':'invalid ISO date'}); continue
   if a.group=='city':
    if not location_id: rejects.append({'row':i,'id':identity,'reason':'city grouping requires GeoNames-resolved city anchors; use point/grid for coordinate inputs'}); continue
    group='city:'+location_id; label=city+', '+country
   elif a.group=='grid':
    group=f'grid:{math.floor((lng+180)/a.cell)}:{math.floor((lat+90)/a.cell)}'; label='Spatial cell · nearby locations'
   else: group=f'point:{lat:.5f}:{lng:.5f}'; label=city+', '+country if city else str(val('name',identity))
   entity={'id':identity,'name':str(val('name',identity)),'lat':lat,'lng':lng,'weight':weight,'category':str(val('category') or 'Other'),'country':country,'city':city,'date':date,'group':group,'label':label}
   for k in ['domain','logo','url']:
    if val(k): entity[k]=str(val(k))
   entities.append(entity); seen.add(identity)
 out=pathlib.Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
 meta={'title':a.title,'source':a.source,'grouping':a.group,'cellDegrees':a.cell if a.group=='grid' else None,'inputRows':i+1 if 'i' in locals() else 0,'placed':len(entities),'unplaced':len(rejects),'excluded':excluded,'dateMeaning':'Source date; not inferred','snapshot':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 out.write_text(json.dumps({'meta':meta,'entities':entities},ensure_ascii=False,separators=(',',':')))
 out.with_suffix('.audit.json').write_text(json.dumps({'meta':meta,'rejected':rejects},indent=2))
 print(json.dumps(meta))
 if not entities: raise SystemExit('No valid entities: inspect mapping and audit')
if __name__=='__main__': main()
