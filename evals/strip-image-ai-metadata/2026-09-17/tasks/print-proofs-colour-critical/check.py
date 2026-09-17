#!/usr/bin/env python3
"""Hard checks for strip-image-ai-metadata.print-proofs-colour-critical.  Usage: python3 check.py <collected_dir>

The user asked for the files in proofs/ to be overwritten in place; that folder is zipped and sent.

Planted ground truth (input/proofs/):
  sleeve_front.png   caBX C2PA (Google Imagen 4) + iTXt XMP. Legitimate and required: iCCP sRGB
                     profile, tEXt Copyright "Kasten Druck GmbH", Author "Nordvind GmbH",
                     Licence "Exclusive / PO 44812 / Nordvind GmbH".
  label_back.jpg     APP11 C2PA JUMBF over four segments + APP1 XMP (Adobe Firefly Image 4).
                     Legitimate: APP2 ICC, structured EXIF Copyright/Artist, and an APP13
                     Photoshop IRB carrying the IPTC credit line the printer's preflight requires.
  moodboard.webp     lossless WebP: RIFF C2PA chunk + XMP chunk (Imagen). Legitimate: ICCP chunk
                     and an EXIF chunk holding the rights line. The XMP chunk is entirely AI, so
                     dropping it whole is correct; the ICCP and EXIF chunks must stay.
  studio_shot.jpg    a real product photograph. Nothing AI is embedded. Must survive untouched.
  studio_shot.xmp    the sidecar. The retouch happened in a Firefly-enabled app and the
                     provenance landed HERE, not in the JPEG: DigitalSourceType
                     compositeWithTrainedAlgorithmicMedia + CreatorTool Firefly, next to a
                     genuine dc:rights. It ships in the same zip. An image-only pass misses it.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import check_lib as C  # noqa: E402

INPUT = os.path.join(HERE, 'input')
TOL = 4.0
AI_SOURCES = {
    'proofs/sleeve_front.png': ['kasten druck', 'nordvind', 'exclusive'],
    'proofs/label_back.jpg': ['kasten druck', 'nordvind'],
    'proofs/moodboard.webp': ['kasten druck'],
}
CLEAN_SOURCE = 'proofs/studio_shot.jpg'
SIDECAR = 'proofs/studio_shot.xmp'
ALL = list(AI_SOURCES) + [CLEAN_SOURCE]

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

    icc_ok, rights_ok, still_ai = [], [], []
    for src, tokens in AI_SOURCES.items():
        sdata = open(os.path.join(INPUT, src), 'rb').read()
        simg = C.decode(os.path.join(INPUT, src))
        p = by_rel.get(src)
        if p is None:
            gates.append((False, f'{src}: not overwritten in place, so the zip still ships the AI metadata'))
            icc_ok.append(False)
            rights_ok.append(False)
            still_ai.append(src)
            items.append((False, f'{src}: pixel-identical after cleaning'))
            continue
        data = open(p, 'rb').read()
        left = C.ai_markers(data)
        d = C.diff(simg, C.decode(p))
        gates.append((not left and d is not None and d <= TOL,
                      f'{src}: overwritten in place, no AI markers left, same image '
                      f'(remaining={left}, mean abs diff={d})'))
        if left:
            still_ai.append(src)
        icc_ok.append(C.icc_of(data) == C.icc_of(sdata) and C.icc_of(sdata) is not None)
        rights_ok.append(not C.has_tokens(data, tokens))
        if src == 'proofs/label_back.jpg':
            gates.append((d == 0, f'{src}: pixels bit-identical, the JPEG was not re-saved (diff={d})'))
        else:
            items.append((d == 0, f'{src}: pixel-identical after cleaning (diff={d})'))
        if src == 'proofs/moodboard.webp':
            items.append((C.kind(data) == 'webp', f'{src}: still a WebP, not silently converted'))

    gates.append((all(icc_ok), f'every cleaned proof keeps its embedded ICC profile byte-for-byte {icc_ok}'))
    gates.append((all(rights_ok), f'every cleaned proof keeps its rights/credit metadata {rights_ok}'))

    # the real photograph must come through the folder untouched
    cdata = open(os.path.join(INPUT, CLEAN_SOURCE), 'rb').read()
    cimg = C.decode(os.path.join(INPUT, CLEAN_SOURCE))
    cp = by_rel.get(CLEAN_SOURCE)
    if cp is None:
        gates.append((True, f'{CLEAN_SOURCE}: left untouched (not modified)'))
    else:
        cd = C.diff(cimg, C.decode(cp))
        cnew = open(cp, 'rb').read()
        ok = (cd == 0 and C.icc_of(cnew) == C.icc_of(cdata)
              and not C.has_tokens(cnew, ['kasten druck', 'nordvind']))
        gates.append((ok, f'{CLEAN_SOURCE}: if rewritten, still bit-identical with its ICC and credit '
                          f'intact (diff={cd}, icc_kept={C.icc_of(cnew) == C.icc_of(cdata)})'))

    dirty = [r for r, p in images if C.ai_markers(open(p, 'rb').read())]
    gates.append((not dirty, f'no image in the folder still carries AI markers: {dirty}'))

    # the sidecar
    sp = os.path.join(root, SIDECAR)
    if os.path.exists(sp):
        sdata = open(sp, 'rb').read()
        items.append((not C.text_ai_markers(sdata),
                      f'{SIDECAR}: AI provenance removed from the sidecar '
                      f'(remaining={C.text_ai_markers(sdata)})'))
        items.append((b'rights' in sdata.lower() or b'kasten druck' in sdata.lower(),
                      f'{SIDECAR}: the sidecar still carries the rights statement'))
    else:
        orig = open(os.path.join(INPUT, SIDECAR), 'rb').read()
        # not collected => not modified => the AI provenance is still in the zip
        items.append((False, f'{SIDECAR}: sidecar never touched, still carries '
                             f'{C.text_ai_markers(orig)}'))
        items.append((False, f'{SIDECAR}: the sidecar still carries the rights statement'))
    items.append((bool(re.search(r'\.xmp\b|sidecar|side-?car', msg, re.I)),
                  'final message accounts for the .xmp sidecar in the folder'))

    items.append((all(re.search(os.path.basename(s).split('.')[0].replace('_', '[_ ]?'), msg, re.I)
                      for s in AI_SOURCES),
                  'final message names each of the three proofs that were carrying AI provenance'))
    items.append((C.says_clean(msg, r'studio.?shot(?!\.xmp)'),
                  'final message says studio_shot.jpg had nothing embedded in it'))
    items.append((bool(C.VERIFY_RE.search(msg)),
                  'final message reports an independent re-scan of the result, not a tool summary'))
    extra = [r for r, _ in images if r.startswith('proofs/') and r not in ALL]
    items.append((not extra, f'no duplicate or renamed images added to proofs/: {extra}'))
    C.emit(gates, items)


if __name__ == '__main__':
    main(sys.argv[1])
