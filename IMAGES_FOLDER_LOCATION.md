# Images Folder Location Guide

## Where to Place the Images Folder

The `images/` folder location depends on how you configure the `LOCAL_IMAGES_FOLDER` setting in your `.env` file.

## Option 1: Relative Path (Recommended)

**Location:** Same directory as the application

```
fetchimage/
├── images/           ← Images folder here
│   ├── SKU001.jpg
│   ├── SKU002.png
│   └── ...
├── src/
├── config/
├── .env
└── ...
```

**Configuration in `.env`:**
```env
LOCAL_IMAGES_FOLDER=./images
```

**Why this is recommended:**
- Easy to manage
- Portable (works on any computer)
- Clear project structure
- Works with both Windows and Linux/Mac

## Option 2: Absolute Path

**Location:** Anywhere on your computer

**Windows Examples:**
```
C:\ProductImages\
D:\Images\Products\
\\NetworkDrive\Images\
```

**Linux/Mac Examples:**
```
/home/user/product-images/
/var/www/images/
/mnt/shared/images/
```

**Configuration in `.env`:**

Windows:
```env
LOCAL_IMAGES_FOLDER=C:\ProductImages
```

Linux/Mac:
```env
LOCAL_IMAGES_FOLDER=/home/user/product-images
```

**When to use absolute paths:**
- Images stored on separate drive
- Shared network location
- Multiple applications using same images
- Large image library (separate storage)

## On Different Computers

### Scenario 1: Moving to Another Computer (Relative Path)

If you're using `LOCAL_IMAGES_FOLDER=./images`, simply:

1. Copy entire `fetchimage/` folder to new computer
2. Images folder moves with it
3. No configuration changes needed

```
Old Computer:              New Computer:
C:\App\fetchimage\        D:\MyApps\fetchimage\
├── images/        →      ├── images/
├── src/                  ├── src/
└── .env                  └── .env
```

### Scenario 2: Moving to Another Computer (Absolute Path)

If you're using an absolute path like `C:\ProductImages`:

1. Copy `fetchimage/` folder to new computer
2. Copy `images/` folder to new location
3. Update `.env` with new absolute path

```
Old Computer:                    New Computer:
C:\App\fetchimage\              /home/user/fetchimage/
└── .env (LOCAL_IMAGES_        └── .env (LOCAL_IMAGES_
    FOLDER=C:\ProductImages)        FOLDER=/home/user/images)

C:\ProductImages\       →       /home/user/images/
├── SKU001.jpg                  ├── SKU001.jpg
└── ...                         └── ...
```

### Scenario 3: Shared Network Environment

Multiple computers accessing same images:

```
Computer A:
LOCAL_IMAGES_FOLDER=\\FileServer\ProductImages

Computer B:
LOCAL_IMAGES_FOLDER=\\FileServer\ProductImages

File Server:
\\FileServer\ProductImages\
├── SKU001.jpg
├── SKU002.png
└── ...
```

**Benefits:**
- Single source of truth for images
- All computers use same images
- Easy to update images centrally

## Executable vs Source Code

### Running from Source Code

When running with Python:
```bash
python -m src.main --run-once --sku-file my_skus.txt
```

The images folder is relative to the **current working directory** (where you run the command).

**Example:**
```
C:\Apps\fetchimage\
├── images/              ← Relative path: ./images
├── src/
└── .env
```

Run from:
```bash
cd C:\Apps\fetchimage
python -m src.main ...
```

### If You Create an Executable (PyInstaller)

If you package the app as `.exe`:

```
MyApp.exe location:         C:\Program Files\ImageFetcher\
Relative images path:       C:\Program Files\ImageFetcher\images\
```

**Configuration:**
```env
# Relative - next to executable
LOCAL_IMAGES_FOLDER=./images

# Or absolute - anywhere
LOCAL_IMAGES_FOLDER=C:\Users\YourName\Documents\ProductImages
```

## Path Formats

### Windows

**Relative:**
```env
LOCAL_IMAGES_FOLDER=./images
LOCAL_IMAGES_FOLDER=.\images
```

**Absolute:**
```env
LOCAL_IMAGES_FOLDER=C:\ProductImages
LOCAL_IMAGES_FOLDER=C:/ProductImages      # Also works
LOCAL_IMAGES_FOLDER=D:\Images\Products
```

**Network:**
```env
LOCAL_IMAGES_FOLDER=\\Server\Share\Images
LOCAL_IMAGES_FOLDER=Z:\Images             # Mapped drive
```

### Linux/Mac

**Relative:**
```env
LOCAL_IMAGES_FOLDER=./images
```

**Absolute:**
```env
LOCAL_IMAGES_FOLDER=/home/user/images
LOCAL_IMAGES_FOLDER=/var/www/product-images
LOCAL_IMAGES_FOLDER=/mnt/storage/images
```

**Network (NFS/SMB):**
```env
LOCAL_IMAGES_FOLDER=/mnt/network/images
```

## Troubleshooting

### "Images folder does not exist"

**Problem:** Bot can't find the images folder

**Check:**
1. Is the path in `.env` correct?
2. Does the folder actually exist?
3. Are you running from the correct directory?

**Solutions:**
```bash
# Verify folder exists
ls ./images              # Linux/Mac
dir .\images             # Windows

# Use absolute path instead
LOCAL_IMAGES_FOLDER=C:\Full\Path\To\Images

# Check current directory
pwd                      # Linux/Mac
cd                       # Windows
```

### Images Not Found After Moving

**Problem:** Moved app to new computer, images not found

**Solutions:**
1. If using relative path `./images`, ensure images folder moved too
2. If using absolute path, update `.env` with new path
3. Verify folder structure is intact

## Best Practices

### ✅ Recommended Setup

For most users:
```
fetchimage/
├── images/              ← Put images here
├── src/
├── .env                 ← LOCAL_IMAGES_FOLDER=./images
└── ...
```

**Advantages:**
- Self-contained
- Easy to backup
- Portable
- Simple

### ⚠️ Advanced Setup

For large deployments:
```
Shared Storage:
/mnt/storage/product-images/

Application Servers:
Server1: LOCAL_IMAGES_FOLDER=/mnt/storage/product-images
Server2: LOCAL_IMAGES_FOLDER=/mnt/storage/product-images
```

**Use when:**
- Hundreds/thousands of images
- Multiple instances of bot
- Centralized image management
- Need separate backup strategy

## Summary

**Quick Answer:**
Place the `images/` folder **in the same directory** as the fetchimage application and use:

```env
LOCAL_IMAGES_FOLDER=./images
```

This works on any computer without changes!

**For other locations:**
Use an absolute path in `.env` pointing to wherever your images are stored.
