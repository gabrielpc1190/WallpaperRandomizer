import pystray
from PIL import Image
import os
import threading

class UITray:
    def __init__(self, config_manager, app_callbacks):
        self.config = config_manager
        self.callbacks = app_callbacks
        self.icon = None

    def create_menu(self):
        return pystray.Menu(
            pystray.MenuItem("Next Wallpaper", self.callbacks['next']),
            pystray.MenuItem("Previous Wallpaper", self.callbacks['prev']),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Force Download Now", self.callbacks['download']),
            pystray.MenuItem("Edit Keywords", self.callbacks['edit_keywords']),
            pystray.MenuItem("Open Download Folder", self.callbacks['open_folder']),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.callbacks['exit'])
        )

    def _load_icon(self):
        icon_path = "W.ico" # Use the original repo icon
        if os.path.exists(icon_path):
            return Image.open(icon_path)
        else:
            # Fallback to a simple 64x64 blue image
            return Image.new('RGB', (64, 64), color=(0, 100, 255))

    def run(self):
        self.icon = pystray.Icon(
            "WallpaperRandomizer",
            self._load_icon(),
            "Wallpaper Randomizer (Python)",
            self.create_menu()
        )
        self.icon.run()

    def stop(self):
        if self.icon:
            self.icon.stop()
