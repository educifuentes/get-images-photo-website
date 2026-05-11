from __future__ import annotations

import datetime
from abc import ABC, abstractmethod
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from helpers.utils import _SEPARATORS_RE, sanitize


class BaseExtractor(ABC):
    def __init__(self, url: str):
        self.url = url

    @abstractmethod
    def extract_images(self, html: str) -> set[str]:
        """Extract all image URLs from the given HTML."""
        pass

    def extract_meta(self, html: str) -> tuple[str, str]:
        """
        Return (author, project) derived from Open Graph / title tags,
        falling back to domain/URL slug.
        """
        soup = BeautifulSoup(html, 'html.parser')

        def og(prop: str) -> str:
            tag = soup.find('meta', property=prop)
            return (tag.get('content') or '').strip() if tag else ''

        def meta_name(name: str) -> str:
            tag = soup.find('meta', attrs={'name': name})
            return (tag.get('content') or '').strip() if tag else ''

        # --- author ---
        author = og('og:site_name') or meta_name('author')
        if not author:
            domain = urlparse(self.url).netloc
            author = domain.split('.')[0].replace('-', ' ').title()

        # --- project ---
        raw = og('og:title')
        if not raw:
            title_tag = soup.find('title')
            raw = title_tag.get_text().strip() if title_tag else ''
        if not raw:
            h1 = soup.find('h1')
            raw = h1.get_text().strip() if h1 else ''

        if raw:
            parts = _SEPARATORS_RE.split(raw)
            project = parts[0].strip() if parts[0].strip() else raw
        else:
            slug = urlparse(self.url).path.strip('/').split('/')[-1]
            project = slug.replace('-', ' ').replace('_', ' ').strip().title()

        if not project:
            project = datetime.datetime.now().strftime("%Y-%m-%d")

        return sanitize(author), sanitize(project)

    def extract_links_same_domain(self, html: str) -> set[str]:
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        domain = urlparse(self.url).netloc
        for a in soup.find_all('a', href=True):
            href = a['href']
            full = urljoin(self.url, href)
            p = urlparse(full)
            if p.scheme in ('http', 'https') and p.netloc == domain:
                links.add(full)
        return links
