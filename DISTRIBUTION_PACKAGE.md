# Distribution Package Guide

## What You Have

After building the executable, you have:
- **Windows**: `dist/ImageFetcherBot.exe` (24 MB)
- **macOS**: `dist/ImageFetcherBot` (built on Mac)

## Creating a Distribution Package

### For Windows Users

Create a folder structure like this for distribution:

```
ImageFetcherBot-Windows/
├── ImageFetcherBot.exe          # The executable (24 MB)
├── config/                      # Configuration folder
│   └── config.yaml
├── .env.example                 # Template for credentials
├── README.txt                   # Quick start guide
├── images/                      # Empty folder for user's images
│   └── README.md
└── sample_skus.txt              # Example SKU file
```

### For macOS Users

Same structure, different executable:

```
ImageFetcherBot-macOS/
├── ImageFetcherBot              # The executable (built on Mac)
├── config/
│   └── config.yaml
├── .env.example
├── README.txt
├── images/
│   └── README.md
└── sample_skus.txt
```

## Step-by-Step Package Creation

### Windows Package

```bash
# Create distribution folder
cd fetchimage
mkdir ImageFetcherBot-Windows
cd ImageFetcherBot-Windows

# Copy executable
copy ..\dist\ImageFetcherBot.exe .

# Copy config
xcopy ..\config config\ /E /I

# Copy .env template
copy ..\.env.example .

# Create empty folders
mkdir images
mkdir data
mkdir logs
mkdir reports

# Copy images README
copy ..\images\README.md images\

# Create sample SKU file
echo 005692548366 > sample_skus.txt
echo 5056716406853 >> sample_skus.txt
```

Create `README.txt`:

```
Image Fetcher Bot - Quick Start Guide
======================================

SETUP (5 minutes):

1. Configure Credentials
   ------------------------
   - Rename .env.example to .env
   - Open .env in Notepad
   - Add your Replit credentials:
     * REPLIT_EMAIL=your_email@example.com
     * REPLIT_PASSWORD=your_password
   - Save and close

2. Add Product Images
   -------------------
   - Place images in the images\ folder
   - Filename must match SKU code (without extension)
   - Example: images\SKU12345.jpg
   - Supported: .jpg, .png, .gif, .webp

3. Create SKU List
   ----------------
   - Create a text file: my_skus.txt
   - Add one SKU per line
   - Example:
     005692548366
     5056716406853

USAGE:

Run Once:
---------
Double-click ImageFetcherBot.exe

OR use Command Prompt:
ImageFetcherBot.exe --run-once --sku-file my_skus.txt

Scheduled (every 6 hours):
--------------------------
ImageFetcherBot.exe --interval 6

CHECK RESULTS:

- Logs: logs\app.log
- Reports: reports\ folder
- Database: data\state.db

IMAGES FOLDER LOCATION:

The images\ folder should be in the SAME folder as the executable:

ImageFetcherBot-Windows\
├── ImageFetcherBot.exe
├── images\              ← Put images here
│   ├── SKU001.jpg
│   └── SKU002.png
└── ...

Configuration in .env:
LOCAL_IMAGES_FOLDER=./images

For more details, see the GitHub repository:
https://github.com/samvaio00/fetchimage
```

### macOS Package

```bash
# Create distribution folder
cd fetchimage
mkdir ImageFetcherBot-macOS
cd ImageFetcherBot-macOS

# Copy executable
cp ../dist/ImageFetcherBot .
chmod +x ImageFetcherBot

# Copy config
cp -r ../config .

# Copy .env template
cp ../.env.example .

# Create empty folders
mkdir -p images data logs reports

# Copy images README
cp ../images/README.md images/

# Create sample SKU file
cat > sample_skus.txt <<EOF
005692548366
5056716406853
EOF
```

Create `README.txt` with macOS-specific commands.

## Zipping the Package

### Windows

```bash
# Right-click folder → Send to → Compressed (zipped) folder
# OR use PowerShell:
Compress-Archive -Path ImageFetcherBot-Windows -DestinationPath ImageFetcherBot-Windows.zip
```

### macOS

```bash
zip -r ImageFetcherBot-macOS.zip ImageFetcherBot-macOS/
```

## What Users Need to Do

### First Time Setup

1. **Unzip** the package
2. **Edit** `.env` with their Replit credentials
3. **Add** their product images to `images/` folder
4. **Create** a SKU list file
5. **Run** the executable

### Running the Bot

**Windows:**
- Double-click `ImageFetcherBot.exe`
- Or command: `ImageFetcherBot.exe --run-once --sku-file my_skus.txt`

**macOS:**
- Open Terminal
- Navigate to folder: `cd /path/to/ImageFetcherBot-macOS`
- Run: `./ImageFetcherBot --run-once --sku-file my_skus.txt`

## File Size Considerations

### Executable Size

- **Windows .exe**: ~24 MB
- **macOS**: ~25-30 MB (estimate, built on Mac)

### ZIP Package Size

- With executable + config + docs: ~25-30 MB
- Users need ~100 MB total space (including images, database, logs)

### Why So Large?

The executable includes:
- Python interpreter (~15 MB)
- All Python libraries (requests, Pillow, etc.)
- Application code

This is normal for PyInstaller executables and allows users to run without installing Python.

## Distribution Methods

### Option 1: GitHub Releases

1. Go to your GitHub repo
2. Click "Releases" → "Create a new release"
3. Tag: `v1.0.0`
4. Upload:
   - `ImageFetcherBot-Windows.zip`
   - `ImageFetcherBot-macOS.zip` (build on Mac first)
5. Add release notes
6. Publish

Users download from: `https://github.com/samvaio00/fetchimage/releases`

### Option 2: Direct Distribution

- Email the ZIP file
- Share via Google Drive / Dropbox
- Host on your own server

### Option 3: Installer (Advanced)

**Windows - Inno Setup:**
- Create a proper installer
- Adds Start Menu shortcuts
- Professional appearance
- ~30 MB installer

**macOS - DMG:**
- Create a disk image
- Drag-and-drop installation
- ~30 MB DMG file

## Security Notes

### For Users

- **Never commit .env** - Contains passwords
- **Scan with antivirus** - Some may flag PyInstaller executables (false positive)
- **Download from trusted source** - Official GitHub releases

### For Distributors

- **Code sign** (optional but recommended):
  - Removes "Unknown Publisher" warning
  - Reduces antivirus false positives
  - Requires certificate (~$100-300/year)

- **Provide checksums**:
  ```bash
  # Windows
  certutil -hashfile ImageFetcherBot-Windows.zip SHA256

  # macOS
  shasum -a 256 ImageFetcherBot-macOS.zip
  ```

## Updating the Executable

When you make code changes:

1. Update version in code
2. Rebuild executable
3. Test thoroughly
4. Create new release (v1.1.0, v1.2.0, etc.)
5. Provide changelog

## Troubleshooting for Users

### Windows: "Windows protected your PC"

**Cause:** Unsigned executable

**Solution:**
1. Click "More info"
2. Click "Run anyway"

Or: Code sign the executable

### macOS: "Cannot be opened because the developer cannot be verified"

**Cause:** Unsigned executable, Gatekeeper protection

**Solution:**
1. Right-click executable → Open
2. Click "Open" in dialog

Or: Code sign and notarize

### Antivirus Blocks Executable

**Cause:** False positive (common with PyInstaller)

**Solutions:**
1. Add exception to antivirus
2. Download from official GitHub releases
3. Verify checksum
4. Code sign the executable (reduces false positives)

### "Config file not found"

**Cause:** Missing config/ folder or wrong location

**Solution:**
- Ensure config/ folder is next to executable
- Check folder structure matches distribution guide

## Summary

### Package Contents

✅ Executable (ImageFetcherBot.exe or ImageFetcherBot)
✅ config/ folder with config.yaml
✅ .env.example template
✅ README.txt with instructions
✅ Empty images/ folder with README
✅ Sample SKU file

### Distribution Size

- ZIP package: ~25-30 MB
- Uncompressed: ~30-40 MB
- With user data: ~100 MB (varies by image count)

### User Requirements

- Windows 10+ or macOS 10.13+
- ~100 MB disk space
- Internet connection (for Replit upload)
- Replit WholesaleHub credentials

### Next Steps

1. Build executable on both platforms
2. Create distribution packages
3. Test on clean machine
4. Upload to GitHub Releases
5. Share with users

For technical details, see:
- `BUILD_EXECUTABLE.md` - Building instructions
- `DEPLOYMENT.md` - Full deployment guide
- `LOCAL_IMAGES_GUIDE.md` - Usage guide
