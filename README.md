# 🚀 TikTok Bulk URL Scraper - Ultra Fast Edition

High-speed TikTok metadata scraper with 3 input modes. No login, no API keys, no video downloads.

## ✨ Features

- ✅ **3 Input Modes**: Paste URLs, File input, or Hashtag scraping
- ✅ **Hashtag Scraping**: Collect videos from hashtags with human-like behavior
- ✅ **Ultra Fast**: 10+ concurrent workers, real-time CSV writing
- ✅ **Proxy Rotation**: Automatic round-robin with failure handling
- ✅ **Profile Scraping**: Extracts bio, email, social links (Instagram, YouTube, Twitter, Twitch)
- ✅ **15 Data Fields**: Views, likes, comments, shares, profile info, and more
- ✅ **Real-time Progress**: See results as they're scraped
- ✅ **No Login Required**: Direct scraping without authentication
- ✅ **Anti-Detection**: Human-like scrolling, random delays, homepage warm-up

## 🎯 Quick Start

### 1. Install

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Add Proxies

**proxies.txt** - Format: `IP:PORT:USERNAME:PASSWORD`
```
1.2.3.4:8080:user1:pass1
5.6.7.8:9090:user2:pass2
```

### 3. Run

```bash
python scraper.py
```

### 4. Choose Mode

- **Mode 1: Paste URLs**
  - Paste URLs one per line
  - Press Enter twice when done
  
- **Mode 2: File Input**
  - Read from urls.txt
  - Good for saved URL lists
  
- **Mode 3: Hashtag Scraping** ⭐ NEW!
  - Enter hashtag (without #)
  - Set max videos or leave blank for unlimited
  - Human-like scrolling with anti-detection

## 🎯 Hashtag Scraping

### Built-in Hashtag Scraper (Mode 3)

The scraper now includes built-in hashtag scraping with anti-detection features:

```bash
python scraper.py
# Choose Mode 3
# Enter hashtag: fyp
# Max videos: 50 (or leave blank for unlimited)
```

**Anti-Detection Features:**
- Homepage warm-up before hashtag visit
- Human-like scrolling with random distances
- Random delays between actions (1-5 seconds)
- Smooth scroll behavior with easing
- Occasional longer pauses (simulates reading)
- Small random scrolls on homepage

**How it works:**
1. Visits TikTok homepage first (warm-up)
2. Navigates to hashtag page
3. Scrolls gradually, collecting video URLs
4. Stops when max reached or no new videos
5. Passes URLs to normal scraping pipeline

**Tips:**
- Use quality proxies to avoid blocks
- Start with smaller limits (10-50 videos)
- Lower concurrency (3-5) is safer
- If blocked, try different proxy or wait

### Alternative: Apify + Mode 1 (More Reliable)

For larger scrapes or if Mode 3 gets blocked:

1. Get URLs with Apify (https://apify.com/clockworks/tiktok-hashtag-scraper)
2. Run `python scraper.py` → Mode 1
3. Paste URLs, set concurrency to 10+

**Result**: 100 fully-scraped videos in ~2.5 minutes total! 🚀

## 📊 Output

Results saved to timestamped CSV with 15 columns:
- video_url
- caption
- hashtags (semicolon-separated)
- likes
- comments_count
- share_count
- username
- upload_date
- thumbnail_url
- bio
- email
- instagram_link
- youtube_link
- twitter_link
- other_links (includes Twitch, Facebook, LinkedIn, etc.)

## Configuration

Edit `src/main.py` to adjust:
- `concurrency`: Number of parallel workers (default: 3)
- `timeout`: Timeout per URL in milliseconds (default: 8000)
- `max_retries`: Retry attempts per URL (default: 1)

## Performance

- **Speed**: 6-8 seconds per URL
- **Throughput**: ~100 URLs in 10 minutes (with 3 workers)
- **Memory**: <500MB RAM usage
- **Proxy Rotation**: Every request + forced every 14 URLs

## What Gets Scraped

**Video Data:**
✅ Video URL  
✅ Caption/Description  
✅ Hashtags  
✅ Like count  
✅ Comment count  
✅ Share count  
✅ Username  
✅ Upload date  
✅ Thumbnail URL  

**Profile Data:**
✅ Bio/Description  
✅ Email (if in bio)  
✅ Instagram link  
✅ YouTube link  
✅ Twitter/X link  
✅ Twitch link (extracted from bio text)  
✅ Other social links (Facebook, LinkedIn, Discord, etc.)  

**Not Included:**
❌ No video downloads  
❌ No comments extraction  
❌ No login required  

## Error Handling

- Failed URLs are automatically retried once with a different proxy
- URLs that fail twice are skipped
- Failed URLs are NOT written to output.csv
- Scraping continues even if some URLs fail

## Logging

Minimal logging shows:
- URL being processed
- Proxy being used
- Success/failure status
- Final summary

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test suite
python -m pytest tests/test_config_properties.py -v
```

## Project Structure

```
src/
├── config/              # Configuration loading
├── proxy/               # Proxy management
├── scraper/
│   ├── browser_pool.py  # Browser context management
│   ├── engine.py        # Scraping orchestration
│   ├── extractor.py     # Data extraction logic
│   └── hashtag_scraper.py  # Hashtag scraping with anti-detection
├── output/              # CSV writer
├── types.py             # Type definitions
└── main.py              # Entry point

tests/                   # Property-based and unit tests
scraper.py               # Main CLI entry point
```

## Notes

- TikTok selectors may change over time - update selectors in `src/scraper/extractor.py` if needed
- Use high-quality proxies for best results
- Respect rate limits and TikTok's terms of service
- This tool is for educational purposes only

## License

MIT
