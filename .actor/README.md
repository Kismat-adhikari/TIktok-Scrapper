# TikTok Bulk Scraper

Fast and efficient TikTok scraper that extracts video metadata, user profiles, and hashtag content.

## Features

- 🚀 **Fast scraping** with concurrent workers (7-10 workers by default)
- 📊 **Bulk scraping** from URLs or hashtags
- 👤 **Profile data** including bio, email, and social links (optional)
- 🏷️ **Hashtag scraping** to collect videos from trending hashtags
- 📸 **Thumbnail URLs** for all videos
- ⚡ **Real-time results** pushed to Apify dataset

## Input

### Video URLs
List of TikTok video URLs to scrape directly.

Example:
```
https://www.tiktok.com/@username/video/1234567890
https://www.tiktok.com/@another/video/9876543210
```

### Hashtags (Experimental)
⚠️ **Note**: Hashtag scraping is currently being blocked by TikTok's anti-bot protection on Apify infrastructure. For reliable results, use direct video URLs instead.

List of hashtags to scrape videos from (without # symbol).

Example:
```
fyp
viral
trending
```

### Max Videos
Maximum number of videos to scrape. If multiple hashtags are provided, this limit applies to the total across all hashtags.

Default: `100`

### Skip Profile Scraping
Enable this for faster scraping (skips bio, email, social links).
- `true` (default): ~0.7 sec/video
- `false`: ~1.3 sec/video

### Concurrency
Number of concurrent workers (1-25).
- Recommended: 5-10 for best performance
- Higher values may trigger rate limiting

## Output

Each scraped video includes:

- `video_url`: TikTok video URL
- `caption`: Video caption/description
- `hashtags`: Semicolon-separated hashtags
- `likes`: Number of likes
- `comments_count`: Number of comments
- `share_count`: Number of shares
- `username`: Creator username
- `upload_date`: Upload timestamp
- `thumbnail_url`: Video thumbnail image URL
- `bio`: User bio (if profile scraping enabled)
- `email`: Email from bio (if found)
- `instagram_link`: Instagram link (if found)
- `youtube_link`: YouTube link (if found)
- `twitter_link`: Twitter link (if found)
- `other_links`: Other social links (if found)

## Performance

- **With profile scraping disabled**: ~100 videos in 1-2 minutes
- **With profile scraping enabled**: ~100 videos in 2-3 minutes
- **Hashtag collection**: ~200-300 videos per hashtag (TikTok limitation)

## Tips

1. **Use direct video URLs** for most reliable results
2. Use `skipProfiles: true` for maximum speed
3. Keep concurrency at 5-10 for best results
4. Hashtag scraping may not work due to TikTok's anti-bot measures
5. Provide real TikTok video URLs in the format: `https://www.tiktok.com/@username/video/VIDEO_ID`

## Support

For issues or questions, please contact support.
