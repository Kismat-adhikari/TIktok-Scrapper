# 🚀 TikTok Bulk URL Scraper

Simple, fast TikTok scraper for bulk URL processing. Scrapes video metadata and profile details.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Add proxies to proxies.txt
# Format: IP:PORT:USERNAME:PASSWORD

# 3. Run scraper
python scraper.py

# 4. Choose mode:
#    Mode 1: Paste URLs
#    Mode 2: Read from urls.txt
```

## What It Scrapes

**Video Data:**
- URL, caption, hashtags
- Likes, comments, shares
- Upload date, thumbnail

**Profile Data:**
- Bio, email
- Social links (Instagram, YouTube, Twitter)
- Followers, following, total likes

## Output

Results saved to `scraped_TIMESTAMP.csv` with 15 columns of data.

## Features

✅ Fast concurrent processing (10+ workers)
✅ Real-time CSV writing
✅ Automatic proxy rotation
✅ Retry logic with different proxies
✅ Full metadata extraction

## Example

```bash
python scraper.py
Mode: 2
# Reads urls.txt, scrapes all videos
# Output: scraped_20251121_160000.csv
```

That's it! Simple and effective. 🎯
