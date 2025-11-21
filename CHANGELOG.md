# Changelog

## [2.0.0] - 2024-11-21

### 🎉 Major Features Added

#### Hashtag Scraping (Mode 3)
- **New scraping mode** for collecting videos from TikTok hashtags
- **Human-like behavior** with random delays and smooth scrolling
- **Configurable limits** - set max videos or scrape unlimited
- **Anti-detection features**:
  - Homepage warm-up before hashtag visit
  - Random scroll distances (300-1200px)
  - Variable delays (1-5 seconds)
  - Occasional longer pauses
  - Smooth scroll behavior with easing

#### Enhanced Profile Scraping
- **Twitch username extraction** from bio text
- Patterns supported: "twitch: username", "ttv: username", "twitch.tv/username"
- Twitch links added to `other_links` column
- Works alongside existing Instagram, YouTube, Twitter extraction

### 📝 Files Added

- `src/scraper/hashtag_scraper.py` - Complete hashtag scraping module
- `test_hashtag.py` - Quick test script for hashtag functionality
- `HASHTAG_USAGE.md` - Comprehensive usage guide
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation details
- `QUICK_REFERENCE.md` - Quick reference card
- `CHANGELOG.md` - This file

### 🔧 Files Modified

- `scraper.py` - Added Mode 3 (hashtag scraping)
- `src/scraper/extractor.py` - Added Twitch extraction
- `README.md` - Updated with hashtag features and Twitch info

### ✨ Improvements

- **Seamless integration** - Hashtag URLs feed into existing pipeline
- **No breaking changes** - All existing modes (1 & 2) work unchanged
- **Modular design** - Easy to maintain and extend
- **Comprehensive docs** - Multiple documentation files for different needs

### 🎯 User Experience

**Before:**
- Mode 1: Paste URLs
- Mode 2: File input
- No hashtag support
- No Twitch extraction

**After:**
- Mode 1: Paste URLs ✅
- Mode 2: File input ✅
- Mode 3: Hashtag scraping ✨ NEW
- Twitch extraction ✨ NEW

### 📊 Performance

**Hashtag Scraping:**
- URL collection: ~2-5 seconds per scroll
- 50 videos: ~2-5 minutes collection time
- Total time: ~7-15 minutes for 50 videos (including scraping)

**Video Scraping:**
- Unchanged from v1.0
- 6-8 seconds per video
- Concurrent processing supported

### 🔒 Anti-Detection

**New Features:**
- Homepage warm-up visit
- Random delays between actions
- Variable scroll distances
- Smooth scrolling animation
- Occasional longer pauses (simulates reading)
- Human-like behavior patterns

### 📚 Documentation

**New Guides:**
- Hashtag usage guide with examples
- Quick reference card
- Implementation summary
- Troubleshooting section

**Updated:**
- README with hashtag section
- Feature list updated
- Output columns documented

### 🐛 Bug Fixes

None - this is a feature release

### ⚠️ Known Limitations

- Hashtag scraping may be blocked by TikTok (use quality proxies)
- Slower than using Apify for URL collection
- Requires good proxy quality for best results

### 🔄 Migration Guide

**No migration needed!** This release is 100% backward compatible.

**To use new features:**
1. Run `python scraper.py`
2. Choose Mode 3 for hashtag scraping
3. Twitch extraction works automatically

### 🎓 Learning Resources

- `HASHTAG_USAGE.md` - Detailed usage guide
- `QUICK_REFERENCE.md` - Quick tips and commands
- `README.md` - Full documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical details

---

## [1.0.0] - 2024-11-20

### Initial Release

- URL scraping (Mode 1 & 2)
- Profile data extraction
- Proxy rotation
- Concurrent processing
- CSV output
- 15 data fields
