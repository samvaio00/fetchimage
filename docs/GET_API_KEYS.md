# How to Get Free API Keys for Image Sources

This guide will walk you through obtaining free API keys from Unsplash, Pexels, and Pixabay.

---

## 1. Unsplash API Key

**Free Tier**: 50 requests per hour

### Steps:
1. Go to **https://unsplash.com/developers**
2. Click **"Register as a developer"** (top right)
3. Create an Unsplash account if you don't have one
4. Once logged in, click **"Your apps"** → **"New Application"**
5. Accept the API Guidelines and Terms
6. Fill in the application details:
   - **Application name**: "ImageFetcher Bot" (or any name)
   - **Description**: "Autonomous bot to fetch product images"
7. Click **"Create Application"**
8. You'll see your **Access Key** and **Secret Key**
9. **Copy the "Access Key"** - this is what you need for the .env file

### Usage Limits:
- **Demo**: 50 requests/hour
- **Production** (requires approval): 5,000 requests/hour

---

## 2. Pexels API Key

**Free Tier**: 200 requests per hour (no daily limit!)

### Steps:
1. Go to **https://www.pexels.com/api/**
2. Click **"Get Started"** button
3. Create a Pexels account (or log in with Google/Facebook)
4. Once logged in, you'll be redirected to the API page
5. Click **"Your API Key"** in the top navigation
6. Accept the API Terms of Service
7. Your **API Key** will be displayed immediately
8. **Copy the API Key** - this is what you need for the .env file

### Usage Limits:
- **200 requests per hour**
- **20,000 requests per month**
- No daily limit

---

## 3. Pixabay API Key

**Free Tier**: 5,000 requests per hour (very generous!)

### Steps:
1. Go to **https://pixabay.com/api/docs/**
2. Scroll down and click **"Get your API key"**
3. Create a Pixabay account if you don't have one
4. After creating/logging in, you'll be redirected to the API documentation page
5. Your **API Key** will be shown in a highlighted box near the top of the page
6. **Copy the API Key** - this is what you need for the .env file

### Usage Limits:
- **5,000 requests per hour** (per IP address)
- No daily/monthly limits

---

## 4. Creating Your .env File

Once you have all three API keys, create a `.env` file in the project root:

```bash
# Copy the .env.example file
cp .env.example .env
```

Then edit `.env` and add your keys:

```env
# Replit WholesaleHub API Configuration
REPLIT_API_URL=https://warnergears.replit.app
REPLIT_EMAIL=your_admin_email@example.com
REPLIT_PASSWORD=your_admin_password

# Image Source APIs
UNSPLASH_ACCESS_KEY=YOUR_UNSPLASH_ACCESS_KEY_HERE
PEXELS_API_KEY=YOUR_PEXELS_API_KEY_HERE
PIXABAY_API_KEY=YOUR_PIXABAY_API_KEY_HERE

# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=production

# Database
DATABASE_PATH=./data/state.db

# Scheduling
SCHEDULE_ENABLED=true
SCHEDULE_INTERVAL_HOURS=6
```

---

## Quick Links:

- **Unsplash**: https://unsplash.com/developers
- **Pexels**: https://www.pexels.com/api/
- **Pixabay**: https://pixabay.com/api/docs/

---

## Testing Your API Keys

After setting up your `.env` file, you can test the API connections:

```bash
python scripts/test_apis.py
```

This will verify that all your API keys are working correctly before running the full bot.

---

## Troubleshooting

### Unsplash:
- **401 Unauthorized**: Check that you copied the Access Key (not Secret Key)
- **403 Forbidden**: Your app may not be approved yet (Demo access works immediately)

### Pexels:
- **401 Unauthorized**: Make sure you accepted the Terms of Service
- **429 Rate Limit**: You've exceeded 200 requests/hour, wait and try again

### Pixabay:
- **400 Bad Request**: Check that your API key is correct
- **429 Rate Limit**: Very rare (5000/hr limit), but wait if it happens

---

**Estimated Time**: 10-15 minutes to get all three API keys
