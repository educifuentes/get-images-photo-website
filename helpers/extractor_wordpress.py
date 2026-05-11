from __future__ import annotations

from helpers.extractor_generic import GenericExtractor
from helpers.utils import dedup_resolutions


class WordPressExtractor(GenericExtractor):
    def extract_images(self, html: str) -> set[str]:
        raw_images = super().extract_images(html)
        return dedup_resolutions(raw_images)
