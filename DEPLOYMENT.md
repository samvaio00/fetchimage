# Deployment Guide

## Folder Structure

When deploying this application to a different computer, maintain this folder structure:

```
fetchimage/                          # Main application directory
├── src/                             # Source code
│   ├── api/
│   ├── services/
│   ├── storage/
│   └── utils/
├── config/                          # Configuration files
│   └── config.yaml
├── images/                          # ⭐ YOUR PRODUCT IMAGES GO HERE
│   ├── SKU001.jpg
│   ├── SKU002.png
│   └── ...
├── data/                            # Database (created automatically)
│   └── state.db
├── logs/                            # Log files (created automatically)
│   └── app.log
├── reports/                         # Reports (created automatically)
├── venv/                            # Virtual environment
├── .env                             # Environment variables (YOU MUST CREATE THIS)
├── requirements.txt
└── README.md
```

## Critical: Images Folder Location

### Relative Path (Default - Recommended)
The **images/** folder should be in the **same directory** as the main application folder.

**Example:**
```
C:\MyApp\fetchimage\
├── images/              ← Images folder here
├── src/
├── config/
├── .env                 ← Set: LOCAL_IMAGES_FOLDER=./images
└── ...
```

**Configuration in `.env`:**
```env
LOCAL_IMAGES_FOLDER=./images
```

### Absolute Path (Alternative)
You can place images anywhere and use an absolute path:

**Example:**
```
D:\ProductImages\
├── SKU001.jpg
├── SKU002.png
└── ...
```

**Configuration in `.env`:**
```env
# Windows
LOCAL_IMAGES_FOLDER=D:\ProductImages

# Linux/Mac
LOCAL_IMAGES_FOLDER=/home/user/ProductImages
```

### Network Drive (For Shared Environments)
```env
# Windows network path
LOCAL_IMAGES_FOLDER=\\NetworkServer\ProductImages

# Mapped network drive
LOCAL_IMAGES_FOLDER=Z:\ProductImages
```

## Deployment Steps

### 1. Clone/Copy the Repository

```bash
# Clone from GitHub
git clone https://github.com/samvaio00/fetchimage.git
cd fetchimage

# OR copy the entire fetchimage folder to your target location
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

### 4. Create Images Folder

```bash
# Create in project directory (recommended)
mkdir images

# OR create anywhere and use absolute path in .env
```

### 5. Configure Environment Variables

Create `.env` file from example:

**Windows:**
```bash
copy .env.example .env
notepad .env
```

**Linux/Mac:**
```bash
cp .env.example .env
nano .env
```

**Edit `.env` with your settings:**
```env
# Replit Configuration
REPLIT_API_URL=https://warnergears.replit.app
REPLIT_EMAIL=your_admin_email@example.com
REPLIT_PASSWORD=your_password

# Local Images Folder
LOCAL_IMAGES_FOLDER=./images

# Database
DATABASE_PATH=./data/state.db

# Logging
LOG_LEVEL=INFO
ENVIRONMENT=production

# Scheduling (optional)
SCHEDULE_ENABLED=true
SCHEDULE_INTERVAL_HOURS=6
```

### 6. Initialize Database

```bash
# Windows
set PYTHONPATH=.
venv\Scripts\python scripts\setup_db.py

# Linux/Mac
PYTHONPATH=. venv/bin/python scripts/setup_db.py
```

### 7. Add Your Product Images

Place images in the configured folder with filename = SKU code:

```
images/
├── 005692548366.jpg
├── 5056716406853.png
├── 687498456177.png
└── ...
```

**Rules:**
- Filename (without extension) must match SKU code
- Supported formats: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- Minimum dimensions: 400x400 pixels
- Maximum file size: 5MB (configurable in `config/config.yaml`)

### 8. Create SKU List File

Create a text file with SKU codes (one per line):

```bash
# Example: my_skus.txt
005692548366
5056716406853
687498456177
```

### 9. Run the Application

**One-time upload:**
```bash
# Windows
venv\Scripts\python -m src.main --run-once --sku-file my_skus.txt

# Linux/Mac
venv/bin/python -m src.main --run-once --sku-file my_skus.txt
```

**Scheduled execution (every 6 hours):**
```bash
# Windows
venv\Scripts\python -m src.main --interval 6

# Linux/Mac
venv/bin/python -m src.main --interval 6
```

## Running as a Service

### Windows - Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, repeat every 6 hours
4. Action: Start a program
   - Program: `C:\path\to\fetchimage\venv\Scripts\python.exe`
   - Arguments: `-m src.main --run-once --sku-file my_skus.txt`
   - Start in: `C:\path\to\fetchimage`

### Linux - Systemd Service

Create `/etc/systemd/system/fetchimage.service`:

```ini
[Unit]
Description=Image Fetcher Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/fetchimage
Environment="PYTHONPATH=/home/youruser/fetchimage"
ExecStart=/home/youruser/fetchimage/venv/bin/python -m src.main --interval 6
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable fetchimage
sudo systemctl start fetchimage
sudo systemctl status fetchimage
```

### Linux - Cron Job

Edit crontab:
```bash
crontab -e
```

Add (runs every 6 hours):
```cron
0 */6 * * * cd /home/youruser/fetchimage && venv/bin/python -m src.main --run-once --sku-file my_skus.txt >> logs/cron.log 2>&1
```

## Docker Deployment (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create necessary directories
RUN mkdir -p data logs reports images

CMD ["python", "-m", "src.main", "--interval", "6"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  fetchimage:
    build: .
    volumes:
      - ./images:/app/images        # Mount images folder
      - ./data:/app/data            # Persist database
      - ./logs:/app/logs            # Persist logs
    env_file:
      - .env
    restart: unless-stopped
```

Run:
```bash
docker-compose up -d
```

## Troubleshooting

### "Images folder does not exist"

**Problem:** Bot can't find the images folder

**Solutions:**
1. Check path in `.env` is correct
2. Use absolute path instead of relative
3. Verify folder exists: `ls ./images` (Linux/Mac) or `dir images` (Windows)

### "No local image found for SKU"

**Problem:** SKU has no matching image file

**Solutions:**
1. Verify filename matches SKU exactly (case-insensitive)
2. Check file extension is supported (.jpg, .png, .gif, .webp)
3. List files: `ls images/` to see what's available

### "Image validation failed"

**Problem:** Image doesn't meet requirements

**Solutions:**
1. Check dimensions are at least 400x400
2. Verify file size is under 5MB
3. Confirm format is JPEG, PNG, GIF, or WebP
4. Adjust validation settings in `config/config.yaml` if needed

### "Failed to attach image to SKU"

**Problem:** Replit rejected the upload

**Solutions:**
1. Verify SKU exists in Replit database (404 = not found)
2. Check authentication credentials in `.env`
3. Ensure you have admin/staff permissions

## Security Best Practices

1. **Never commit `.env` to git** - Contains sensitive credentials
2. **Use environment-specific configs** - Different .env for dev/production
3. **Restrict file permissions** - `chmod 600 .env` on Linux/Mac
4. **Rotate credentials regularly** - Update passwords periodically
5. **Use encrypted connections** - Ensure HTTPS for Replit API

## Monitoring

### Check Logs
```bash
# View recent logs
tail -f logs/app.log

# Windows
type logs\app.log
```

### Database Stats
```bash
# View processing statistics
python -c "from src.storage.state_manager import StateManager; sm = StateManager(); print(sm.get_processing_stats())"
```

### Reports
Check `reports/` folder for needs_review files listing failed SKUs.

## Performance Optimization

### Large Image Collections

If you have 1000+ images:

1. **Process in batches:**
   ```bash
   # Create multiple SKU files
   split -l 100 all_skus.txt batch_

   # Run each batch separately
   python -m src.main --run-once --sku-file batch_aa
   ```

2. **Increase validation limits:**
   Edit `config/config.yaml`:
   ```yaml
   validation:
     min_width: 300    # Lower if needed
     min_height: 300
     max_file_size_mb: 10
   ```

3. **Use faster storage:**
   Place images on SSD for faster validation

## Updates

To update the application:

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart the service
```

## Support

For issues or questions:
1. Check `logs/app.log` for detailed error messages
2. Review `TROUBLESHOOTING.md`
3. Verify configuration in `.env` and `config/config.yaml`
4. Check database state: `data/state.db`

## Summary

**Key Points:**
- ✅ Images folder can be relative (`./images`) or absolute path
- ✅ Configure path in `.env` using `LOCAL_IMAGES_FOLDER`
- ✅ Filename must match SKU code (without extension)
- ✅ Bot skips already-processed SKUs automatically
- ✅ Database tracks all uploads in `data/state.db`
- ✅ Logs saved to `logs/app.log`
