import re

_WP_SIZE_RE = re.compile(r'-(\d+)x(\d+)(\.[^.?]+)$', re.I)

def dedup_resolutions(urls):
    groups = {}
    for url in urls:
        path = url.split('?')[0]
        # Check if it has a -WxH suffix
        m = _WP_SIZE_RE.search(path)
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
                m = _WP_SIZE_RE.search(path)
                if m:
                    w, h = int(m.group(1)), int(m.group(2))
                    area = w * h
                    if area > max_area:
                        max_area = area
                        best_url = u
            result.add(best_url)
            
    return result

urls = {
    "http://example.com/img-300x200.jpg",
    "http://example.com/img-1024x768.jpg",
    "http://example.com/other.jpg",
    "http://example.com/other-150x150.jpg",
    "http://example.com/other-300x300.jpg"
}

print(dedup_resolutions(urls))
