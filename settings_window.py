import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import requests


class SettingsWindow:
    """GUI Settings window using tkinter with tabs for all configuration."""

    def __init__(self, config_manager, on_save_callback=None):
        self.config = config_manager
        self.on_save_callback = on_save_callback
        self.window = None

    def show(self, first_run=False):
        """Open the settings window. Thread-safe: can be called from any thread."""
        if self.window is not None:
            try:
                self.window.lift()
                self.window.focus_force()
                return
            except Exception:
                self.window = None

        self.window = tk.Tk()
        self.window.title("WallpaperRandomizer — Configuración")
        self.window.geometry("520x480")
        self.window.resizable(False, False)

        # Try to set icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "W.ico")
        if os.path.exists(icon_path):
            try:
                self.window.iconbitmap(icon_path)
            except Exception:
                pass

        # Header
        if first_run:
            header = tk.Frame(self.window, bg="#2563eb", height=50)
            header.pack(fill=tk.X)
            header.pack_propagate(False)
            tk.Label(header, text="¡Bienvenido a WallpaperRandomizer!",
                     font=("Segoe UI", 13, "bold"), fg="white", bg="#2563eb").pack(pady=12)

            info_frame = tk.Frame(self.window, bg="#eff6ff", padx=10, pady=8)
            info_frame.pack(fill=tk.X)
            tk.Label(info_frame,
                     text="Configura al menos una API Key para empezar a descargar fondos de pantalla.",
                     font=("Segoe UI", 9), bg="#eff6ff", fg="#1e40af", wraplength=480).pack()

        # Notebook (tabs)
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 0))

        # === Tab 1: General ===
        tab_general = ttk.Frame(notebook, padding=15)
        notebook.add(tab_general, text="  General  ")

        ttk.Label(tab_general, text="Motor de búsqueda preferido:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_pref_var = tk.StringVar(value=self.config.get('api_preference', 'google'))
        api_combo = ttk.Combobox(tab_general, textvariable=self.api_pref_var,
                                 values=["google", "brave"], state="readonly", width=15)
        api_combo.grid(row=0, column=1, sticky=tk.W, padx=10)

        ttk.Label(tab_general, text="Descargar cada (minutos):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.download_interval_var = tk.IntVar(value=self.config.get('intervals.download_minutes', 60))
        ttk.Spinbox(tab_general, from_=1, to=1440, textvariable=self.download_interval_var,
                     width=8).grid(row=1, column=1, sticky=tk.W, padx=10)

        ttk.Label(tab_general, text="Rotar fondo cada (minutos):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.rotate_interval_var = tk.IntVar(value=self.config.get('intervals.rotate_minutes', 15))
        ttk.Spinbox(tab_general, from_=1, to=1440, textvariable=self.rotate_interval_var,
                     width=8).grid(row=2, column=1, sticky=tk.W, padx=10)

        ttk.Label(tab_general, text="Borrar imágenes después de (días):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.cleanup_days_var = tk.IntVar(value=self.config.get('system.cleanup_days_old', 7))
        ttk.Spinbox(tab_general, from_=1, to=365, textvariable=self.cleanup_days_var,
                     width=8).grid(row=3, column=1, sticky=tk.W, padx=10)

        # === Tab 2: API Keys ===
        tab_api = ttk.Frame(notebook, padding=15)
        notebook.add(tab_api, text="  API Keys  ")

        ttk.Label(tab_api, text="Google Custom Search API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.google_key_var = tk.StringVar(value=self._clean_placeholder(self.config.get('auth.google_api_key', '')))
        ttk.Entry(tab_api, textvariable=self.google_key_var, width=45).grid(row=1, column=0, columnspan=2, sticky=tk.W)

        ttk.Label(tab_api, text="Google Custom Search CX (ID del buscador):").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        self.google_cx_var = tk.StringVar(value=self._clean_placeholder(self.config.get('auth.google_cx', '')))
        ttk.Entry(tab_api, textvariable=self.google_cx_var, width=45).grid(row=3, column=0, columnspan=2, sticky=tk.W)

        ttk.Label(tab_api, text="Brave Search API Key:").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        self.brave_key_var = tk.StringVar(value=self._clean_placeholder(self.config.get('auth.brave_api_key', '')))
        ttk.Entry(tab_api, textvariable=self.brave_key_var, width=45).grid(row=5, column=0, columnspan=2, sticky=tk.W)

        ttk.Button(tab_api, text="Verificar conexión", command=self._verify_api).grid(row=6, column=0, pady=15, sticky=tk.W)

        # === Tab 3: Palabras Clave ===
        tab_keywords = ttk.Frame(notebook, padding=15)
        notebook.add(tab_keywords, text="  Palabras Clave  ")

        kw_top = ttk.Frame(tab_keywords)
        kw_top.pack(fill=tk.X)
        ttk.Label(kw_top, text="Las imágenes se buscan usando estas palabras clave:").pack(anchor=tk.W)

        kw_list_frame = ttk.Frame(tab_keywords)
        kw_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.keyword_listbox = tk.Listbox(kw_list_frame, height=8, font=("Segoe UI", 10))
        scrollbar = ttk.Scrollbar(kw_list_frame, orient=tk.VERTICAL, command=self.keyword_listbox.yview)
        self.keyword_listbox.configure(yscrollcommand=scrollbar.set)
        self.keyword_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for kw in self.config.get_keywords_list():
            self.keyword_listbox.insert(tk.END, kw)

        kw_buttons = ttk.Frame(tab_keywords)
        kw_buttons.pack(fill=tk.X, pady=5)

        self.new_keyword_var = tk.StringVar()
        ttk.Entry(kw_buttons, textvariable=self.new_keyword_var, width=30).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(kw_buttons, text="Agregar", command=self._add_keyword).pack(side=tk.LEFT, padx=2)
        ttk.Button(kw_buttons, text="Eliminar seleccionado", command=self._remove_keyword).pack(side=tk.LEFT, padx=2)

        # === Tab 4: Rutas ===
        tab_paths = ttk.Frame(notebook, padding=15)
        notebook.add(tab_paths, text="  Rutas  ")

        ttk.Label(tab_paths, text="Carpeta de descarga de imágenes:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.download_dir_var = tk.StringVar(value=self.config.get('paths.download_dir', 'DownloadedWallpapers'))

        dir_frame = ttk.Frame(tab_paths)
        dir_frame.grid(row=1, column=0, sticky=tk.EW)
        ttk.Entry(dir_frame, textvariable=self.download_dir_var, width=40).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(dir_frame, text="Examinar...", command=self._browse_folder).pack(side=tk.LEFT)

        full_path = os.path.abspath(self.download_dir_var.get())
        self.path_label = ttk.Label(tab_paths, text=f"Ruta completa: {full_path}", foreground="gray")
        self.path_label.grid(row=2, column=0, sticky=tk.W, pady=5)

        # Bottom action buttons
        btn_frame = ttk.Frame(self.window, padding=10)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="Guardar", command=self._save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self._close).pack(side=tk.RIGHT, padx=5)

        # If first run, go to API Keys tab
        if first_run:
            notebook.select(tab_api)

        self.window.protocol("WM_DELETE_WINDOW", self._close)
        self.window.mainloop()

    def _clean_placeholder(self, value):
        """Clear placeholder values so the user sees an empty field."""
        placeholders = ["YOUR_GOOGLE_API_KEY", "YOUR_GOOGLE_CX", "YOUR_BRAVE_API_KEY"]
        if value in placeholders:
            return ""
        return value

    def _add_keyword(self):
        kw = self.new_keyword_var.get().strip()
        if kw:
            self.keyword_listbox.insert(tk.END, kw)
            self.new_keyword_var.set("")

    def _remove_keyword(self):
        selection = self.keyword_listbox.curselection()
        if selection:
            self.keyword_listbox.delete(selection[0])

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta de descarga")
        if folder:
            self.download_dir_var.set(folder)
            self.path_label.config(text=f"Ruta completa: {os.path.abspath(folder)}")

    def _verify_api(self):
        """Test API connectivity with a quick query."""
        pref = self.api_pref_var.get()
        try:
            if pref == "google":
                key = self.google_key_var.get().strip()
                cx = self.google_cx_var.get().strip()
                if not key or not cx:
                    messagebox.showwarning("Verificación", "Ingresa la API Key y el CX de Google primero.")
                    return
                r = requests.get("https://www.googleapis.com/customsearch/v1",
                                 params={'q': 'test', 'cx': cx, 'key': key, 'searchType': 'image', 'num': 1},
                                 timeout=10)
                if r.status_code == 200:
                    messagebox.showinfo("Verificación", "✅ Conexión con Google exitosa.")
                else:
                    data = r.json()
                    msg = data.get('error', {}).get('message', r.text[:200])
                    messagebox.showerror("Verificación", f"❌ Error de Google ({r.status_code}):\n{msg}")
            elif pref == "brave":
                key = self.brave_key_var.get().strip()
                if not key:
                    messagebox.showwarning("Verificación", "Ingresa la API Key de Brave primero.")
                    return
                r = requests.get("https://api.search.brave.com/res/v1/images/search",
                                 headers={'Accept': 'application/json', 'X-Subscription-Token': key},
                                 params={'q': 'test', 'count': 1}, timeout=10)
                if r.status_code == 200:
                    messagebox.showinfo("Verificación", "✅ Conexión con Brave exitosa.")
                else:
                    messagebox.showerror("Verificación", f"❌ Error de Brave ({r.status_code}):\n{r.text[:200]}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Verificación", "❌ Sin conexión a Internet.")
        except Exception as e:
            messagebox.showerror("Verificación", f"❌ Error inesperado:\n{e}")

    def _save(self):
        """Save all settings to config and keywords file."""
        self.config.set('api_preference', self.api_pref_var.get())
        self.config.set('intervals.download_minutes', self.download_interval_var.get())
        self.config.set('intervals.rotate_minutes', self.rotate_interval_var.get())
        self.config.set('system.cleanup_days_old', self.cleanup_days_var.get())

        google_key = self.google_key_var.get().strip()
        google_cx = self.google_cx_var.get().strip()
        brave_key = self.brave_key_var.get().strip()
        self.config.set('auth.google_api_key', google_key)
        self.config.set('auth.google_cx', google_cx)
        self.config.set('auth.brave_api_key', brave_key)

        self.config.set('paths.download_dir', self.download_dir_var.get())

        self.config.save()

        # Save keywords
        keywords = list(self.keyword_listbox.get(0, tk.END))
        self.config.save_keywords_list(keywords)

        messagebox.showinfo("Guardado", "✅ Configuración guardada correctamente.")
        self._close()

        if self.on_save_callback:
            self.on_save_callback()

    def _close(self):
        if self.window:
            self.window.destroy()
            self.window = None
