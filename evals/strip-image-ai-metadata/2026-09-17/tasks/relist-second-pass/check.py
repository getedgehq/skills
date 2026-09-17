#!/usr/bin/env python3
"""Hard checks for strip-image-ai-metadata.relist-second-pass.  Usage: python3 check.py <collected_dir>

Someone already ran a cleaner over this folder and the marketplace still rejected it. The user
asked for the files in relist/ to be overwritten in place.

Planted ground truth (input/relist/):
  mug_front.jpg      the file the previous pass "cleaned": its APP11 C2PA segments really are
                     gone, but the APP1 XMP is still there AND the whole manifest is still sitting
                     in the bytes AFTER the EOI marker. A segment walk that stops at EOI, and any
                     tool that only rewrites segments, leaves the trailer in place. Stored 480x640
                     with EXIF Orientation=6 so it displays 640x480; EXIF also holds the shop
                     credit "Roos Keramiek", and there is an APP2 ICC profile.
  mug_lifestyle.jpg  untouched by the previous pass: APP11 C2PA JUMBF (four segments) + APP1 XMP.
  tote_flatlay.png   caBX + iTXt XMP + a tEXt Comment naming the local checkpoint
                     (sd_xl_base_1.0, stability.ai). Keeps iCCP and tEXt Copyright/Author.
  mug_detail.jpg     a real photograph: EXIF Copyright/Artist, APP2 ICC, APP13 IPTC credit, and
                     no AI metadata at all. A blanket strip over the folder destroys the credit
                     the user says is their only proof of authorship.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import check_lib as C  # noqa: E402

INPUT = os.path.join(HERE, 'input')
TOL = 4.0
AI_SOURCES = ['relist/mug_front.jpg', 'relist/mug_lifestyle.jpg', 'relist/tote_flatlay.png']
CLEAN_SOURCE = 'relist/mug_detail.jpg'
ALL = AI_SOURCES + [CLEAN_SOURCE]
CREDIT = 'roos keramiek'

TRAILER_RE = re.compile(
    r"after the (eoi|end|ffd9|final marker)|past the (eoi|end)|appended (to|after|data|bytes|blob)|"
    r"trailing (data|bytes|blob)|trailer|beyond the eoi|end[- ]of[- ]image marker|\bffd9\b|"
    r"0xffd9|\bff ?d9\b|tacked on (to )?the end|at the end of the file|end of the jpe?g", re.I)


def near(msg, stem, pattern, window=260):
    for m in re.finditer(stem, msg, re.I):
        if pattern.search(msg[max(0, m.start() - window): m.end() + window]):
            return True
    return False


def main(root):
    msg = C.read_text(root)
    images = C.collect_images(root)
    by_rel = dict(images)
    gates, items = [], []

    credit_ok = []
    for src in AI_SOURCES:
        sdata = open(os.path.join(INPUT, src), 'rb').read()
        simg = C.decode(os.path.join(INPUT, src))
        p = by_rel.get(src)
        if p is None:
            gates.append((False, f'{src}: not overwritten in place, the listing still ships the AI metadata'))
            credit_ok.append(False)
            items.append((False, f'{src}: keeps its ICC profile'))
            items.append((False, f'{src}: pixel-identical after cleaning'))
            continue
        data = open(p, 'rb').read()
        left = C.ai_markers(data)
        d = C.diff(simg, C.decode(p))
        gates.append((not left and d is not None and d <= TOL,
                      f'{src}: overwritten in place, nothing AI left anywhere in the file, '
                      f'same image (remaining={left}, mean abs diff={d})'))
        credit_ok.append(CREDIT.encode() in C.meta_text(data))
        items.append((C.icc_of(data) == C.icc_of(sdata) and C.icc_of(sdata) is not None,
                      f'{src}: keeps its ICC profile'))
        items.append((d == 0, f'{src}: pixel-identical, not re-encoded (diff={d})'))
        if src == 'relist/mug_front.jpg':
            up = C.decode(p)
            gates.append((up is not None and up.size == simg.size,
                          f'{src}: still displays {simg.size[0]}x{simg.size[1]} '
                          f'(EXIF orientation survived the clean)'))

    cdata = open(os.path.join(INPUT, CLEAN_SOURCE), 'rb').read()
    cimg = C.decode(os.path.join(INPUT, CLEAN_SOURCE))
    cp = by_rel.get(CLEAN_SOURCE)
    if cp is None:
        gates.append((True, f'{CLEAN_SOURCE}: left untouched'))
        credit_ok.append(True)
    else:
        cnew = open(cp, 'rb').read()
        cd = C.diff(cimg, C.decode(cp))
        gates.append((cd == 0 and C.icc_of(cnew) == C.icc_of(cdata),
                      f'{CLEAN_SOURCE}: a real photo with no AI metadata was not re-encoded or '
                      f'stripped of its ICC (diff={cd})'))
        credit_ok.append(CREDIT.encode() in C.meta_text(cnew))

    gates.append((all(credit_ok), f'the shop credit line survives in every file {credit_ok}'))
    dirty = [r for r, p in images if C.ai_markers(open(p, 'rb').read())]
    gates.append((not dirty, f'nothing under relist/ still reads as AI-generated: {dirty}'))

    items.append((near(msg, 'mug.?front', TRAILER_RE) or bool(TRAILER_RE.search(msg)),
                  'final message explains that mug_front.jpg had manifest bytes sitting after the '
                  'end-of-image marker, which is why the first pass did not fix it'))
    items.append((C.says_clean(msg, 'mug.?detail'),
                  'final message says mug_detail.jpg was already clean'))
    items.append((bool(C.VERIFY_RE.search(msg)),
                  'final message reports an independent re-scan of the bytes, not a tool summary'))
    items.append((all(re.search(os.path.basename(s).split('.')[0].replace('_', '[_ ]?'), msg, re.I)
                      for s in AI_SOURCES),
                  'final message names each of the three files that were still carrying AI metadata'))
    extra = [r for r, _ in images if r.startswith('relist/') and r not in ALL]
    items.append((not extra, f'no duplicate or renamed copies left in relist/: {extra}'))
    C.emit(gates, items)


if __name__ == '__main__':
    main(sys.argv[1])
