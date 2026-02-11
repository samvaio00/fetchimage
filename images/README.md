# Local Images Folder

This folder is used for storing product images that will be matched and uploaded to SKUs based on filename.

## How It Works

1. **Filename = SKU Code**: Each image filename (without extension) should match the SKU code exactly.
   - Example: `ABC123.jpg` will be matched to SKU `ABC123`
   - Matching is **case-insensitive**: `abc123.png` also matches SKU `ABC123`

2. **Supported Formats**:
   - `.jpg` / `.jpeg`
   - `.png`
   - `.gif`
   - `.webp`

3. **Image Requirements**:
   - Minimum dimensions: 800x600 pixels
   - Maximum file size: 10MB (Replit limit)
   - Aspect ratio: 0.5 to 2.0

## Usage

### Step 1: Add Images
Place your product images in this folder with filenames matching your SKU codes:

```
images/
  ├── SKU001.jpg
  ├── SKU002.png
  ├── PROD-ABC-123.webp
  └── item-xyz-456.jpg
```

### Step 2: Configure
Ensure `.env` has the local images folder configured:

```env
LOCAL_IMAGES_FOLDER=./images
```

### Step 3: Run the Bot
```bash
python src/main.py --run-once
```

The bot will:
1. Read SKU list from your configured source
2. For each SKU, look for matching image file in this folder
3. Validate the image (dimensions, format, size)
4. Upload to Replit WholesaleHub app

## Notes

- **Exact Match Required**: If no image file matches the SKU, the bot will log a warning and skip that SKU
- **Duplicates**: If multiple files with same SKU but different extensions exist (e.g., `SKU123.jpg` and `SKU123.png`), the first one found will be used
- **Original Filenames Preserved**: The original filename is used when uploading to Replit
- **No API Calls**: When using local images, the bot does NOT make any calls to Unsplash, Pexels, or Pixabay

## Example

If you have SKU `WG-TOOL-001` in your database and place `WG-TOOL-001.jpg` in this folder, the bot will:

1. Find `WG-TOOL-001.jpg`
2. Validate it meets size/format requirements
3. Upload it to Replit as the product image for SKU `WG-TOOL-001`
4. Mark the SKU as processed in the database

## Migration from API Search

To switch from API-based image search to local images:

1. Comment out or remove image API keys from `.env`
2. Set `LOCAL_IMAGES_FOLDER=./images` in `.env`
3. Place your images in this folder
4. Run the bot

The bot automatically detects the `LOCAL_IMAGES_FOLDER` setting and uses local matching instead of API search.
