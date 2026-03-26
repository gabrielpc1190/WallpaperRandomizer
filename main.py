import os
import sys
import threading
import time
import subprocess
from config_manager import ConfigManager
from download_engine import DownloadEngine
from wallpaper_engine import WallpaperEngine
from hotkey_manager import HotkeyManager
from ui_tray import UITray

class Application:
    def __init__(self):
        self.config = ConfigManager()
        self.downloader = DownloadEngine(self.config)
        self.wallpaper = WallpaperEngine(self.config)
        
        self.running = True
        
        # Callbacks for UI/Hotkeys
        self.callbacks = {
            'next': self.on_next,
            'prev': self.on_prev,
            'download': self.on_download,
            'edit_keywords': self.on_edit_keywords,
            'open_folder': self.on_open_folder,
            'exit': self.on_exit
        }
        
        self.hotkeys = HotkeyManager(self.on_next, self.on_prev)
        self.ui = UITray(self.config, self.callbacks)

    def on_next(self, *args):
        print("Handling Next Action")
        self.wallpaper.apply_next()

    def on_prev(self, *args):
        print("Handling Previous Action")
        self.wallpaper.apply_previous()

    def on_download(self, *args):
        print("Forcing Download")
        self.downloader.download_new()

    def on_edit_keywords(self, *args):
        path = self.config.get('paths.keywords_file')
        if os.name == 'nt':
            os.startfile(path)

    def on_open_folder(self, *args):
        path = self.config.get('paths.download_dir')
        if os.name == 'nt':
            os.startfile(os.path.abspath(path))

    def on_exit(self, *args):
        print("Exiting...")
        self.running = False
        if os.name == 'nt':
            self.hotkeys.stop()
        self.ui.stop()

    def download_loop(self):
        while self.running:
            interval = self.config.get('intervals.download_minutes', 60) * 60
            self.downloader.download_new()
            time.sleep(interval)

    def rotation_loop(self):
        while self.running:
            interval = self.config.get('intervals.rotate_minutes', 15) * 60
            self.wallpaper.apply_next()
            time.sleep(interval)

    def start(self):
        # Start background threads
        threading.Thread(target=self.download_loop, daemon=True).start()
        threading.Thread(target=self.rotation_loop, daemon=True).start()
        
        if os.name == 'nt':
            self.hotkeys.start()
            
        # UI must run on main thread
        self.ui.run()

if __name__ == "__main__":
    app = Application()
    app.start()
