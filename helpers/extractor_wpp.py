from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from helpers.base_extractor import BaseExtractor
from helpers.utils import BROWSER_UA, sanitize


class WPPExtractor(BaseExtractor):
    """Extractor for worldpressphoto.org paginated galleries (/1, /2, …)."""

    def extract_meta(self, html: str) -> tuple[str, str]:
        parts = [p for p in urlparse(self.url).path.split('/') if p]
        if parts and parts[-1].isdigit():
            parts = parts[:-1]
        author_slug = parts[-1] if parts else 'Unknown'
        author = sanitize(author_slug.replace('-', ' ').title())

        soup = BeautifulSoup(html, 'html.parser')
        h1 = soup.find('h1', class_=re.compile(r'title'))
        project = sanitize(h1.get_text(strip=True)) if h1 else author
        return author, project

    def extract_images(self, html: str) -> set[str]:
        soup = BeautifulSoup(html, 'html.parser')
        meta = soup.find('meta', property='og:image')
        if meta and meta.get('content'):
            return {urljoin(self.url, meta['content'])}
        return set()

    def collect_images(self, session: requests.Session, start_url: str) -> set[str]:
        """Iterate through paginated gallery pages and collect all image URLs."""
        base = re.sub(r'/\d+/?$', '/', start_url.rstrip('/') + '/')
        images: set[str] = set()
        for i in range(1, 500):
            url = f"{base}{i}"
            try:
                r = session.get(url, timeout=10)
                if r.status_code != 200:
                    print(f"  End of series at page {i} (status {r.status_code}).")
                    break
                found = self.extract_images(r.text)
                if not found:
                    print(f"  No image on page {i}, stopping.")
                    break
                images.update(found)
                print(f"  [{i:03d}] {next(iter(found))}")
            except Exception as e:
                print(f"  Error on page {i}: {e}")
                break
        return images
