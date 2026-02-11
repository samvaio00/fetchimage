# Quick Start Guide - Run Your First Test in 20 Minutes

This guide will get you from zero to running your first test with 10 real images.

---

## ⏱️ Time Required: 20 minutes

- **Step 1-2**: Get API keys (15 min)
- **Step 3-4**: Configure and test (3 min)
- **Step 5**: Run test (2 min)

---

## 📋 Step 1: Get Free API Keys (15 minutes)

You need 3 free API keys. Open these links in your browser:

### 1️⃣ Unsplash (50 requests/hour - free)
- Go to: https://unsplash.com/developers
- Click "Register as a developer"
- Create app → Copy the **Access Key**

### 2️⃣ Pexels (200 requests/hour - free)
- Go to: https://www.pexels.com/api/
- Click "Get Started"
- Accept terms → Copy the **API Key**

### 3️⃣ Pixabay (5000 requests/hour - free)
- Go to: https://pixabay.com/api/docs/
- Click "Get your API key"
- Copy the **API Key**

**Detailed instructions**: See `docs/GET_API_KEYS.md`

---

## 🔧 Step 2: Configure Your .env File (2 minutes)

1. **Copy the example**:
   ```bash
   copy .env.example .env
   ```

2. **Edit `.env`** and paste your keys:
   ```env
   # WholesaleHub credentials
   REPLIT_API_URL=https://warnergears.replit.app
   REPLIT_EMAIL=your_admin_email@wholesalehub.com
   REPLIT_PASSWORD=your_password
   
   # Paste your API keys here
   UNSPLASH_ACCESS_KEY=paste_unsplash_access_key_here
   PEXELS_API_KEY=paste_pexels_key_here
   PIXABAY_API_KEY=paste_pixabay_key_here
   
   # Leave these as-is
   LOG_LEVEL=INFO
   ENVIRONMENT=production
   DATABASE_PATH=./data/state.db
   SCHEDULE_ENABLED=true
   SCHEDULE_INTERVAL_HOURS=6
   ```

3. **Save the file**

---

## ✅ Step 3: Test API Connectivity (1 minute)

Verify all your API keys work:

```bash
python scripts\test_apis.py
```

Expected output:
```
Testing API connections...
✅ Unsplash API: Connected
✅ Pexels API: Connected  
✅ Pixabay API: Connected
✅ WholesaleHub API: Authenticated
```

If you see ❌ errors, double-check your API keys in `.env`

---

## 📝 Step 4: Prepare Test SKUs (1 minute)

### Option A: Use sample SKUs (quick test)

Edit `test_skus.txt` with 10 SKU IDs from your WholesaleHub:

```
MEN-SHIRT-BLUE-L
LAPTOP-DELL-15IN
PHONE-CASE-IPHONE
HEADPHONES-WIRELESS
BACKPACK-TRAVEL
SHOES-RUNNING-NIKE
WATCH-DIGITAL-SPORTS
SUNGLASSES-AVIATOR
CAMERA-CANON-EOS
TABLET-SAMSUNG-10INCH
```

### Option B: Use inline SKUs

You can also pass SKUs directly in the command:

```bash
python scripts\test_with_manual_skus.py --skus "SKU1,SKU2,SKU3" --limit 10
```

---

## 🚀 Step 5: Run Your First Test! (2 minutes)

```bash
python scripts\test_with_manual_skus.py --file test_skus.txt --limit 10
```

**What happens:**
1. Bot loads your configuration
2. Authenticates with WholesaleHub
3. For each SKU:
   - Extracts keywords (e.g., "MEN-SHIRT-BLUE-L" → "men", "shirt", "blue", "large")
   - Searches Unsplash → Pexels → Pixabay for matching images
   - Finds best match (relevance score 0.6+)
   - Downloads and validates image
   - Uploads to WholesaleHub
4. Saves results to database
5. Generates report for SKUs with no images found

---

## 📊 Check Your Results

### 1. Console Output
You'll see real-time progress:
```
Processing SKU: MEN-SHIRT-BLUE-L
Keywords: men, shirt, blue, large
✅ SUCCESS: Image attached
   Source: UNSPLASH
   Relevance: 0.85
```

### 2. WholesaleHub
Log into https://warnergears.replit.app and verify images are attached!

### 3. Logs
```bash
type logs\app.log
```

### 4. Database
```bash
sqlite3 data\state.db
SELECT * FROM processed_skus;
```

### 5. Reports (if any SKUs failed)
```bash
dir reports\
type reports\needs_review_*.txt
```

---

## 🎉 Success Criteria

✅ **8-10 out of 10** SKUs should get images successfully  
✅ Images should be **relevant** to the product names  
✅ Images should appear in **WholesaleHub**  
✅ No errors in `logs/app.log`  

---

## 🔄 Run It Again

If you want to reprocess the same SKUs:

```bash
python scripts\test_with_manual_skus.py --file test_skus.txt --limit 10 --reset-state
```

The `--reset-state` flag clears previous results so you can test again.

---

## ⚡ Next Steps

Once your test is successful:

### 1. Process More SKUs
```bash
python src\main.py --run-once
```

This will fetch SKUs from WholesaleHub (once the API endpoint is implemented) and process up to 50 at a time.

### 2. Run on Schedule
```bash
python src\main.py --schedule --interval 6
```

Bot will run automatically every 6 hours.

### 3. Fine-Tune Settings
Edit `config/config.yaml` to adjust:
- Minimum relevance score (default: 0.6)
- Image dimensions (default: 800x600 minimum)
- Max file size (default: 5MB)
- Batch size (default: 50 SKUs)

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| **"Error loading configuration"** | Make sure `.env` exists and has all keys |
| **"Authentication failed"** | Check WholesaleHub email/password in `.env` |
| **"401 Unauthorized"** (Unsplash) | You copied the Secret Key instead of Access Key |
| **"No suitable image found"** | SKU name is too generic, try more descriptive names |
| **"Product not found"** | SKU doesn't exist in WholesaleHub |
| **"429 Rate Limit"** | You exceeded hourly limit, wait 1 hour |

**Full troubleshooting guide**: See `docs/TESTING_GUIDE.md`

---

## 📚 Documentation

- **`docs/GET_API_KEYS.md`** - Detailed API key setup instructions
- **`docs/TESTING_GUIDE.md`** - Comprehensive testing guide
- **`WHOLESALEHUB_API.md`** - WholesaleHub API documentation
- **`README.md`** - Full project documentation

---

**Ready? Let's go! 🚀**

```bash
# 1. Get API keys (15 min)
# 2. Copy .env.example to .env and add keys (2 min)
# 3. Test connectivity
python scripts\test_apis.py

# 4. Edit test_skus.txt with your SKUs (1 min)
# 5. Run test!
python scripts\test_with_manual_skus.py --file test_skus.txt --limit 10
```
