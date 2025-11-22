# Apify Deployment Guide

## Files Created for Apify

✅ **main.py** - Apify Actor entry point
✅ **Dockerfile** - Docker configuration for Apify
✅ **apify.json** - Apify project configuration
✅ **.actor/actor.json** - Actor metadata
✅ **.actor/input_schema.json** - Input form configuration
✅ **.actor/README.md** - Actor documentation
✅ **.dockerignore** - Files to exclude from Docker build
✅ **requirements.txt** - Updated with `apify>=2.0.0`

## Deployment Steps

### Option 1: Deploy via Apify Console (Recommended)

1. **Create a new Actor on Apify**
   - Go to https://console.apify.com/actors
   - Click "Create new" → "Empty Actor"
   - Name it "tiktok-bulk-scraper"

2. **Connect your GitHub repository**
   - In Actor settings, go to "Source" tab
   - Select "Git repository"
   - Enter your repo URL: `https://github.com/Kismat-adhikari/TIktok-Scrapper.git`
   - Branch: `main`
   - Click "Save"

3. **Build the Actor**
   - Click "Build" button
   - Wait for build to complete (~2-3 minutes)

4. **Test the Actor**
   - Go to "Input" tab
   - Add test URLs or hashtags
   - Click "Start"
   - Check results in "Dataset" tab

### Option 2: Deploy via Apify CLI

1. **Install Apify CLI**
   ```bash
   npm install -g apify-cli
   ```

2. **Login to Apify**
   ```bash
   apify login
   ```

3. **Push to Apify**
   ```bash
   apify push
   ```

## Configuration

### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| urls | array | [] | List of TikTok video URLs |
| hashtags | array | [] | List of hashtags (without #) |
| maxVideos | integer | 100 | Max videos to scrape |
| skipProfiles | boolean | true | Skip profile scraping for speed |
| concurrency | integer | 7 | Number of concurrent workers |

### Example Input

```json
{
  "urls": [
    "https://www.tiktok.com/@username/video/1234567890"
  ],
  "hashtags": ["fyp", "viral"],
  "maxVideos": 100,
  "skipProfiles": true,
  "concurrency": 7
}
```

## Performance on Apify

- **100 videos (skip profiles)**: ~1-2 minutes
- **100 videos (with profiles)**: ~2-3 minutes
- **Memory usage**: ~512MB - 1GB
- **Recommended compute units**: 1-2 CU

## Proxy Configuration

The actor automatically uses **Apify Proxy** (included in your plan):
- Residential proxies for best results
- Automatic rotation
- No manual proxy configuration needed

## Output

Results are automatically saved to Apify Dataset with fields:
- video_url, caption, hashtags
- likes, comments_count, share_count
- username, upload_date, thumbnail_url
- bio, email, social links (if profile scraping enabled)

## Troubleshooting

### Build fails
- Check that all files are committed to git
- Verify Dockerfile syntax
- Check requirements.txt has `apify>=2.0.0`

### Actor times out
- Reduce `maxVideos` or `concurrency`
- Enable `skipProfiles` for faster scraping
- Check Apify compute unit limits

### No results
- Verify input URLs are valid TikTok links
- Check hashtags exist and have videos
- Review Actor logs for errors

## Cost Estimation

Based on Apify pricing:
- **100 videos**: ~$0.01 - $0.02
- **1000 videos**: ~$0.10 - $0.20
- Actual cost depends on profile scraping and concurrency

## Support

For issues:
1. Check Actor logs in Apify Console
2. Review this deployment guide
3. Test locally with `test_apify_local.py`
