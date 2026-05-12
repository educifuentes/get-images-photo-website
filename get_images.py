#!/usr/bin/env python3
"""
Generic photo-portfolio image downloader.

Usage:
  python get_images.py <url>

Dependencies: requests, beautifulsoup4, tqdm
"""

import os
import sys
import requests

from helpers.downloader import crawl_and_collect, download_images
from helpers.factory import get_extractor
from helpers.utils import BROWSER_UA, dedup_resolutions


def process_url(start_url: str, base_out_dir: str):
    print(f"\n--- Processing {start_url} ---")
    try:
        r = requests.get(start_url, headers={'User-Agent': BROWSER_UA}, timeout=20)
        r.raise_for_status()
        html = r.text
        extractor = get_extractor(start_url, html)
        author, project = extractor.extract_meta(html)
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return

    # Format the subfolder name
    if author and project:
        folder_name = f"{author} - {project}"
    elif project:
        folder_name = project
    elif author:
        folder_name = author
    else:
        folder_name = "unknown"

    out_dir = os.path.join(base_out_dir, folder_name)
    os.makedirs(out_dir, exist_ok=True)
    print(f"Saving to: {out_dir}")

    session = requests.Session()
    session.headers.update({'User-Agent': BROWSER_UA})

    if hasattr(extractor, 'collect_images'):
        images_all = extractor.collect_images(session, start_url)
    else:
        images_all = crawl_and_collect(start_url, depth=0)

    images_all = dedup_resolutions(images_all)

    if not images_all:
        print('No images found.')
        return

    download_images(images_all, start_url, out_dir, concurrency=6)

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python get_images.py <url_or_file>")
        return 1

    target = sys.argv[1]
    base_out_dir = "downloads"
    os.makedirs(base_out_dir, exist_ok=True)

    if os.path.isfile(target):
        print(f"Reading URLs from file: {target}")
        with open(target, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'):
                    process_url(url, base_out_dir)
    else:
        process_url(target, base_out_dir)

    return 0

if __name__ == '__main__':
    sys.exit(main())
