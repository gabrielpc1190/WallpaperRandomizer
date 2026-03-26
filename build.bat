@echo off
echo =======================================
echo Compilando WallpaperRandomizer a EXE...
echo =======================================

echo Instalando PyInstaller...
pip install pyinstaller

echo Empaquetando la aplicacion...
REM --noconsole: Evita que aparezca una ventana de CMD al ejecutar
REM --onefile: Agrupa todo en un solo ejecutable .exe
REM --icon: Aplica el icono nativo
REM --add-data: Asegura que el icono original este disponible internamente para pystray
pyinstaller --noconsole --onefile --icon=W.ico --add-data "W.ico;." main.py

echo.
echo Proceso de compilacion completado.
echo Tu archivo compilado se encuentra en la carpeta "dist\main.exe".
echo Puedes renombrarlo a "WallpaperRandomizer.exe".
pause
