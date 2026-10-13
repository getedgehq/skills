"""Download full-quality originals from iCloud through PhotoKit (works when the file is only in iCloud).
Photos: current (edited) version as HEIC/JPEG. Videos: the original movie resource.
Usage: python fetch.py OUT_DIR <uuid> [<uuid> ...]   or   python fetch.py OUT_DIR --from uuids.txt"""
import sys, os, threading
import Photos, Foundation

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
uuids = [l.strip() for l in open(sys.argv[3])] if sys.argv[2:3] == ["--from"] else sys.argv[2:]
free_gb = os.statvfs(out).f_bavail * os.statvfs(out).f_frsize / 2**30
if free_gb < float(os.environ.get("MIN_FREE_GB", 5)):
    sys.exit(f"Only {free_gb:.1f} GB free. iCloud refuses downloads when the disk is nearly full "
             "(CloudPhotoLibraryErrorDomain 1005). Free space first, or for a few small photos set MIN_FREE_GB=1.")

HINTS = {"CloudPhotoLibraryErrorDomain": "iCloud refused the download; usually the disk is nearly full. Free space and re-run.",
         "3169": "iCloud download failed (PHPhotosErrorDomain 3169, network error). Check iCloud Photos is online and the disk "
                 "has free space, then re-run.",
         "3305": "Not enough disk space for this original (PHPhotosErrorDomain 3305). Free space and re-run.",
         "3164": "Network access to iCloud was needed but denied. Check that iCloud Photos is signed in and online."}
def fail(err):
    msg = str(err); hint = next((h for k, h in HINTS.items() if k in msg), "")
    return f"FAIL {msg[:160]}" + (f"\n    -> {hint}" if hint else "")
mgr = Photos.PHImageManager.defaultManager()
rmgr = Photos.PHAssetResourceManager.defaultManager()
status = Photos.PHPhotoLibrary.authorizationStatusForAccessLevel_(Photos.PHAccessLevelReadWrite)
if status != Photos.PHAuthorizationStatusAuthorized:
    print("Photos access not granted to this app (status %d). Run once interactively and choose Full Access,"
          " or allow it in System Settings > Privacy & Security > Photos." % status)
    ev = threading.Event(); Photos.PHPhotoLibrary.requestAuthorizationForAccessLevel_handler_(Photos.PHAccessLevelReadWrite, lambda s: ev.set()); ev.wait(120)

def video(asset, u):
    res = [r for r in Photos.PHAssetResource.assetResourcesForAsset_(asset) if r.type() in (Photos.PHAssetResourceTypeFullSizeVideo, Photos.PHAssetResourceTypeVideo)]
    res.sort(key=lambda r: r.type() != Photos.PHAssetResourceTypeFullSizeVideo)
    if not res: return "no video resource"
    r = res[0]; ext = os.path.splitext(r.originalFilename())[1].lower() or ".mov"
    dest = f"{out}/{u}{ext}"
    if os.path.exists(dest): return "have"
    o = Photos.PHAssetResourceRequestOptions.alloc().init(); o.setNetworkAccessAllowed_(True)
    ev, box = threading.Event(), {}
    def done(err): box["e"] = err; ev.set()
    rmgr.writeDataForAssetResource_toFile_options_completionHandler_(r, Foundation.NSURL.fileURLWithPath_(dest), o, done)
    while not ev.is_set():   # the handler is delivered on the run loop
        Foundation.NSRunLoop.currentRunLoop().runUntilDate_(Foundation.NSDate.dateWithTimeIntervalSinceNow_(0.2))
    if box.get("e"):
        if os.path.exists(dest) and not os.path.getsize(dest): os.remove(dest)   # no empty file left behind
        return fail(box["e"])
    return f"ok {os.path.getsize(dest)//1024} KB"

def photo(asset, u):
    if any(os.path.exists(f"{out}/{u}.{e}") for e in ("heic", "jpg")): return "have"
    o = Photos.PHImageRequestOptions.alloc().init()
    o.setNetworkAccessAllowed_(True); o.setSynchronous_(True)
    o.setDeliveryMode_(Photos.PHImageRequestOptionsDeliveryModeHighQualityFormat)
    o.setVersion_(Photos.PHImageRequestOptionsVersionCurrent)
    box = {}
    def cb(data, uti, orient, info): box.update(d=data, u=uti, i=info)
    mgr.requestImageDataAndOrientationForAsset_options_resultHandler_(asset, o, cb)
    if box.get("d") is None: return fail((box.get("i") or {}).get("PHImageErrorKey") or box.get("i"))
    ext = "heic" if "heic" in str(box.get("u")).lower() else "jpg"
    open(f"{out}/{u}.{ext}", "wb").write(bytes(box["d"])); return f"ok {len(bytes(box['d']))//1024} KB"

for u in uuids:
    found = Photos.PHAsset.fetchAssetsWithLocalIdentifiers_options_([u + "/L0/001"], None)
    if not found.count(): print(u[:8], "NOT FOUND"); continue
    a = found.objectAtIndex_(0)
    print(u[:8], video(a, u) if a.mediaType() == Photos.PHAssetMediaTypeVideo else photo(a, u), flush=True)
