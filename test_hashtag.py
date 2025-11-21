"""Quick test for hashtag scraper functionality."""

import asyncio
from src.scraper.hashtag_scraper import HashtagScraper
from src.scraper.browser_pool import BrowserPool
from src.proxy.manager import RoundRobinProxyManager
from src.config.loader import ConfigLoader
from src.types import BrowserOptions


async def test_hashtag():
    """Test hashtag scraping."""
    
    # Load proxies
    config_loader = ConfigLoader()
    proxies = await config_loader.load_proxies('proxies.txt')
    proxy_manager = RoundRobinProxyManager(proxies)
    
    # Initialize browser
    browser_options = BrowserOptions(headless=True, timeout=30000)
    browser_pool = BrowserPool(browser_options)
    await browser_pool.initialize()
    
    # Get proxy
    proxy = proxy_manager.get_next_proxy()
    proxy_str = f"{proxy.ip}:{proxy.port}"
    
    # Create context
    context = await browser_pool.create_context(proxy)
    
    try:
        # Test hashtag scraper
        hashtag_scraper = HashtagScraper()
        urls = await hashtag_scraper.scrape_hashtag(
            context=context,
            hashtag="fyp",
            max_videos=5,
            proxy_str=proxy_str
        )
        
        print(f"\n✅ Collected {len(urls)} URLs:")
        for i, url in enumerate(urls, 1):
            print(f"  {i}. {url}")
        
    finally:
        await browser_pool.close_context(context)
        await browser_pool.close()


if __name__ == "__main__":
    asyncio.run(test_hashtag())
