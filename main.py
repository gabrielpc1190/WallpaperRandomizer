import os
import sys
import threading
import time
import datetime
from config_manager import ConfigManager
from download_engine import DownloadEngine
from wallpaper_engine import WallpaperEngine
from google_photos_engine import GooglePhotosEngine, SessionError
from hotkey_manager import HotkeyManager
from ui_tray import UITray
from settings_window import SettingsWindow
import startup_toast


class Application:
    def __init__(self):
        self.config = ConfigManager()
        self.downloader = DownloadEngine(self.config)
        self.wallpaper = WallpaperEngine(self.config)
        self.photos = GooglePhotosEngine(self.config)
        self._last_photos_error = None
        
        self.running = True
        self.settings_window = SettingsWindow(self.config, on_save_callback=self.on_settings_saved)
        
        self.callbacks = {
            'next': self.on_next,
            'prev': self.on_prev,
            'download': lambda: threading.Thread(target=self.on_download, daemon=True).start(),
            'settings': self.on_settings,
            'edit_keywords': self.on_settings,
            'open_folder': self.on_open_folder,
            'about': self.on_about,
            'exit': self.on_exit
        }
        
        self.hotkeys = HotkeyManager(self.on_next, self.on_prev)
        self.ui = UITray(self.config, self.callbacks)

    def _show_initial_wizard(self):
        """Bloquea el hilo principal hasta que el usuario cierre el Wizard."""
        self.settings_window.show(first_run=True)

    def on_settings_saved(self):
        """Llamado cuando el usuario hace clic en Guardar en la GUI."""
        self.ui.notify("Configuración", "Los cambios se aplicarán en el próximo ciclo.")

    def on_next(self, *args):
        if self.wallpaper.apply_next():
            self.ui.notify("Wallpaper", "Se aplicó el fondo más reciente.")
        else:
            self.ui.notify("Wallpaper", "No hay fondos descargados aún. Forzando descarga...")
            threading.Thread(target=self.on_download, daemon=True).start()

    def on_prev(self, *args):
        if self.wallpaper.apply_previous():
            self.ui.notify("Wallpaper", "Se aplicó el fondo anterior en el historial.")
        else:
            self.ui.notify("Wallpaper", "No se encontró un fondo anterior.")

    def _use_photos(self):
        """Google Photos is the active source; re-read each cycle so a settings change applies."""
        active = self.config.get('source') == 'google_photos'
        self.wallpaper.photos = self.photos if active else None
        return active

    def _download_photos(self):
        try:
            result = self.photos.download_daily()
        except SessionError as e:
            result = {'success': False, 'message': str(e)}
        except Exception as e:
            result = {'success': False, 'message': f"Error con Google Fotos: {e}"}
        if result['success']:
            self._last_photos_error = None
            self.ui.notify("Google Fotos", result['message'])
            self.wallpaper.last_slot = None
            self.wallpaper.apply_scheduled() or self.wallpaper.apply_next()
        elif result['message'] != self._last_photos_error:  # same error: notify once
            self._last_photos_error = result['message']
            self.ui.notify("Google Fotos", result['message'])

    def on_download(self):
        if self._use_photos():
            self._last_photos_error = None
            self._download_photos()
            return
        self.ui.notify("Descarga iniciada", "Buscando un nuevo fondo de pantalla...")
        result = self.downloader.download_new()
        
        if result['success']:
            self.ui.notify("Descarga completada", f"Nuevo fondo: {result.get('filename', '')}")
            self.wallpaper.apply_wallpaper(result.get('path'))
        else:
            self.ui.notify("Error de descarga", result.get('message', 'Fallo desconocido'))

    def on_settings(self, *args):
        # Correr la ventana en un hilo separado o encolado para evitar bloquear el UI Tray de pystray
        threading.Thread(target=lambda: self.settings_window.show(first_run=False), daemon=True).start()

    def on_open_folder(self, *args):
        path = self.config.get('paths.download_dir', 'DownloadedWallpapers')
        if self._use_photos():
            path = self.photos.folder
        if not os.path.exists(path):
            os.makedirs(path)
        if os.name == 'nt':
            os.startfile(os.path.abspath(path))

    def on_about(self, *args):
        import tkinter.messagebox as mb
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        mb.showinfo("Acerca de", "WallpaperRandomizer 2.0 (Python Edition)\n\n"
                                 "Basado en el trabajo de DannyBen.\n"
                                 "Descarga fondos de Google, Brave o tu Google Fotos.")
        root.destroy()

    def on_exit(self, *args):
        self.running = False
        if os.name == 'nt':
            self.hotkeys.stop()
        self.ui.stop()

    def download_loop(self):
        while self.running:
            if self._use_photos():
                if (datetime.datetime.now().hour >= self.config.get('google_photos.start_hour', 8)
                        and self.photos.needs_download()):
                    self._download_photos()
                time.sleep(600)
                continue
            interval = self.config.get('intervals.download_minutes', 60) * 60
            result = self.downloader.download_new()
            # Opcional: Notificar silenciosamente o solo loquear
            # if result['success']: print("Auto-download success")
            time.sleep(interval)

    def rotation_loop(self):
        while self.running:
            if self._use_photos():
                self.wallpaper.apply_scheduled()
                time.sleep(60)
                continue
            interval = self.config.get('intervals.rotate_minutes', 15) * 60
            self.wallpaper.apply_next()
            time.sleep(interval)

    def start(self):
        # 1. Onboarding / Wizard si no hay API Keys
        first_run = self.config.is_first_run()
        if first_run:
            self._show_initial_wizard()

        # 2. Iniciar Hilos de Fondo
        threading.Thread(target=self.download_loop, daemon=True).start()
        threading.Thread(target=self.rotation_loop, daemon=True).start()

        if os.name == 'nt':
            self.hotkeys.start()

        # 3. Toast de arranque (omitido tras el wizard para no apilar ventanas)
        if not first_run:
            startup_toast.show("Se inició correctamente.")

        # 4. Iniciar UI Tray (Este método bloquea y debe ser el último)
        self.ui.run()

if __name__ == "__main__":
    app = Application()
    app.start()
