@echo off
REM Build script for Windows executable

echo Installing build dependencies...
pip install -r requirements-build.txt

echo Building Windows executable...
pyinstaller --clean ^
    --onefile ^
    --name ImageFetcherBot ^
    --add-data "config;config" ^
    --hidden-import=src.api.replit_client ^
    --hidden-import=src.services.local_image_service ^
    --hidden-import=src.services.sku_processor ^
    --hidden-import=src.storage.state_manager ^
    --hidden-import=src.utils.config ^
    --hidden-import=src.utils.logger ^
    --hidden-import=PIL._tkinter_finder ^
    --icon=NONE ^
    src/main.py

echo.
echo Build complete! Executable is in: dist\ImageFetcherBot.exe
echo.
echo IMPORTANT: Copy these items to the same folder as the .exe:
echo   1. config\ folder
echo   2. .env file (with your credentials)
echo   3. images\ folder (for your product images)
echo   4. Create data\ and logs\ folders
echo.
pause
