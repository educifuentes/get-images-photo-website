from __future__ import annotations

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from helpers.base_extractor import BaseExtractor
from helpers.utils import IMG_EXTS, is_image_url


class GenericExtractor(BaseExtractor):
    def extract_images(self, html: str) -> set[str]:
        soup = BeautifulSoup(html, 'html.parser')
        urls = set()
        
        # <img> and lazy attributes
        img_attrs = [
            'src', 'data-src', 'data-lazy-src', 'data-original', 'data-large_image',
            'data-zoom-image', 'data-lazy', 'data-bg', 'data-image', 'data-flickity-lazyload',
            'data-srcset', 'data-orig-file', 'data-large-file', 'data-full-url', 'data-permalink'
        ]
        
        for img in soup.find_all('img'):
            for a in img_attrs:
                val = img.get(a)
                if val:
                    if ',' in val and ' ' in val:
                        parts = [p.strip().split(' ')[0] for p in val.split(',') if p.strip()]
                        for p in parts:
                            urls.add(urljoin(self.url, p))
                    else:
                        urls.add(urljoin(self.url, val))

            srcset = img.get('srcset')
            if srcset:
                parts = [p.strip().split(' ')[0] for p in srcset.split(',') if p.strip()]
                for p in parts:
                    urls.add(urljoin(self.url, p))

        # <source> (picture) and video sources
        for source in soup.find_all('source'):
            s = source.get('src') or source.get('srcset')
            if s:
                parts = [p.strip().split(' ')[0] for p in s.split(',') if p.strip()]
                for p in parts:
                    urls.add(urljoin(self.url, p))

        # Inline styles: background-image:url(...)
        url_func_re = re.compile(r'url\((?:\s*["\']?)(.*?)(?:["\']?\s*)\)', re.I)
        for tag in soup.find_all(style=True):
            for m in url_func_re.finditer(tag['style']):
                u = m.group(1).strip()
                if u:
                    urls.add(urljoin(self.url, u))

        # <style> blocks
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                for m in url_func_re.finditer(style_tag.string):
                    u = m.group(1).strip()
                    if u:
                        urls.add(urljoin(self.url, u))

        # <a href> that links directly to image file
        for a in soup.find_all('a', href=True):
            href = a['href']
            if is_image_url(href):
                urls.add(urljoin(self.url, href))

        # Heuristic: embed image URLs in JSON or JS
        ext_pattern = '(' + '|'.join([re.escape(ext) for ext in IMG_EXTS]) + ')'
        script_regex = re.compile(r'https?://[^\s\'"\)<>]+?' + ext_pattern + r'(?:\?[^\s\'"\)<>]*)?', re.I)
        for m in script_regex.finditer(html):
            urls.add(m.group(0))

        # data-* attributes on any tag
        for tag in soup.find_all(True):
            for attr, val in tag.attrs.items():
                if isinstance(val, str):
                    if is_image_url(val) or 'data:image' in val or 'format=webp' in val:
                        urls.add(urljoin(self.url, val))

        return urls
