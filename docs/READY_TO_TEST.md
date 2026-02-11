# ✅ Ready to Test - Your Bot is Set Up!

All code is complete and ready for testing. Here's what you need to do to run your first test with 10 real images.

---

## 🎯 Your Mission: Test with 10 Real SKUs

**Goal**: Verify the bot can successfully find and attach images to 10 products in WholesaleHub.

**Time Required**: 20 minutes total

---

## 📋 Checklist - What You Need

### ✅ Already Done (by me):
- [x] Complete bot implementation
- [x] WholesaleHub API integration (session-based auth)
- [x] Multi-source image search (Unsplash, Pexels, Pixabay)
- [x] State tracking with SQLite
- [x] Report generation for failed SKUs
- [x] Test script for manual SKU lists
- [x] Comprehensive documentation
- [x] Code pushed to GitHub

### ⏳ You Need to Do:
- [ ] Get 3 free API keys (15 minutes) - **SEE STEP 1 BELOW**
- [ ] Create .env file with credentials (2 minutes) - **SEE STEP 2 BELOW**
- [ ] Get 10 SKU IDs from WholesaleHub (1 minute) - **SEE STEP 3 BELOW**
- [ ] Run the test (2 minutes) - **SEE STEP 4 BELOW**

---

## 🚀 Step-by-Step Instructions

### STEP 1: Get Free API Keys (15 minutes)

Open **`QUICKSTART.md`** or **`docs/GET_API_KEYS.md`** for detailed instructions.

**Quick links**:
1. **Unsplash**: https://unsplash.com/developers (Register → Create App → Copy Access Key)
2. **Pexels**: https://www.pexels.com/api/ (Get Started → Copy API Key)
3. **Pixabay**: https://pixabay.com/api/docs/ (Get API Key → Copy)

You'll get 3 keys that look like:
```
Unsplash: WkS9vxQp2L8fH3mN7bR1tY4cV6jK0zD...
Pexels: abc123def456ghi789jkl012mno345...
Pixabay: 12345678-abc123def456ghi789jkl012...
```

---

### STEP 2: Create Your .env File (2 minutes)

1. **Copy the example**:
   ```bash
   copy .env.example .env
   ```

2. **Open `.env` in a text editor** (Notepad, VS Code, etc.)

3. **Replace the placeholder values**:
   ```env
   # WholesaleHub credentials
   REPLIT_API_URL=https://warnergears.replit.app
   REPLIT_EMAIL=your_actual_admin_email@example.com    ← CHANGE THIS
   REPLIT_PASSWORD=your_actual_password                 ← CHANGE THIS
   
   # Image API keys (paste the keys you got from Step 1)
   UNSPLASH_ACCESS_KEY=paste_your_unsplash_key_here    ← CHANGE THIS
   PEXELS_API_KEY=paste_your_pexels_key_here           ← CHANGE THIS
   PIXABAY_API_KEY=paste_your_pixabay_key_here         ← CHANGE THIS
   
   # Application Settings (leave these as-is)
   LOG_LEVEL=INFO
   ENVIRONMENT=production
   DATABASE_PATH=./data/state.db
   SCHEDULE_ENABLED=true
   SCHEDULE_INTERVAL_HOURS=6
   ```

4. **Save the file**

---

### STEP 3: Get 10 Test SKUs (1 minute)

**Option A: From WholesaleHub Dashboard**
1. Log into https://warnergears.replit.app
2. Go to Products section
3. Find 10 products that **don't have images yet**
4. Copy their SKU IDs

**Option B: Use Sample SKUs (Quick Test)**
If you just want to test the bot's functionality, you can use descriptive sample SKUs like:
- `MEN-SHIRT-BLUE-L`
- `LAPTOP-DELL-15IN`
- `PHONE-CASE-IPHONE-14`

**Edit `test_skus.txt`** and replace the examples with your SKU IDs (one per line):
```
YOUR-SKU-ID-1
YOUR-SKU-ID-2
YOUR-SKU-ID-3
...
```

---

### STEP 4: Run Your Test! (2 minutes)

**First, test API connectivity**:
```bash
python scripts\test_apis.py
```

You should see:
```
✅ Unsplash API: Connected
✅ Pexels API: Connected
✅ Pixabay API: Connected
✅ WholesaleHub API: Authenticated
```

**Then run the bot**:
```bash
python scripts\test_with_manual_skus.py --file test_skus.txt --limit 10
```

---

## 📊 What to Expect

### During the Test:
The bot will process each SKU and show real-time progress:

```
============================================================
STARTING TEST RUN
============================================================
SKUs to process: 10
Image sources: Unsplash → Pexels → Pixabay
============================================================

============================================================
Processing SKU: MEN-SHIRT-BLUE-L
============================================================
Keywords: men, shirt, blue, large
Searching Unsplash...
Found 15 candidate images
Best match score: 0.85
Downloading image...
Uploading to WholesaleHub...
✅ SUCCESS: Image attached for MEN-SHIRT-BLUE-L
   Source: UNSPLASH
   Relevance: 0.85

============================================================
Processing SKU: LAPTOP-DELL-15IN
============================================================
Keywords: laptop, dell, 15, inch
Searching Unsplash...
No good match (best: 0.45)
Searching Pexels...
Found match (score: 0.72)
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

Check logs/app.log for detailed output
Check data/state.db for processing records
Check reports/ folder for any SKUs needing review
============================================================
```

### Success Rate:
- **80-100%** is excellent! Most SKUs found good images.
- **60-80%** is good. Some SKUs may need more descriptive names.
- **Below 60%** - SKU names may be too generic or unclear.

---

## 🎉 After the Test

### 1. Verify in WholesaleHub
- Log into https://warnergears.replit.app
- Check your products
- Confirm images are attached and look good!

### 2. Check the Reports
If some SKUs didn't get images:
```bash
dir reports\
type reports\needs_review_*.txt
```

This file lists SKUs that need manual images.

### 3. Review Logs
```bash
type logs\app.log
```

Look for any errors or warnings.

---

## 🔄 Run It Again

Want to reprocess the same SKUs?
```bash
python scripts\test_with_manual_skus.py --file test_skus.txt --limit 10 --reset-state
```

The `--reset-state` flag clears previous results.

---

## 🚀 Next Steps After Successful Test

Once your test works:

### 1. Process More SKUs
```bash
python src\main.py --run-once
```

*(Note: This requires WholesaleHub to implement the product listing endpoint)*

### 2. Run on Schedule
```bash
python src\main.py --schedule --interval 6
```

Bot runs automatically every 6 hours!

### 3. Fine-Tune Settings
Edit `config/config.yaml` to adjust:
- Minimum relevance score (default: 0.6)
- Image size requirements
- Batch size
- Rate limits

---

## 📚 Documentation Reference

| Document | Purpose |
|----------|---------|
| **`QUICKSTART.md`** | 20-minute quick start guide |
| **`docs/GET_API_KEYS.md`** | Detailed API key setup |
| **`docs/TESTING_GUIDE.md`** | Comprehensive testing guide |
| **`WHOLESALEHUB_API.md`** | WholesaleHub API docs |
| **`README.md`** | Full project documentation |

---

## 🆘 Common Issues

| Problem | Solution |
|---------|----------|
| **"Error loading configuration"** | Make sure `.env` file exists with all keys |
| **"Authentication failed"** | Check WholesaleHub email/password in `.env` |
| **"401 Unauthorized" (Unsplash)** | You copied Secret Key instead of Access Key |
| **"No suitable image found"** | SKU name is too generic, use more descriptive names |
| **"Product not found for SKU"** | SKU doesn't exist in WholesaleHub |

**Full troubleshooting**: See `docs/TESTING_GUIDE.md`

---

## 💡 Tips for Best Results

1. **Use Descriptive SKU Names**:
   - ❌ `PROD-123`
   - ✅ `MEN-SHIRT-BLUE-COTTON-LARGE`

2. **Start Small**: Test with 10 SKUs first, then scale up

3. **Monitor Logs**: Check `logs/app.log` for any issues

4. **Review Images**: Make sure uploaded images are relevant

5. **Adjust Threshold**: If too many "needs review", lower the relevance threshold in `config/config.yaml`

---

## ✅ You're Ready!

Everything is set up. Just follow the 4 steps above and you'll have your first 10 product images attached in 20 minutes!

**Questions?** Check the documentation or review the code - it's well-commented!

---

**Good luck! 🚀**

---

## Quick Command Reference

```bash
# Test API connectivity
python scripts\test_apis.py

# Run test with 10 SKUs
python scripts\test_with_manual_skus.py --file test_skus.txt --limit 10

# Reset and run again
python scripts\test_with_manual_skus.py --file test_skus.txt --limit 10 --reset-state

# Check logs
type logs\app.log

# Check database
sqlite3 data\state.db
SELECT * FROM processed_skus;

# Check reports
dir reports\
type reports\needs_review_*.txt
```
