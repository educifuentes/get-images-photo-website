from __future__ import annotations

import re
from urllib.parse import urlparse

from helpers.base_extractor import BaseExtractor
from helpers.utils import sanitize


_SHORTCODE_RE = re.compile(r'/p/([A-Za-z0-9_-]+)')


class InstagramExtractor(BaseExtractor):
    def __init__(self, url: str):
        super().__init__(url)
        self._post = None

    def _shortcode(self) -> str:
        m = _SHORTCODE_RE.search(urlparse(self.url).path)
        if not m:
            raise ValueError(f"Could not extract shortcode from URL: {self.url}")
        return m.group(1)

    def _get_post(self):
        if self._post is None:
            try:
                import instaloader
            except ImportError:
                raise ImportError("instaloader is required for Instagram URLs: pip install instaloader")
            L = instaloader.Instaloader()
            self._post = instaloader.Post.from_shortcode(L.context, self._shortcode())
        return self._post

    # extract_meta is called with html from process_url, but for Instagram
    # the page is JS-rendered so html is useless — use instaloader instead.
    def extract_meta(self, html: str) -> tuple[str, str]:
        post = self._get_post()
        username = post.owner_username
        date_str = post.date_utc.strftime('%Y-%m-%d')
        return sanitize(username), sanitize(date_str)

    def extract_images(self, html: str) -> set[str]:
        return set()

    def collect_images(self, session, url: str) -> set[str]:
        post = self._get_post()
        images: set[str] = set()
        if post.typename == 'GraphSidecar':
            for node in post.get_sidecar_nodes():
                if not node.is_video:
                    images.add(node.display_url)
        elif not post.is_video:
            images.add(post.url)
        return images
