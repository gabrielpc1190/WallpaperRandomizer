import os
import random
import time
import requests
import datetime
from urllib.parse import urlparse

class DownloadEngine:
    def __init__(self, config_manager):
        self.config = config_manager
        self.download_dir = self.config.get('paths.download_dir', 'DownloadedWallpapers')
        self.keywords_file = self.config.get('paths.keywords_file', 'search_keywords.txt')
        self._ensure_paths()

    def _ensure_paths(self):
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        if not os.path.exists(self.keywords_file):
            with open(self.keywords_file, 'w') as f:
                f.write("Cyberpunk City,Nature Landscape 4K,Abstract Art,Space Nebula")

    def _get_random_keyword(self):
        try:
            with open(self.keywords_file, 'r') as f:
                content = f.read()
                keywords = [k.strip() for k in content.split(',') if k.strip()]
                return random.choice(keywords) if keywords else "Wallpaper"
        except Exception:
            return "Wallpaper"

    def download_new(self):
        keyword = self._get_random_keyword()
        api_pref = self.config.get('api_preference', 'google')
        
        image_url = None
        if api_pref == 'google':
            image_url = self._search_google(keyword)
        elif api_pref == 'brave':
            image_url = self._search_brave(keyword)

        if image_url:
            return self._download_image(image_url, keyword)
        return False

    def _search_google(self, query):
        api_key = self.config.get('auth.google_api_key')
        cx = self.config.get('auth.google_cx')
        if not api_key or not cx: return None
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': query,
            'cx': cx,
            'key': api_key,
            'searchType': 'image',
            'imgSize': 'huge',
            'num': 10
        }
        try:
            r = requests.get(url, params=params)
            data = r.json()
            items = data.get('items', [])
            if items:
                return random.choice(items)['link']
        except Exception as e:
            print(f"Google Search Error: {e}")
        return None

    def _search_brave(self, query):
        api_key = self.config.get('auth.brave_api_key')
        if not api_key: return None
        
        url = "https://api.search.brave.com/res/v1/images/search"
        headers = {'Accept': 'application/json', 'X-Subscription-Token': api_key}
        params = {'q': query, 'count': 20}
        try:
            r = requests.get(url, headers=headers, params=params)
            data = r.json()
            results = data.get('results', [])
            if results:
                return random.choice(results)['properties']['url']
        except Exception as e:
            print(f"Brave Search Error: {e}")
        return None

    def _download_image(self, url, keyword):
        try:
            # Fake user agent to avoid basic blocks
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            r = requests.get(url, headers=headers, stream=True, timeout=15)
            if r.status_code == 200:
                # Check if it actually returned an image
                content_type = r.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    print(f"URL did not point to an image. Content-Type: {content_type}")
                    return False
                    
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                clean_keyword = "".join(x for x in keyword if x.isalnum() or x in " -_").strip()
                ext = os.path.splitext(urlparse(url).path)[1].lower()
                
                # Enforce valid extensions based on ctypes requirements
                if ext not in ['.jpg', '.jpeg', '.png', '.bmp']: 
                    ext = ".jpg" 
                
                filename = f"{timestamp}_{clean_keyword}{ext}"
                filepath = os.path.join(self.download_dir, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                print(f"Downloaded: {filename}")
                self.cleanup_old_files()
                return filepath
        except Exception as e:
            print(f"Download Error: {e}")
        return False

    def cleanup_old_files(self):
        days = self.config.get('system.cleanup_days_old', 7)
        now = time.time()
        for f in os.listdir(self.download_dir):
            path = os.path.join(self.download_dir, f)
            if os.path.isfile(path):
                if os.stat(path).st_mtime < now - (days * 86400):
                    try:
                        os.remove(path)
                        print(f"Cleaned up: {f}")
                    except Exception as e:
                        print(f"Cleanup Error: {e}")
