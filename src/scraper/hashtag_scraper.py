"""Hashtag scraper for collecting video URLs from TikTok hashtag pages."""

import asyncio
import logging
import random
from typing import List, Set
from playwright.async_api import Page, BrowserContext
from src.types import ProxyConfig

logger = logging.getLogger(__name__)


class HashtagScraper:
    """Scrapes video URLs from TikTok hashtag pages with human-like behavior."""
    
    def __init__(self):
        """Initialize hashtag scraper."""
        self.collected_urls: Set[str] = set()
    
    async def scrape_hashtag(
        self,
        context: BrowserContext,
        hashtag: str,
        max_videos: int = None,
        proxy_str: str = "unknown"
    ) -> List[str]:
        """
        Scrape video URLs from a hashtag page.
        
        Args:
            context: Browser context with proxy
            hashtag: Hashtag name (without #)
            max_videos: Maximum number of videos to collect (None = all)
            proxy_str: Proxy string for logging
            
        Returns:
            List of video URLs
        """
        self.collected_urls.clear()
        
        try:
            page = await context.new_page()
            
            # Step 1: Warm-up - visit homepage first (human-like behavior)
            logger.info(f"[Hashtag] Warming up - visiting TikTok homepage...")
            await self._visit_homepage(page)
            
            # Step 2: Navigate to hashtag page
            hashtag_url = f"https://www.tiktok.com/tag/{hashtag}"
            logger.info(f"[Hashtag] Navigating to {hashtag_url} with proxy {proxy_str}")
            
            await page.goto(hashtag_url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load - increased for better detection
            await self._human_delay(2000, 3000)
            
            # Try to wait for video elements to appear
            try:
                await page.wait_for_selector('a[href*="/video/"]', timeout=5000)
                logger.info(f"[Hashtag] Video elements detected on page")
            except:
                logger.warning(f"[Hashtag] No video elements detected immediately, will try scrolling...")
            
            # Step 3: Debug - check page content
            page_content = await page.evaluate('''() => {
                return {
                    title: document.title,
                    hasVideoLinks: document.querySelectorAll('a[href*="/video/"]').length,
                    totalLinks: document.querySelectorAll('a').length,
                    bodyText: document.body ? document.body.innerText.substring(0, 200) : 'No body'
                };
            }''')
            logger.info(f"[Hashtag] Page info: {page_content['hasVideoLinks']} video links, {page_content['totalLinks']} total links")
            
            # Step 4: Scroll and collect video URLs
            logger.info(f"[Hashtag] Starting to collect videos (max: {max_videos or 'unlimited'})...")
            await self._scroll_and_collect(page, max_videos)
            
            # If no videos found, save screenshot for debugging
            if len(self.collected_urls) == 0:
                try:
                    screenshot_path = f"debug_hashtag_{hashtag}.png"
                    await page.screenshot(path=screenshot_path)
                    logger.warning(f"[Hashtag] No videos found. Screenshot saved to {screenshot_path}")
                    
                    # Also save HTML for inspection
                    html_path = f"debug_hashtag_{hashtag}.html"
                    html_content = await page.content()
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    logger.warning(f"[Hashtag] HTML saved to {html_path} for inspection")
                except Exception as e:
                    logger.warning(f"[Hashtag] Could not save debug files: {e}")
            
            logger.info(f"[Hashtag] ✓ Collected {len(self.collected_urls)} video URLs from #{hashtag}")
            
            await page.close()
            return list(self.collected_urls)
            
        except Exception as e:
            logger.error(f"[Hashtag] ✗ Failed to scrape hashtag #{hashtag}: {e}")
            return list(self.collected_urls)
    
    async def _visit_homepage(self, page: Page) -> None:
        """
        Visit TikTok homepage briefly as warm-up (optimized for speed).
        
        Args:
            page: Playwright page object
        """
        try:
            await page.goto("https://www.tiktok.com", wait_until='domcontentloaded', timeout=30000)
            await self._human_delay(800, 1500)  # Reduced from 1500-3000
            
            # Quick small scroll on homepage
            scroll_amount = random.randint(200, 400)
            await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            await self._human_delay(400, 800)  # Reduced from 800-1500
            
        except Exception as e:
            logger.warning(f"[Hashtag] Homepage warm-up failed: {e}")
    
    async def _scroll_and_collect(self, page: Page, max_videos: int = None) -> None:
        """
        Scroll page and collect video URLs - tries hard to reach max_videos.
        
        Args:
            page: Playwright page object
            max_videos: Maximum number of videos to collect
        """
        no_new_videos_count = 0
        scroll_count = 0
        
        # AGGRESSIVE: Try harder based on how far we are from target
        if max_videos:
            # More attempts for larger targets
            if max_videos >= 100:
                max_no_new_attempts = 10  # Try 10 times for 100+
            elif max_videos >= 50:
                max_no_new_attempts = 8   # Try 8 times for 50+
            else:
                max_no_new_attempts = 5   # Try 5 times for smaller
        else:
            max_no_new_attempts = 5
        
        logger.info(f"[Hashtag] Will try {max_no_new_attempts} scroll attempts if no new videos found")
        
        while True:
            # STRICT: Check limit BEFORE extracting more
            if max_videos and len(self.collected_urls) >= max_videos:
                logger.info(f"[Hashtag] ✓ Reached max videos limit: {max_videos}")
                break
            
            # Extract video URLs from current view
            previous_count = len(self.collected_urls)
            await self._extract_video_urls(page, max_videos)
            new_count = len(self.collected_urls)
            
            # STRICT: Check again after extraction
            if max_videos and new_count >= max_videos:
                logger.info(f"[Hashtag] ✓ Collected {max_videos} videos (limit reached)")
                break
            
            # Check if we found new videos
            if new_count == previous_count:
                no_new_videos_count += 1
                logger.info(f"[Hashtag] No new videos (attempt {no_new_videos_count}/{max_no_new_attempts})")
                
                # Give up only after max attempts
                if no_new_videos_count >= max_no_new_attempts:
                    logger.warning(f"[Hashtag] Stopping at {new_count} videos (TikTok stopped showing more)")
                    break
            else:
                no_new_videos_count = 0
                logger.info(f"[Hashtag] Progress: {new_count}/{max_videos or '∞'} videos...")
            
            # Aggressive scrolling to load more videos
            scroll_count += 1
            await self._human_scroll(page, scroll_count)
            
            # Minimal delay for speed (but still looks human)
            await self._human_delay(300, 700)  # Even faster
    
    async def _extract_video_urls(self, page: Page, max_videos: int = None) -> None:
        """
        Extract video URLs from current page view with strict limit enforcement.
        
        Args:
            page: Playwright page object
            max_videos: Maximum number of videos to collect
        """
        try:
            # Extract video URLs using multiple selectors (TikTok changes structure often)
            urls = await page.evaluate('''() => {
                // Try multiple selector strategies
                let links = [];
                
                // Strategy 1: Direct video links
                links = Array.from(document.querySelectorAll('a[href*="/video/"]'));
                
                // Strategy 2: Try data attributes
                if (links.length === 0) {
                    links = Array.from(document.querySelectorAll('a[data-e2e="challenge-item"]'));
                }
                
                // Strategy 3: Try div containers with video links
                if (links.length === 0) {
                    const containers = document.querySelectorAll('div[data-e2e="challenge-item-list"] a');
                    links = Array.from(containers);
                }
                
                // Strategy 4: Any link with @username/video pattern
                if (links.length === 0) {
                    links = Array.from(document.querySelectorAll('a[href*="/@"]')).filter(a => 
                        a.href.includes('/video/')
                    );
                }
                
                return links
                    .map(link => link.href)
                    .filter(href => href && href.includes('/video/') && href.includes('tiktok.com'))
                    .map(href => href.split('?')[0]); // Remove query params
            }''')
            
            if len(urls) > 0:
                logger.info(f"[Hashtag] Found {len(urls)} video links on page")
            
            # Add new URLs to collection with strict limit
            for url in urls:
                # STRICT: Stop immediately if limit reached
                if max_videos and len(self.collected_urls) >= max_videos:
                    break
                    
                if url not in self.collected_urls:
                    self.collected_urls.add(url)
                    
        except Exception as e:
            logger.warning(f"[Hashtag] Failed to extract URLs: {e}")
    
    async def _human_scroll(self, page: Page, scroll_count: int) -> None:
        """
        Perform human-like scrolling with randomization.
        
        Args:
            page: Playwright page object
            scroll_count: Current scroll iteration
        """
        try:
            # Randomize scroll distance (smaller scrolls are more human-like)
            if scroll_count % 3 == 0:
                # Occasional larger scroll
                scroll_distance = random.randint(800, 1200)
            else:
                # Mostly smaller scrolls
                scroll_distance = random.randint(300, 600)
            
            # Smooth scroll with easing
            await page.evaluate(f'''
                window.scrollBy({{
                    top: {scroll_distance},
                    behavior: 'smooth'
                }});
            ''')
            
            # Wait for scroll to complete
            await self._human_delay(500, 1000)
            
        except Exception as e:
            logger.warning(f"[Hashtag] Scroll failed: {e}")
    
    async def _human_delay(self, min_ms: int, max_ms: int) -> None:
        """
        Random delay to simulate human behavior.
        
        Args:
            min_ms: Minimum delay in milliseconds
            max_ms: Maximum delay in milliseconds
        """
        delay = random.randint(min_ms, max_ms) / 1000.0
        await asyncio.sleep(delay)
