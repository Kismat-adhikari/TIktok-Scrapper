"""Scraper engine orchestrating the scraping process."""

import asyncio
import logging
from typing import List
from src.types import ScrapingResult, ProxyConfig, ScraperOptions, VideoMetadata
from src.scraper.browser_pool import BrowserPool
from src.scraper.extractor import DataExtractor
from src.proxy.manager import RoundRobinProxyManager

logger = logging.getLogger(__name__)


class ScraperEngine:
    """Orchestrates TikTok scraping with retry logic and concurrency."""
    
    def __init__(
        self,
        proxy_manager: RoundRobinProxyManager,
        browser_pool: BrowserPool,
        extractor: DataExtractor,
        options: ScraperOptions = None
    ):
        """
        Initialize scraper engine.
        
        Args:
            proxy_manager: Proxy rotation manager
            browser_pool: Browser pool for contexts
            extractor: Data extractor
            options: Scraper options
        """
        self.proxy_manager = proxy_manager
        self.browser_pool = browser_pool
        self.extractor = extractor
        self.options = options or ScraperOptions()
    
    async def scrape_urls(self, urls: List[str], concurrency: int = 3, on_result_callback=None) -> List[ScrapingResult]:
        """
        Scrape multiple URLs with concurrency.
        
        Args:
            urls: List of URLs to scrape
            concurrency: Number of concurrent workers
            on_result_callback: Optional callback function called after each URL is scraped
            
        Returns:
            List of scraping results
        """
        results = []
        semaphore = asyncio.Semaphore(concurrency)
        
        async def scrape_with_semaphore(url: str):
            async with semaphore:
                result = await self.scrape_url(url, self.proxy_manager.get_next_proxy(), 0)
                results.append(result)
                
                # Call callback immediately after scraping (real-time)
                if on_result_callback:
                    await on_result_callback(result)
                
                return result
        
        # Process all URLs concurrently
        tasks = [scrape_with_semaphore(url) for url in urls]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def scrape_url(
        self,
        url: str,
        proxy: ProxyConfig,
        retry_count: int
    ) -> ScrapingResult:
        """
        Scrape single URL with retry logic.
        
        Args:
            url: URL to scrape
            proxy: Proxy to use
            retry_count: Current retry count
            
        Returns:
            Scraping result
        """
        proxy_str = f"{proxy.ip}:{proxy.port}"
        
        try:
            logger.info(f"Scraping {url} with proxy {proxy_str}")
            
            # Create browser context
            context = await self.browser_pool.create_context(proxy)
            
            try:
                # Create page and navigate
                page = await context.new_page()
                
                # Navigate to URL with aggressive timeout
                await page.goto(url, wait_until='domcontentloaded', timeout=self.options.timeout)
                
                # Detect URL type and extract accordingly
                if '/video/' in url:
                    # Video URL - extract video + profile data
                    metadata = await self.extractor.extract_metadata(page, url)
                else:
                    # Profile URL - extract profile data only
                    metadata = await self.extractor.extract_profile_only(page, url)
                
                logger.info(f"✓ Successfully scraped {url}")
                
                return ScrapingResult(
                    success=True,
                    url=url,
                    proxy_used=proxy_str,
                    retry_count=retry_count,
                    data=metadata
                )
                
            finally:
                # Always close context
                await self.browser_pool.close_context(context)
        
        except Exception as e:
            logger.error(f"✗ Failed to scrape {url}: {e}")
            
            # Retry logic
            if retry_count < self.options.max_retries:
                logger.info(f"Retrying {url} (attempt {retry_count + 1})")
                
                # Mark proxy as failed and get new one
                self.proxy_manager.mark_proxy_failed(proxy)
                new_proxy = self.proxy_manager.get_next_proxy()
                
                # Retry with new proxy
                return await self.scrape_url(url, new_proxy, retry_count + 1)
            
            # Max retries reached
            return ScrapingResult(
                success=False,
                url=url,
                proxy_used=proxy_str,
                retry_count=retry_count,
                error=str(e)
            )
