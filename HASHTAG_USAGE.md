# 🏷️ Hashtag Scraping Guide

## Quick Start

```bash
python scraper.py
```

Choose **Mode 3** when prompted.

## Example Session

```
💡 Choose scraping mode:
   1. Paste URLs (one per line)
   2. Use File (read from urls.txt)
   3. Scrape Hashtag (collect videos from a hashtag)

Mode (1, 2, or 3): 3

🏷️  Hashtag Scraping Mode
Enter hashtag (without #): fyp
Max videos to collect (Enter for unlimited): 50

⚡ Concurrency (simultaneous scrapes)?
   3-5 = Stable, 10+ = Ultra Fast
   Concurrency (Enter for 10): 5
```

## How It Works

### Phase 1: URL Collection (Hashtag Scraping)

1. **Homepage Warm-up** (2-4 seconds)
   - Visits TikTok homepage
   - Small random scroll
   - Simulates normal user behavior

2. **Navigate to Hashtag** (2-4 seconds)
   - Goes to `https://www.tiktok.com/tag/{hashtag}`
   - Waits for page load

3. **Scroll & Collect** (varies by max_videos)
   - Scrolls page gradually
   - Extracts video URLs from current view
   - Random delays between scrolls (1-2.5 seconds)
   - Occasional longer pauses (3-5 seconds)
   - Stops when:
     - Max videos reached, OR
     - No new videos found after 5 scroll attempts

### Phase 2: Video Scraping (Normal Pipeline)

Once URLs are collected, they're passed to the normal scraping pipeline:
- Concurrent processing (your chosen concurrency)
- Proxy rotation
- Retry logic
- Profile data extraction
- Real-time CSV writing

## Anti-Detection Features

### Human-Like Scrolling
- **Variable scroll distances**: 300-600px (mostly), 800-1200px (occasionally)
- **Smooth scrolling**: Uses `behavior: 'smooth'` for natural movement
- **Random delays**: 1-2.5 seconds between scrolls
- **Pause simulation**: Every 5 scrolls, pauses 3-5 seconds (simulates reading)

### Behavioral Patterns
- **Homepage warm-up**: Visits homepage before hashtag (looks like normal browsing)
- **Small random actions**: Random scroll on homepage (200-500px)
- **Realistic timing**: All delays are randomized within ranges

### Technical
- **Proxy rotation**: Uses your proxy pool
- **Resource blocking**: Blocks images/media for speed
- **Headless mode**: Runs in background

## Tips for Success

### 1. Start Small
```
Max videos: 10-20 (test run)
Concurrency: 3-5 (safer)
```

### 2. Use Quality Proxies
- Residential proxies work best
- Datacenter proxies may get blocked faster
- Rotate proxies frequently

### 3. Adjust Based on Results

**If getting blocked:**
- Lower max_videos (try 10-20)
- Lower concurrency (try 3)
- Use better proxies
- Wait between runs

**If working well:**
- Increase max_videos (try 50-100)
- Increase concurrency (try 10+)
- Run multiple hashtags

### 4. Monitor Logs

Watch for these patterns:

**Good signs:**
```
[Hashtag] Progress: 15 videos collected...
[Hashtag] Progress: 30 videos collected...
✓ Successfully scraped https://...
```

**Warning signs:**
```
[Hashtag] No new videos found (attempt 3/5)
✗ Failed to scrape https://... (timeout)
```

## Comparison: Built-in vs Apify

### Built-in Hashtag Scraper (Mode 3)

**Pros:**
- ✅ All-in-one solution
- ✅ No external tools needed
- ✅ Free (just proxy costs)
- ✅ Anti-detection features

**Cons:**
- ⚠️ May get blocked on large scrapes
- ⚠️ Slower URL collection
- ⚠️ Requires good proxies

**Best for:**
- Small to medium scrapes (10-100 videos)
- Testing hashtags
- Quick one-off scrapes

### Apify + Mode 1

**Pros:**
- ✅ More reliable for large scrapes
- ✅ Faster URL collection
- ✅ Apify handles detection

**Cons:**
- ⚠️ Requires Apify account
- ⚠️ Two-step process
- ⚠️ May cost money (free tier limited)

**Best for:**
- Large scrapes (100+ videos)
- Production use
- When built-in gets blocked

## Troubleshooting

### "No videos collected from hashtag"

**Possible causes:**
1. Hashtag doesn't exist
2. Proxy blocked by TikTok
3. Page structure changed

**Solutions:**
- Try different hashtag
- Try different proxy
- Check if hashtag exists on TikTok website

### "Failed to scrape" errors during video scraping

**This is normal!** Some videos may fail due to:
- Deleted videos
- Private accounts
- Proxy issues

**The scraper will:**
- Retry once with different proxy
- Skip after 2 failures
- Continue with remaining videos

### Slow collection

**If URL collection is slow:**
- This is intentional (anti-detection)
- Expect ~2-5 seconds per scroll
- For 50 videos: ~2-5 minutes collection time

**If video scraping is slow:**
- Increase concurrency
- Check proxy speed
- Reduce timeout in code

## Example Output

After running hashtag scraper with max_videos=10:

```
[Hashtag] Warming up - visiting TikTok homepage...
[Hashtag] Navigating to https://www.tiktok.com/tag/fyp...
[Hashtag] Starting to collect videos (max: 10)...
[Hashtag] Progress: 8 videos collected...
[Hashtag] Progress: 12 videos collected...
[Hashtag] Reached max videos limit: 10
[Hashtag] ✓ Collected 10 video URLs from #fyp

🚀 Starting scraping!
   Workers: 5
   Output: scraped_20251121_162045.csv
   Real-time: ENABLED

📝 Progress: 5/10 (0.8/sec)
📝 Progress: 10/10 (0.9/sec)

🎉 COMPLETE!
📊 Results:
   ✅ Success: 9/10
   ❌ Failed: 1/10

⏱️  Performance:
   Time: 11.2 seconds
   Speed: 0.80 URLs/second

💾 Saved to: scraped_20251121_162045.csv
```

## Advanced Usage

### Unlimited Videos

Leave max_videos blank to collect all available videos:

```
Max videos to collect (Enter for unlimited): [press Enter]
```

**Warning:** This may take a long time and increase block risk!

### Custom Delays

Edit `src/scraper/hashtag_scraper.py` to adjust delays:

```python
# Line ~150: Delay between scrolls
await self._human_delay(1000, 2500)  # 1-2.5 seconds

# Line ~155: Occasional longer pause
await self._human_delay(3000, 5000)  # 3-5 seconds
```

### Scroll Distance

Edit `src/scraper/hashtag_scraper.py`:

```python
# Line ~180-185: Scroll distances
scroll_distance = random.randint(300, 600)  # Small scrolls
scroll_distance = random.randint(800, 1200)  # Large scrolls
```

## Best Practices

1. **Test first**: Always test with small limits (10-20 videos)
2. **Monitor logs**: Watch for block patterns
3. **Rotate proxies**: Use multiple proxies
4. **Space out runs**: Don't hammer same hashtag repeatedly
5. **Use Mode 1 for large scrapes**: Apify + Mode 1 is more reliable for 100+ videos
6. **Keep concurrency reasonable**: 3-5 for hashtag mode, 10+ for URL mode

## Need Help?

- Check logs for error messages
- Try different proxy
- Reduce max_videos
- Use Apify + Mode 1 as fallback
- Open GitHub issue with logs
