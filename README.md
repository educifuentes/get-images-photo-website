# get-images-photo-website

A minimal utility to download and organize images from photographer portfolio websites (e.g., Squarespace, WordPress).

## Installation

```bash
pip install -r requirements.txt
```

## Usage

You can run the script by providing either a single target gallery URL or a text file containing a list of URLs (one per line):

**Single URL:**
```bash
python get_images.py <url>
```

**List of URLs:**
```bash
python get_images.py list_url/list_matr_sites.txt

python get_images.py list_url/list_docu_sites.txt

```

**Example:**
```bash
python get_images.py https://www.allinwhitewedding.com/cici-rivarola
```

## Output

Images are automatically deduplicated and saved to the `downloads/` directory, organized in a subfolder named after the inferred author and project:
`downloads/<Author Name> - <Project Name>/`
