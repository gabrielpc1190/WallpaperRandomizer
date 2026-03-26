<#
.SYNOPSIS
Instalador Automático para WallpaperRandomizer en Windows 10/11.

.DESCRIPTION
Este script realiza lo siguiente:
1. Comprueba si el ejecutable ya fue compilado (dist/main.exe). Si no, intenta compilarlo usando Python y PyInstaller.
2. Crea una carpeta en la ruta de Aplicaciones del Usuario (LocalAppData).
3. Copia el ejecutable terminado y sus archivos (config, iconos) a esa ruta segura.
4. Crea un acceso directo automático en la carpeta de "Inicio" de Windows para que el programa arranque solo al encender el PC.
#>

$AppName = "WallpaperRandomizer"
$InstallDir = "$env:LOCALAPPDATA\$AppName"
$StartupFolder = [Environment]::GetFolderPath('Startup')
$ShortcutPath = "$StartupFolder\$AppName.lnk"
$ExeSource = ".\dist\main.exe"
$ExeTarget = "$InstallDir\main.exe"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Instalador de $AppName para Windows" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Comprobar o generar el .exe
if (-not (Test-Path $ExeSource)) {
    Write-Host "[*] El ejecutable no existe. Intentando compilarlo ahora..." -ForegroundColor Yellow
    
    # Comprobar si Python esta instalado
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Host " -> Python detectado. Instalando dependencias y compilando..."
        pip install -r requirements.txt pyinstaller
        pyinstaller --noconsole --onefile --icon=W.ico --add-data "W.ico;." main.py
    } else {
        Write-Host "[X] ERROR: No se encontro Python ni el archivo main.exe pre-compilado." -ForegroundColor Red
        Write-Host "Por favor, instala Python o descarga la version .exe ya lista." -ForegroundColor Red
        Pause
        exit
    }
}

# 2. Crear directorio de instalacion
Write-Host "[*] Configurando directorio de instalacion: $InstallDir"
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
}

# 3. Copiar archivos necesarios
Write-Host "[*] Copiando archivos del programa..."
Copy-Item -Path $ExeSource -Destination $ExeTarget -Force
Copy-Item -Path ".\config.json" -Destination "$InstallDir\config.json" -Force -ErrorAction SilentlyContinue
Copy-Item -Path ".\search_keywords.txt" -Destination "$InstallDir\search_keywords.txt" -Force -ErrorAction SilentlyContinue
Copy-Item -Path ".\W.ico" -Destination "$InstallDir\W.ico" -Force -ErrorAction SilentlyContinue

# 4. Crear acceso directo en el Inicio de Windows
Write-Host "[*] Creando acceso directo en el Inicio de Windows..."
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $ExeTarget
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.IconLocation = "$InstallDir\W.ico"
$Shortcut.Description = "Inicia WallpaperRandomizer en segundo plano."
$Shortcut.Save()

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host " Instalacion Completada con Exito!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "- El programa esta instalado en: $InstallDir"
Write-Host "- Arrancara automaticamente al iniciar Windows."
Write-Host ""
Write-Host "Deseas iniciar el programa ahora mismo? (S/N)" -NoNewline
$resp = Read-Host
if ($resp -eq 'S' -or $resp -eq 's') {
    Start-Process -FilePath $ExeTarget -WorkingDirectory $InstallDir
    Write-Host "Iniciando..." -ForegroundColor Green
} else {
    Write-Host "Puedes iniciarlo reiniciando tu PC o abriendolo desde la carpeta de instalacion."
}

Pause
