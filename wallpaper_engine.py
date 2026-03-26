import os
import ctypes

class WallpaperEngine:
    def __init__(self, config_manager):
        self.config = config_manager
        self.download_dir = self.config.get('paths.download_dir', 'DownloadedWallpapers')
        self.current_wallpaper_path = None

    def _get_sorted_images(self):
        if not os.path.exists(self.download_dir):
            return []
        
        files = [os.path.join(self.download_dir, f) for f in os.listdir(self.download_dir) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        # Sort by creation/modification time
        files.sort(key=os.path.getmtime)
        return files

    def apply_next(self):
        images = self._get_sorted_images()
        if not images:
            return False
            
        # "Next" logic requested: Always show the most recent one
        target = images[-1]
        return self.apply_wallpaper(target)

    def apply_previous(self):
        images = self._get_sorted_images()
        if not images or len(images) < 2:
            return False
            
        # "Previous" logic: Find the one before the current one in time
        if self.current_wallpaper_path in images:
            idx = images.index(self.current_wallpaper_path)
            if idx > 0:
                return self.apply_wallpaper(images[idx - 1])
        
        # Fallback if current isn't tracked or is the first: apply the second to last
        return self.apply_wallpaper(images[-2])

    def apply_wallpaper(self, image_path):
        full_path = os.path.abspath(image_path)
        if not os.path.exists(full_path):
            return False
            
        try:
            # SPI_SETDESKWALLPAPER = 20
            # SPIF_UPDATEINIFILE = 0x01
            # SPIF_SENDWININICHANGE = 0x02
            if os.name == 'nt':
                ctypes.windll.user32.SystemParametersInfoW(20, 0, full_path, 0x01 | 0x02)
            else:
                print(f"[UNSUPPORTED OS] Would apply wallpaper: {full_path}")
            
            self.current_wallpaper_path = image_path
            return True
        except Exception as e:
            print(f"Error applying wallpaper: {e}")
            return False
