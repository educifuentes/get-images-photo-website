import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

class WPPDownloader:
    def __init__(self, base_url, base_folder="outputs"):
        # If the user passed a URL ending in a number (like /1), strip it to get the base series URL
        import re
        self.base_url = re.sub(r'/\d+/?$', '/', base_url.rstrip('/') + '/')
        
        # Extract subfolder from the part before the last slash
        parts = [p for p in self.base_url.split('/') if p]
        self.raw_author_slug = parts[-1] if parts else "unknown_author"
        self.author = self.raw_author_slug.replace('-', ' ').title()
        self.series_title = "Unknown Series"
        self.base_folder = base_folder
        self.folder = os.path.join(self.base_folder, self.raw_author_slug)
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        }

    def fetch_metadata(self):
        """Fetches the first page to extract series title."""
        url = f"{self.base_url}1"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                h1 = soup.find('h1', class_="title title--72 title--white title--font-normal")
                if h1:
                    import re
                    title = h1.get_text(strip=True)
                    # Replace anything that isn't safe for windows/mac filenames
                    self.series_title = re.sub(r'[\\/:*?"<>|]', '-', title)
        except Exception as e:
            print(f"⚠️ Failed to fetch metadata: {e}")

    def fetch_image_url(self, index):
        """Extracts the high-res image URL from a specific page index."""
        url = f"{self.base_url}{index}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code != 200:
                print(f"⚠️ Page {index} returned status {resp.status_code}")
                return None
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Method 1: Try OpenGraph meta tag
            meta_img = soup.find("meta", property="og:image")
            if meta_img and meta_img.get("content"):
                return urljoin(url, meta_img["content"])
            
            # Method 2: Try finding high-res images in the main content container
            # (Fallback in case og:image isn't present)
            for img in soup.find_all('img'):
                src = img.get('src')
                if src and ('/cache/' in src or '.jpg' in src.lower() or '.jpeg' in src.lower()):
                    if getattr(img, 'parent', None) and img.parent.name == 'picture':
                        return urljoin(url, src)
                    if 'wpp' in src.lower() or 'collection' in src.lower():
                        return urljoin(url, src)
            
            print(f"⚠️ No image found on page {index}. HTML snippet: {resp.text[:200]}...")
            return None
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Network error fetching index {index}: {e}")
            return None
        except Exception as e:
            print(f"⚠️ Unexpected error on index {index}: {e}")
            return None

    def download_image(self, img_url, index):
        """Downloads and saves the image file."""
        try:
            img_data = requests.get(img_url, headers=self.headers).content
            filename = f"{self.author} - {self.series_title} - {index:03d}.jpg"
            path = os.path.join(self.folder, filename)
            
            with open(path, 'wb') as f:
                f.write(img_data)
            print(f"✅ Saved: {filename}")
            return True
        except Exception as e:
            print(f"❌ Error downloading photo {index}: {e}")
            return False

    def run(self, max_search=20):
        """Iterates through the series and downloads content."""
        print(f"🚀 Starting archival for: {self.base_url}")
        
        self.fetch_metadata()
        
        # Format the subfolder with the same naming convention as the images
        subfolder_name = f"{self.author} - {self.series_title}"
        self.folder = os.path.join(self.base_folder, subfolder_name)
        
        if not os.path.exists(self.folder):
            os.makedirs(self.folder, exist_ok=True)

        print(f"📸 Scraping: {self.series_title} by {self.author}")
        
        # We use a ThreadPool for faster concurrent checking/downloading
        with ThreadPoolExecutor(max_workers=5) as executor:
            for i in range(1, max_search + 1):
                img_url = self.fetch_image_url(i)
                if img_url:
                    executor.submit(self.download_image, img_url, i)
                else:
                    print(f"🏁 End of series reached at index {i}.")
                    break

if __name__ == "__main__":
    # You can change the URL here for your IDE tests

    # home url
    # https://www.worldpressphoto.org/collection/photocontest/2026


    # series
    TARGET_URL = "https://www.worldpressphoto.org/collection/photo-contest/2025/Musuk-Nolte/1"
    # TARGET_URL = "https://www.worldpressphoto.org/collection/photo-contest/2026/Elise-Blanchard/1"
    
    downloader = WPPDownloader(TARGET_URL)
    downloader.run()