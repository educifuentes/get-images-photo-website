# get-images-photo-website

Small utility to download images from photo-portfolio gallery pages.

Usage:

python get_images.py https://marcoszegers.cl/2018_-93-chileans-who-went-to-russia/ -o ./downloads


```bash
python get_images.py https://adrianazehbrauskas.com/faith/lf6gj10o9iu9b1fxn2ywsqxp9wf7t1 -o ./downloads
```

Options:
- `-d, --depth`: crawl same-domain links up to this depth (default 0)
- `-c, --concurrency`: concurrent downloads (default 6)
- `--allow-external`: allow images hosted on other domains
- `--max-pages`: stop after crawling this many pages

Install dependencies:

```bash
pip install -r requirements.txt
```

Notes:
- The script extracts images from `img`, `source`, inline `background-image` styles, `srcset`, and direct links.
- It aims to be generic but some photographer sites use JS or APIs; for those, a site-specific approach may be needed.
