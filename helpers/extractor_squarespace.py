from __future__ import annotations

from urllib.parse import urlparse

from helpers.extractor_generic import GenericExtractor


class SquarespaceExtractor(GenericExtractor):
    def extract_images(self, html: str) -> set[str]:
        # Get raw images from GenericExtractor
        raw_images = super().extract_images(html)
        
        processed_images = set()
        for url in raw_images:
            parsed = urlparse(url)
            if 'squarespace-cdn.com' in parsed.netloc or 'squarespace.com' in parsed.netloc:
                # To get the highest quality on squarespace, we can append format=original
                # Strip existing format arguments by just taking the base path
                base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                processed_images.add(f"{base_url}?format=original")
            else:
                processed_images.add(url)
                
        return processed_images
