# Hashtag Scraping Troubleshooting

## Issue: 0 Videos Collected

### What I Fixed

1. **Better Selectors** - Added 4 different strategies to find video links
2. **Better Page Load Detection** - Wait for `networkidle` instead of just `domcontentloaded`
3. **Longer Initial Wait** - Increased to 2-3 seconds for content to load
4. **Debug Mode** - Saves screenshot + HTML when no videos found
5. **Better Logging** - Shows how many links found on page

### About "Unlimited"

**Q: What does unlimited mean?**
**A:** It means scrape ALL videos from the hashtag until no more are found.

- Could be 50 videos
- Could be 500 videos  
- Could be 5000 videos
- Stops when TikTok stops showing more

**Recommendation:** Always set a limit (10, 50, 100) unless you really want everything.

### Why 0 Videos?

**Possible causes:**

1. **TikTok Blocking Proxy**
   - Your proxy might be blocked
   - Try different proxy
   - Check if proxy works for regular URLs (Mode 1)

2. **TikTok Changed Page Structure**
   - TikTok updates their site frequently
   - Selectors might need updating
   - Check debug files (see below)

3. **Hashtag Doesn't Exist**
   - Typo in hashtag name
   - Hashtag has no videos
   - Try popular hashtag like "fyp" or "foryou"

4. **Captcha/Login Required**
   - TikTok might be asking for login
   - Check debug screenshot
   - Try better proxy

### How to Debug

**Run the scraper and check these files:**

1. **`debug_hashtag_FYP.png`** - Screenshot of what the scraper sees
2. **`debug_hashtag_FYP.html`** - Full HTML of the page

**What to look for:**

✅ **Good signs:**
- See video thumbnails in screenshot
- HTML contains `/video/` links
- No captcha or login page

❌ **Bad signs:**
- Blank page in screenshot
- "Sign up" or "Log in" text
- Captcha challenge
- "This content isn't available" message

### Quick Fixes

#### Fix 1: Try Different Hashtag

```bash
# Instead of: FYP, Valorant
# Try: fyp, foryou, viral, trending
```

**Note:** Lowercase usually works better!

#### Fix 2: Test Your Proxies

```bash
python scraper.py
# Mode 1 (Paste URLs)
# Paste a known working video URL
# If this works, proxies are OK
```

#### Fix 3: Check Proxy Quality

**Your proxies might be:**
- Blocked by TikTok
- Too slow
- Datacenter (residential work better)

**Solution:** Get better proxies or use fewer concurrent workers.

#### Fix 4: Increase Wait Times

Edit `src/scraper/hashtag_scraper.py`:

```python
# Line ~65: Increase wait after page load
await self._human_delay(3000, 5000)  # Was 2000-3000

# Line ~70: Increase selector wait
await page.wait_for_selector('a[href*="/video/"]', timeout=10000)  # Was 5000
```

### Testing Steps

**1. Test with known working hashtag:**
```bash
python scraper.py
Mode: 3
Hashtag: foryou
Max: 5
```

**2. Check debug files:**
```bash
# Look at screenshot
open debug_hashtag_foryou.png

# Search HTML for video links
grep -i "video" debug_hashtag_foryou.html
```

**3. If still 0 videos:**
- Check screenshot for captcha/login
- Try Mode 1 with direct URLs to test proxies
- Try different proxy provider

### Alternative: Use Apify

If hashtag scraping keeps failing:

1. Go to https://apify.com/clockworks/tiktok-hashtag-scraper
2. Enter hashtag, get URLs
3. Use Mode 1 to scrape those URLs

**This is more reliable** because Apify handles the hashtag page complexity.

### Logs to Watch

**Good logs:**
```
[Hashtag] Video elements detected on page
[Hashtag] Found 15 video links on page
[Hashtag] Progress: 5/10 videos...
[Hashtag] ✓ Collected 10 video URLs
```

**Bad logs:**
```
[Hashtag] No video elements detected immediately
[Hashtag] Found 0 video links on page
[Hashtag] No more new videos. Stopping at 0 videos.
[Hashtag] No videos found. Screenshot saved to debug_hashtag_FYP.png
```

### Getting Help

If still not working, provide:

1. Debug screenshot (`debug_hashtag_*.png`)
2. Full logs from terminal
3. Hashtag you're trying
4. Proxy type (residential/datacenter)

## Summary

- ✅ **Fixed:** Better selectors, longer waits, debug mode
- ✅ **"Unlimited":** Means scrape all videos (set a limit!)
- ✅ **Debug:** Check screenshot + HTML files
- ✅ **Alternative:** Use Apify + Mode 1 if hashtag mode fails

Try running again with a popular hashtag like "foryou" or "viral" (lowercase) and check the debug files!
