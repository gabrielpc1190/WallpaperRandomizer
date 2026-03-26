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
        
        result = {'success': False, 'message': 'Unknown error', 'filename': ''}
        
        if api_pref == 'google':
            result = self._search_google(keyword)
        elif api_pref == 'brave':
            result = self._search_brave(keyword)
        else:
            result['message'] = f"API preferida '{api_pref}' no soportada."

        if result['success'] and 'url' in result:
            return self._download_image(result['url'], keyword)
            
        return result

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
            if items:
                return {'success': True, 'url': random.choice(items)['link']}
            else:
                return {'success': False, 'message': f"No se encontraron imágenes para '{query}'."}
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
            if results:
                return {'success': True, 'url': random.choice(results)['properties']['url']}
            else:
                return {'success': False, 'message': f"No se encontraron imágenes para '{query}'."}
        except Exception as e:
            return {'success': False, 'message': f"Fallo de red: {e}"}

    def _download_image(self, url, keyword):
        try:
            # Fake latest Brave browser user agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            }
            r = requests.get(url, headers=headers, stream=True, timeout=15)
            if r.status_code == 200:
                content_type = r.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    return {'success': False, 'message': f"La URL entregó {content_type} en lugar de una imagen."}
                    
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                clean_keyword = "".join(x for x in keyword if x.isalnum() or x in " -_").strip()
                ext = os.path.splitext(urlparse(url).path)[1].lower()
                
                if ext not in ['.jpg', '.jpeg', '.png', '.bmp']: 
                    ext = ".jpg" 
                
                filename = f"{timestamp}_{clean_keyword}{ext}"
                filepath = os.path.join(self.download_dir, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                
                self.cleanup_old_files()
                return {'success': True, 'message': 'Descarga completada', 'filename': filename, 'path': filepath}
            else:
                return {'success': False, 'message': f"El servidor de la imagen rechazó la conexión (HTTP {r.status_code})."}
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
