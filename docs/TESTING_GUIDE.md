# Testing Guide - Image Fetcher Bot

This guide will help you run your first test of the image fetcher bot.

---

## Prerequisites

Before running the test, make sure you have:

1. ✅ **API Keys**: Obtained from Unsplash, Pexels, and Pixabay (see `docs/GET_API_KEYS.md`)
2. ✅ **WholesaleHub Credentials**: Admin email and password for https://warnergears.replit.app
3. ✅ **.env File**: Created with all your credentials
4. ✅ **Virtual Environment**: Activated (`venv\Scripts\activate` on Windows)
5. ✅ **Dependencies**: Installed (`pip install -r requirements.txt`)

---

## Step 1: Get Your API Keys

Follow the instructions in `docs/GET_API_KEYS.md` to obtain:
- Unsplash Access Key (free, 50 requests/hour)
- Pexels API Key (free, 200 requests/hour)
- Pixabay API Key (free, 5000 requests/hour)

This should take about 10-15 minutes.

---

## Step 2: Create Your .env File

1. Copy the example file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and fill in your credentials:
   ```env
   # Replit WholesaleHub API Configuration
   REPLIT_API_URL=https://warnergears.replit.app
   REPLIT_EMAIL=your_actual_admin_email@example.com
   REPLIT_PASSWORD=your_actual_password
   
   # Image Source APIs (paste your keys here)
   UNSPLASH_ACCESS_KEY=your_unsplash_access_key_here
   PEXELS_API_KEY=your_pexels_api_key_here
   PIXABAY_API_KEY=your_pixabay_api_key_here
   ```

3. Save the file

---

## Step 3: Test API Connectivity

Before running the full bot, verify that all your API keys work:

```bash
python scripts/test_apis.py
```

Expected output:
```
Testing API connections...
✅ Unsplash API: Connected
✅ Pexels API: Connected
✅ Pixabay API: Connected
✅ WholesaleHub API: Authenticated
```

If any test fails, double-check your API keys in the `.env` file.

---

## Step 4: Get Test SKUs from WholesaleHub

**Current Limitation**: The WholesaleHub API doesn't yet have an endpoint to list products without images.

**Workaround**: Manually get 10 SKU IDs from your WholesaleHub app:

1. Log into https://warnergears.replit.app
2. Navigate to your products page
3. Find 10 products that don't have images yet
4. Copy their SKU IDs

Example SKU IDs:
- `MEN-SHIRT-BLUE-L`
- `LAPTOP-DELL-15IN`
- `PHONE-CASE-IPHONE-14`
- etc.

---

## Step 5: Run the Test

### Option A: Test with SKU list in command line

```bash
python scripts/test_with_manual_skus.py --skus "SKU1,SKU2,SKU3" --limit 10
```

Replace `SKU1,SKU2,SKU3` with your actual SKU IDs (comma-separated).

### Option B: Test with SKU list in a file

1. Edit `test_skus.txt` and add your SKU IDs (one per line)
2. Run:
   ```bash
   python scripts/test_with_manual_skus.py --file test_skus.txt --limit 10
   ```

### Reset State (Optional)

If you want to re-process SKUs that were already processed:

```bash
python scripts/test_with_manual_skus.py --file test_skus.txt --limit 10 --reset-state
```

---

## Step 6: Monitor the Test

The bot will:

1. **Load configuration** from `.env` and `config/config.yaml`
2. **Authenticate** with WholesaleHub
3. **For each SKU**:
   - Extract keywords from the SKU name
   - Search Unsplash for matching images
   - If no match found (score < 0.6), try Pexels
   - If still no match, try Pixabay
   - Validate the image (format, dimensions, file size)
   - Download the image
   - Upload to WholesaleHub
   - Mark as processed in database

Watch the console output for progress:
```
Processing SKU: MEN-SHIRT-BLUE-L
Keywords: men, shirt, blue, large
Searching Unsplash...
✅ Found image (score: 0.85)
Downloading image...
Uploading to WholesaleHub...
✅ SUCCESS: Image attached for MEN-SHIRT-BLUE-L
```

---

## Step 7: Check the Results

### 1. Check Logs
```bash
type logs\app.log
```

Look for:
- Authentication success
- Image search results
- Upload confirmations
- Any errors or warnings

### 2. Check Database
The database tracks all processed SKUs:
```bash
sqlite3 data/state.db
```

Query:
```sql
SELECT * FROM processed_skus;
```

You'll see:
- `sku_id`: The SKU that was processed
- `status`: SUCCESS, FAILED, or NEEDS_REVIEW
- `image_source`: Which API provided the image (UNSPLASH, PEXELS, PIXABAY)
- `relevance_score`: How well the image matched (0.0 to 1.0)
- `processed_at`: Timestamp

### 3. Check WholesaleHub
Log into https://warnergears.replit.app and verify that:
- Images were successfully attached to the SKUs
- Images are displayed correctly
- Images are relevant to the products

### 4. Check Reports
If any SKUs couldn't find images, check:
```bash
dir reports\
```

You'll find a file like `needs_review_20260210_143025.txt` listing SKUs that need manual images.

---

## Expected Results

### Success Case:
```
============================================================
STARTING TEST RUN
============================================================
SKUs to process: 10
Image sources: Unsplash → Pexels → Pixabay
============================================================

Processing SKU: MEN-SHIRT-BLUE-L
✅ SUCCESS: Image attached for MEN-SHIRT-BLUE-L
   Source: UNSPLASH
   Relevance: 0.85

Processing SKU: LAPTOP-DELL-15IN
✅ SUCCESS: Image attached for LAPTOP-DELL-15IN
   Source: PEXELS
   Relevance: 0.72

...

============================================================
TEST RUN COMPLETE
============================================================
Successful: 8
Failed: 0
Needs Review: 2
Success Rate: 80.0%
```

### Partial Success:
Some SKUs may not find suitable images (relevance < 0.6). These will be saved to `reports/needs_review_*.txt` for manual processing.

---

## Troubleshooting

### "Error loading configuration"
- Make sure `.env` file exists in the project root
- Check that all required environment variables are set

### "Authentication failed"
- Verify your WholesaleHub email and password in `.env`
- Make sure you can log into https://warnergears.replit.app manually

### "401 Unauthorized" from image APIs
- Double-check your API keys in `.env`
- Make sure you copied the correct keys (Access Key for Unsplash, not Secret Key)

### "No suitable image found"
- The SKU name may be too generic or unclear
- Try with more descriptive SKU names
- Check `reports/needs_review_*.txt` for these SKUs

### "Product not found for SKU"
- The SKU doesn't exist in WholesaleHub
- Check that you typed the SKU correctly
- Verify the SKU exists in your WholesaleHub products

### Rate Limit Errors (429)
- You've exceeded the API's hourly limit
- Wait for the limit to reset (usually 1 hour)
- Consider using fewer SKUs in your test

---

## Next Steps After Successful Test

1. **Review Results**: Check that images are relevant and high quality
2. **Adjust Configuration**: Tune `config/config.yaml` settings if needed
   - Minimum relevance score (default: 0.6)
   - Image validation rules (dimensions, file size)
   - Rate limits
3. **Run with More SKUs**: Process 50-100 SKUs to test at scale
4. **Set Up Scheduling**: Configure automatic runs every 6 hours
   ```bash
   python src/main.py --schedule --interval 6
   ```
5. **Monitor Logs**: Check `logs/app.log` regularly for errors

---

## Production Deployment

Once testing is successful, you can run the bot autonomously:

### Option 1: Python Scheduler (Recommended)
```bash
python src/main.py --schedule --interval 6
```

This will run the bot every 6 hours continuously. Press Ctrl+C to stop.

### Option 2: Windows Task Scheduler
1. Open Task Scheduler
2. Create new task
3. Set trigger: Repeat every 6 hours
4. Set action: `python C:\Users\Samva\projects\imagefetcher\src\main.py --run-once`

---

**Good luck with your test! 🚀**
