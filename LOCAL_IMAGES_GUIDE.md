# Local Images Feature - Implementation Guide

## Overview

The Image Fetcher Bot has been updated to support **local image matching** instead of API-based image search. This solves the problem of irrelevant images being fetched from stock photo APIs.

## How It Works

### Old Flow (API-Based)
1. Bot fetches SKU list from Replit
2. Extracts keywords from SKU name (e.g., "MEN-SHIRT-BLUE" → ["men", "shirt", "blue"])
3. Searches Unsplash/Pexels/Pixabay for images matching keywords
4. Scores images by relevance
5. Downloads and uploads best match to Replit

**Problem**: Keywords from SKU codes often don't match the actual product, resulting in incorrect images.

### New Flow (Local Images)
1. Bot loads SKU list from text file or Replit API
2. For each SKU, looks for matching image file in local folder
3. Validates image (format, size, dimensions)
4. Uploads image to Replit with SKU

**Solution**: You control exactly which image matches each SKU by using filename = SKU code.

## Configuration

### 1. Environment Variables (.env)

Add or uncomment this line in your `.env` file:

```env
LOCAL_IMAGES_FOLDER=./images
```

When this variable is set, the bot will:
- Use local image matching instead of API search
- Ignore Unsplash/Pexels/Pixabay APIs (no API calls made)
- Match images by filename = SKU code

### 2. Image Folder Structure

Place your images in the configured folder with filenames matching SKU codes:

```
images/
  ├── 00076171913999.jpg
  ├── 00076171931368.png
  ├── 00076171934635.webp
  └── 001300000042.jpg
```

**Rules**:
- Filename (without extension) must match SKU code exactly
- Matching is case-insensitive: `abc123.png` matches SKU `ABC123`
- Supported formats: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- First match wins if duplicates exist

### 3. Image Requirements

Images must meet these criteria to pass validation:
- **Minimum dimensions**: 800x600 pixels
- **Maximum file size**: 10MB (Replit API limit)
- **Aspect ratio**: 0.5 to 2.0
- **Formats**: JPEG, PNG, GIF, WebP

## Usage

### Option 1: Use SKU File (Recommended)

Create a text file with SKU codes (one per line):

```txt
# test_skus.txt
00076171913999
00076171931368
00076171934635
001300000042
```

Run the bot with the SKU file:

```bash
python src/main.py --run-once --sku-file test_skus.txt
```

### Option 2: Use Replit API

If the Replit API provides a list of products without images:

```bash
python src/main.py --run-once
```

(The bot will call `get_skus_without_images()` automatically)

## What Changed

### New Files

1. **`src/services/local_image_service.py`**
   - `LocalImageService` class for matching SKUs to local images
   - Builds index of available images on startup
   - Provides `find_image_for_sku()` method

2. **`images/README.md`**
   - Documentation for the images folder
   - Usage instructions and examples

3. **`LOCAL_IMAGES_GUIDE.md`** (this file)
   - Complete implementation guide

### Modified Files

1. **`src/services/sku_processor.py`**
   - Added `_load_skus_from_file()` method to read SKU list from text file
   - Added `_process_with_local_image()` method for local image processing
   - Refactored `_process_with_api_search()` (original logic)
   - `process_single_sku()` now routes to local or API based on config

2. **`src/utils/config.py`**
   - Added `local_images_folder` to `AppConfig` (from `LOCAL_IMAGES_FOLDER` env var)

3. **`src/storage/models.py`**
   - Added `ImageSource.LOCAL` to track local image uploads

4. **`src/main.py`**
   - Added `--sku-file` command-line option
   - Passes SKU file to processor

5. **`.env` and `.env.example`**
   - Added `LOCAL_IMAGES_FOLDER` configuration option
   - Updated credentials to actual values

## Command-Line Options

```bash
python src/main.py --help
```

**Options**:
- `--run-once`: Run once and exit (default: run on schedule)
- `--interval HOURS`: Schedule interval in hours (default: 6)
- `--config PATH`: Path to config YAML file (default: config/config.yaml)
- `--sku-file PATH`: Path to SKU list file (one SKU per line, # for comments)

## Examples

### Example 1: Process Test SKUs with Local Images

```bash
# 1. Place images in ./images folder
cp /path/to/product/images/*.jpg ./images/

# 2. Create SKU list
cat > test_skus.txt <<EOF
00076171913999
00076171931368
001300000042
EOF

# 3. Configure local images in .env
echo "LOCAL_IMAGES_FOLDER=./images" >> .env

# 4. Run bot
python src/main.py --run-once --sku-file test_skus.txt
```

### Example 2: Process All SKUs from Replit API

```bash
# Configure .env
LOCAL_IMAGES_FOLDER=./images

# Run without SKU file (uses Replit API)
python src/main.py --run-once
```

### Example 3: Switch Back to API Search

```bash
# Comment out or remove local images folder in .env
# LOCAL_IMAGES_FOLDER=./images

# Add API keys back
UNSPLASH_ACCESS_KEY=your_key
PEXELS_API_KEY=your_key
PIXABAY_API_KEY=your_key

# Run bot
python src/main.py --run-once
```

## Troubleshooting

### "No local image found for SKU"

**Cause**: No image file matches the SKU code

**Solutions**:
- Check filename matches SKU exactly (case-insensitive)
- Verify file has supported extension (.jpg, .png, .gif, .webp)
- Run `ls images/` to see available files
- Check for typos in SKU code or filename

### "Image validation failed"

**Cause**: Image doesn't meet requirements

**Solutions**:
- Check dimensions: must be at least 800x600
- Check file size: must be under 10MB
- Verify format is JPEG, PNG, GIF, or WebP
- Check aspect ratio is between 0.5 and 2.0

### "Images folder does not exist"

**Cause**: `LOCAL_IMAGES_FOLDER` path is invalid

**Solutions**:
- Create the folder: `mkdir -p ./images`
- Check path in `.env` is correct
- Use absolute path if relative path doesn't work

### "Failed to attach image to SKU"

**Cause**: Replit API rejected the upload

**Solutions**:
- Verify SKU exists in Replit database (404 = SKU not found)
- Check authentication credentials in `.env`
- Review Replit API logs for error details
- Ensure you have admin/staff permissions

## Migration Checklist

To migrate from API search to local images:

- [ ] Create `images/` folder
- [ ] Copy product images to folder (filename = SKU code)
- [ ] Add `LOCAL_IMAGES_FOLDER=./images` to `.env`
- [ ] (Optional) Create SKU list file with codes to process
- [ ] Test with small batch: `python src/main.py --run-once --sku-file test_skus.txt`
- [ ] Review logs for validation errors
- [ ] Fix any images that fail validation
- [ ] Run full batch

## Logging

The bot logs all operations. Key log messages:

```
INFO - Initialized LocalImageService with folder: ./images
INFO - Indexed 150 SKU images
INFO - Using local images from: ./images
INFO - Loaded 10 SKUs from test_skus.txt
INFO - Found local image for SKU 00076171913999: 00076171913999.jpg
INFO - SKU 00076171913999 processed successfully with local image
WARNING - No local image found for SKU: 00076171939951
```

Check `logs/app.log` for detailed execution history.

## Database Tracking

The bot tracks processed SKUs in SQLite database at `./data/state.db`.

When using local images:
- `image_source` = `"local"`
- `image_url` = local file path
- `relevance_score` = 1.0 (perfect match)

To reset processing state:

```bash
# Delete database to reprocess all SKUs
rm ./data/state.db
python scripts/setup_db.py
```

## Benefits of Local Images

✅ **Accuracy**: You control which image matches which SKU
✅ **No API Limits**: No rate limits from Unsplash/Pexels/Pixabay
✅ **No API Keys**: No need to manage API credentials
✅ **Offline**: Works without internet (except for Replit upload)
✅ **Speed**: No time spent searching/downloading from APIs
✅ **Cost**: No API costs (all free tiers have limits)

## Support

For issues or questions:

1. Check logs: `logs/app.log`
2. Review configuration: `.env` and `config/config.yaml`
3. Verify image files exist and meet requirements
4. Test with small batch first

## Technical Details

### Code Architecture

```
┌─────────────────────────────────────────────────────┐
│              main.py (entry point)                  │
│  - Parses --sku-file option                         │
│  - Initializes Config and SKUProcessor              │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│         SKUProcessor.process_all_skus()             │
│  - Loads SKUs from file or Replit API               │
│  - Calls process_single_sku() for each              │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
         ┌───────────┴───────────┐
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ Local Images     │    │ API Search       │
│ (if configured)  │    │ (if no local)    │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ LocalImageService│    │ImageSearchService│
│ - find_image     │    │ - search_image   │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │   ImageValidator      │
         │   - validate_image    │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │   ReplitClient        │
         │   - attach_image      │
         └───────────────────────┘
```

### Image Source Priority

When `LOCAL_IMAGES_FOLDER` is set:
1. Bot uses **local images only**
2. API search is completely bypassed
3. No calls to Unsplash/Pexels/Pixabay

When `LOCAL_IMAGES_FOLDER` is not set:
1. Bot uses **API search** (original behavior)
2. Searches in priority order: Unsplash → Pexels → Pixabay
3. Selects best match by relevance score

You can switch between modes by commenting/uncommenting `LOCAL_IMAGES_FOLDER` in `.env`.
