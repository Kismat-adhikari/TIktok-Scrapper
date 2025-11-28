# TikTok Bulk Scraper

Fast and efficient TikTok scraper that extracts video metadata, profile information, and social media links.

## Features

- Scrape TikTok videos by URL or hashtag
- Extract video metadata (caption, likes, comments, shares, etc.)
- Extract profile data (bio, email, Instagram, YouTube, Twitter links)
- Fast concurrent scraping with Apify proxies
- Automatic retry logic and error handling

## Input

- **Video URLs**: List of TikTok video URLs to scrape
- **Hashtags**: List of hashtags to collect videos from (without # symbol)
- **Max Videos per Hashtag**: Maximum number of videos to collect from each hashtag (default: 100)
- **Skip Profile Scraping**: Skip profile data extraction for faster scraping (default: false)
- **Concurrency**: Number of concurrent workers (default: 5, max: 20)

## Output

The actor outputs a dataset with the following fields for each video:

- `video_url`: URL of the video
- `caption`: Video caption/description
- `hashtags`: Hashtags used in the video (semicolon-separated)
- `likes`: Number of likes
- `comments_count`: Number of comments
- `share_count`: Number of shares
- `username`: TikTok username
- `upload_date`: Upload timestamp
- `thumbnail_url`: Video thumbnail URL
- `bio`: User bio/description
- `email`: Email address (if found in bio)
- `instagram_link`: Instagram profile link
- `youtube_link`: YouTube channel link
- `twitter_link`: Twitter profile link
- `other_links`: Other social media links (semicolon-separated)

## Usage Tips

- For faster scraping, enable "Skip Profile Scraping"
- Increase concurrency for faster processing (but uses more resources)
- Use hashtags to discover and scrape trending content
- Apify proxies are automatically used to avoid rate limiting

## Example Input

```json
{
  "urls": [
    "https://www.tiktok.com/@user/video/123456789"
  ],
  "hashtags": ["fyp", "viral"],
  "maxVideos": 50,
  "skipProfiles": false,
  "concurrency": 5
}
```
