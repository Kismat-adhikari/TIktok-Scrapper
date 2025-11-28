"""Apify Actor main entry point for TikTok Bulk Scraper."""

import asyncio
import logging
from apify import Actor
from src.config.loader import ConfigLoader
from src.scraper.browser_pool import BrowserPool
from src.scraper.extractor import DataExtractor
from src.types import BrowserOptions, ScrapingResult
from playwright.async_api import async_playwright

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
        skip_profiles = actor_input.get('skipProfiles', False)
        concurrency = actor_input.get('concurrency', 5)
        custom_proxies = actor_input.get('customProxies', [])
        
        # Convert proxy format if needed (host:port:user:pass -> http://user:pass@host:port)
        formatted_proxies = []
        for proxy in custom_proxies:
            if proxy.startswith('http://') or proxy.startswith('https://'):
                formatted_proxies.append(proxy)
            else:
                # Parse host:port:user:pass format
                parts = proxy.split(':')
                if len(parts) == 4:
                    host, port, user, password = parts
                    formatted_proxies.append(f"http://{user}:{password}@{host}:{port}")
                elif len(parts) == 2:
                    formatted_proxies.append(f"http://{proxy}")
                else:
                    logger.warning(f"Invalid proxy format: {proxy}")
        
        custom_proxies = formatted_proxies if formatted_proxies else custom_proxies
        
        logger.info(f"Starting TikTok scraper with {len(urls)} URLs and {len(hashtags)} hashtags")
        
        # Collect URLs from hashtags if provided
        all_urls = list(urls)
        
        if hashtags:
            from src.scraper.hashtag_scraper import HashtagScraper
            
            # Setup proxy configuration
            if custom_proxies:
                logger.info(f"Using {len(custom_proxies)} custom proxies")
                proxy_index = 0
            else:
                proxy_config = await Actor.create_proxy_configuration()
                logger.info("Using Apify proxies")
            
            # Initialize browser for hashtag scraping
            browser_options = BrowserOptions(headless=True, timeout=60000)
            browser_pool = BrowserPool(browser_options)
            await browser_pool.initialize()
            
            # Initialize hashtag scraper
            hashtag_scraper = HashtagScraper()
            
            for hashtag in hashtags:
                logger.info(f"Collecting videos from #{hashtag}")
                try:
                    # Get proxy
                    if custom_proxies:
                        proxy_url = custom_proxies[proxy_index % len(custom_proxies)]
                        proxy_index += 1
                    else:
                        proxy_url = await proxy_config.new_url()
                    
                    # Create browser context with proxy
                    context = await browser_pool.browser.new_context(
                        proxy={"server": proxy_url}
                    )
                    
                    # Scrape hashtag with context
                    hashtag_urls = await hashtag_scraper.scrape_hashtag(
                        context=context,
                        hashtag=hashtag,
                        max_videos=max_videos // len(hashtags) if len(hashtags) > 1 else max_videos,
                        proxy_str=proxy_url
                    )
                    
                    await context.close()
                    
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
        
        # Setup proxy configuration
        if custom_proxies:
            logger.info(f"Using {len(custom_proxies)} custom proxies for scraping")
            proxy_index = 0
        else:
            proxy_config = await Actor.create_proxy_configuration()
            logger.info("Using Apify proxies for scraping")
        
        # Initialize browser pool
        browser_options = BrowserOptions(
            headless=True,
            block_resources=['image', 'media', 'font', 'stylesheet'],
            timeout=60000
        )
        browser_pool = BrowserPool(browser_options)
        browser_pool.playwright = await async_playwright().start()
        browser_pool.browser = await browser_pool.playwright.chromium.launch(
            headless=True,
            args=['--disable-dev-shm-usage', '--no-sandbox']
        )
        
        # Initialize extractor
        extractor = DataExtractor(skip_profiles=skip_profiles)
        
        # Scrape all URLs with Apify proxies
        logger.info(f"Starting scraping with {concurrency} concurrent workers")
        results = []
        semaphore = asyncio.Semaphore(concurrency)
        
        async def scrape_single_url(url: str):
            nonlocal proxy_index
            async with semaphore:
                try:
                    # Get proxy for this request
                    if custom_proxies:
                        proxy_url = custom_proxies[proxy_index % len(custom_proxies)]
                        proxy_index += 1
                    else:
                        proxy_url = await proxy_config.new_url()
                    logger.info(f"Scraping {url}")
                    
                    # Create context with Apify proxy
                    context = await browser_pool.browser.new_context(
                        proxy={"server": proxy_url},
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        viewport={"width": 1920, "height": 1080}
                    )
                    context.set_default_timeout(60000)
                    
                    # Block resources
                    async def block_resources(route):
                        resource_type = route.request.resource_type
                        if resource_type in ['image', 'media', 'font', 'stylesheet']:
                            await route.abort()
                        else:
                            await route.continue_()
                    await context.route("**/*", block_resources)
                    
                    try:
                        page = await context.new_page()
                        
                        # Try with networkidle first, fallback to domcontentloaded
                        try:
                            await page.goto(url, wait_until='networkidle', timeout=30000)
                        except:
                            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                        
                        # Wait for TikTok JSON data to be available (with fallback)
                        try:
                            await page.wait_for_selector('#__UNIVERSAL_DATA_FOR_REHYDRATION__', timeout=5000)
                        except:
                            # If JSON not found, wait a bit and continue anyway
                            await page.wait_for_timeout(3000)
                        
                        # Debug: Check page content
                        page_content = await page.content()
                        if 'captcha' in page_content.lower():
                            logger.warning(f"Captcha detected on {url}")
                        if '__UNIVERSAL_DATA_FOR_REHYDRATION__' not in page_content:
                            logger.warning(f"JSON data not found on {url}, page might be blocked")
                        
                        # Extract metadata
                        if '/video/' in url:
                            metadata = await extractor.extract_metadata(page, url)
                        else:
                            metadata = await extractor.extract_profile_only(page, url)
                        
                        logger.info(f"✓ Successfully scraped {url}")
                        results.append(ScrapingResult(success=True, url=url, proxy_used=proxy_url, retry_count=0, data=metadata))
                    finally:
                        await context.close()
                        
                except Exception as e:
                    logger.error(f"✗ Failed to scrape {url}: {e}")
                    results.append(ScrapingResult(success=False, url=url, proxy_used="", retry_count=0, error=str(e)))
        
        # Scrape all URLs concurrently
        tasks = [scrape_single_url(url) for url in all_urls]
        await asyncio.gather(*tasks, return_exceptions=True)
        
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
