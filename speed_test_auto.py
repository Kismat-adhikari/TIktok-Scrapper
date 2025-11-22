"""Automated speed test for the scraper."""

import asyncio
import time
from src.config.loader import ConfigLoader
from src.proxy.manager import RoundRobinProxyManager
from src.scraper.browser_pool import BrowserPool
from src.scraper.extractor import DataExtractor
from src.scraper.engine import ScraperEngine
from src.output.csv_writer import CSVWriter
from src.types import BrowserOptions, ScraperOptions
from datetime import datetime

# Test with 20 URLs to test the new concurrency=20 setting
TEST_URLS = [
    "https://www.tiktok.com/@ajanimalking/video/7304831778055916843",
    "https://www.tiktok.com/@crinklecutfrenchfry/video/7575353684004031774",
    "https://www.tiktok.com/@tikjpgtjlqc/video/7575353484325686546",
    "https://www.tiktok.com/@willlll.__/video/7575355574783577374",
    "https://www.tiktok.com/@q2k0ld/video/7575358579729796407",
    "https://www.tiktok.com/@kimberlykimpena/video/7550079975332842782",
    "https://www.tiktok.com/@adamrayokay/video/6785686942647389445",
    "https://www.tiktok.com/@maddubs40/video/7365212680426179870",
    "https://www.tiktok.com/@derpdogdaily/video/7530910225465953566",
    "https://www.tiktok.com/@cate.okeson/video/7575352878148242718",
    "https://www.tiktok.com/@ghjkjpntfug/video/7575354169368907063",
    "https://www.tiktok.com/@itss.kiki.xx/video/7575354808018734367",
    "https://www.tiktok.com/@lyriclandfill/video/7457400968066501934",
    "https://www.tiktok.com/@prasanth_g9/video/7575357487587593527",
    "https://www.tiktok.com/@deezin67/video/7575355679637015838",
    "https://www.tiktok.com/@fw_selean/video/7575355685152574775",
    "https://www.tiktok.com/@_amourrxsophiaa/video/7575354569178369293",
    "https://www.tiktok.com/@shyt2fye/video/7575355219480022285",
    "https://www.tiktok.com/@teddydafauq/video/7544859246765133111",
    "https://www.tiktok.com/@sieraahope/video/7376227925429095726",
]

async def speed_test():
    """Test scraping speed with new concurrency settings."""
    
    print("=" * 70)
    print("⚡ SPEED TEST - New Concurrency Settings")
    print("=" * 70)
    
    config_loader = ConfigLoader()
    browser_pool = None
    csv_writer = None
    
    try:
        proxies = await config_loader.load_proxies('proxies.txt')
        print(f"✓ Loaded {len(proxies)} proxies")
        print(f"✓ Testing with {len(TEST_URLS)} URLs")
        
        proxy_manager = RoundRobinProxyManager(proxies)
        
        browser_options = BrowserOptions(
            headless=True,
            block_resources=['image', 'media', 'font', 'stylesheet'],
            timeout=15000
        )
        browser_pool = BrowserPool(browser_options)
        await browser_pool.initialize()
        
        # Test WITHOUT profile scraping (faster)
        extractor = DataExtractor(skip_profiles=True)
        
        # Should auto-select 15 workers for 20 URLs
        scraper_options = ScraperOptions(
            max_retries=1,
            timeout=15000,
            concurrency=15  # 20 URLs = 15 workers
        )
        engine = ScraperEngine(proxy_manager, browser_pool, extractor, scraper_options)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"speed_test_{timestamp}.csv"
        csv_writer = CSVWriter(output_filename)
        await csv_writer.write_header()
        
        print(f"⚡ Concurrency: {scraper_options.concurrency} workers")
        print(f"⚡ Profile scraping: DISABLED (speed mode)")
        print("=" * 70)
        print("⏱️  Starting timer...")
        print("=" * 70)
        
        # TIME IT
        start_time = time.time()
        
        results = await engine.scrape_urls(TEST_URLS, scraper_options.concurrency)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Write results
        success_count = 0
        failed_count = 0
        
        for result in results:
            if result.success and result.data:
                await csv_writer.write_row(result.data)
                success_count += 1
            else:
                failed_count += 1
        
        # Results
        print("\n" + "=" * 70)
        print("⚡ SPEED TEST RESULTS")
        print("=" * 70)
        print(f"Total URLs: {len(TEST_URLS)}")
        print(f"Successful: {success_count} ({success_count/len(TEST_URLS)*100:.1f}%)")
        print(f"Failed: {failed_count}")
        print(f"")
        print(f"⏱️  Total Time: {elapsed:.2f} seconds")
        print(f"⚡ Speed: {elapsed/len(TEST_URLS):.2f} sec/URL")
        print(f"⚡ Throughput: {len(TEST_URLS)/elapsed:.2f} URLs/sec")
        print(f"")
        print(f"📊 Estimated for 100 URLs: {(elapsed/len(TEST_URLS))*100:.1f} seconds ({((elapsed/len(TEST_URLS))*100)/60:.1f} min)")
        print(f"📊 Output: {output_filename}")
        print("=" * 70)
        
        if elapsed/len(TEST_URLS) < 1.0:
            print("🎉 EXCELLENT! Under 1 second per URL!")
        elif elapsed/len(TEST_URLS) < 1.5:
            print("✅ GOOD! Under 1.5 seconds per URL!")
        else:
            print("⚠️  Could be faster...")
        
    finally:
        if csv_writer:
            await csv_writer.close()
        if browser_pool:
            await browser_pool.close()

if __name__ == "__main__":
    asyncio.run(speed_test())
