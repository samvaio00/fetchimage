# Creating GitHub Releases

## What Are GitHub Releases?

GitHub Releases let you distribute compiled executables and packages to users without bloating your git repository. Perfect for distributing your Windows and macOS executables.

## Benefits

✅ **Separate from repository** - Doesn't bloat git history
✅ **Version tagging** - v1.0.0, v1.1.0, v2.0.0
✅ **Release notes** - Describe changes
✅ **Download statistics** - Track usage
✅ **Multiple files** - Windows .zip, macOS .zip, source code
✅ **Large file support** - Up to 2GB per file

## File Size Limits

- **Per file:** 2GB maximum (your 24MB .exe is fine!)
- **Per release:** Unlimited number of files
- **Repository:** Releases don't count toward repo size

## Step-by-Step: Creating Your First Release

### Step 1: Prepare Distribution Packages

**Windows Package:**

```bash
cd fetchimage

# Create distribution folder
mkdir -p releases/ImageFetcherBot-Windows-v1.0.0
cd releases/ImageFetcherBot-Windows-v1.0.0

# Copy executable
cp ../../dist/ImageFetcherBot.exe .

# Copy required files
cp -r ../../config .
cp ../../.env.example .env.example
mkdir -p images data logs reports
cp ../../images/README.md images/

# Create user guide
cat > README.txt <<'EOF'
Image Fetcher Bot v1.0.0
========================

QUICK START:

1. Rename .env.example to .env
2. Edit .env with your Replit credentials
3. Place product images in images/ folder (filename = SKU code)
4. Create SKU list file: my_skus.txt
5. Run: ImageFetcherBot.exe --run-once --sku-file my_skus.txt

For detailed instructions: https://github.com/samvaio00/fetchimage

IMAGES FOLDER:
Place images in the images/ folder next to this executable.
In .env: LOCAL_IMAGES_FOLDER=./images
EOF

# Go back and zip
cd ..
powershell Compress-Archive -Path ImageFetcherBot-Windows-v1.0.0 -DestinationPath ImageFetcherBot-Windows-v1.0.0.zip
```

**macOS Package (build on Mac):**

```bash
cd fetchimage

# Create distribution folder
mkdir -p releases/ImageFetcherBot-macOS-v1.0.0
cd releases/ImageFetcherBot-macOS-v1.0.0

# Copy executable
cp ../../dist/ImageFetcherBot .
chmod +x ImageFetcherBot

# Copy required files
cp -r ../../config .
cp ../../.env.example .
mkdir -p images data logs reports
cp ../../images/README.md images/

# Create user guide
cat > README.txt <<'EOF'
Image Fetcher Bot v1.0.0
========================

QUICK START:

1. Rename .env.example to .env
2. Edit .env with your Replit credentials
3. Place product images in images/ folder (filename = SKU code)
4. Create SKU list file: my_skus.txt
5. Open Terminal, navigate here
6. Run: ./ImageFetcherBot --run-once --sku-file my_skus.txt

For detailed instructions: https://github.com/samvaio00/fetchimage

IMAGES FOLDER:
Place images in the images/ folder next to this executable.
In .env: LOCAL_IMAGES_FOLDER=./images
EOF

# Go back and zip
cd ..
zip -r ImageFetcherBot-macOS-v1.0.0.zip ImageFetcherBot-macOS-v1.0.0/
```

### Step 2: Generate Checksums (Optional but Recommended)

**Windows (PowerShell):**
```powershell
Get-FileHash ImageFetcherBot-Windows-v1.0.0.zip -Algorithm SHA256 | Format-List
```

**macOS/Linux:**
```bash
shasum -a 256 ImageFetcherBot-macOS-v1.0.0.zip
```

Save these checksums for the release notes.

### Step 3: Create Release on GitHub

#### Option A: Web Interface (Easiest)

1. **Go to your repository:**
   - Navigate to: https://github.com/samvaio00/fetchimage

2. **Click "Releases":**
   - On right sidebar, click "Releases" (or "Create a new release")
   - Or go directly to: https://github.com/samvaio00/fetchimage/releases/new

3. **Create a new release:**
   - Click "Draft a new release"

4. **Choose a tag:**
   - Click "Choose a tag"
   - Type: `v1.0.0`
   - Click "Create new tag: v1.0.0 on publish"

5. **Fill in release details:**

   **Release title:**
   ```
   Image Fetcher Bot v1.0.0
   ```

   **Description (example):**
   ```markdown
   ## 🎉 First Official Release - Local Image Matching

   ### Features
   - ✅ **Local Image Matching**: Match images by filename = SKU code
   - ✅ **Standalone Executables**: No Python installation required
   - ✅ **Duplicate Prevention**: Automatically skips processed SKUs
   - ✅ **Image Validation**: Format, size, and dimension checks
   - ✅ **Comprehensive Logging**: Track all operations

   ### Download

   Choose your platform:
   - **Windows**: Download `ImageFetcherBot-Windows-v1.0.0.zip`
   - **macOS**: Download `ImageFetcherBot-macOS-v1.0.0.zip`

   Extract and follow the README.txt inside for setup instructions.

   ### Requirements
   - Replit WholesaleHub account credentials
   - Product images (filename = SKU code)
   - ~100MB disk space

   ### Images Folder Location
   Place your product images in the `images/` folder next to the executable.
   Set in `.env`: `LOCAL_IMAGES_FOLDER=./images`

   ### Quick Start
   1. Extract the ZIP file
   2. Rename `.env.example` to `.env`
   3. Add your Replit credentials to `.env`
   4. Place images in `images/` folder
   5. Create SKU list: `my_skus.txt`
   6. Run the executable

   ### Documentation
   - [Complete Guide](https://github.com/samvaio00/fetchimage#readme)
   - [Local Images Guide](https://github.com/samvaio00/fetchimage/blob/main/LOCAL_IMAGES_GUIDE.md)
   - [Deployment Guide](https://github.com/samvaio00/fetchimage/blob/main/DEPLOYMENT.md)
   - [Images Folder Location](https://github.com/samvaio00/fetchimage/blob/main/IMAGES_FOLDER_LOCATION.md)

   ### Checksums (SHA256)
   ```
   Windows: [paste checksum here]
   macOS:   [paste checksum here]
   ```

   ### What's Changed
   - Local image matching by SKU filename
   - Windows and macOS standalone executables
   - Comprehensive documentation
   - Tested with 9 successful uploads

   **Full Changelog**: https://github.com/samvaio00/fetchimage/commits/v1.0.0
   ```

6. **Attach files:**
   - Drag and drop or click "Attach binaries..."
   - Upload: `ImageFetcherBot-Windows-v1.0.0.zip`
   - Upload: `ImageFetcherBot-macOS-v1.0.0.zip` (when built)

7. **Publish:**
   - Check "Set as the latest release" ✓
   - Click "Publish release"

#### Option B: GitHub CLI (Advanced)

```bash
# Install GitHub CLI first: https://cli.github.com/

# Authenticate
gh auth login

# Create release
gh release create v1.0.0 \
  --title "Image Fetcher Bot v1.0.0" \
  --notes-file release-notes.md \
  releases/ImageFetcherBot-Windows-v1.0.0.zip \
  releases/ImageFetcherBot-macOS-v1.0.0.zip
```

### Step 4: Verify Release

1. Go to: https://github.com/samvaio00/fetchimage/releases
2. You should see your v1.0.0 release
3. Test downloading and extracting
4. Verify checksums match

## What Users Will See

Users visiting your releases page will see:

```
samvaio00/fetchimage
Releases

v1.0.0 - Latest
Image Fetcher Bot v1.0.0
Released on Feb 12, 2026

[Release notes here]

Assets
📦 ImageFetcherBot-Windows-v1.0.0.zip    25.4 MB
📦 ImageFetcherBot-macOS-v1.0.0.zip      26.1 MB
📄 Source code (zip)
📄 Source code (tar.gz)

Downloads: [count shown here]
```

## Version Numbering

Use **Semantic Versioning** (semver):

- **v1.0.0** - Major.Minor.Patch
- **v1.0.1** - Bug fix (backward compatible)
- **v1.1.0** - New feature (backward compatible)
- **v2.0.0** - Breaking change

Examples:
- v1.0.0 - Initial release
- v1.0.1 - Fixed validation bug
- v1.1.0 - Added batch processing
- v2.0.0 - Changed config format (breaking)

## Updating Releases

### For Bug Fixes (v1.0.1)

1. Fix bug in code
2. Commit and push
3. Rebuild executables
4. Create new release: v1.0.1
5. Upload new packages
6. Describe fixes in release notes

### For Features (v1.1.0)

1. Add feature to code
2. Test thoroughly
3. Update documentation
4. Rebuild executables
5. Create new release: v1.1.0
6. Highlight new features

## Best Practices

### DO ✅

- ✅ Use semantic versioning (v1.0.0)
- ✅ Write detailed release notes
- ✅ Include checksums
- ✅ Test before releasing
- ✅ Provide README.txt in package
- ✅ Keep executables out of git repo

### DON'T ❌

- ❌ Commit executables to repository
- ❌ Skip version tags
- ❌ Forget checksums
- ❌ Release without testing
- ❌ Use vague release notes
- ❌ Delete old releases (users may depend on them)

## File Organization

Your repository should look like:

```
fetchimage/                      # Git repository
├── src/                         # Source code
├── config/
├── docs/
├── .gitignore                   # Excludes dist/, build/, releases/
├── README.md
└── ...

dist/                            # Local only (in .gitignore)
├── ImageFetcherBot.exe          # Built locally

build/                           # Local only (in .gitignore)
└── ...                          # PyInstaller build files

releases/                        # Local only (in .gitignore)
├── ImageFetcherBot-Windows-v1.0.0/
│   ├── ImageFetcherBot.exe
│   ├── config/
│   └── ...
└── ImageFetcherBot-Windows-v1.0.0.zip  # Upload to GitHub Releases
```

The `dist/`, `build/`, and `releases/` folders should be in `.gitignore`.

## .gitignore Setup

Ensure these are in your `.gitignore`:

```gitignore
# Build artifacts
dist/
build/
*.spec

# PyInstaller
*.manifest
*.exe
*.app

# Distribution packages
releases/
*.zip
*.tar.gz

# Python
__pycache__/
*.pyc
```

This keeps binaries out of git while allowing GitHub Releases distribution.

## Automation with GitHub Actions

You can automate building and releasing:

`.github/workflows/release.yml`:

```yaml
name: Create Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-and-release:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest]

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller

      - name: Build executable
        run: |
          pyinstaller --clean --onefile --name ImageFetcherBot \
            --add-data "config:config" src/main.py

      - name: Create package
        run: |
          mkdir package
          cp dist/ImageFetcherBot* package/
          cp -r config package/
          cp .env.example package/

      - name: Upload to release
        uses: softprops/action-gh-release@v1
        with:
          files: package/*
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Then just push a tag to trigger:
```bash
git tag v1.0.0
git push origin v1.0.0
```

## Linking from README

Add a download section to your README.md:

```markdown
## Download

### Pre-built Executables

Download the latest release:

**[📦 Download for Windows](https://github.com/samvaio00/fetchimage/releases/latest/download/ImageFetcherBot-Windows-v1.0.0.zip)**

**[📦 Download for macOS](https://github.com/samvaio00/fetchimage/releases/latest/download/ImageFetcherBot-macOS-v1.0.0.zip)**

Or view all releases: [Releases Page](https://github.com/samvaio00/fetchimage/releases)

### Build from Source

See [BUILD_EXECUTABLE.md](BUILD_EXECUTABLE.md) for build instructions.
```

## Summary

### GitHub Releases: YES ✅
- Upload executables to Releases
- Perfect for distribution
- No repository bloat

### Git Repository: NO ❌
- Don't commit executables
- Keep repo clean
- Source code only

### Your Next Steps

1. **Build macOS version** (on Mac when available)
2. **Create distribution packages** (both platforms)
3. **Generate checksums**
4. **Create v1.0.0 release** on GitHub
5. **Upload packages** to release
6. **Update README** with download links
7. **Share with users!**

Your 24MB Windows .exe is perfect for GitHub Releases! 🎉
