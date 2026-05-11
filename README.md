# get-images-photo-website

A minimal utility to download and organize images from photographer portfolio websites (e.g., Squarespace, WordPress).

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the script by providing the target gallery URL:

```bash
python get_images.py <url>
```

**Example:**
```bash
python get_images.py https://www.allinwhitewedding.com/cici-rivarola
```

## Output

Images are automatically deduplicated and saved to the `downloads/` directory, organized in a subfolder named after the inferred author and project:
`downloads/<Author Name> - <Project Name>/`
