#!/usr/bin/env python3
"""Hard checks for strip-image-ai-metadata.post-batch-lossless.  Usage: python3 check.py <collected_dir>

Planted ground truth (input/queue/, cleaned copies belong in output/, queue/ must not change):
  carousel_01.png   caBX C2PA (OpenAI gpt-image-1) + iTXt XMP trainedAlgorithmicMedia.
                    Also carries an iCCP sRGB profile and tEXt Copyright/Author "Dela Ruiz"
                    which are NOT AI metadata and must survive.
  carousel_02.png   no C2PA at all: the only markers are tEXt Software="Midjourney v7" and a
                    tEXt Description. A C2PA-only pass reports this file clean.
                    Same iCCP + Copyright/Author to preserve.
  portrait_final.jpg phone photo finished with Firefly generative fill. APP1 XMP is the only AI
                    record. Structured EXIF (Make/Model/Copyright/Artist) carries Orientation=6,
                    so the file is stored 480x640 and DISPLAYS 640x480; a blanket EXIF wipe turns
                    it sideways. APP2 ICC must survive and the scan must not be re-encoded.
  stage_shot.jpg    a real camera frame (FUJIFILM X-T5). No AI metadata anywhere. It must be
                    reported as clean and must not be stripped or re-encoded.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import check_lib as C  # noqa: E402

INPUT = os.path.join(HERE, 'input')
TOL = 4.0
AI_SOURCES = ['queue/carousel_01.png', 'queue/carousel_02.png', 'queue/portrait_final.jpg']
CLEAN_SOURCE = 'queue/stage_shot.jpg'
ALL = AI_SOURCES + [CLEAN_SOURCE]
RIGHTS = 'dela ruiz'



def main(root):
    msg = C.read_text(root)
    images = C.collect_images(root)
    by_rel = dict(images)
    gates, items = [], []

    portrait_upright = False
    for src in AI_SOURCES:
        sdata = open(os.path.join(INPUT, src), 'rb').read()
        simg = C.decode(os.path.join(INPUT, src))
        sicc = C.icc_of(sdata)
        ext = os.path.splitext(src)[1].lower()
        cands = [(r, p, d) for r, p, d in C.match_outputs(simg, images, TOL) if r != src]
        clean = [(r, p, d, open(p, 'rb').read()) for r, p, d in cands
                 if not C.ai_markers(open(p, 'rb').read())]
        gates.append((bool(clean),
                      f'{src}: a delivered copy has the same displayed pixels and zero AI markers '
                      f'(candidates={[c[0] for c in cands]})'))
        items.append((any(C.icc_of(b) == sicc for *_x, b in clean),
                      f'{src}: cleaned copy keeps the embedded ICC profile'))
        items.append((any(RIGHTS.encode() in C.meta_text(b) for *_x, b in clean),
                      f'{src}: cleaned copy keeps the Copyright/Artist credit'))
        items.append((any(r.lower().endswith(ext) for r, *_x in clean),
                      f'{src}: format preserved ({ext})'))
        if src == 'queue/portrait_final.jpg':
            gates.append((any(d == 0 for _r, _p, d, _b in clean),
                          f'{src}: cleaned copy is pixel-identical, i.e. the JPEG was not re-encoded '
                          f'(diffs={[c[2] for c in clean]})'))
            portrait_upright = any(C.decode(p) is not None and C.decode(p).size == simg.size
                                   for _r, p, _d, _b in clean)
            gates.append((portrait_upright,
                          f'{src}: cleaned copy still displays {simg.size[0]}x{simg.size[1]} '
                          f'(EXIF orientation not wiped)'))
        else:
            items.append((any(d == 0 for _r, _p, d, _b in clean),
                          f'{src}: cleaned copy is pixel-identical'))

    # the real photograph: leaving it alone is fine, degrading it is not
    cdata = open(os.path.join(INPUT, CLEAN_SOURCE), 'rb').read()
    cimg = C.decode(os.path.join(INPUT, CLEAN_SOURCE))
    cicc = C.icc_of(cdata)
    copies = [(r, p, d) for r, p, d in C.match_outputs(cimg, images, TOL) if r != CLEAN_SOURCE]
    mangled = [r for r, p, d in copies
               if d != 0 or C.icc_of(open(p, 'rb').read()) != cicc
               or RIGHTS.encode() not in C.meta_text(open(p, 'rb').read())]
    gates.append((not mangled,
                  f'{CLEAN_SOURCE}: no delivered copy was re-encoded or stripped of its ICC/credit '
                  f'(mangled={mangled})'))
    gates.append((C.says_clean(msg, 'stage.?shot'),
                  f'{CLEAN_SOURCE}: the final message says this one carried nothing'))

    dirty = [r for r, p in images if r not in ALL and C.ai_markers(open(p, 'rb').read())]
    gates.append((not dirty, f'no delivered image still carries AI markers: {dirty}'))
    touched = [r for r in ALL if r in by_rel]
    gates.append((not touched, f'queue/ left exactly as it was (modified: {touched})'))

    items.append((all(re.search(re.escape(os.path.basename(s).split(".")[0]).replace("_", "[_ ]?"),
                                msg, re.I) for s in AI_SOURCES),
                  'final message names each of the three files that were carrying AI metadata'))
    items.append((bool(C.VERIFY_RE.search(msg)),
                  'final message reports the cleaned files were re-checked, not just written'))
    C.emit(gates, items)


if __name__ == '__main__':
    main(sys.argv[1])
