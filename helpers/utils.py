from __future__ import annotations

import os
import re
from urllib.parse import urlparse

import requests

IMG_EXTS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.tif', '.tiff', '.bmp')

_SIZE_RE = re.compile(r'-(\d+)x(\d+)(\.[^.?]+)$', re.I)

BROWSER_UA = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
)

_UNSAFE_CHARS_RE = re.compile(r'[\\/:*?"<>|]')
_SEPARATORS_RE = re.compile(r'\s*[–—|]\s*')


def dedup_resolutions(urls: set[str]) -> set[str]:
    """
    Detect duplicate images with varying resolution suffixes (e.g., -300x200)
    and keep only the highest quality version (or the base URL if present).
    """
    groups = {}
    for url in urls:
        path = url.split('?')[0]
        # Check if it has a -WxH suffix
        m = _SIZE_RE.search(path)
        if m:
            base_path = path[:m.start()] + m.group(3)
            base_url = base_path + url[len(path):]
        else:
            base_url = url
            
        if base_url not in groups:
            groups[base_url] = []
        groups[base_url].append(url)
        
    result = set()
    for base_url, group_urls in groups.items():
        if base_url in group_urls:
            # Base URL is explicitly in the set, keep it
            result.add(base_url)
        else:
            # Base URL not in set, find the one with largest area
            best_url = group_urls[0]
            max_area = -1
            for u in group_urls:
                path = u.split('?')[0]
                m = _SIZE_RE.search(path)
                if m:
                    w, h = int(m.group(1)), int(m.group(2))
                    area = w * h
                    if area > max_area:
                        max_area = area
                        best_url = u
            result.add(best_url)
            
    return result


def is_image_url(url: str) -> bool:
    if not url:
        return False
    path = url.split('#')[0].split('?')[0]
    if path.lower().endswith(IMG_EXTS):
        return True
    if re.search(r'format=(?:webp|jpeg|png|jpg)', url, re.I):
        return True
    return False


def sanitize(s: str, max_len: int = 80) -> str:
    s = _UNSAFE_CHARS_RE.sub('', s).strip()
    return re.sub(r'\s+', ' ', s)[:max_len]


def download_one(session: requests.Session, url: str, out_dir: str, seen_names: set[str]) -> tuple[str, bool]:
    try:
        r = session.get(url, stream=True, timeout=20)
        r.raise_for_status()
    except Exception:
        return url, False

    path = urlparse(url).path
    name = os.path.basename(path) or 'image'
    name = name.split('?')[0]

    base, ext = os.path.splitext(name)
    if not ext:
        ext = '.jpg'
    candidate = base + ext
    i = 1
    while candidate in seen_names:
        candidate = f"{base}_{i}{ext}"
        i += 1
    seen_names.add(candidate)

    out_path = os.path.join(out_dir, candidate)
    try:
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except Exception:
        return url, False
    return out_path, True
