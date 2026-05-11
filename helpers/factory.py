from __future__ import annotations

from helpers.base_extractor import BaseExtractor
from helpers.extractor_generic import GenericExtractor
from helpers.extractor_squarespace import SquarespaceExtractor
from helpers.extractor_wordpress import WordPressExtractor


def get_extractor(url: str, html: str) -> BaseExtractor:
    """Return the appropriate extractor based on the site's HTML."""
    if '<!-- This is Squarespace. -->' in html or 'squarespace-cdn.com' in html:
        return SquarespaceExtractor(url)
    
    if 'wp-content/uploads' in html or 'wp-includes' in html:
        return WordPressExtractor(url)
        
    return GenericExtractor(url)
