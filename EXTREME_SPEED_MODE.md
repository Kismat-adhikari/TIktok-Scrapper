# Extreme Speed Mode - Skip Profile Scraping

## The Bottleneck

**Profile scraping is the slowest part:**
- Video data extraction: ~0.5 seconds
- Profile scraping: ~1-2 seconds
- **Total per video: ~2-3 seconds**

**Solution:** Skip profile scraping for 3-5x speed boost!

## Speed Comparison

### With Profile Scraping (Default)

| Videos | Time | Speed |
|--------|------|-------|
| 10 | ~20s | 0.5/sec |
| 100 | ~60s | 1.67/sec |
| 1000 | ~600s (10 min) | 1.67/sec |

**What you get:**
- ✅ Video URL, caption, hashtags
- ✅ Likes, comments, shares
- ✅ Username, upload date
- ✅ Bio, email, social links

### Without Profile Scraping (SPEED MODE)

| Videos | Time | Speed |
|--------|------|-------|
| 10 | ~5s | 2/sec |
| 100 | ~20s | 5/sec |
| 1000 | ~200s (3.3 min) | 5/sec |

**What you get:**
- ✅ Video URL, caption, hashtags
- ✅ Likes, comments, shares
- ✅ Username, upload date
- ❌ No bio, email, social links

**Result: 3x faster!** 🚀

## How to Use

### When Running Scraper

```bash
python scraper.py
# Mode 3 (Hashtag)
# Hashtags: fyp, viral
# Max: 100

⚡ Profile scraping (bio, email, social links)?
   YES = Full data but slower (~1 min per 100 videos)
   NO = Video data only but MUCH faster (~20 sec per 100 videos)
   Skip profiles for speed? (y/N): y

⚡ SPEED MODE: Skipping profile scraping
```

**Type `y` for extreme speed!**

## What You Lose

**Skipped fields (will be empty in CSV):**
- bio
- email
- instagram_link
- youtube_link
- twitter_link
- other_links

**Still get (video data):**
- video_url ✅
- caption ✅
- hashtags ✅
- likes ✅
- comments_count ✅
- share_count ✅
- username ✅
- upload_date ✅
- thumbnail_url ✅

## When to Use Speed Mode

### ✅ Use Speed Mode When:

1. **You only need video data**
   - Analyzing hashtags, captions, engagement
   - Don't need creator contact info

2. **Scraping large volumes**
   - 500+ videos
   - Time is critical

3. **Testing/prototyping**
   - Quick tests
   - Checking if hashtags work

4. **You'll scrape profiles later**
   - Get video URLs fast
   - Scrape profiles separately if needed

### ❌ Don't Use Speed Mode When:

1. **You need contact info**
   - Influencer outreach
   - Creator research
   - Email collection

2. **Small batches**
   - <50 videos
   - Time difference is minimal

3. **Complete data required**
   - Full dataset needed
   - No second pass planned

## Performance Comparison

### Apify vs This Scraper

**Apify (fastest):**
- 100 videos: ~5 seconds
- Speed: ~20 videos/sec
- Cost: $$$

**This Scraper (Speed Mode):**
- 100 videos: ~20 seconds
- Speed: ~5 videos/sec
- Cost: Just proxies

**This Scraper (Full Mode):**
- 100 videos: ~60 seconds
- Speed: ~1.67 videos/sec
- Cost: Just proxies

**Verdict:**
- Speed Mode is 4x slower than Apify
- But FREE and gets profile data option!
- Full Mode is 12x slower but has unique data

## Real-World Examples

### Example 1: Quick Hashtag Analysis

**Goal:** Analyze 500 videos from #gaming

**Speed Mode:**
```
Time: ~100 seconds (1.7 minutes)
Data: Video stats, captions, hashtags
Perfect for: Trend analysis
```

**Full Mode:**
```
Time: ~300 seconds (5 minutes)
Data: Everything including profiles
Overkill for: Just analyzing trends
```

### Example 2: Influencer Outreach

**Goal:** Find 100 creators with contact info

**Speed Mode:**
```
Time: ~20 seconds
Data: No email/social links ❌
Result: Need to run again
```

**Full Mode:**
```
Time: ~60 seconds
Data: Email, Instagram, etc. ✅
Result: Ready to contact
```

### Example 3: Large Dataset

**Goal:** Scrape 5000 videos for research

**Speed Mode:**
```
Time: ~1000 seconds (16.7 minutes)
Data: Core video metrics
Perfect for: Statistical analysis
```

**Full Mode:**
```
Time: ~3000 seconds (50 minutes)
Data: Everything
Better if: Need complete dataset
```

## Tips for Maximum Speed

### 1. Use Speed Mode

```
Skip profiles? y
```

**Result:** 3x faster

### 2. Use More Hashtags

```
Instead of: fyp (1 hashtag)
Use: fyp, viral, trending, foryou (4 hashtags)
```

**Why:** Parallel collection from multiple sources

### 3. Increase Concurrency

Edit `scraper.py` line ~160:
```python
concurrency = 30  # Instead of auto-calculated
```

**Warning:** Higher block risk!

### 4. Use Fast Proxies

- Residential proxies > Datacenter
- Low latency proxies
- Test proxy speed first

### 5. Skip Retries

Edit `src/types.py`:
```python
max_retries: int = 0  # No retries
```

**Warning:** More failures!

## Combining All Speed Tricks

**Maximum speed configuration:**
1. ✅ Skip profiles (y)
2. ✅ High concurrency (20-30)
3. ✅ Fast proxies
4. ✅ Multiple hashtags
5. ✅ No retries

**Result:**
- 100 videos: ~10-15 seconds
- 1000 videos: ~100-150 seconds (1.7-2.5 min)
- **~7-10 videos/sec!**

**Approaching Apify speeds!** 🚀

## Summary

| Mode | 100 Videos | Profile Data | Best For |
|------|-----------|--------------|----------|
| **Speed Mode** | ~20s | ❌ | Large volumes, quick analysis |
| **Full Mode** | ~60s | ✅ | Contact info, complete data |
| **Apify** | ~5s | ❌ | Maximum speed, has budget |

**Recommendation:**
- Need contact info? → Full Mode
- Just video data? → Speed Mode
- Have budget? → Apify

**Speed Mode is the sweet spot for most use cases!** ⚡
