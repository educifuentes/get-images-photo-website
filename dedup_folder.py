#!/usr/bin/env python3
"""
dedup_folder.py - Remove duplicate images from a folder, keeping the highest-resolution copy.

Duplicate detection groups files that share the same base image name after stripping:
  - -WxH size suffixes  (e.g. photo-1024x768.jpg  vs  photo-300x200.jpg)
  - _N collision suffixes added by the downloader  (e.g. photo.jpg, photo_1.jpg, photo_2.jpg)

Quality ranking: actual pixel count via Pillow, falling back to file size.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

IMG_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.tif', '.tiff', '.bmp'}

# Matches  -WxH  immediately before the extension  (WordPress-style resized variants)
_SIZE_RE = re.compile(r'-(\d+)x(\d+)$', re.I)
# Matches  _N  at the end of the stem  (collision suffix from downloader)
_COLLISION_RE = re.compile(r'_(\d+)$')


def canonical_stem(stem: str) -> str:
    m = _SIZE_RE.search(stem)
    if m:
        stem = stem[:m.start()]
    m = _COLLISION_RE.search(stem)
    if m:
        stem = stem[:m.start()]
    return stem


def pixel_count(path: str) -> int:
    if HAS_PIL:
        try:
            with Image.open(path) as img:
                return img.width * img.height
        except Exception:
            pass
    return os.path.getsize(path)


def dedup_folder(folder: str, dry_run: bool = True) -> None:
    folder = os.path.expanduser(folder)
    files = [
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
        and os.path.splitext(f)[1].lower() in IMG_EXTS
    ]

    groups: dict[tuple[str, str], list[str]] = {}
    for fname in files:
        stem, ext = os.path.splitext(fname)
        key = (canonical_stem(stem), ext.lower())
        groups.setdefault(key, []).append(fname)

    dup_groups = 0
    to_delete: list[str] = []

    for (canon, ext), group in sorted(groups.items()):
        if len(group) == 1:
            continue
        dup_groups += 1
        ranked = sorted(
            group,
            key=lambda f: pixel_count(os.path.join(folder, f)),
            reverse=True,
        )
        keeper = ranked[0]
        losers = ranked[1:]
        to_delete.extend(losers)

        keeper_px = pixel_count(os.path.join(folder, keeper))
        print(f"KEEP   {keeper}  ({keeper_px:,} px)")
        for f in losers:
            px = pixel_count(os.path.join(folder, f))
            print(f"  del  {f}  ({px:,} px)")

    print(f"\nDuplicate groups : {dup_groups}")
    print(f"Files to delete  : {len(to_delete)}")
    print(f"Files to keep    : {len(files) - len(to_delete)}")

    if dry_run:
        print("\n[DRY RUN] No files deleted. Pass --delete to remove them.")
        return

    for f in to_delete:
        os.remove(os.path.join(folder, f))
    print(f"\nDeleted {len(to_delete)} files.")


if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description='Remove duplicate images from a folder, keeping highest resolution.'
    )
    ap.add_argument('folder', help='Folder to deduplicate')
    ap.add_argument('--delete', action='store_true',
                    help='Actually delete files (default: dry run)')
    args = ap.parse_args()
    dedup_folder(args.folder, dry_run=not args.delete)
