# WallpaperRandomizer 2.0 (Python Edition)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-green.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-yellow.svg)

Aplicación de escritorio para Windows que descarga automáticamente fondos de pantalla de alta resolución (Full HD mínimo) desde internet y los rota periódicamente. Se ejecuta de forma silenciosa en la bandeja del sistema (System Tray).

> **Origen:** Proyecto inspirado en el script original de AutoHotkey de [DannyBen/WallpaperRandomizer](https://github.com/DannyBen/WallpaperRandomizer). Reimaginado completamente en Python 3.

---

## Características

| Función | Descripción |
|---|---|
| **Descarga Automática** | Busca imágenes vía API de Google Custom Search o Brave Search. |
| **Google Fotos** | Opcional: cada día baja N fotos horizontales al azar de tu propia biblioteca de Google Fotos y las rota en un horario (ver abajo). |
| **Filtro de Resolución** | Solo descarga imágenes de al menos 1920×1080 (Full HD). |
| **Doble Temporizador** | Intervalos independientes para descarga y rotación de fondo. |
| **Configuración Visual** | Ventana gráfica con pestañas (API Keys, intervalos, palabras clave, rutas). |
| **Atajos Globales** | `Win+F5` (siguiente fondo) y `Win+Shift+F5` (fondo anterior). |
| **Notificaciones Nativas** | Globos informativos de Windows en cada descarga, error o cambio. |
| **Limpieza Automática** | Elimina imágenes antiguas según los días configurados. |
| **Actualizaciones Seguras** | El instalador preserva tu configuración al actualizar de versión. |

---

## Compatibilidad

| Requisito | Detalle |
|---|---|
| **Sistema Operativo** | Windows 10 / Windows 11 (x64) |
| **Python** (solo desarrollo) | 3.8 o superior |
| **Resolución de pantalla** | 1920×1080 recomendado |
| **Conexión a Internet** | Requerida para descargar imágenes |
| **API Key** | Se necesita al menos una: Google Custom Search **o** Brave Search |

> **Nota:** El ejecutable pre-compilado (`.exe`) no requiere tener Python instalado.

---

## Instalación

### Opción 1: Ejecutable Pre-compilado (Recomendado)

1. Descarga el archivo `.zip` desde [Releases](../../releases) o desde la pestaña **Actions** del repositorio.
2. Extrae el contenido en una carpeta temporal.
3. Haz clic derecho sobre `install.ps1` → **Ejecutar con PowerShell**.
4. El instalador copiará los archivos a `%LOCALAPPDATA%\WallpaperRandomizer` y creará un acceso directo de inicio automático.

### Opción 2: Desde el Código Fuente (Desarrolladores)

```bash
git clone https://github.com/gabrielpc1190/WallpaperRandomizer.git
cd WallpaperRandomizer
pip install -r requirements.txt
pythonw main.py
```

### Dependencias (requirements.txt)

| Paquete | Uso |
|---|---|
| `requests` | Comunicación HTTP con las APIs de búsqueda |
| `pystray` | Icono y menú en la bandeja del sistema |
| `Pillow` | Procesamiento del icono del tray |
| `pynput` | Registro de atajos de teclado globales |
| `websocket-client` | Lee las cookies de Chrome por su puerto de depuración (fuente Google Fotos) |

---

## Primer Uso

Al ejecutar la aplicación por primera vez:

1. Se abrirá automáticamente la **ventana de configuración**.
2. Ve a la pestaña **API Keys** e ingresa tu clave de Google o Brave (no necesitas ambas).
3. Ve a la pestaña **Palabras Clave** y agrega los temas que desees (ej: `Neon City`, `Mountains 4K`).
4. Haz clic en **Guardar**. La aplicación comenzará a descargar y rotar fondos automáticamente.

### Obtener una API Key

- **Brave Search:** Regístrate gratis en [brave.com/search/api](https://brave.com/search/api/).
- **Google Custom Search:** Crea un proyecto en [Google Cloud Console](https://console.cloud.google.com/) y activa la API de Custom Search.

---

## Fuente Google Fotos

Google retiró en marzo de 2025 el acceso de lectura a la biblioteca por OAuth, así que esta fuente usa la sesión web de photos.google.com de un Chrome local:

1. Abre Chrome con puerto de depuración local: `chrome.exe --remote-debugging-port=9222 --user-data-dir=<carpeta de perfil>` e inicia sesión en Google Fotos.
2. En Configuración → General elige **Fuente de fondos: google_photos** y la cantidad de fotos por día.
3. Cada día (desde las 8:00) la app lee las cookies de ese Chrome, recorre la biblioteca de a poco (saltando videos y fotos verticales o menores a 1920 px) y baja el lote del día a `GooglePhotosWallpapers/`. Los lotes de días anteriores se borran.
4. De 8 a 22 h cambia el fondo cada «Rotar fondo cada» minutos recorriendo el lote; `Win+F5` / `Win+Shift+F5` avanzan o retroceden dentro del lote.

Las cookies no se guardan en disco. Si Chrome está cerrado o Google pide iniciar sesión, la app lo avisa con una notificación y lo reintenta cada 10 minutos. Opciones avanzadas en `config.json` → `google_photos` (`start_hour`, `end_hour`, `chrome_debug_port`, `account_index`, `min_width`, `pages_per_run`).

> Usa endpoints internos no documentados de Google Fotos: pueden cambiar sin aviso.

---

## Uso Diario

| Acción | Cómo |
|---|---|
| Abrir configuración | Click izquierdo en el icono del tray |
| Forzar descarga | Click derecho → *Descargar Ahora* |
| Siguiente fondo | `Win + F5` |
| Fondo anterior | `Win + Shift + F5` |
| Ver carpeta de imágenes | Click derecho → *Abrir Carpeta* |
| Salir | Click derecho → *Salir* |

---

## Estructura del Proyecto

```
WallpaperRandomizer/
├── main.py              # Orquestador principal
├── config_manager.py    # Lectura/escritura de config.json
├── download_engine.py   # Motor de búsqueda y descarga de imágenes
├── google_photos_engine.py # Fuente Google Fotos (sesión de Chrome local)
├── wallpaper_engine.py  # Aplicación nativa de fondos (ctypes/WinAPI)
├── settings_window.py   # GUI de configuración (tkinter)
├── ui_tray.py           # Icono y menú del System Tray
├── hotkey_manager.py    # Atajos de teclado globales
├── config.json          # Configuración del usuario
├── search_keywords.txt  # Palabras clave de búsqueda
├── install.ps1          # Instalador automático para Windows
├── build.bat            # Script de compilación con PyInstaller
└── docs/
    └── SIMULACIONES.md  # Análisis de 20 casos de uso y edge cases
```

---

## Compilación

Para generar el ejecutable `.exe` manualmente:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --icon=W.ico --name=WallpaperRandomizer main.py
```

También puede compilarse automáticamente vía GitHub Actions al hacer push a `master`.

---

## Contribuir

1. Haz un fork del proyecto.
2. Crea una rama (`git checkout -b feature/MiMejora`).
3. Commit y push (`git push origin feature/MiMejora`).
4. Abre un Pull Request.

---

## Licencia

Distribuido bajo la **Licencia MIT**, al igual que el proyecto original de Danny Ben Shitrit.

Cualquier distribución de este código debe incluir el aviso de copyright original (ver archivo [LICENSE](LICENSE)).
