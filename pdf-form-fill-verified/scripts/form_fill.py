#!/usr/bin/env python3
"""Fill AcroForms; success requires saved-PDF raster evidence, not only /V.
Dependencies: PyMuPDF, pypdf, Pillow, numpy; system pdftoppm (Poppler).
"""
import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import fitz
import numpy as np
from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, BooleanObject, DecodedStreamObject,
                            DictionaryObject, FloatObject, NameObject, NumberObject)

BUTTON = '/Btn'


def qualified(obj):
    parts, seen = [], set()
    while obj:
        if id(obj) in seen:
            raise ValueError('Cyclic field parent')
        seen.add(id(obj))
        if obj.get('/T') is not None:
            parts.append(str(obj['/T']))
        obj = obj['/Parent'].get_object() if '/Parent' in obj else None
    return '.'.join(reversed(parts))


def inherited(obj, key, default=None):
    seen = set()
    while obj:
        if id(obj) in seen:
            raise ValueError('Cyclic field parent')
        seen.add(id(obj))
        if key in obj:
            return obj[key]
        obj = obj['/Parent'].get_object() if '/Parent' in obj else None
    return default


def widgets(pdf):
    for pi, page in enumerate(pdf.pages):
        wi = 0
        for ref in page.get('/Annots', []):
            obj = ref.get_object()
            if obj.get('/Subtype') == '/Widget':
                wi += 1
                yield f'p{pi+1}:w{wi}', pi, obj


def on_values(obj):
    normal = obj.get('/AP', {}).get('/N', {})
    if hasattr(normal, 'get_object'):
        normal = normal.get_object()
    return [str(k)[1:] for k in normal.keys() if k != '/Off'] if isinstance(normal, DictionaryObject) and not hasattr(normal, 'get_data') else []


def inventory(path):
    reader = PdfReader(path)
    doc = fitz.open(path)
    positions = {}
    for page in doc:
        for wi, w in enumerate(page.widgets() or [], 1):
            # Widget rect is unrotated MuPDF coordinates; page PNG uses rotation.
            positions[f'p{page.number+1}:w{wi}'] = list(w.rect * page.rotation_matrix)
    records = []
    for ident, pi, obj in widgets(reader):
        flags = int(inherited(obj, '/Ff', 0))
        ft = str(inherited(obj, '/FT', ''))
        records.append(dict(id=ident, name=qualified(obj), page=pi+1,
                            type=ft, flags=flags, value=str(inherited(obj, '/V', '')),
                            rect_pdf=[float(v) for v in obj['/Rect']],
                            rect_png_points=positions.get(ident),
                            on_values=on_values(obj),
                            appearance_state=str(obj.get('/AS', '')),
                            radio=ft == BUTTON and bool(flags & (1 << 15))))
    all_fields = []
    for name, field in (reader.get_fields() or {}).items():
        all_fields.append(dict(name=name, type=str(field.get('/FT', 'container')),
                               value=str(field.get('/V', ''))))
    result = dict(pages=len(reader.pages), widgets=records, fields=all_fields)
    doc.close()
    return result


def resolve(inv, spec):
    if not isinstance(spec, dict) or set(spec) != {'fields'} or not isinstance(spec['fields'], dict):
        raise ValueError('Mapping must be {"fields": {"full field name or widget id": value}}')
    if not inv['widgets']:
        raise ValueError('No AcroForm widgets: scanned, flattened or XFA-only forms are unsupported')
    resolved = {}
    for key, val in spec['fields'].items():
        found = [r for r in inv['widgets'] if key in (r['id'], r['name'])]
        if not found:
            raise ValueError(f'Unknown field: {key}')
        if len(found) > 1 and any(r['type'] != BUTTON for r in found):
            raise ValueError(f'Ambiguous field: use widget ids: {key}')
        for r in found:
            ident = r['id']
            if ident in resolved:
                raise ValueError(f'Duplicate mapping for {ident}')
            if r['flags'] & 1:
                raise ValueError(f'Read-only field: {key}')
            if r['type'] == BUTTON:
                if r['flags'] & (1 << 16):
                    raise ValueError('Pushbuttons cannot be filled')
                if val is True:
                    if len(found) != 1 or len(r['on_values']) != 1 or r['radio']:
                        raise ValueError(f'Use explicit export value for {key}')
                    selected = r['on_values'][0]
                elif val is False or val == 'Off':
                    selected = 'Off'
                elif isinstance(val, str) and val in r['on_values']:
                    selected = val
                elif len(found) > 1 and isinstance(val, str) and any(val in f['on_values'] for f in found):
                    selected = 'Off'
                else:
                    raise ValueError(f'Invalid button value {val!r} for {key}: {r["on_values"]}')
                resolved[ident] = selected
            elif r['type'] in ('/Tx', '/Ch') and isinstance(val, str):
                if sum(s['name'] == r['name'] for s in inv['widgets']) > 1:
                    raise ValueError(f'Repeated text/choice field name needs manual handling: {r["name"]}')
                resolved[ident] = val
            else:
                raise ValueError(f'Unsupported field type/value: {key} {r["type"]}')
    # A radio group must have one consistent parent /V. Widget ids can select a member.
    for name in {r['name'] for r in inv['widgets'] if r['radio']}:
        group = [r for r in inv['widgets'] if r['name'] == name]
        if any(r['id'] in resolved for r in group):
            chosen = [resolved[r['id']] for r in group if resolved.get(r['id'], 'Off') != 'Off']
            if len(chosen) > 1:
                raise ValueError(f'Multiple selected radio widgets: {name}')
            for r in group:
                resolved.setdefault(r['id'], 'Off')
    return resolved


def appearance(writer, width, height, tick=False):
    # A font-independent visible X; no reliance on viewer-generated appearances.
    stream = DecodedStreamObject()
    ops = ''
    if tick:
        m = min(width, height) * .20
        ops = (f'q 0 G {max(.7, min(width,height)*.12):.3f} w '
               f'{m:.3f} {m:.3f} m {width-m:.3f} {height-m:.3f} l S '
               f'{m:.3f} {height-m:.3f} m {width-m:.3f} {m:.3f} l S Q')
    stream.set_data(ops.encode('ascii'))
    stream.update({NameObject('/Type'): NameObject('/XObject'),
                   NameObject('/Subtype'): NameObject('/Form'),
                   NameObject('/BBox'): ArrayObject([FloatObject(v) for v in (0, 0, width, height)]),
                   NameObject('/Resources'): DictionaryObject()})
    return writer._add_object(stream)


def set_buttons(writer, inv, values, regenerate=False, all_off=False):
    records = {r['id']: r for r in inv['widgets']}
    radio_groups = {}
    for ident, pi, obj in widgets(writer):
        if ident not in values or records[ident]['type'] != BUTTON:
            continue
        r = records[ident]
        value = 'Off' if all_off else values[ident]
        rect = [float(v) for v in obj['/Rect']]
        width, height = abs(rect[2]-rect[0]), abs(rect[3]-rect[1])
        ap = obj.get('/AP', DictionaryObject()).get_object()
        normal = ap.get('/N', DictionaryObject()).get_object()
        if not isinstance(normal, DictionaryObject) or hasattr(normal, 'get_data'):
            normal = DictionaryObject()
        if '/Off' not in normal:
            normal[NameObject('/Off')] = appearance(writer, width, height)
        # Ensure all known export states stay discoverable after repair.
        for on in r['on_values']:
            if regenerate or '/' + on not in normal:
                normal[NameObject('/' + on)] = appearance(writer, width, height, tick=True)
        ap[NameObject('/N')] = normal
        obj[NameObject('/AP')] = ap
        obj[NameObject('/AS')] = NameObject('/' + value)
        # Make the appearance printable and visible.
        flags = int(obj.get('/F', 0))
        obj[NameObject('/F')] = NumberObject((flags | 4) & ~(1 | 2 | 32))
        owner = obj
        while '/T' not in owner and '/Parent' in owner:
            owner = owner['/Parent'].get_object()
        if r['radio']:
            radio_groups.setdefault(r['name'], []).append((owner, value))
        else:
            owner[NameObject('/V')] = NameObject('/' + value)
    for group in radio_groups.values():
        value = next((v for _, v in group if v != 'Off'), 'Off')
        for owner, _ in group:
            owner[NameObject('/V')] = NameObject('/' + value)
    acro = writer.root_object.get('/AcroForm')
    if acro:
        acro.get_object()[NameObject('/NeedAppearances')] = BooleanObject(False)
        # Hybrid IRS PDFs carry stale XML. Keep the verified AcroForm view authoritative.
        if '/XFA' in acro.get_object():
            del acro.get_object()['/XFA']


def build(source, target, inv, values, regenerate=False, all_off=False, flatten=False):
    writer = PdfWriter(clone_from=source)
    text = {r['name']: values[r['id']] for r in inv['widgets']
            if r['id'] in values and r['type'] in ('/Tx', '/Ch')}
    if text:
        writer.update_page_form_field_values(None, text, auto_regenerate=False)
    set_buttons(writer, inv, values, regenerate, all_off)
    with open(target, 'wb') as out:
        writer.write(out)
    if flatten:
        with fitz.open(target) as doc:
            doc.bake(annots=False, widgets=True)
            flattened = doc.tobytes(garbage=4, deflate=True)
        Path(target).write_bytes(flattened)


def render(pdf, directory, dpi=180):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    subprocess.run(['pdftoppm', '-png', '-r', str(dpi), str(pdf), str(directory/'page')],
                   check=True, capture_output=True, timeout=180)
    files = sorted(directory.glob('page-*.png'), key=lambda p: int(p.stem.split('-')[-1]))
    with fitz.open(pdf) as doc:
        if len(files) != len(doc):
            raise ValueError('Renderer did not produce every page')
    return files


def compare(inv, values, actual_files, off_files, directory):
    checks = []
    for r in inv['widgets']:
        if r['id'] not in values or r['type'] != BUTTON:
            continue
        p = r['page'] - 1
        with Image.open(actual_files[p]) as im, Image.open(off_files[p]) as ref:
            if im.size != ref.size:
                raise ValueError('Render dimensions differ')
            # PNG pixels correspond to rotated CropBox coordinates, at fixed DPI.
            scale = 180 / 72
            rect = r['rect_png_points']
            if rect is None:
                raise ValueError(f'No render coordinates: {r["id"]}')
            x0,y0,x1,y1 = [v*scale for v in rect]
            # Ignore border; only new dark ink inside the checkbox counts.
            inset = min(x1-x0, y1-y0)*.15
            box = (math.ceil(x0+inset), math.ceil(y0+inset),
                   math.floor(x1-inset), math.floor(y1-inset))
            if box[2]-box[0] < 5 or box[3]-box[1] < 5 or min(box) < 0 or box[2] > im.width or box[3] > im.height:
                raise ValueError(f'Checkbox too small or outside page: {r["id"]}')
            a = np.array(im.convert('L').crop(box), dtype=np.int16)
            b = np.array(ref.convert('L').crop(box), dtype=np.int16)
            new_ink = (a < 150) & (b-a > 70)
            pixels = int(new_ink.sum())
            fraction = float(new_ink.mean())
            rows = int(np.any(new_ink, axis=1).sum())
            cols = int(np.any(new_ink, axis=0).sum())
            expected = values[r['id']] != 'Off'
            visible = pixels >= max(6, a.size*.035) and rows >= a.shape[0]*.35 and cols >= a.shape[1]*.35
            # An intentionally unchecked box must match the off reference.
            ok = visible if expected else pixels <= max(2, a.size*.01)
            crop = Path(directory)/(r['id'].replace(':','-')+'.png')
            im.crop((math.floor(x0)-3,math.floor(y0)-3,math.ceil(x1)+3,math.ceil(y1)+3)).resize((180,180)).save(crop)
            checks.append(dict(id=r['id'], name=r['name'], page=r['page'],
                               expected=values[r['id']], visible_tick=bool(visible),
                               new_dark_pixels=pixels, ink_fraction=round(fraction,4),
                               occupied_rows=rows, occupied_columns=cols, passed=bool(ok), crop=str(crop)))
    return checks


def verify(source, candidate, spec, evidence):
    inv = inventory(source)
    values = resolve(inv, spec)
    evidence = Path(evidence).resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        off = Path(tmp)/'off.pdf'
        build(source, off, inv, values, all_off=True)
        off_images = render(off, evidence/'off')
        actual_images = render(candidate, evidence/'pages')
    checks = compare(inv, values, actual_images, off_images, evidence)
    with fitz.open(candidate) as doc:
        flattened = not any(list(p.widgets() or []) for p in doc)
    metadata = []
    if not flattened:
        objects = {ident: obj for ident, _, obj in widgets(PdfReader(candidate))}
        for r in inv['widgets']:
            if r['type'] != BUTTON or r['id'] not in values:
                continue
            obj = objects.get(r['id'])
            expected_v = values[r['id']]
            if r['radio']:
                expected_v = next((values[s['id']] for s in inv['widgets'] if s['name'] == r['name'] and values.get(s['id'],'Off') != 'Off'), 'Off')
            ok = obj is not None and str(obj.get('/AS')) == '/'+values[r['id']] and str(inherited(obj, '/V')) == '/'+expected_v
            metadata.append(dict(id=r['id'], passed=ok))
    report = dict(passed=all(c['passed'] for c in checks) and all(c['passed'] for c in metadata),
                  intended_ticks=sum(v != 'Off' for k,v in values.items() if any(r['id']==k and r['type']==BUTTON for r in inv['widgets'])),
                  pages_rendered=len(actual_images), flattened=flattened, checks=checks,
                  metadata_checks=metadata, hybrid_xfa_removed='/XFA' in PdfReader(source).trailer['/Root'].get('/AcroForm', {}), sha256=hashlib.sha256(Path(candidate).read_bytes()).hexdigest())
    (evidence/'verification.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def fill(source, target, spec, evidence, flatten=False):
    source, target = Path(source).resolve(), Path(target).resolve()
    if source == target:
        raise ValueError('Output must differ from the original')
    inv = inventory(source)
    values = resolve(inv, spec)
    evidence = Path(evidence).resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    attempts = []
    # Keep failed candidates as evidence; publish output path only on verified success.
    for attempt, regenerate in enumerate((False, True), 1):
        attempt_dir = evidence/f'attempt-{attempt}'
        attempt_dir.mkdir(parents=True, exist_ok=True)
        candidate = attempt_dir/'candidate.pdf'
        build(source, candidate, inv, values, regenerate=regenerate, flatten=flatten)
        report = verify(source, candidate, spec, attempt_dir)
        attempts.append(dict(attempt=attempt, regenerated=regenerate, passed=report['passed']))
        if report['passed']:
            shutil.copyfile(candidate, target)
            report.update(output=str(target), attempts=attempts)
            (evidence/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
            return report
    (evidence/'verification.json').write_text(json.dumps(dict(passed=False, attempts=attempts), indent=2)+'\n')
    raise ValueError('Visible checkbox verification failed after 2 attempts; inspect evidence, do not deliver candidate')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    ls = sub.add_parser('list'); ls.add_argument('pdf')
    for name in ('fill', 'verify'):
        p = sub.add_parser(name)
        p.add_argument('source'); p.add_argument('output')
        p.add_argument('--data', required=True); p.add_argument('--evidence', required=True)
        if name == 'fill': p.add_argument('--flatten', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'list': result = inventory(args.pdf)
        else:
            spec = json.loads(Path(args.data).read_text())
            if args.command == 'fill': result = fill(args.source,args.output,spec,args.evidence,args.flatten)
            else: result = verify(args.source,args.output,spec,args.evidence)
        print(json.dumps(result, indent=2))
        return 0 if result.get('passed',True) else 1
    except (ValueError, RuntimeError, subprocess.SubprocessError) as err:
        print(f'ERROR: {err}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
