# Quick Reference Card

## Running the Scraper

```bash
python scraper.py
```

## Modes

| Mode | Description | Best For |
|------|-------------|----------|
| **1** | Paste URLs | Quick scrapes, Apify results |
| **2** | File input (urls.txt) | Saved URL lists |
| **3** | Hashtag scraping | Discovering videos by hashtag |

## Mode 3: Hashtag Scraping

### Input
```
Hashtag: fyp (without #)
Max videos: 50 (or blank for unlimited)
Concurrency: 5 (3-5 safer, 10+ faster)
```

### What Happens
1. Visits homepage (warm-up)
2. Goes to hashtag page
3. Scrolls & collects URLs
4. Scrapes each video
5. Saves to CSV

### Timing
- **URL collection**: ~2-5 minutes for 50 videos
- **Video scraping**: ~5-10 minutes for 50 videos
- **Total**: ~7-15 minutes for 50 videos

## Output Columns (15 total)

### Video Data
- video_url
- caption
- hashtags
- likes
- comments_count
- share_count
- username
- upload_date
- thumbnail_url

### Profile Data
- bio
- email
- instagram_link
- youtube_link
- twitter_link
- other_links (Twitch, Facebook, etc.)

## Tips

### For Best Results
✅ Use quality proxies (residential > datacenter)  
✅ Start with small limits (10-20 videos)  
✅ Use concurrency 3-5 for hashtag mode  
✅ Monitor logs for blocks  

### If Getting Blocked
⚠️ Lower max_videos (try 10-20)  
⚠️ Lower concurrency (try 3)  
⚠️ Try different proxy  
⚠️ Use Apify + Mode 1 instead  

### For Large Scrapes (100+ videos)
💡 Use Apify + Mode 1 (more reliable)  
💡 Or run multiple small hashtag scrapes  
💡 Space out runs (don't hammer same hashtag)  

## Common Issues

### "No videos collected"
- Check hashtag exists
- Try different proxy
- Check logs for errors

### "Failed to scrape" during video scraping
- Normal! Some videos fail
- Scraper retries once
- Continues with remaining videos

### Slow collection
- Intentional (anti-detection)
- ~2-5 seconds per scroll
- Can't be sped up safely

## Files

### Input
- `proxies.txt` - Format: `IP:PORT:USER:PASS`
- `urls.txt` - One URL per line (Mode 2 only)

### Output
- `scraped_YYYYMMDD_HHMMSS.csv` - Results with timestamp

## Anti-Detection Features

✅ Homepage warm-up  
✅ Random delays (1-5s)  
✅ Variable scroll distances  
✅ Smooth scrolling  
✅ Occasional pauses  
✅ Human-like behavior  

## Need Help?

- Read `HASHTAG_USAGE.md` for detailed guide
- Read `README.md` for full documentation
- Check logs for error messages
- Try different proxy if blocked
