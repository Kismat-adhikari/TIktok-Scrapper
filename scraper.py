"""
🚀 TikTok Bulk URL Scraper
Scrapes individual video URLs with full metadata
Ultra-fast with real-time results!
"""

import asyncio
import logging
import sys
from datetime import datetime
from playwright.async_api import async_playwright

from src.config.loader import ConfigLoader
from src.proxy.manager import RoundRobinProxyManager
from src.scraper.browser_pool import BrowserPool
from src.scraper.extractor import DataExtractor
from src.scraper.engine import ScraperEngine
from src.scraper.hashtag_scraper import HashtagScraper
from src.output.csv_writer import CSVWriter
from src.types import BrowserOptions, ScraperOptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


async def main():
    """Main execution function."""
    
    print("\n" + "=" * 70)
    print("🚀 TikTok Bulk URL Scraper")
    print("=" * 70)
    
    print("\n💡 Choose scraping mode:")
    print("   1. Paste URLs (one per line)")
    print("   2. Use File (read from urls.txt)")
    print("   3. Scrape Hashtag (collect videos from a hashtag)")
    
    mode = input("\nMode (1, 2, or 3): ").strip()
    
    urls = []
    
    # Load proxies first
    config_loader = ConfigLoader()
    proxies = await config_loader.load_proxies('proxies.txt')
    proxy_manager = RoundRobinProxyManager(proxies)
    logger.info(f"🔄 Loaded {len(proxies)} proxies")
    
    if mode == "1":
        # PASTE URLs MODE
        print("\n📝 Paste TikTok URLs (one per line, press Enter twice when done):")
        while True:
            line = input().strip()
            if not line:
                if urls:
                    break
                continue
            if 'tiktok.com' in line:
                urls.append(line)
                print(f"   ✓ Added ({len(urls)} total)")
    
    elif mode == "2":
        # FILE MODE
        urls = await config_loader.load_urls('urls.txt')
        logger.info(f"📂 Loaded {len(urls)} URLs from urls.txt")
    
    elif mode == "3":
        # HASHTAG MODE
        print("\n🏷️  Hashtag Scraping Mode")
        print("   Enter one hashtag or multiple separated by commas")
        print("   Example: fyp, viral, trending")
        hashtag_input = input("\nHashtags (without #): ").strip()
        
        if not hashtag_input:
            logger.error("❌ No hashtag provided")
            sys.exit(1)
        
        # Parse hashtags (split by comma if multiple)
        if ',' in hashtag_input:
            hashtags = [h.strip() for h in hashtag_input.split(',') if h.strip()]
        else:
            hashtags = [hashtag_input]
        
        max_videos_input = input("Max videos TOTAL across all hashtags (Enter for unlimited): ").strip()
        max_videos_total = None
        if max_videos_input:
            try:
                max_videos_total = int(max_videos_input)
                if max_videos_total < 1:
                    max_videos_total = None
            except:
                logger.warning("⚠️  Invalid number, using unlimited")
                max_videos_total = None
        
        # Ask about profile scraping (SPEED BOOST)
        print("\n⚡ Profile scraping (bio, email, social links)?")
        print("   YES = Full data but slower (~1 min per 100 videos)")
        print("   NO = Video data only but MUCH faster (~20 sec per 100 videos)")
        skip_profiles_input = input("   Skip profiles for speed? (y/N): ").strip().lower()
        skip_profiles = skip_profiles_input in ['y', 'yes']
        
        if skip_profiles:
            logger.info("⚡ SPEED MODE: Skipping profile scraping")
        
        # Calculate per-hashtag limit to reach total (AGGRESSIVE)
        if max_videos_total and len(hashtags) > 1:
            # Distribute evenly across hashtags with generous buffer for duplicates
            per_hashtag_limit = int((max_videos_total / len(hashtags)) * 1.5)  # 50% buffer
            logger.info(f"🏷️  Target: {max_videos_total} TOTAL videos from {len(hashtags)} hashtag(s)")
            logger.info(f"   Strategy: Collect ~{per_hashtag_limit} per hashtag, then dedupe and trim")
        else:
            per_hashtag_limit = max_videos_total
            logger.info(f"🏷️  Collecting videos from {len(hashtags)} hashtag(s) (max {max_videos_total or 'unlimited'} total)")
        
        # Initialize browser and hashtag scraper (FAST mode)
        browser_options = BrowserOptions(headless=True, timeout=15000)
        browser_pool = BrowserPool(browser_options)
        await browser_pool.initialize()
        
        hashtag_scraper = HashtagScraper()
        
        # Collect URLs from all hashtags with TOTAL limit enforcement
        urls = []
        for i, hashtag in enumerate(hashtags):
            # Check if we've already reached the total limit
            if max_videos_total and len(urls) >= max_videos_total:
                logger.info(f"✓ Already collected {len(urls)} videos (reached total limit), skipping remaining hashtags")
                break
            
            # Calculate how many more videos we need (AGGRESSIVE)
            if max_videos_total:
                remaining = max_videos_total - len(urls)
                # Be aggressive: collect more than needed to account for duplicates
                # Use per_hashtag_limit unless we're close to the end
                if len(hashtags) - i <= 2:  # Last 2 hashtags
                    # Push hard to reach the limit
                    this_hashtag_limit = remaining + int(remaining * 0.3)  # 30% buffer
                else:
                    this_hashtag_limit = per_hashtag_limit
                
                logger.info(f"\n📍 Processing #{hashtag} ({i+1}/{len(hashtags)})")
                logger.info(f"   Current: {len(urls)}, Need: {remaining}, Will collect: up to {this_hashtag_limit}")
            else:
                this_hashtag_limit = None
                logger.info(f"\n📍 Processing #{hashtag} ({i+1}/{len(hashtags)})...")
            
            # Get a proxy for this hashtag
            proxy = proxy_manager.get_next_proxy()
            proxy_str = f"{proxy.ip}:{proxy.port}"
            
            # Create context and scrape hashtag
            context = await browser_pool.create_context(proxy)
            try:
                hashtag_urls = await hashtag_scraper.scrape_hashtag(context, hashtag, this_hashtag_limit, proxy_str)
                urls.extend(hashtag_urls)
                
                logger.info(f"✓ Collected {len(hashtag_urls)} from #{hashtag}, total so far: {len(urls)}")
            finally:
                await browser_pool.close_context(context)
        
        if not urls:
            logger.error("❌ No videos collected from any hashtag")
            await browser_pool.close()
            sys.exit(1)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        urls = unique_urls
        
        # FINAL TRIM: Enforce exact total limit after deduplication
        if max_videos_total and len(urls) > max_videos_total:
            logger.info(f"⚠️  Collected {len(urls)} unique videos, trimming to exactly {max_videos_total}")
            urls = urls[:max_videos_total]
        
        logger.info(f"\n✅ Final count: {len(urls)} unique video URLs from {len(hashtags)} hashtag(s)")
        
        if max_videos_total:
            if len(urls) < max_videos_total:
                logger.warning(f"⚠️  Collected {len(urls)}/{max_videos_total} videos (some hashtags may have fewer videos available)")
            else:
                logger.info(f"✓ Successfully collected exactly {max_videos_total} videos!")
    
    else:
        logger.error("❌ Invalid mode selected")
        sys.exit(1)
    
    if not urls:
        logger.error("❌ No URLs to scrape")
        sys.exit(1)
    
    # Initialize skip_profiles for non-hashtag modes
    if mode != "3":
        skip_profiles = False
    
    # Categorize URLs
    video_urls = [url for url in urls if '/video/' in url]
    profile_urls = [url for url in urls if '/video/' not in url and '@' in url]
    
    logger.info(f"\n📊 Analysis:")
    logger.info(f"   Video URLs: {len(video_urls)}")
    logger.info(f"   Profile URLs: {len(profile_urls)}")
    logger.info(f"   Total: {len(urls)}")
    
    # Auto-calculate optimal concurrency based on video count (AGGRESSIVE)
    if len(urls) <= 10:
        concurrency = 5  # Increased from 3
    elif len(urls) <= 30:
        concurrency = 10  # Increased from 5
    elif len(urls) <= 100:
        concurrency = 15  # Increased from 10
    else:
        concurrency = 20  # Increased from 15
    
    logger.info(f"⚡ Auto-selected concurrency: {concurrency} workers (optimized for {len(urls)} videos)")
    
    # Initialize scraper (skip if already initialized in hashtag mode)
    if mode != "3":
        browser_options = BrowserOptions(headless=True, timeout=15000)  # Reduced timeout
        browser_pool = BrowserPool(browser_options)
        await browser_pool.initialize()
    
    extractor = DataExtractor(skip_profiles=skip_profiles if mode == "3" else False)
    scraper_options = ScraperOptions(max_retries=1, timeout=15000, concurrency=concurrency)  # Reduced timeout
    engine = ScraperEngine(proxy_manager, browser_pool, extractor, scraper_options)
    
    # CSV writer
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"scraped_{timestamp}.csv"
    
    csv_writer = CSVWriter(output_filename)
    await csv_writer.write_header()
    
    logger.info("\n" + "=" * 70)
    logger.info(f"🚀 Starting scraping!")
    logger.info(f"   Workers: {concurrency}")
    logger.info(f"   Output: {output_filename}")
    logger.info(f"   Real-time: ENABLED")
    logger.info("=" * 70 + "\n")
    
    # Track progress
    success_count = 0
    failed_count = 0
    start_time = datetime.now()
    
    # Real-time callback (SHOWS EVERY VIDEO)
    async def on_result(result):
        nonlocal success_count, failed_count
        if result.success and result.data:
            await csv_writer.write_row(result.data)
            success_count += 1
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = success_count / elapsed if elapsed > 0 else 0
            # Show progress for EVERY video (not just every 5)
            logger.info(f"✓ [{success_count}/{len(urls)}] Scraped in {elapsed:.1f}s ({rate:.2f}/sec)")
        else:
            failed_count += 1
            logger.warning(f"✗ [{success_count + failed_count}/{len(urls)}] Failed: {result.url[:50]}...")
    
    # Scrape!
    results = await engine.scrape_urls(urls, scraper_options.concurrency, on_result_callback=on_result)
    
    await csv_writer.close()
    await browser_pool.close()
    
    # Final stats
    total_time = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "=" * 70)
    print("🎉 COMPLETE!")
    print("=" * 70)
    print(f"\n📊 Results:")
    print(f"   ✅ Success: {success_count}/{len(urls)}")
    print(f"   ❌ Failed: {failed_count}/{len(urls)}")
    print(f"\n⏱️  Performance:")
    print(f"   Time: {total_time:.1f} seconds")
    print(f"   Speed: {success_count/total_time:.2f} URLs/second")
    print(f"\n💾 Saved to: {output_filename}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
