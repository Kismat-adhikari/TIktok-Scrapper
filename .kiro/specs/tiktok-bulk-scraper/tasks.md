# Implementation Plan

- [x] 1. Set up project structure and dependencies




  - Initialize Node.js project with TypeScript configuration
  - Install dependencies: playwright, csv-writer, vitest, fast-check, pino
  - Create directory structure: src/config, src/scraper, src/proxy, src/output, src/types
  - Set up tsconfig.json with strict mode enabled


  - Configure vitest for unit and property-based testing



  - _Requirements: All_



- [ ] 2. Implement core type definitions and interfaces
  - Create TypeScript interfaces for ProxyConfig, VideoMetadata, ProfileData, Config, ScrapingResult
  - Define interface for ProxyManager, DataExtractor, CSVWriter, ScraperEngine
  - Add profile fields to VideoMetadata: email, instagram_link, youtube_link, twitter_link, other_links
  - Create error types for different failure categories
  - _Requirements: 1.1, 2.1, 3.1-3.9, 11.1-11.8_

- [x] 3. Implement configuration loader

  - [ ] 3.1 Create ConfigLoader class with file reading methods
    - Implement loadUrls() to read and parse urls.txt
    - Implement loadProxies() to read and parse proxies.txt with IP:PORT:USERNAME:PASSWORD format


    - Add validation for file existence and content
    - _Requirements: 1.1, 1.3, 2.1, 2.3_

  - [ ] 3.2 Write property test for configuration loading
    - **Property 1: Configuration file loading completeness**


    - **Validates: Requirements 1.1, 2.1**

  - [ ] 3.3 Write property test for proxy parsing
    - **Property 2: Proxy format parsing correctness**
    - **Validates: Requirements 2.2**


  - [ ] 3.4 Write property test for malformed input handling
    - **Property 3: Malformed input skipping**

    - **Validates: Requirements 1.4, 2.4**

  - [x] 3.5 Write unit tests for ConfigLoader

    - Test missing file handling (edge case)
    - Test empty file handling (edge case)
    - Test malformed proxy format parsing


    - _Requirements: 1.3, 1.4, 2.3, 2.4_

- [ ] 4. Implement proxy manager with rotation logic
  - [x] 4.1 Create RoundRobinProxyManager class



    - Implement getNextProxy() with round-robin rotation
    - Implement markProxyFailed() to track failed proxies
    - Implement forceRotation() to reset after 14 requests
    - Add request counter and proxy cycling logic
    - _Requirements: 6.1, 6.2, 6.4, 5.3_

  - [ ] 4.2 Write property test for consecutive proxy rotation
    - **Property 10: Consecutive proxy rotation**
    - **Validates: Requirements 6.1**

  - [ ] 4.3 Write property test for round-robin cycling
    - **Property 11: Round-robin proxy cycling**
    - **Validates: Requirements 6.4**

  - [ ] 4.4 Write property test for proxy rotation on failure
    - **Property 9: Proxy rotation on failure**
    - **Validates: Requirements 5.3, 6.3**

  - [ ] 4.5 Write unit tests for ProxyManager
    - Test force rotation after 14 requests (example test)
    - Test proxy exhaustion detection (edge case)
    - _Requirements: 6.2, 5.4_

- [ ] 5. Implement browser pool with optimized settings
  - [ ] 5.1 Create BrowserPool class
    - Initialize Playwright chromium browser in headless mode
    - Implement createContext() with proxy configuration
    - Add resource blocking route handler for images, media, fonts, stylesheets
    - Implement closeContext() for cleanup
    - Set timeout to 8 seconds
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.6, 4.7_

  - [ ] 5.2 Write property test for browser resource blocking
    - **Property 5: Browser resource blocking**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

  - [ ] 5.3 Write property test for resource cleanup
    - **Property 7: Resource cleanup**
    - **Validates: Requirements 4.7, 7.3**

  - [ ] 5.4 Write unit tests for BrowserPool
    - Test context creation with proxy
    - Test resource blocking configuration
    - Test context cleanup
    - _Requirements: 4.1-4.4, 4.7_

- [ ] 6. Implement data extractor for TikTok metadata
  - [ ] 6.1 Create DataExtractor class
    - Implement extractMetadata() with targeted DOM selectors
    - Extract video_url, caption, likes, comments_count, share_count, username, upload_date, thumbnail_url
    - Parse hashtags from caption and format with semicolon separators
    - Handle missing fields gracefully with default values
    - Use minimal DOM queries for performance
    - _Requirements: 3.1-3.9, 7.1, 8.3_

  - [ ] 6.2 Write property test for complete metadata extraction
    - **Property 4: Complete metadata extraction**
    - **Validates: Requirements 3.1-3.9, 11.2-11.6**

  - [ ] 6.3 Write property test for hashtag formatting
    - **Property 14: Hashtag formatting**
    - **Validates: Requirements 8.3**

  - [ ] 6.4 Write unit tests for DataExtractor
    - Test extraction with mock page data
    - Test handling of missing fields
    - Test hashtag parsing and semicolon formatting
    - _Requirements: 3.1-3.9, 8.3_

- [-] 6.5 Add profile scraping functionality to DataExtractor




  - [ ] 6.5.1 Implement extractProfileData() method
    - Navigate to user profile page using username
    - Extract bio/description text from profile
    - Search bio for email patterns using regex
    - Extract Instagram, YouTube, Twitter/X links from profile
    - Categorize other social media links
    - Format multiple links with semicolon separators
    - Handle profile navigation failures gracefully
    - _Requirements: 11.1-11.8_

  - [ ] 6.5.2 Write property test for profile navigation
    - **Property 18: Profile navigation and extraction**
    - **Validates: Requirements 11.1**

  - [ ] 6.5.3 Write property test for email extraction
    - **Property 19: Email extraction from bio**
    - **Validates: Requirements 11.2**

  - [ ] 6.5.4 Write property test for social media link extraction
    - **Property 20: Social media link extraction**
    - **Validates: Requirements 11.3, 11.4, 11.5**

  - [ ] 6.5.5 Write property test for social media link formatting
    - **Property 22: Social media link formatting**
    - **Validates: Requirements 8.4**

  - [ ] 6.5.6 Write property test for graceful profile failure
    - **Property 21: Graceful profile extraction failure**
    - **Validates: Requirements 11.7, 11.8**

  - [ ] 6.5.7 Write unit tests for profile extraction
    - Test email regex pattern matching
    - Test social media link categorization
    - Test profile navigation failure handling
    - Test empty profile data handling
    - _Requirements: 11.1-11.8_

- [ ] 7. Implement CSV writer with proper escaping
  - [ ] 7.1 Create CSVWriter class
    - Implement writeHeader() to write column names including profile fields
    - Update columns to include: email, instagram_link, youtube_link, twitter_link, other_links
    - Implement writeRow() with proper CSV escaping for commas and quotes
    - Implement close() to finalize file
    - Use csv-writer library for reliable formatting
    - _Requirements: 8.1, 8.2, 8.4, 8.6_

  - [ ] 7.2 Write property test for CSV serialization
    - **Property 15: CSV serialization round-trip**
    - **Validates: Requirements 8.6**

  - [ ] 7.3 Write property test for CSV structure
    - **Property 13: CSV output structure and completeness**
    - **Validates: Requirements 8.1, 8.2, 8.5**

  - [ ] 7.4 Write unit tests for CSVWriter
    - Test CSV escaping for special characters
    - Test header generation with all 14 columns
    - Test row writing with profile data
    - _Requirements: 8.1, 8.2, 8.6_

- [ ] 8. Implement logging system
  - [ ] 8.1 Configure pino logger with minimal output
    - Set up logger to output URL processed, proxy used, success/failure status
    - Configure log levels (info for success, error for failures)
    - Keep logging minimal for performance
    - _Requirements: 7.2_

  - [ ] 8.2 Write property test for logging information
    - **Property 12: Essential logging information**
    - **Validates: Requirements 7.2**

- [ ] 9. Implement core scraper engine
  - [ ] 9.1 Create ScraperEngine class
    - Implement scrapeUrl() method with retry logic
    - Add timeout enforcement (6-8 seconds per URL)
    - Integrate ProxyManager for proxy rotation
    - Integrate BrowserPool for browser management
    - Integrate DataExtractor for metadata extraction
    - Handle errors and log results
    - _Requirements: 4.6, 5.1, 5.2, 5.3_

  - [ ] 9.2 Write property test for timeout enforcement
    - **Property 6: Timeout enforcement**
    - **Validates: Requirements 4.6**

  - [ ] 9.3 Write property test for retry logic
    - **Property 8: Retry with proxy rotation**
    - **Validates: Requirements 5.1, 5.2**

  - [ ] 9.4 Write unit tests for ScraperEngine
    - Test single URL scraping
    - Test retry on failure
    - Test timeout handling
    - _Requirements: 4.6, 5.1, 5.2_

- [ ] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Implement concurrent processing with worker pool
  - [ ] 11.1 Add scrapeUrls() method with concurrency control
    - Implement worker pool pattern with configurable concurrency (default: 3)
    - Process multiple URLs in parallel
    - Maintain proxy rotation across concurrent workers
    - Aggregate results from all workers
    - _Requirements: 9.1, 9.2_

  - [ ] 11.2 Write property test for concurrent processing
    - **Property 16: Concurrent processing capability**
    - **Validates: Requirements 9.1**

  - [ ] 11.3 Write property test for thread-safe CSV writing
    - **Property 17: Thread-safe CSV writing**
    - **Validates: Requirements 9.3**

  - [ ] 11.4 Write integration tests for concurrency
    - Test processing 50+ URLs concurrently
    - Verify no race conditions in CSV writing
    - Verify proxy rotation under concurrent load
    - _Requirements: 9.1, 9.2, 9.3_

- [ ] 12. Implement main entry point and orchestration
  - [ ] 12.1 Create main.ts entry point
    - Load configuration from urls.txt and proxies.txt
    - Initialize all components (ProxyManager, BrowserPool, ScraperEngine, CSVWriter)
    - Execute scraping with concurrent processing
    - Write results to output.csv
    - Handle errors and exit gracefully
    - _Requirements: 1.1, 1.2, 2.1, 8.1, 8.4_

  - [ ] 12.2 Write end-to-end integration test
    - Create mock TikTok HTML pages
    - Test full pipeline from input files to CSV output
    - Verify all components work together correctly
    - _Requirements: All_

- [ ] 13. Add error handling and edge cases
  - Implement graceful termination on missing/empty input files
  - Add error handling for all proxies exhausted scenario
  - Ensure failed URLs are skipped and not written to CSV
  - Add proper exit codes for different error scenarios
  - _Requirements: 1.3, 2.3, 5.4, 8.4_

- [ ] 14. Create custom generators for property-based tests
  - Implement proxyConfigGenerator() for valid proxy configs
  - Implement videoMetadataGenerator() for complete metadata objects
  - Implement tiktokUrlGenerator() for valid TikTok URL patterns
  - Implement malformedInputGenerator() for invalid inputs
  - _Requirements: Testing infrastructure_

- [ ] 15. Optimize performance and validate targets
  - Profile memory usage and ensure it stays under 500MB
  - Verify timeout enforcement is working (6-8 seconds per URL)
  - Test throughput with 100 URLs to ensure completion under 10 minutes
  - Optimize DOM queries and resource usage if needed
  - _Requirements: 4.6, 7.1, 7.3_

- [ ] 16. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 17. Create README with usage instructions
  - Document input file formats (urls.txt, proxies.txt)
  - Explain how to run the scraper
  - Document configuration options (concurrency, timeout)
  - Add troubleshooting section
  - Include example input and output files
  - _Requirements: Documentation_
