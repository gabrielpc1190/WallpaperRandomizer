import os
import random
import time
import hashlib
import requests
import datetime
from urllib.parse import urlparse

class DownloadEngine:
    def __init__(self, config_manager):
        self.config = config_manager
        self.download_dir = self.config.get('paths.download_dir', 'DownloadedWallpapers')
        self._ensure_paths()

    def _ensure_paths(self):
        self.download_dir = self.config.get('paths.download_dir', 'DownloadedWallpapers')
        if not os.path.exists(self.download_dir):
            try:
                os.makedirs(self.download_dir)
            except Exception:
                pass

    def _get_random_keyword(self):
        keywords = self.config.get_keywords_list()
        return random.choice(keywords) if keywords else "Wallpaper"

    def download_new(self):
        self._ensure_paths()
        keyword = self._get_random_keyword()
        api_pref = self.config.get('api_preference', 'google')

        if api_pref == 'google':
            search = self._search_google(keyword)
        elif api_pref == 'brave':
            search = self._search_brave(keyword)
        else:
            return {'success': False, 'message': f"API preferida '{api_pref}' no soportada.", 'filename': ''}

        if not search.get('success'):
            return search

        urls = list(search.get('urls', []))
        random.shuffle(urls)

        existing_hashes = self._existing_hashes()
        last_message = f"No se encontraron imágenes nuevas para '{keyword}' (todas duplicadas)."

        for url in urls:
            result = self._download_image(url, keyword, existing_hashes)
            if result.get('success'):
                return result
            last_message = result.get('message', last_message)
            if result.get('duplicate'):
                # Try the next candidate; known-duplicate shouldn't fail the whole run.
                continue

        return {'success': False, 'message': last_message, 'filename': ''}

    def _existing_hashes(self):
        """SHA1 digests of every file currently in the download dir.

        Used to skip re-downloading identical images even if the URL / filename
        differ. Files are small (wallpapers) and the folder is pruned by
        cleanup_old_files, so hashing on each run is cheap.
        """
        hashes = set()
        try:
            for f in os.listdir(self.download_dir):
                path = os.path.join(self.download_dir, f)
                if not os.path.isfile(path):
                    continue
                try:
                    h = hashlib.sha1()
                    with open(path, 'rb') as fp:
                        for chunk in iter(lambda: fp.read(65536), b''):
                            h.update(chunk)
                    hashes.add(h.hexdigest())
                except Exception:
                    pass
        except Exception:
            pass
        return hashes

    def _search_google(self, query):
        api_key = self.config.get('auth.google_api_key', '').strip()
        cx = self.config.get('auth.google_cx', '').strip()
        
        if not api_key or not cx or api_key.startswith('YOUR_'): 
            return {'success': False, 'message': 'API Key o CX de Google no configurado.'}
        
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
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            if r.status_code != 200:
                msg = data.get('error', {}).get('message', 'Error desconocido en Google')
                return {'success': False, 'message': f"Error de Google: {msg}"}
                
            items = data.get('items', [])
            
            # Filter minimum 1920x1080
            high_res_items = []
            for item in items:
                img_info = item.get('image', {})
                w = img_info.get('width', 0)
                h = img_info.get('height', 0)
                if w >= 1920 and h >= 1080:
                    high_res_items.append(item)
                    
            # Fallback a menos exigente si no hay 1080p puro
            if not high_res_items:
                high_res_items = [i for i in items if i.get('image', {}).get('width', 0) >= 1280]

            if high_res_items:
                return {'success': True, 'urls': [i['link'] for i in high_res_items]}
            else:
                return {'success': False, 'message': f"No se encontraron imágenes en Full HD para '{query}'."}
        except Exception as e:
            return {'success': False, 'message': f"Fallo de red: {e}"}

    def _search_brave(self, query):
        api_key = self.config.get('auth.brave_api_key', '').strip()
        if not api_key or api_key.startswith('YOUR_'): 
            return {'success': False, 'message': 'API Key de Brave no configurada.'}
        
        url = "https://api.search.brave.com/res/v1/images/search"
        headers = {'Accept': 'application/json', 'X-Subscription-Token': api_key}
        params = {'q': query, 'count': 20}
        try:
            r = requests.get(url, headers=headers, params=params, timeout=10)
            data = r.json()
            if r.status_code != 200:
                return {'success': False, 'message': f"Error de Brave: {r.status_code}"}
                
            results = data.get('results', [])
            
            # Filter minimum 1920x1080
            high_res_results = []
            for res in results:
                props = res.get('properties', {})
                w = props.get('width', 0)
                h = props.get('height', 0)
                if w >= 1920 and h >= 1080:
                    high_res_results.append(res)
                    
            # Fallback
            if not high_res_results:
                high_res_results = [r for r in results if r.get('properties', {}).get('width', 0) >= 1280]

            if high_res_results:
                return {'success': True, 'urls': [r['properties']['url'] for r in high_res_results]}
            else:
                return {'success': False, 'message': f"No se encontraron imágenes en Full HD para '{query}'."}
        except Exception as e:
            return {'success': False, 'message': f"Fallo de red: {e}"}

    def _download_image(self, url, keyword, existing_hashes=None):
        try:
            # Fake latest Brave browser user agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            }
            r = requests.get(url, headers=headers, stream=True, timeout=15)
            if r.status_code != 200:
                return {'success': False, 'message': f"El servidor de la imagen rechazó la conexión (HTTP {r.status_code})."}

            content_type = r.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                return {'success': False, 'message': f"La URL entregó {content_type} en lugar de una imagen."}

            # Read the full body into memory so we can hash before committing to disk.
            # Wallpaper images are small enough that this is cheaper than writing and
            # deleting duplicates.
            data = r.content
            digest = hashlib.sha1(data).hexdigest()

            if existing_hashes is not None and digest in existing_hashes:
                return {
                    'success': False,
                    'duplicate': True,
                    'message': f"Imagen duplicada ({digest[:8]}), ya está descargada."
                }

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_keyword = "".join(x for x in keyword if x.isalnum() or x in " -_").strip()
            ext = os.path.splitext(urlparse(url).path)[1].lower()

            if ext not in ['.jpg', '.jpeg', '.png', '.bmp']:
                ext = ".jpg"

            filename = f"{timestamp}_{clean_keyword}_{digest[:16]}{ext}"
            filepath = os.path.join(self.download_dir, filename)

            with open(filepath, 'wb') as f:
                f.write(data)

            if existing_hashes is not None:
                existing_hashes.add(digest)

            self.cleanup_old_files()
            return {'success': True, 'message': 'Descarga completada', 'filename': filename, 'path': filepath}
        except Exception as e:
            return {'success': False, 'message': f"Error al descargar imagen: {e}"}

    def cleanup_old_files(self):
        days = self.config.get('system.cleanup_days_old', 7)
        now = time.time()
        for f in os.listdir(self.download_dir):
            path = os.path.join(self.download_dir, f)
            if os.path.isfile(path):
                if os.stat(path).st_mtime < now - (days * 86400):
                    try:
                        os.remove(path)
                    except Exception:
                        pass
