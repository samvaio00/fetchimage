# Building Executables

This guide explains how to create standalone executables for Windows and macOS.

## Overview

The build process creates a single executable file that includes:
- Python interpreter
- All dependencies
- Application code

**Note:** Cross-compilation is NOT supported. You must build on the target platform:
- Build Windows `.exe` on Windows
- Build macOS executable on macOS

## Prerequisites

### Windows
- Python 3.8+ installed
- Git Bash or Command Prompt
- Virtual environment activated

### macOS
- Python 3.8+ installed
- Xcode Command Line Tools: `xcode-select --install`
- Virtual environment activated

## Building on Windows

### Step 1: Activate Virtual Environment

```bash
cd fetchimage
venv\Scripts\activate
```

### Step 2: Run Build Script

```bash
build_windows.bat
```

Or manually:
```bash
pip install -r requirements-build.txt
pyinstaller --clean --onefile --name ImageFetcherBot --add-data "config;config" src/main.py
```

### Step 3: Find Your Executable

Location: `dist\ImageFetcherBot.exe`

**File size:** Approximately 50-70 MB (includes Python + all libraries)

## Building on macOS

### Step 1: Activate Virtual Environment

```bash
cd fetchimage
source venv/bin/activate
```

### Step 2: Run Build Script

```bash
./build_mac.sh
```

Or manually:
```bash
pip install -r requirements-build.txt
pyinstaller --clean --onefile --name ImageFetcherBot --add-data "config:config" src/main.py
```

### Step 3: Find Your Executable

Location: `dist/ImageFetcherBot`

**File size:** Approximately 50-70 MB

### Step 4: Make it Executable (if needed)

```bash
chmod +x dist/ImageFetcherBot
```

## Distributing the Executable

### Required Files Structure

When distributing to other computers, package these files together:

```
ImageFetcherBot/               # Folder to distribute
├── ImageFetcherBot.exe        # Windows executable
│   OR
├── ImageFetcherBot            # macOS executable
├── config/                    # Configuration folder
│   └── config.yaml
├── .env.example               # Template (user fills in credentials)
├── images/                    # Empty folder for images
│   └── README.md
├── data/                      # Empty folder (created automatically)
├── logs/                      # Empty folder (created automatically)
├── reports/                   # Empty folder (created automatically)
└── README.txt                 # Usage instructions
```

### Setup Instructions for End Users

Create a `README.txt` file:

```
Image Fetcher Bot - Setup Instructions
======================================

1. CONFIGURATION
   - Copy .env.example to .env
   - Edit .env with your Replit credentials:
     * REPLIT_EMAIL=your_email@example.com
     * REPLIT_PASSWORD=your_password

2. ADD IMAGES
   - Place product images in the images/ folder
   - Filename (without extension) must match SKU code
   - Example: images/SKU12345.jpg

3. CREATE SKU FILE
   - Create a text file with SKU codes (one per line)
   - Example: my_skus.txt

4. RUN THE APPLICATION

   Windows:
   --------
   Double-click ImageFetcherBot.exe
   OR
   Open Command Prompt:
   ImageFetcherBot.exe --run-once --sku-file my_skus.txt

   macOS:
   ------
   Open Terminal:
   ./ImageFetcherBot --run-once --sku-file my_skus.txt

5. CHECK RESULTS
   - View logs in logs/app.log
   - Check reports/ folder for any issues
   - Database tracking in data/state.db

SUPPORT
-------
See DEPLOYMENT.md for detailed instructions
See LOCAL_IMAGES_GUIDE.md for comprehensive usage guide
```

## Important Notes

### Configuration Files

The executable needs these configuration files at runtime:

1. **config/config.yaml** - Application settings
   - Bundled with executable using `--add-data`
   - Contains validation rules, batch size, etc.

2. **.env** - User credentials and paths
   - NOT bundled (contains sensitive data)
   - User must create from .env.example

### Relative Paths

The executable uses its own directory as the working directory:

```
# If executable is at: C:\MyApp\ImageFetcherBot.exe
# Then paths resolve as:
./images      → C:\MyApp\images
./data        → C:\MyApp\data
./logs        → C:\MyApp\logs
```

### Database and Logs

These are created automatically on first run:
- `data/state.db` - SQLite database
- `logs/app.log` - Application logs
- `reports/` - Processing reports

## Testing the Executable

### Windows Testing

```bash
# Navigate to dist folder
cd dist

# Create required folders
mkdir images data logs reports

# Copy config
xcopy ..\config config\ /E /I

# Create .env
copy ..\env.example .env
notepad .env

# Create test SKU file
echo 005692548366 > test_skus.txt

# Add test image
copy ..\images\005692548366.jpg images\

# Run executable
ImageFetcherBot.exe --run-once --sku-file test_skus.txt
```

### macOS Testing

```bash
# Navigate to dist folder
cd dist

# Create required folders
mkdir -p images data logs reports

# Copy config
cp -r ../config .

# Create .env
cp ../.env.example .env
nano .env

# Create test SKU file
echo "005692548366" > test_skus.txt

# Add test image
cp ../images/005692548366.jpg images/

# Run executable
./ImageFetcherBot --run-once --sku-file test_skus.txt
```

## Troubleshooting Build Issues

### "Module not found" Error

**Problem:** PyInstaller didn't include a required module

**Solution:** Add to build script with `--hidden-import`:
```bash
--hidden-import=missing.module.name
```

### "config/config.yaml not found"

**Problem:** Config folder not bundled correctly

**Solution:** Check `--add-data` parameter:
- Windows: `--add-data "config;config"`
- macOS/Linux: `--add-data "config:config"`

### Executable is Too Large

**Problem:** Executable is 100+ MB

**Solutions:**
1. Use `--exclude-module` for unused packages:
   ```bash
   --exclude-module=matplotlib
   --exclude-module=pandas
   ```

2. Use UPX compression (Windows):
   ```bash
   pip install pyinstaller[compression]
   pyinstaller --onefile --upx-dir=C:\path\to\upx ...
   ```

### "Permission Denied" on macOS

**Problem:** Executable not marked as executable

**Solution:**
```bash
chmod +x dist/ImageFetcherBot
```

If Gatekeeper blocks it:
```bash
xattr -d com.apple.quarantine dist/ImageFetcherBot
```

### Antivirus False Positive (Windows)

**Problem:** Antivirus flags executable as malware

**Why:** PyInstaller executables sometimes trigger false positives

**Solutions:**
1. Add exception to antivirus
2. Sign the executable with a code signing certificate
3. Build with specific PyInstaller version known to work
4. Submit to antivirus vendor as false positive

## Code Signing (Optional but Recommended)

### Windows Code Signing

Requires a code signing certificate:

```bash
# Sign with signtool (Windows SDK)
signtool sign /f mycert.pfx /p password /t http://timestamp.digicert.com dist\ImageFetcherBot.exe
```

**Benefits:**
- Removes "Unknown Publisher" warning
- Reduces antivirus false positives
- Builds user trust

### macOS Code Signing

Requires Apple Developer account:

```bash
# Sign the executable
codesign --force --sign "Developer ID Application: Your Name" dist/ImageFetcherBot

# Verify signature
codesign --verify --verbose dist/ImageFetcherBot

# Notarize for Gatekeeper
xcrun notarytool submit dist/ImageFetcherBot.zip --apple-id your@email.com --wait
```

## Advanced: Creating an Installer

### Windows - Inno Setup

Create `installer.iss`:

```iss
[Setup]
AppName=Image Fetcher Bot
AppVersion=1.0
DefaultDirName={pf}\ImageFetcherBot
DefaultGroupName=Image Fetcher Bot
OutputDir=installers
OutputBaseFilename=ImageFetcherBot-Setup

[Files]
Source: "dist\ImageFetcherBot.exe"; DestDir: "{app}"
Source: "config\*"; DestDir: "{app}\config"; Flags: recursesubdirs
Source: ".env.example"; DestDir: "{app}"
Source: "images\README.md"; DestDir: "{app}\images"

[Icons]
Name: "{group}\Image Fetcher Bot"; Filename: "{app}\ImageFetcherBot.exe"
```

Compile with Inno Setup Compiler.

### macOS - DMG

```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
  --volname "ImageFetcherBot" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --app-drop-link 450 185 \
  ImageFetcherBot.dmg \
  dist/
```

## CI/CD Automation

### GitHub Actions Example

`.github/workflows/build.yml`:

```yaml
name: Build Executables

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          pip install -r requirements.txt
          pip install -r requirements-build.txt
          pyinstaller --clean --onefile --name ImageFetcherBot --add-data "config;config" src/main.py
      - uses: actions/upload-artifact@v3
        with:
          name: ImageFetcherBot-Windows
          path: dist/ImageFetcherBot.exe

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          pip install -r requirements.txt
          pip install -r requirements-build.txt
          pyinstaller --clean --onefile --name ImageFetcherBot --add-data "config:config" src/main.py
      - uses: actions/upload-artifact@v3
        with:
          name: ImageFetcherBot-macOS
          path: dist/ImageFetcherBot
```

## Summary

### Build Commands

**Windows:**
```bash
build_windows.bat
```

**macOS:**
```bash
./build_mac.sh
```

### Output Locations

- Windows: `dist\ImageFetcherBot.exe`
- macOS: `dist/ImageFetcherBot`

### Distribution Checklist

- [ ] Executable built and tested
- [ ] config/ folder included
- [ ] .env.example provided
- [ ] README.txt with setup instructions
- [ ] Empty images/, data/, logs/ folders created
- [ ] Tested on clean machine
- [ ] (Optional) Code signed
- [ ] (Optional) Installer created

### Next Steps

1. Build executable on target platform
2. Test thoroughly
3. Package with required files
4. Distribute to users
5. Provide setup instructions

For detailed deployment instructions, see `DEPLOYMENT.md`.
