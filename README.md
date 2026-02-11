# Image Fetcher Bot 🤖

Autonomous bot that attaches product images to SKUs in your Replit WholesaleHub app. Supports both **local image matching** and **API-based image search**.

## Features

- **🆕 Local Image Matching**: Match images by SKU filename (filename = SKU code)
- **Multi-Source API Search**: Searches Unsplash, Pexels, and Pixabay with intelligent fallback
- **Smart Keyword Extraction**: Automatically extracts searchable keywords from SKU names
- **Relevance Scoring**: Scores images based on keyword match, quality, and source priority
- **Image Validation**: Validates format, dimensions, file size before uploading
- **State Persistence**: Tracks processed SKUs to avoid reprocessing
- **Duplicate Prevention**: Skips already-uploaded SKUs automatically
- **Scheduled Execution**: Runs autonomously on configurable schedule (default: every 6 hours)
- **Comprehensive Logging**: JSON-formatted logs with rotation
- **Error Recovery**: Retry logic with exponential backoff for transient failures

## Architecture

```
Scheduler → SKU Processor → Image Search Service → [Unsplash/Pexels/Pixabay]
                ↓                                              ↓
         Replit API Client                            Image Validator
                ↓                                              ↓
         State Manager (SQLite) ←─────────────────────────────┘
```

## Prerequisites

- Python 3.8+
- **Replit WholesaleHub** credentials (email + password)
- **Optional** - API Keys (only if using API search mode):
  - **Unsplash** Access Key ([Get it here](https://unsplash.com/developers))
  - **Pexels** API Key ([Get it here](https://www.pexels.com/api/))
  - **Pixabay** API Key ([Get it here](https://pixabay.com/api/docs/))

## Modes of Operation

### 🆕 Local Images Mode (Recommended)
- Place product images in `./images/` folder
- Filename (without extension) must match SKU code
- No API keys required
- 100% accurate matching

### API Search Mode
- Searches Unsplash, Pexels, Pixabay for images
- Uses keyword extraction from SKU names
- Requires API keys
- May not always match the actual product

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/samvaio00/fetchimage.git
cd fetchimage
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file from the template:

**Windows:**
```bash
copy .env.example .env
```

**Linux/Mac:**
```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Replit WholesaleHub Configuration
REPLIT_API_URL=https://warnergears.replit.app
REPLIT_EMAIL=your_admin_email@example.com
REPLIT_PASSWORD=your_password

# Local Images (recommended - comment out to use API search)
LOCAL_IMAGES_FOLDER=./images

# Image Source APIs (only needed if NOT using local images)
# FREEPIK_API_KEY=your_freepik_api_key
# PEXELS_API_KEY=your_pexels_api_key
# PIXABAY_API_KEY=your_pixabay_api_key

# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=production

# Database
DATABASE_PATH=./data/state.db

# Scheduling
SCHEDULE_ENABLED=true
SCHEDULE_INTERVAL_HOURS=6
```

### 5. Create Necessary Folders

```bash
mkdir images data logs reports
```

### 6. Initialize Database

**Windows:**
```bash
set PYTHONPATH=.
venv\Scripts\python scripts\setup_db.py
```

**Linux/Mac:**
```bash
PYTHONPATH=. venv/bin/python scripts/setup_db.py
```

## Quick Start - Local Images Mode

### 1. Add Product Images

Place images in `./images/` folder with filename = SKU code:

```
images/
├── 005692548366.jpg
├── 5056716406853.png
├── 687498456177.png
└── ...
```

**Rules:**
- Filename (without extension) = SKU code
- Supported: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- Minimum: 400x400 pixels
- Maximum: 5MB

### 2. Create SKU List File

Create `my_skus.txt` with SKU codes (one per line):

```
005692548366
5056716406853
687498456177
```

### 3. Run the Bot

**Windows:**
```bash
venv\Scripts\python -m src.main --run-once --sku-file my_skus.txt
```

**Linux/Mac:**
```bash
venv/bin/python -m src.main --run-once --sku-file my_skus.txt
```

The bot will:
1. Match each SKU to its image file
2. Validate images (size, format, dimensions)
3. Upload to Replit WholesaleHub
4. Track progress in database
5. Skip already-processed SKUs

## Usage

### Run Once (Manual Execution)

```bash
python src\main.py --run-once
```

This will:
1. Fetch all SKUs without images from Replit app
2. Extract keywords from each SKU name
3. Search for matching images across all sources
4. Validate and attach images
5. Generate a summary report

### Run on Schedule

```bash
python src\main.py --interval 6
```

This starts the scheduler to run automatically every 6 hours.

### Custom Config File

```bash
python src\main.py --run-once --config path\to\config.yaml
```

## Configuration

### Main Config (`config/config.yaml`)

```yaml
app:
  name: "Image Fetcher Bot"
  batch_size: 50  # Max SKUs to process per run

image_search:
  sources:
    unsplash: 1      # Priority order (1 = highest)
    pexels: 2
    pixabay: 3
  
  minimum_relevance_score: 0.6  # Threshold for image selection
  
  validation:
    min_width: 800
    min_height: 600
    max_file_size_mb: 5
    allowed_formats: ["JPEG", "PNG", "WebP"]

keywords:
  max_keywords: 5
  expand_abbreviations: true

retry:
  max_attempts: 3
  exponential_base: 2
```

## How It Works

### 1. Keyword Extraction

SKU names are transformed into searchable keywords:

- `"MEN-SHIRT-BLUE-L"` → `["men", "shirt", "blue", "large"]`
- `"LAPTOP-DELL-15IN"` → `["laptop", "dell", "15 inch"]`

### 2. Multi-Source Cascade

The bot tries each image source in priority order until a suitable image is found:

1. **Unsplash** (priority 1) - High-quality photos
2. **Pexels** (priority 2) - Free stock photos
3. **Pixabay** (priority 3) - Large free image library

### 3. Relevance Scoring

Each image is scored based on:
- **60%**: Keyword matches in image title
- **20%**: Image quality (resolution)
- **20%**: Source priority

Images with score ≥ 0.6 are selected.

### 4. Image Validation

Before uploading, images are validated for:
- Format (JPEG, PNG, WebP)
- Dimensions (min 800x600)
- File size (max 5MB)
- Aspect ratio (0.5 to 2.0)

### 5. State Tracking

SQLite database tracks:
- Successfully processed SKUs
- Failed SKUs (with retry count)
- Processing statistics
- Execution history

## API Rate Limits

| Source | Free Tier Limit |
|--------|----------------|
| Unsplash | 50 requests/hour |
| Pexels | 200 requests/hour |
| Pixabay | 100 requests/minute |

The bot handles rate limiting automatically with exponential backoff.

## Logging

Logs are written to:
- **Console**: Human-readable format
- **File**: `logs/app.log` (JSON format, auto-rotating at 10MB)

View recent logs:
```bash
tail -n 100 logs\app.log
```

## Troubleshooting

### No Images Found

**Problem**: Bot runs but finds no suitable images

**Solutions**:
- Lower `minimum_relevance_score` in config (try 0.4)
- Add more descriptive SKU names
- Check if API keys are valid

### Database Locked

**Problem**: `database is locked` error

**Solutions**:
- Ensure only one instance is running
- Check file permissions on `data/state.db`

### API Rate Limits

**Problem**: `429 Too Many Requests` errors

**Solutions**:
- Reduce `batch_size` in config
- Increase schedule interval
- Wait for rate limit window to reset

### Import Errors

**Problem**: `ModuleNotFoundError`

**Solutions**:
- Activate virtual environment: `venv\Scripts\activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## Project Structure

```
imagefetcher/
├── src/
│   ├── api/                    # API clients
│   │   ├── base_client.py      # HTTP client with retry
│   │   ├── unsplash_client.py
│   │   ├── pexels_client.py
│   │   ├── pixabay_client.py
│   │   └── replit_client.py
│   ├── services/               # Business logic
│   │   ├── sku_processor.py    # Main orchestrator
│   │   ├── image_search_service.py
│   │   ├── image_validator.py
│   │   └── keyword_extractor.py
│   ├── storage/                # Data persistence
│   │   ├── state_manager.py    # SQLite operations
│   │   └── models.py           # Pydantic models
│   ├── utils/                  # Utilities
│   │   ├── config.py
│   │   └── logger.py
│   ├── scheduler/
│   │   └── job_scheduler.py
│   └── main.py                 # Entry point
├── config/
│   ├── config.yaml
│   └── logging.yaml
├── data/
│   └── state.db                # SQLite database
├── logs/
│   └── app.log
├── scripts/
│   └── setup_db.py
├── .env                        # API keys (not in git)
├── requirements.txt
└── README.md
```

## Development

### Run Tests

```bash
pip install -r requirements-dev.txt
pytest
```

### Code Quality

```bash
# Format code
black src/

# Lint
flake8 src/

# Type check
mypy src/

# Security scan
bandit -r src/
```

## Customization

### Add Custom Image Source

1. Create new client in `src/api/`:
```python
class CustomClient(BaseAPIClient):
    def search_images(self, query, per_page=5):
        # Implementation
        pass
```

2. Register in `ImageSearchService`

3. Add API key to `.env`

### Adjust Relevance Scoring

Edit `ImageSearchService.score_image_relevance()`:

```python
def score_image_relevance(self, image, keywords):
    score = 0.0
    # Custom scoring logic
    return min(score, 1.0)
```

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check logs in `logs/app.log`
2. Review configuration in `config/config.yaml`
3. Verify API keys in `.env`

## Credits

- Powered by [Unsplash](https://unsplash.com), [Pexels](https://pexels.com), and [Pixabay](https://pixabay.com)
- Built with Python, Pydantic, APScheduler, and Pillow
