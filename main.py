"""Apify Actor main entry point for TikTok Bulk Scraper."""

import asyncio
import logging
from apify import Actor
from src.config.loader import ConfigLoader
from src.proxy.manager import RoundRobinProxyManager
from src.scraper.browser_pool import BrowserPool
from src.scraper.extractor import DataExtractor
from src.scraper.engine import ScraperEngine
from src.types import BrowserOptions, ScraperOptions, ProxyConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


async def main():
    """Main Apify Actor function."""
    async with Actor:
        # Get input from Apify
        actor_input = await Actor.get_input() or {}
        
        # Extract configuration
        urls = actor_input.get('urls', [])
        hashtags = actor_input.get('hashtags', [])
        max_videos = actor_input.get('maxVideos', 100)
        skip_profiles = actor_input.get('skipProfiles', True)
        concurrency = actor_input.get('concurrency', 7)
        
        logger.info(f"Starting TikTok scraper with {len(urls)} URLs and {len(hashtags)} hashtags")
        
        # Collect URLs from hashtags if provided
        all_urls = list(urls)
        
        if hashtags:
            from src.scraper.hashtag_scraper import HashtagScraper
            
            # Get Apify proxy configuration
            proxy_config = await Actor.create_proxy_configuration()
            
            # Initialize browser for hashtag scraping
            browser_options = BrowserOptions(headless=True, timeout=15000)
            browser_pool = BrowserPool(browser_options)
            await browser_pool.initialize()
            
            hashtag_scraper = HashtagScraper(browser_pool)
            
            for hashtag in hashtags:
                logger.info(f"Collecting videos from #{hashtag}")
                try:
                    # Use Apify proxy
                    proxy_url = await proxy_config.new_url()
                    
                    # Create a ProxyConfig from Apify proxy URL
                    # Parse proxy URL format: http://username:password@host:port
                    from urllib.parse import urlparse
                    parsed = urlparse(proxy_url)
                    
                    proxy = ProxyConfig(
                        ip=parsed.hostname,
                        port=parsed.port,
                        username=parsed.username or '',
                        password=parsed.password or ''
                    )
                    
                    hashtag_urls = await hashtag_scraper.scrape_hashtag(
                        hashtag=hashtag,
                        max_videos=max_videos // len(hashtags) if len(hashtags) > 1 else max_videos,
                        proxy=proxy
                    )
                    all_urls.extend(hashtag_urls)
                    logger.info(f"Collected {len(hashtag_urls)} URLs from #{hashtag}")
                except Exception as e:
                    logger.error(f"Failed to collect from #{hashtag}: {e}")
            
            await browser_pool.close()
        
        # Remove duplicates
        all_urls = list(set(all_urls))
        logger.info(f"Total unique URLs to scrape: {len(all_urls)}")
        
        if not all_urls:
            logger.warning("No URLs to scrape")
            return
        
        # Initialize scraper components
        # Use Apify proxy configuration
        proxy_config = await Actor.create_proxy_configuration()
        
        # Create proxy manager with Apify proxies
        class ApifyProxyManager:
            def __init__(self, proxy_config):
                self.proxy_config = proxy_config
                self.current_proxy = None
            
            def get_next_proxy(self):
                # This will be called synchronously, so we return a cached proxy
                # The actual proxy rotation happens in Apify's proxy configuration
                if not self.current_proxy:
                    # Create a dummy proxy config - Apify handles the actual proxy
                    self.current_proxy = ProxyConfig(
                        ip="apify-proxy",
                        port=8000,
                        username="auto",
                        password="auto"
                    )
                return self.current_proxy
            
            def mark_proxy_failed(self, proxy):
                pass  # Apify handles proxy rotation
            
            def force_rotation(self):
                pass  # Apify handles proxy rotation
            
            def has_available_proxies(self):
                return True
        
        proxy_manager = ApifyProxyManager(proxy_config)
        
        # Initialize browser pool
        browser_options = BrowserOptions(
            headless=True,
            block_resources=['image', 'media', 'font', 'stylesheet'],
            timeout=15000
        )
        browser_pool = BrowserPool(browser_options)
        await browser_pool.initialize()
        
        # Initialize extractor
        extractor = DataExtractor(skip_profiles=skip_profiles)
        
        # Initialize scraper engine
        scraper_options = ScraperOptions(
            max_retries=1,
            timeout=15000,
            concurrency=concurrency
        )
        engine = ScraperEngine(proxy_manager, browser_pool, extractor, scraper_options)
        
        # Scrape all URLs
        logger.info(f"Starting scraping with {concurrency} concurrent workers")
        results = await engine.scrape_urls(all_urls, concurrency)
        
        # Push results to Apify dataset
        success_count = 0
        failed_count = 0
        
        for result in results:
            if result.success and result.data:
                # Convert VideoMetadata to dict for Apify
                data_dict = {
                    'video_url': result.data.video_url,
                    'caption': result.data.caption,
                    'hashtags': result.data.hashtags,
                    'likes': result.data.likes,
                    'comments_count': result.data.comments_count,
                    'share_count': result.data.share_count,
                    'username': result.data.username,
                    'upload_date': result.data.upload_date,
                    'thumbnail_url': result.data.thumbnail_url,
                    'bio': result.data.bio,
                    'email': result.data.email,
                    'instagram_link': result.data.instagram_link,
                    'youtube_link': result.data.youtube_link,
                    'twitter_link': result.data.twitter_link,
                    'other_links': result.data.other_links
                }
                
                await Actor.push_data(data_dict)
                success_count += 1
            else:
                failed_count += 1
        
        # Cleanup
        await browser_pool.close()
        
        # Log summary
        logger.info("=" * 60)
        logger.info("Scraping Complete!")
        logger.info(f"✓ Successful: {success_count}")
        logger.info(f"✗ Failed: {failed_count}")
        logger.info(f"Total: {len(results)}")
        logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
