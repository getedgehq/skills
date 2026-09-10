#!/usr/bin/env python3
"""Strip C2PA and AI-generation metadata from PNG/JPEG/WebP images."""

import sys
import struct
import argparse
import os
import stat
import tempfile
from pathlib import Path
from datetime import datetime

PNG_SIG = b'\x89PNG\r\n\x1a\n'
JPEG_SOI = b'\xFF\xD8'
WEBP_SIG = b'RIFF'

AI_KEYWORDS = [b'c2pa', b'openai', b'chatgpt', b'gpt-image', b'trainedalgorithmicmedia',
               b'org.contentauth', b'trufo', b'midjourney', b'stable diffusion',
               b'stability.ai', b'firefly', b'imagen', b'grok', b'adobe stock']

C2PA_JUMBF_UUID = bytes.fromhex('6332706100110010800000aa00389b71')
JPEG_XMP_HEADERS = (
    b'http://ns.adobe.com/xap/1.0/\x00',
    b'http://ns.adobe.com/xmp/extension/\x00',
)


def _is_structured_exif(payload: bytes) -> bool:
    """Recognize an EXIF/TIFF payload whose orientation and thumbnails matter."""
    if not payload.startswith(b'Exif\x00\x00') or len(payload) < 14:
        return False
    tiff = payload[6:]
    if tiff[:2] == b'II':
        return tiff[2:4] == b'\x2a\x00'
    if tiff[:2] == b'MM':
        return tiff[2:4] == b'\x00\x2a'
    return False


def strip_png(data: bytes):
    if not data.startswith(PNG_SIG):
        raise ValueError("Not a valid PNG")
    out = bytearray(PNG_SIG)
    idx = 8
    removed = []
    while idx < len(data):
        if idx + 8 > len(data):
            out.extend(data[idx:])
            break
        length = struct.unpack('>I', data[idx:idx+4])[0]
        chunk_type = data[idx+4:idx+8]
        end = idx + 8 + length + 4
        if end > len(data):
            out.extend(data[idx:])
            break
        if chunk_type == b'caBX':
            removed.append(f"caBX ({length} bytes)")
            idx = end
            continue
        # Only textual metadata is eligible for keyword-based removal. Removing
        # an entire eXIf chunk can also remove orientation and thumbnails.
        if chunk_type in (b'tEXt', b'iTXt', b'zTXt'):
            text = data[idx+8:idx+8+length].decode('utf-8', errors='ignore').lower()
            if any(k.decode() in text for k in AI_KEYWORDS):
                removed.append(f"{chunk_type.decode()} ({length} bytes)")
                idx = end
                continue
        out.extend(data[idx:end])
        idx = end
    return bytes(out), removed


def _jpeg_segment(data: bytes, idx: int):
    """Return (marker, end, payload) for a length-bearing marker at idx."""
    if idx + 4 > len(data) or data[idx] != 0xFF:
        return None
    marker = data[idx + 1]
    if marker in (0x00, 0x01, 0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
        return None
    length = struct.unpack('>H', data[idx + 2:idx + 4])[0]
    end = idx + 2 + length
    if length < 2 or end > len(data):
        return None
    return marker, end, data[idx + 4:end]


def _jpeg_app11_group(data: bytes, idx: int):
    """Return the contiguous JPEG-XT APP11 group beginning at idx, if any."""
    first = _jpeg_segment(data, idx)
    if first is None or first[0] != 0xEB or len(first[2]) < 8 or first[2][:2] != b'JP':
        return None
    instance = first[2][2:4]
    expected_sequence = struct.unpack('>I', first[2][4:8])[0]
    if expected_sequence != 1:
        return None

    end = idx
    box_data = bytearray()
    count = 0
    while True:
        segment = _jpeg_segment(data, end)
        if segment is None or segment[0] != 0xEB:
            break
        payload = segment[2]
        if len(payload) < 8 or payload[:2] != b'JP' or payload[2:4] != instance:
            break
        sequence = struct.unpack('>I', payload[4:8])[0]
        if sequence != expected_sequence:
            break
        box_data.extend(payload[8:])
        end = segment[1]
        count += 1
        expected_sequence += 1

    is_c2pa = _is_c2pa_jumbf(box_data)
    return end, count, is_c2pa


def _box_at(data: bytes, idx: int, limit: int):
    """Parse one ISO BMFF/JUMBF box without accepting truncated lengths."""
    if idx + 8 > limit:
        return None
    size = struct.unpack('>I', data[idx:idx + 4])[0]
    box_type = data[idx + 4:idx + 8]
    header_size = 8
    if size == 1:
        if idx + 16 > limit:
            return None
        size = struct.unpack('>Q', data[idx + 8:idx + 16])[0]
        header_size = 16
    elif size == 0:
        size = limit - idx
    end = idx + size
    if size < header_size or end > limit:
        return None
    return box_type, idx + header_size, end


def _is_c2pa_jumbf(data: bytes) -> bool:
    """Match the C2PA manifest-store UUID and label in its JUMBF description."""
    outer = _box_at(data, 0, len(data))
    if outer is None or outer[0] != b'jumb':
        return False
    description = _box_at(data, outer[1], outer[2])
    if description is None or description[0] != b'jumd':
        return False
    payload = data[description[1]:description[2]]
    if len(payload) < 17 or payload[:16] != C2PA_JUMBF_UUID:
        return False
    toggles = payload[16]
    if not toggles & 0x02:
        return False
    label_end = payload.find(b'\x00', 17)
    return label_end != -1 and payload[17:label_end] == b'c2pa'


def strip_jpeg(data: bytes):
    if not data.startswith(JPEG_SOI):
        raise ValueError("Not a valid JPEG")
    out = bytearray(JPEG_SOI)
    idx = 2
    removed = []
    in_scan = False
    marker_from_scan = False
    while idx < len(data):
        if in_scan:
            marker_start = data.find(b'\xFF', idx)
            if marker_start == -1:
                out.extend(data[idx:])
                break
            out.extend(data[idx:marker_start])
            marker_code = marker_start
            while marker_code < len(data) and data[marker_code] == 0xFF:
                marker_code += 1
            if marker_code == len(data):
                out.extend(data[marker_start:])
                break
            marker = data[marker_code]
            if marker == 0x00 or 0xD0 <= marker <= 0xD7:
                out.extend(data[marker_start:marker_code + 1])
                idx = marker_code + 1
                continue
            # Any leading 0xFF bytes are fill; the final one prefixes the marker.
            out.extend(data[marker_start:marker_code - 1])
            idx = marker_code - 1
            in_scan = False
            marker_from_scan = True

        # Preserve malformed/out-of-place bytes rather than silently dropping
        # them. This is also the safety net for incomplete JPEGs without EOI.
        if data[idx] != 0xFF:
            out.append(data[idx])
            idx += 1
            continue
        if idx + 1 >= len(data):
            out.extend(data[idx:])
            idx = len(data)
            break
        marker = data[idx+1]
        # 0xFF fill, stuffed 0xFF00, SOI, restart markers, TEM: no length field.
        if marker == 0xFF:
            out.append(data[idx])
            idx += 1
            continue
        if marker in (0x00, 0x01, 0xD8) or 0xD0 <= marker <= 0xD7:
            out.extend(data[idx:idx+2])
            idx += 2
            marker_from_scan = False
            continue
        if marker == 0xD9:
            out.extend(data[idx:idx+2])
            idx += 2
            # Bytes after EOI can be a second image (MPF/MPO) or an application
            # trailer. They are outside this codestream but are still user data.
            out.extend(data[idx:])
            break

        app11_group = _jpeg_app11_group(data, idx) if marker == 0xEB else None
        if app11_group is not None:
            group_end, count, is_c2pa = app11_group
            if is_c2pa:
                removed.append(f"APP11/C2PA ({count} segment{'s' if count != 1 else ''})")
                idx = group_end
                marker_from_scan = False
                continue

        segment = _jpeg_segment(data, idx)
        if segment is None:
            out.extend(data[idx:])
            break
        marker, end, payload = segment
        # Strip only XMP APP1 records. EXIF can carry orientation and thumbnails;
        # APP13/APP14 can affect presentation and are never keyword-stripped.
        is_xmp = payload.startswith(JPEG_XMP_HEADERS)
        is_unstructured_ai_exif = payload.startswith(b'Exif\x00\x00') and not _is_structured_exif(payload)
        if marker == 0xE1 and (is_xmp or is_unstructured_ai_exif):
            text = payload.decode('utf-8', errors='ignore').lower()
            if any(k.decode() in text for k in AI_KEYWORDS):
                removed.append(f"APP1/AI ({len(payload)} bytes)")
                idx = end
                marker_from_scan = False
                continue
        out.extend(data[idx:end])
        idx = end
        if marker == 0xDA:
            in_scan = True
        elif marker == 0xDC and marker_from_scan:
            # DNL may interrupt entropy-coded data without ending the scan.
            in_scan = True
        marker_from_scan = False
    return bytes(out), removed


def strip_webp(data: bytes):
    if not data.startswith(WEBP_SIG) or len(data) < 12 or data[8:12] != b'WEBP':
        raise ValueError("Not a valid WebP")
    declared_size = struct.unpack('<I', data[4:8])[0]
    riff_end = 8 + declared_size
    if declared_size < 4 or riff_end > len(data):
        raise ValueError("Truncated WebP RIFF container")
    out = bytearray(data[:12])
    idx = 12
    removed = []
    vp8x_flags_offset = None
    removed_xmp = False
    kept_xmp = False
    while idx < riff_end:
        if idx + 8 > riff_end:
            raise ValueError("Truncated WebP chunk header")
        fourcc = data[idx:idx+4]
        size = struct.unpack('<I', data[idx+4:idx+8])[0]
        pad = 1 if size % 2 else 0
        end = idx + 8 + size + pad
        if end > riff_end:
            raise ValueError("Truncated WebP chunk payload")
        name = fourcc.decode('ascii', errors='replace')
        body = data[idx+8:idx+8+size]
        remove = fourcc == b'C2PA'
        if fourcc == b'XMP ' and any(k in body.lower() for k in AI_KEYWORDS):
            remove = True
            removed_xmp = True
        elif fourcc == b'XMP ':
            kept_xmp = True
        if remove:
            removed.append(f"{name} ({size} bytes)")
            idx = end
            continue
        if fourcc == b'VP8X' and size >= 1:
            vp8x_flags_offset = len(out) + 8
        out.extend(data[idx:end])
        idx = end
    if removed_xmp and not kept_xmp and vp8x_flags_offset is not None:
        out[vp8x_flags_offset] &= ~0x04
    struct.pack_into('<I', out, 4, len(out) - 8)
    out.extend(data[riff_end:])
    return bytes(out), removed


def neutral_name(path: Path) -> Path:
    """Generate a camera-style neutral filename in the same directory."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate = path.parent / f"IMG_{ts}{path.suffix.lower()}"
    n = 1
    while candidate.exists():
        candidate = path.parent / f"IMG_{ts}_{n}{path.suffix.lower()}"
        n += 1
    return candidate


def verify_pixels(original: bytes, cleaned: bytes) -> str | None:
    """Confirm the strip did not touch a single pixel. Returns an error or None."""
    try:
        from PIL import Image, ImageSequence
    except ImportError:
        return "pixel verification unavailable: Pillow is not installed"
    import io
    import hashlib
    try:
        a = Image.open(io.BytesIO(original))
        a.verify()
        a = Image.open(io.BytesIO(original))
    except Exception as exc:
        return f"original file does not decode as an image: {exc}"
    try:
        b = Image.open(io.BytesIO(cleaned))
        b.verify()
        b = Image.open(io.BytesIO(cleaned))
        if getattr(a, 'n_frames', 1) != getattr(b, 'n_frames', 1):
            return (f"frame count changed: {getattr(a, 'n_frames', 1)} -> "
                    f"{getattr(b, 'n_frames', 1)}")
        for frame_index, (af, bf) in enumerate(zip(ImageSequence.Iterator(a),
                                                   ImageSequence.Iterator(b))):
            if af.size != bf.size:
                return f"frame {frame_index} dimensions changed: {af.size} -> {bf.size}"
            ha = hashlib.sha256(af.convert('RGBA').tobytes()).digest()
            hb = hashlib.sha256(bf.convert('RGBA').tobytes()).digest()
            if ha != hb:
                return f"frame {frame_index} pixel data changed"
    except Exception as exc:
        return f"cleaned file no longer decodes as an image: {exc}"
    return None


def _same_file_state(before, after) -> bool:
    return (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)


def _atomic_replace(path: Path, data: bytes, expected_state):
    """Durably replace path while keeping the old file until the new one is safe."""
    current = path.stat()
    if not _same_file_state(expected_state, current):
        raise RuntimeError("input changed while it was being processed")

    fd, temp_name = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
            os.fchmod(handle.fileno(), stat.S_IMODE(current.st_mode))
            try:
                os.fchown(handle.fileno(), current.st_uid, current.st_gid)
            except PermissionError:
                pass
        if temp_path.read_bytes() != data:
            raise OSError("temporary-file verification failed")
        os.replace(temp_path, path)
        try:
            directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except OSError:
            # The complete file has already been atomically installed. Directory
            # fsync is unavailable on some filesystems and platforms.
            pass
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _atomic_output(path: Path, data: bytes):
    """Write an explicit output without ever truncating an existing file."""
    existing_mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
    fd, temp_name = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
            os.fchmod(handle.fileno(), existing_mode)
        if temp_path.read_bytes() != data:
            raise OSError("temporary-file verification failed")
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def process(path: Path, output: Path | None = None, in_place: bool = False):
    source_path = path.resolve(strict=True)
    source_state = source_path.stat()
    data = source_path.read_bytes()
    if not _same_file_state(source_state, source_path.stat()):
        print(f"ABORTED {path}: input changed while it was being read")
        sys.exit(1)
    if data.startswith(PNG_SIG):
        cleaned, removed = strip_png(data)
    elif data.startswith(JPEG_SOI):
        cleaned, removed = strip_jpeg(data)
    elif data.startswith(WEBP_SIG):
        cleaned, removed = strip_webp(data)
    else:
        print(f"Unsupported format: {path}")
        sys.exit(1)

    if not removed:
        print(f"No AI/C2PA metadata found in {path}")
        return

    # Refuse to write anything that is not byte-identical in pixels. Without this
    # an in-place run can destroy the user's only copy of a photo.
    damage = verify_pixels(data, cleaned)
    if damage:
        print(f"ABORTED {path}: {damage}")
        print("  Original left untouched. This is a bug, please report it.")
        sys.exit(1)

    if output:
        out_path = output
    elif in_place:
        out_path = path
    else:
        out_path = neutral_name(path)

    if output and not out_path.parent.is_dir():
        print(f"Error: output directory does not exist: {out_path.parent}")
        sys.exit(1)

    replacing_source = in_place
    if output:
        replacing_source = output.resolve() == source_path

    if replacing_source:
        _atomic_replace(source_path, cleaned, source_state)
        out_path = path
    elif output:
        _atomic_output(out_path, cleaned)
    else:
        out_path.write_bytes(cleaned)
    print(f"Cleaned {path} -> {out_path}")
    for r in removed:
        print(f"  Removed: {r}")
    print("  Pixels: unchanged (verified)")

    verify = out_path.read_bytes()
    remaining = [k.decode() for k in AI_KEYWORDS if k in verify.lower()]
    if remaining:
        print(f"  WARNING: possible remaining signatures: {remaining}")


def main():
    parser = argparse.ArgumentParser(description="Strip C2PA/AI metadata from images")
    parser.add_argument("paths", nargs="+", help="Image file(s) to clean")
    destination = parser.add_mutually_exclusive_group()
    destination.add_argument("-o", "--output", help="Explicit output path (single input only)")
    destination.add_argument("-i", "--in-place", action="store_true",
                             help="Overwrite the original file instead of renaming")
    args = parser.parse_args()

    if args.output and len(args.paths) > 1:
        print("Error: -o/--output can only be used with a single input file")
        sys.exit(1)

    for p in args.paths:
        path = Path(p)
        if not path.is_file():
            print(f"No such file: {p}")
            sys.exit(1)
        process(path, Path(args.output) if args.output else None, args.in_place)


if __name__ == "__main__":
    main()
