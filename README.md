# Image Fetcher Bot 🤖

Autonomous bot that fetches and attaches images to product SKUs in your Replit app using multiple free image sources.

## Features

- **Multi-Source Image Search**: Searches Unsplash, Pexels, and Pixabay APIs with intelligent fallback
- **Smart Keyword Extraction**: Automatically extracts searchable keywords from SKU names
- **Relevance Scoring**: Scores images based on keyword match, quality, and source priority
- **Image Validation**: Validates format, dimensions, file size before uploading
- **State Persistence**: Tracks processed SKUs to avoid reprocessing
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
- API Keys:
  - **Replit App API** key and URL
  - **Unsplash** Access Key ([Get it here](https://unsplash.com/developers))
  - **Pexels** API Key ([Get it here](https://www.pexels.com/api/))
  - **Pixabay** API Key ([Get it here](https://pixabay.com/api/docs/))

## Installation

### 1. Clone or Download

```bash
cd C:\Users\Samva\projects\imagefetcher
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file from the template:

```bash
copy .env.example .env
```

Edit `.env` and add your API keys:

```env
# Replit API Configuration
REPLIT_API_URL=https://your-replit-app.com/api
REPLIT_API_KEY=your_api_key_here

# Image Source APIs
UNSPLASH_ACCESS_KEY=your_unsplash_access_key
PEXELS_API_KEY=your_pexels_api_key
PIXABAY_API_KEY=your_pixabay_api_key

# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=production

# Database
DATABASE_PATH=./data/state.db

# Scheduling
SCHEDULE_ENABLED=true
SCHEDULE_INTERVAL_HOURS=6
```

### 5. Initialize Database

```bash
python scripts\setup_db.py
```

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
