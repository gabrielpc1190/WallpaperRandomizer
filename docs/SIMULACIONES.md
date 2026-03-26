# 20 Simulaciones Teóricas: Casos de Uso y Automatización (WallpaperRandomizer)

Este documento contiene un análisis exhaustivo del comportamiento de la aplicación bajo **20 escenarios críticos, extremos y de automatización**. Se tomó en consideración la verificación mediante la API Key de Brave y el motor de Google.

---

### 1. Manejo de Palabras Clave (Keywords)

#### 1. Búsqueda con string vacío (`""` o espacios en blanco)
* **Condición**: El usuario introdujo `""`, `   ` o borró todo el listado.
* **Comportamiento**: `config_manager.py` sanitiza la lista (`[k.strip() for k in ... if k.strip()]`). Si la lista queda vacía, la aplicación inyecta forzosamente la palabra clave `"Wallpaper"`. Nunca se manda un query nulo a la API.

#### 2. Búsqueda de palabra clave incomprensible (ej. `"hfgdkkdfhgjk"`)
* **Condición**: API devuelve 0 resultados.
* **Comportamiento**: Brave API responde con `{"results": []}` (vacío). La app intercepta la lista vacía y lanza una notificación Balloon native: *"No se encontraron imágenes en Full HD para 'hfgdkkdfhgjk'"*. No se aplican fondos rotos ni pantalla negra.

#### 3. Búsqueda con inyección de código (ej. `"\" OR 1=1"`)
* **Condición**: Intentos de romper la URL.
* **Comportamiento**: La librería `requests` realiza el `urlencoding` automático (e.g., `%22+OR+1%3D1`). La API de búsqueda (Brave/Google) trata el string como texto natural. No hay riesgo de inyección local ni remota.

---

### 2. Resolución y Calidad de Imagen

#### 4. Ninguna imagen supera los 1080p en la primera página
* **Condición**: Todas las imágenes devueltas por la API tienen 800x600 o similar.
* **Comportamiento**: El nuevo filtro recorre el array descartando todo < 1920x1080. Al quedar la lista `high_res` vacía, se activa la Red de Seguridad y vuelve a evaluar el array buscando imágenes de mínimo 1280x720 (`>= 1280`). Si encuentra alguna, la escoge.

#### 5. Ninguna imagen supera los 720p (Condición Extrema)
* **Condición**: La Red de Seguridad (Fallback a 1280) también queda vacía.
* **Comportamiento**: El programa bloquea la descarga, no ensucia la carpeta local y notifica al usuario: *"No se encontraron imágenes en Full HD..."*.

---

### 3. Red y Descargas

#### 6. Desconexión de Internet justo al descargar
* **Condición**: El ping a la API funciona, pero se cae el WiFi al bajar los MBs de la foto.
* **Comportamiento**: El objeto `requests.get(stream=True, timeout=15)` arrojará una excepción de `Timeout` o `ConnectionError`. Es atrapada por un `try/except`. Notifica: *"Error al descargar imagen: [Detalle del log]"*. El wallpaper actual se mantiene intacto.

#### 7. Bloqueo por Firewall Estricto / Red Corporativa
* **Condición**: La red bloquea URLs como `googleapis.com` o el Content-Type.
* **Comportamiento**: Al recibir código HTTP 403 / 401 / 500, la app no se crashea. Notifica: *"Error de Google (403): Acceso denegado"*. El hilo principal sobrevive.

#### 8. URL no es realmente una imagen (HTML fraudulento)
* **Condición**: El link apunta a una web en vez de un JPG.
* **Comportamiento**: Se revisa la cabecera `Content-Type`. Si no empieza con `image/`, se aborta la descarga con el mensaje: *"La URL entregó text/html en lugar de una imagen."*. Se evita el formato corrupto en el disco duro.

#### 9. Baneos del servidor de destino (Modo Anti-Bot)
* **Condición**: El servidor de destino de la imagen bloquea Python.
* **Comportamiento**: Minimizado casi al 0% porque inyectamos un `User-Agent` moderno de un navegador real (`Chrome/123.0`). 

---

### 4. Ciclo de Vida del Daemon y Automation

#### 10. Rotación sin imágenes descargadas
* **Condición**: El timer de *Rotate* (15 min) ocurre pero la carpeta está vacía.
* **Comportamiento**: `get_sorted_images()` devuelve `[]`. El método `apply_next()` devuelve `False`. El bucle solo reintenta en el próximo intervalo. Para acciones forzadas, la UI dispara un hilo que descarga una imagen inmediatamente y luego la aplica.

#### 11. Presionar "Siguiente" o "Anterior" a repetición frenética
* **Condición**: Spam del atajo `Win+F5`
* **Comportamiento**: La llamada al API de Windows `SystemParametersInfoW` es sincrónica y muy ligera. El equipo aguantará el spam cambiando el fondo fluidamente siguiendo el array de archivos locales en memoria caché temporal.

#### 12. Modificación en caliente del archivo de configuración (`config.json`)
* **Condición**: Un script de automatización corporativa empuja un nuevo `config.json` remotamente y altera los intervalos.
* **Comportamiento**: El objeto `ConfigManager` carga los valores solo al arranque. Al cambiar de intervalo en el UI oficial o ser notificado, el *Sleep* se encolará. Ojo: Ediciones al `.txt` crudo solo se aplican si la app consulta el ciclo manual actual de nuevo (No hay Live-Reload watch-dog).

#### 13. Limpieza de Disco bajo Carga (Auto Cleanup)
* **Condición**: Más de 10,000 imágenes generadas en el equipo.
* **Comportamiento**: En cada descarga exitosa, el hilo dispara de forma asíncrona la limpieza de imágenes con `mtime` antiguo a 7 días (o configurable). Evita Memory Leaks o Disk Full Exceptions de forma pasiva.

---

### 5. API Keys y Respuestas

#### 14. Uso de API Key vencida / límite alcanzado (Rate Limit 429)
* **Condición**: Google (100 diarias) responde *Quota Exceded*.
* **Comportamiento**: Parsea el JSON de error de Google, extrae el string y lo manda al Balloon Tray: *"Error de Google (429): Rate Limit..."*.

#### 15. Primer arranque en un equipo nuevo (Onboarding automatizado)
* **Condición**: Se corre sin modificar `config.json`.
* **Comportamiento**: Las variables de la llave en `config.json` inician con "YOUR_...". El programa detecta esto con `is_first_run()`, detiene las solicitudes HTTP y lanza una GUI en primer plano amigable (Tkinter) bloqueando el flujo hasta configuración segura.

---

### 6. Sistema Operativo y Errores Fatales

#### 16. Fallo en el System Tray de Windows (explorer.exe se reinicia)
* **Condición**: Explorer se congela y reinicia, perdiendo iconos.
* **Comportamiento**: La librería `pystray` tiene listeners nativos para engancharse nuevamente cuando Windows recrea el taskbar shell (típicamente reaparecen los systrays).

#### 17. Permisos Denegados en la carpeta de descargas
* **Condición**: La ruta configurada (ej. `C:/Windows/SysWOW64`) no permite escritura *User Mode*.
* **Comportamiento**: El intento de escritura crashea el `open()`, capturado por el bloque general `except Exception`. Notifica *"Error al descargar: Permission Denied"*.

#### 18. Salida Forzada (Taskmgr `End Process Tree`)
* **Condición**: El usuario mata el ejecutable.
* **Comportamiento**: Cierre abortado. Teclas como `Win+F5` retornan al sistema instantáneamente ya que el Hook global muere junto al Thread (`ctypes.windll.user32.UnregisterHotKey` virtual nativo o desenganche de pynput abstracto).

#### 19. Desapareció la foto seleccionada en disco
* **Condición**: Antivirus borró el fondo justo cuando iba a aplicarse.
* **Comportamiento**: `os.path.exists()` dentro del módulo de wallpaper abortará antes de llamar a Windows, evitando pantallas en negro.

#### 20. Instalación manual sobre una versión antigua
* **Condición**: Se ejecuta el script `.ps1` de la actualización.
* **Comportamiento**: El `install.ps1` hace `Test-Path` sobre la configuración y explícitamente **evita el reemplazo** de `config.json` si ya existe, protegiendo llaves y preferencias para siempre.
