from __future__ import annotations

import concurrent.futures
import os
from collections import deque
from urllib.parse import urlparse

import requests
from tqdm import tqdm

from helpers.factory import get_extractor
from helpers.utils import BROWSER_UA, download_one


def crawl_and_collect(start_url: str, depth: int = 0, max_pages: int | None = None) -> set[str]:
    parsed = urlparse(start_url)
    domain = parsed.netloc
    to_visit = deque([(start_url, 0)])
    visited_pages = set()
    image_urls = set()

    session = requests.Session()
    session.headers.update({'User-Agent': BROWSER_UA})

    extractor = None

    while to_visit:
        url, d = to_visit.popleft()
        if url in visited_pages:
            continue
        if max_pages and len(visited_pages) >= max_pages:
            break
        try:
            r = session.get(url, timeout=20)
            r.raise_for_status()
            html = r.text
        except Exception:
            visited_pages.add(url)
            continue

        visited_pages.add(url)

        if extractor is None:
            extractor = get_extractor(url, html)
        else:
            # Re-use the extractor type but initialize with current url if needed,
            # actually we can just ask the factory again, or use the first one's logic.
            extractor = get_extractor(url, html)

        found_images = extractor.extract_images(html)
        for iu in found_images:
            image_urls.add(iu)

        if d < depth:
            links = extractor.extract_links_same_domain(html)
            for link in links:
                if link not in visited_pages:
                    to_visit.append((link, d + 1))

    return image_urls

def download_images(image_urls: set[str], start_url: str, out_dir: str, concurrency: int = 6):
    print(f'Found {len(image_urls)} image URLs. Downloading...')
    session = requests.Session()
    session.headers.update({
        'User-Agent': BROWSER_UA,
        'Referer': start_url,
    })

    seen_names = set()
    succeeded = 0

    images = sorted(image_urls)
    pbar = tqdm(total=len(images), desc='images')

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = {ex.submit(download_one, session, url, out_dir, seen_names): url for url in images}
        for fut in concurrent.futures.as_completed(futures):
            _url = futures[fut]
            _out, ok = fut.result()
            if ok:
                succeeded += 1
            pbar.update(1)

    pbar.close()
    print(f'Downloaded {succeeded}/{len(images)} images into {out_dir}')
