# ✅ Corrected Setup Guide - What You Actually Need

## Important Clarifications

### 1. WholesaleHub Authentication ✅ Already Done!

**You DON'T need API keys for WholesaleHub** - it uses email/password authentication, which is already implemented in the code!

The `.env` file needs:
```env
REPLIT_API_URL=https://warnergears.replit.app
REPLIT_EMAIL=your_admin_email@example.com
REPLIT_PASSWORD=your_admin_password
```

This is what you use to log into the WholesaleHub website.

---

### 2. Image Source API Keys ✅ Still Needed!

**You DO need free API keys for the image search services:**

These are the services that will **find product images** to attach to your SKUs:

- **Unsplash** - Free image search API (50 requests/hour)
- **Pexels** - Free image search API (200 requests/hour)
- **Pixabay** - Free image search API (5000 requests/hour)

**Why you need these:**
The bot needs to search for images that match your product SKUs. These APIs provide access to millions of free stock photos.

**How to get them:**
See `docs/GET_API_KEYS.md` for step-by-step instructions (takes 15 minutes).

---

### 3. Smart Filtering ✅ No Duplicate Processing!

**The bot now automatically skips SKUs that were already successfully processed!**

**How it works:**
1. Bot checks the database before processing each SKU
2. If SKU already has `SUCCESS` status → **SKIP IT**
3. If SKU has `FAILED` or `NEEDS_REVIEW` status → **RETRY IT**
4. If SKU never processed → **PROCESS IT**

**Example:**
```bash
# First run with 100 SKUs
python scripts/test_with_manual_skus.py --file real_skus.txt --limit 100
# Result: 80 success, 15 needs review, 5 failed

# Second run with same file
python scripts/test_with_manual_skus.py --file real_skus.txt --limit 100
# Result: Automatically skips the 80 successful ones
#         Only retries the 20 that failed or need review!
```

**Override behavior:**
```bash
# Force reprocess ALL SKUs (ignores database)
python scripts/test_with_manual_skus.py --file real_skus.txt --limit 100 --force

# Skip database check entirely (faster but may duplicate)
python scripts/test_with_manual_skus.py --file real_skus.txt --limit 100 --skip-check
```

---

## What You Need to Do

### Step 1: Create .env File (2 minutes)

```bash
copy .env.example .env
```

Edit `.env`:
```env
# WholesaleHub Login (your admin credentials)
REPLIT_API_URL=https://warnergears.replit.app
REPLIT_EMAIL=your_actual_email@example.com    ← YOUR WHOLESALEHUB LOGIN
REPLIT_PASSWORD=your_actual_password          ← YOUR WHOLESALEHUB PASSWORD

# Image Search APIs (get these from the free services)
UNSPLASH_ACCESS_KEY=get_from_unsplash_com     ← SEE docs/GET_API_KEYS.md
PEXELS_API_KEY=get_from_pexels_com            ← SEE docs/GET_API_KEYS.md
PIXABAY_API_KEY=get_from_pixabay_com          ← SEE docs/GET_API_KEYS.md

# App Settings (leave as-is)
LOG_LEVEL=INFO
ENVIRONMENT=production
DATABASE_PATH=./data/state.db
SCHEDULE_ENABLED=true
SCHEDULE_INTERVAL_HOURS=6
```

---

### Step 2: Get Image API Keys (15 minutes)

Follow the guide: `docs/GET_API_KEYS.md`

Quick links:
- **Unsplash**: https://unsplash.com/developers
- **Pexels**: https://www.pexels.com/api/
- **Pixabay**: https://pixabay.com/api/docs/

---

### Step 3: Test API Connectivity (1 minute)

```bash
python scripts\test_apis.py
```

Should see:
```
✅ Unsplash API: Connected
✅ Pexels API: Connected
✅ Pixabay API: Connected
✅ WholesaleHub API: Authenticated
```

---

### Step 4: Run Your First Test (2 minutes)

With the 10 test SKUs:
```bash
python scripts\test_with_manual_skus.py --file test_skus.txt --limit 10
```

Or with all 9,739 real SKUs (process 100 at a time):
```bash
python scripts\test_with_manual_skus.py --file real_skus.txt --limit 100
```

**The bot will automatically:**
- ✅ Skip SKUs that were already successfully processed
- ✅ Retry SKUs that failed or need review
- ✅ Track everything in the database
- ✅ Generate reports for SKUs with no images

---

### Step 5: Process All 9,739 SKUs (run multiple times)

Since the bot now **remembers what it's already processed**, you can run it multiple times:

```bash
# First batch: 100 SKUs
python scripts\test_with_manual_skus.py --file real_skus.txt --limit 100

# Second batch: next 100 SKUs (automatically skips first batch if successful)
python scripts\test_with_manual_skus.py --file real_skus.txt --limit 100

# Third batch: keeps going...
python scripts\test_with_manual_skus.py --file real_skus.txt --limit 100
```

Or process larger batches:
```bash
# Process 500 at a time
python scripts\test_with_manual_skus.py --file real_skus.txt --limit 500
```

Or just run it all at once (will take several hours due to API rate limits):
```bash
# Process all 9,739 SKUs
python scripts\test_with_manual_skus.py --file real_skus.txt --limit 9739
```

---

## Understanding the Output

### First Run:
```
============================================================
STARTING TEST RUN
============================================================
Total SKUs in file: 9739
SKUs to process: 100
Image sources: Unsplash → Pexels → Pixabay
============================================================

Processing SKU 1/100: 00076171913999
✅ SUCCESS: Image attached
   Source: UNSPLASH
   Relevance: 0.78

...

============================================================
TEST RUN COMPLETE
============================================================
Total in file: 9739
Attempted this run: 100
✅ Successful: 75
❌ Failed: 5
⚠️  Needs Review: 20
Success Rate: 75.0%
============================================================
```

### Second Run (Same File):
```
============================================================
STARTING TEST RUN
============================================================
Total SKUs in file: 9739
Already processed: 75          ← SKIPPED! ✅
SKUs to process: 25           ← Only retrying failures
Image sources: Unsplash → Pexels → Pixabay
============================================================

Processing SKU 1/25: 00305731347197  ← Only failed/needs_review
...
```

---

## Key Differences from Previous Instructions

| Old Understanding | ✅ Correct Understanding |
|-------------------|-------------------------|
| Need WholesaleHub API key | ❌ No - just email/password |
| May process SKUs multiple times | ✅ Auto-skips successful SKUs |
| Must manually track processed SKUs | ✅ Database tracks automatically |
| Can't resume after stopping | ✅ Can stop/resume anytime |

---

## Commands Reference

```bash
# Test with 10 SKUs
python scripts\test_with_manual_skus.py --file test_skus.txt --limit 10

# Process 100 real SKUs (auto-skips already processed)
python scripts\test_with_manual_skus.py --file real_skus.txt --limit 100

# Force reprocess everything (ignore database)
python scripts\test_with_manual_skus.py --file real_skus.txt --limit 100 --force

# Process all 9,739 SKUs (resumable)
python scripts\test_with_manual_skus.py --file real_skus.txt --limit 9739

# Check API connectivity
python scripts\test_apis.py

# Check database
sqlite3 data\state.db
SELECT COUNT(*) FROM processed_skus WHERE status='SUCCESS';
```

---

**You're ready! Just get the 3 image API keys and you can start processing your 9,739 SKUs! 🚀**
