import os
import sys
import threading
import time
from config_manager import ConfigManager
from download_engine import DownloadEngine
from wallpaper_engine import WallpaperEngine
from hotkey_manager import HotkeyManager
from ui_tray import UITray
from settings_window import SettingsWindow


class Application:
    def __init__(self):
        self.config = ConfigManager()
        self.downloader = DownloadEngine(self.config)
        self.wallpaper = WallpaperEngine(self.config)
        
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

    def on_download(self):
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
                                 "Descarga fondos de Google y Brave automáticamente.")
        root.destroy()

    def on_exit(self, *args):
        self.running = False
        if os.name == 'nt':
            self.hotkeys.stop()
        self.ui.stop()

    def download_loop(self):
        while self.running:
            interval = self.config.get('intervals.download_minutes', 60) * 60
            result = self.downloader.download_new()
            # Opcional: Notificar silenciosamente o solo loquear
            # if result['success']: print("Auto-download success")
            time.sleep(interval)

    def rotation_loop(self):
        while self.running:
            interval = self.config.get('intervals.rotate_minutes', 15) * 60
            self.wallpaper.apply_next()
            time.sleep(interval)

    def start(self):
        # 1. Onboarding / Wizard si no hay API Keys
        if self.config.is_first_run():
            self._show_initial_wizard()

        # 2. Iniciar Hilos de Fondo
        threading.Thread(target=self.download_loop, daemon=True).start()
        threading.Thread(target=self.rotation_loop, daemon=True).start()
        
        if os.name == 'nt':
            self.hotkeys.start()
            
        # 3. Iniciar UI Tray (Este método bloquea y debe ser el último)
        self.ui.run()

if __name__ == "__main__":
    app = Application()
    app.start()
