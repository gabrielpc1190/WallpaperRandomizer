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
            pystray.MenuItem("Siguiente fondo", self.callbacks['next']),
            pystray.MenuItem("Fondo anterior", self.callbacks['prev']),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Forzar descarga ahora", self.callbacks['download']),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Configuración...", self.callbacks['settings']),
            pystray.MenuItem("Editar palabras clave", self.callbacks['edit_keywords']),
            pystray.MenuItem("Abrir carpeta de descargas", self.callbacks['open_folder']),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Acerca de", self.callbacks['about']),
            pystray.MenuItem("Salir", self.callbacks['exit'])
        )

    def _load_icon(self):
        # Try multiple search paths for the icon
        possible_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "W.ico"),
            "W.ico",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "W.ico"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    return Image.open(path)
                except Exception:
                    continue
        # Fallback to a simple 64x64 blue image
        return Image.new('RGB', (64, 64), color=(0, 100, 255))

    def _get_tooltip(self):
        dl = self.config.get('intervals.download_minutes', 60)
        rot = self.config.get('intervals.rotate_minutes', 15)
        download_dir = self.config.get('paths.download_dir', 'DownloadedWallpapers')
        count = 0
        if os.path.exists(download_dir):
            count = len([f for f in os.listdir(download_dir)
                         if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
        return f"WallpaperRandomizer | {count} fondos | Rota cada {rot}min | Descarga cada {dl}min"

    def notify(self, title, message):
        """Show a native Windows balloon notification."""
        if self.icon:
            try:
                self.icon.notify(message, title)
            except Exception as e:
                print(f"Notification error: {e}")

    def run(self):
        self.icon = pystray.Icon(
            "WallpaperRandomizer",
            self._load_icon(),
            self._get_tooltip(),
            self.create_menu()
        )
        # Set default (left-click) action to open settings
        self.icon.default_action = self.callbacks.get('settings')
        self.icon.run()

    def stop(self):
        if self.icon:
            self.icon.stop()
