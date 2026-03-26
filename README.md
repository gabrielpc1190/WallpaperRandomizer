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
