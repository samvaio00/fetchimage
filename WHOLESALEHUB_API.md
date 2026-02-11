# WholesaleHub Replit API Integration

## Overview

The Image Fetcher Bot integrates with the WholesaleHub Replit app at `https://warnergears.replit.app` to automatically upload product images by SKU.

## Authentication

The API uses **session-based authentication** (not API keys). The bot:

1. Logs in with admin credentials to get a `connect.sid` session cookie
2. Uses this cookie for all subsequent image upload requests
3. Automatically re-authenticates if the session expires

## Configuration

Add these to your `.env` file:

```env
REPLIT_API_URL=https://warnergears.replit.app
REPLIT_EMAIL=warnergears@gmail.com
REPLIT_PASSWORD=Choti00shaf#
```

## API Endpoints Used

### 1. Login (Authentication)
```
POST https://warnergears.replit.app/api/auth/login
Content-Type: application/json

{
  "email": "warnergears@gmail.com",
  "password": "Choti00shaf#"
}
```

**Response**: Session cookie `connect.sid` is set

### 2. Upload Image by SKU
```
POST https://warnergears.replit.app/api/admin/products/upload-image
Cookie: connect.sid=<session-cookie-value>
Content-Type: multipart/form-data

Form fields:
  - image: (file) JPEG, PNG, GIF, or WebP (max 10MB)
  - sku: (string) Product SKU (case-insensitive)
```

**Success Response**:
```json
{
  "success": true,
  "message": "Image uploaded successfully",
  "filename": "1424313000372912001.png",
  "path": "/product-images/1424313000372912001.png"
}
```

**Error Responses**:
- `400` - Missing SKU, no image file, or invalid file type
- `404` - No product found with that SKU
- `401/403` - Not authenticated or not admin/staff

## How the Bot Works

1. **Fetch SKUs** (Manual for now)
   - Currently: You provide a list of SKUs to process
   - Future: API endpoint to list products without images

2. **Search for Images**
   - Extracts keywords from SKU name
   - Searches Unsplash, Pexels, Pixabay
   - Scores images by relevance

3. **Upload to WholesaleHub**
   - Validates image (format, size, dimensions)
   - Logs in if not authenticated
   - Uploads via `/api/admin/products/upload-image`
   - Passes SKU + image file

4. **Track State**
   - Successful uploads logged in SQLite
   - Failed SKUs saved to `reports/needs_review_*.txt`
   - No reprocessing of completed SKUs

## Important Notes

### Session Management
- Session cookie expires after inactivity
- Bot automatically re-authenticates on 401/403 errors
- One retry attempt after re-authentication

### SKU Matching
- SKU matching is case-insensitive on server
- Server logs all uploads to `bot-upload-log.txt`

### Image Requirements
- **Formats**: JPEG, PNG, GIF, WebP
- **Max Size**: 10MB
- **Bot Validation**: Min 800x600, aspect ratio 0.5-2.0

### Upload Behavior
- Uploaded images take precedence over Zoho-sourced images
- `imageSource` field set to `'uploaded'` after success
- Images saved as `public/product-images/<zohoItemId>.<ext>`

## Getting SKU List

**Current Approach**: Manual list
- Create a text file with SKU codes (one per line)
- Read and process via custom script

**Future Enhancement**: API endpoint
- Request: `GET /api/admin/products?hasImage=false&limit=50`
- Response: List of products without images

## Testing

Test the integration:

```bash
# 1. Set up .env with credentials
cp .env.example .env
# Edit .env with actual credentials

# 2. Test authentication
python -c "from src.api.replit_client import ReplitClient; \
client = ReplitClient('https://warnergears.replit.app', 'warnergears@gmail.com', 'Choti00shaf#'); \
print('Auth success' if client.authenticate() else 'Auth failed')"

# 3. Run bot in test mode (manual SKU list)
python src/main.py --run-once
```

## Troubleshooting

### "Authentication failed - no session cookie"
- Check email/password in `.env`
- Verify network connectivity to Replit app
- Check if admin account is active

### "404 - No product found with that SKU"
- SKU doesn't exist in WholesaleHub database
- Check SKU spelling/format
- SKU added to `needs_review` report

### "401/403 - Not authenticated"
- Session expired - bot will auto re-authenticate
- If persists, check admin permissions

### "400 - Invalid file type"
- Only JPEG, PNG, GIF, WebP supported
- Check image validation passed before upload

## Security Notes

- ⚠️ **Credentials in .env**: Never commit `.env` to git
- ✅ `.env` is in `.gitignore`
- ✅ Use `.env.example` as template
- ⚠️ Session cookies are temporary - not stored persistently
- ✅ Bot creates new session on each run

## Future Enhancements

1. **Product Listing API**
   - GET endpoint to fetch SKUs without images
   - Pagination support for large catalogs

2. **Batch Upload**
   - Upload multiple images in single request
   - Reduce API calls

3. **Webhook Integration**
   - Trigger bot when new products added
   - Real-time image attachment

4. **Image Source Preference**
   - Let WholesaleHub specify preferred image sources
   - Custom keyword hints per product category
