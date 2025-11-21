"""Main entry point for TikTok bulk scraper."""

import asyncio
import logging
import sys
from pathlib import Path

from src.config.loader import ConfigLoader
from src.proxy.manager import RoundRobinProxyManager
from src.scraper.browser_pool import BrowserPool
from src.scraper.extractor import DataExtractor
from src.scraper.engine import ScraperEngine
from src.output.csv_writer import CSVWriter
from src.types import BrowserOptions, ScraperOptions, ConfigurationError, ResourceExhaustionError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


async def main():
    """Main execution function."""
    
    logger.info("=" * 60)
    logger.info("TikTok Bulk URL Scraper")
    logger.info("=" * 60)
    
    # Initialize components
    config_loader = ConfigLoader()
    browser_pool = None
    csv_writer = None
    
    try:
        # Get URLs from user input
        print("\n📝 Enter TikTok video URLs:")
        print("   - For single URL: paste the URL and press Enter")
        print("   - For multiple URLs: separate with commas")
        print("   Example: https://www.tiktok.com/@user/video/123, https://www.tiktok.com/@user/video/456\n")
        
        url_input = input("URLs: ").strip()
        
        if not url_input:
            logger.error("No URLs provided. Exiting.")
            sys.exit(1)
        
        # Parse URLs (split by comma if multiple)
        if ',' in url_input:
            urls = [url.strip() for url in url_input.split(',') if url.strip()]
        else:
            urls = [url_input]
        
        # Validate URLs
        urls = [url for url in urls if 'tiktok.com' in url]
        
        if not urls:
            logger.error("No valid TikTok URLs found. Exiting.")
            sys.exit(1)
        
        logger.info(f"Loaded {len(urls)} URL(s) from input")
        
        # Load configuration
        logger.info("Loading proxy configuration...")
        proxies = await config_loader.load_proxies('proxies.txt')
        
        logger.info(f"Loaded {len(urls)} URLs")
        logger.info(f"Loaded {len(proxies)} proxies")
        
        # Initialize proxy manager
        proxy_manager = RoundRobinProxyManager(proxies)
        
        # Initialize browser pool with optimized settings
        browser_options = BrowserOptions(
            headless=True,
            block_resources=['image', 'media', 'font', 'stylesheet'],
            timeout=30000  # Increased to 30 seconds
        )
        browser_pool = BrowserPool(browser_options)
        await browser_pool.initialize()
        
        # Initialize data extractor
        extractor = DataExtractor()
        
        # Initialize scraper engine
        scraper_options = ScraperOptions(
            max_retries=1,
            timeout=30000,
            concurrency=3  # Process 3 URLs at once
        )
        engine = ScraperEngine(proxy_manager, browser_pool, extractor, scraper_options)
        
        # Initialize CSV writer with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"output_{timestamp}.csv"
        csv_writer = CSVWriter(output_filename)
        await csv_writer.write_header()
        
        logger.info("=" * 60)
        logger.info(f"Starting scraping with {scraper_options.concurrency} concurrent workers...")
        logger.info(f"Output will be saved to: {output_filename}")
        logger.info("=" * 60)
        
        # Scrape all URLs
        results = await engine.scrape_urls(urls, scraper_options.concurrency)
        
        # Write successful results to CSV
        success_count = 0
        failed_count = 0
        
        for result in results:
            if result.success and result.data:
                await csv_writer.write_row(result.data)
                success_count += 1
            else:
                failed_count += 1
        
        # Summary
        logger.info("=" * 60)
        logger.info("Scraping Complete!")
        logger.info(f"✓ Successful: {success_count}")
        logger.info(f"✗ Failed: {failed_count}")
        logger.info(f"Total: {len(results)}")
        logger.info(f"Output saved to: {output_filename}")
        logger.info("=" * 60)
        
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    except ResourceExhaustionError as e:
        logger.error(f"Resource exhaustion: {e}")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
    
    finally:
        # Cleanup
        if csv_writer:
            await csv_writer.close()
        if browser_pool:
            await browser_pool.close()
        
        logger.info("Cleanup complete")


if __name__ == "__main__":
    asyncio.run(main())
