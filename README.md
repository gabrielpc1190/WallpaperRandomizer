# WallpaperRandomizer 2.0 (Python Edition)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-green.svg)

Una modernización completa del original WallpaperRandomizer, ahora escrito 100% en Python 3. Esta aplicación se ejecuta de forma silenciosa en la bandeja del sistema (System Tray) y descarga automáticamente fondos de pantalla de alta calidad basados en tus palabras clave.

> **Inspiración y Origen:** Este proyecto es una reimaginación 100% Python inspirada en el excelente script original de AutoHotkey creado por DannyBen: [DannyBen/WallpaperRandomizer](https://github.com/DannyBen/WallpaperRandomizer)

## ✨ Características Principales

- **Descarga Automática**: Busca imágenes en Google y Brave usando APIs rest.
- **Doble Temporizador**: Intervalos independientes para descargar nuevas imágenes y para rotar el fondo de pantalla actual.
- **Historial Cronológico**: Los atajos de teclado `Win + F5` (Siguiente) y `Win + Shift + F5` (Anterior) respetan el orden de descarga en el disco.
- **Limpieza Automática**: Borra imágenes antiguas automáticamente para ahorrar espacio en disco.
- **Icono en System Tray**: Menú contextual completo para forzar descargas, pausar o configurar palabras clave.
- **Sin Dependencias de AHK**: Arquitectura moderna y nativa para Windows 10 y 11.

## 🚀 Instalación Rápida (Windows)

Si no tienes Python instalado, solicita el ejecutable `main.exe` pre-compilado. 

### Método Automático (Recomendado)
1. Descarga este repositorio.
2. Haz clic derecho sobre `install.ps1` y selecciona **"Ejecutar con PowerShell"**.
3. El script configurará todo: compilará (si es necesario), moverá los archivos a `%LOCALAPPDATA%` y creará el inicio automático con Windows.

### Método Manual (Para Desarrolladores)
1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Configura tus API Keys en `config.json`.
3. Ejecuta con:
   ```bash
   pythonw main.py
   ```

## ⚙️ Configuración (`config.json`)

- `auth`: Tus llaves de API para Google/Brave.
- `intervals`: Tiempos de descarga y rotación (en minutos).
- `system.cleanup_days_old`: Cuántos días guardar las imágenes antes de borrarlas.
- `paths.download_dir`: Carpeta donde se guardan las descargas.
- `api_preference`: Elige entre `"google"` o `"brave"`.

## ⌨️ Atajos de Teclado (Globales)

- **Win + F5**: Aplicar el fondo de pantalla más reciente descargado.
- **Win + Shift + F5**: Volver al fondo de pantalla anterior en el historial de archivos.

## 🛠️ Contribuir

1. Haz un fork del proyecto.
2. Crea una rama para tu mejora (`git checkout -b feature/MejoraIncreible`).
3. Haz commit de tus cambios (`git commit -am 'Agregada nueva mejora'`).
4. Sube la rama (`git push origin feature/MejoraIncreible`).
5. Abre un Pull Request.

## 📄 Licencia

Este proyecto se distribuye bajo la **Licencia MIT**, al igual que el proyecto original.

**Requisito de la Licencia MIT:** Cualquier distribución de este código (incluso parcial o modificado) debe incluir el aviso de copyright original de Danny Ben Shitrit y la nota de permiso (ver archivo `LICENSE` adjunto en la raíz del proyecto). Eres libre de usar, modificar, distribuir o usar comercialmente este código, siempre y cuando mantengas visible ese archivo de licencia.
