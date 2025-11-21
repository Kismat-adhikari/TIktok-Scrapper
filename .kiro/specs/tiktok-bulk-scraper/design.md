# Design Document

## Overview

The TikTok Bulk URL Scraper is a high-performance metadata extraction system built with Playwright for Node.js. The system prioritizes speed through aggressive resource optimization, intelligent proxy rotation, and concurrent processing. The architecture follows a modular design with clear separation between input handling, browser automation, data extraction, proxy management, and output generation.

## Architecture

The system follows a pipeline architecture with these main components:

```
Input Files (urls.txt, proxies.txt)
    ↓
Configuration Loader
    ↓
Proxy Manager ←→ Browser Pool
    ↓              ↓
URL Queue → Scraper Engine → Data Extractor
    ↓
Result Aggregator
    ↓
CSV Writer (output.csv)
```

### Key Design Decisions

1. **Playwright over Puppeteer**: Playwright offers better performance, built-in proxy support per context, and more reliable element waiting mechanisms
2. **Concurrent Processing**: Use a worker pool pattern to process multiple URLs simultaneously while respecting proxy rotation rules
3. **Aggressive Resource Blocking**: Disable all non-essential resources (images, fonts, stylesheets, media) to minimize bandwidth and parsing time
4. **Minimal DOM Interaction**: Use targeted selectors to extract only required data with minimal traversal
5. **Fail-Fast Strategy**: Implement strict timeouts and immediate retry logic to avoid wasting time on problematic URLs

## Components and Interfaces

### 1. Configuration Loader

**Responsibility**: Load and validate input files

```typescript
interface Config {
  urls: string[];
  proxies: ProxyConfig[];
}

interface ProxyConfig {
  ip: string;
  port: number;
  username: string;
  password: string;
}

class ConfigLoader {
  loadUrls(filePath: string): string[]
  loadProxies(filePath: string): ProxyConfig[]
  validateConfig(config: Config): ValidationResult
}
```

### 2. Proxy Manager

**Responsibility**: Handle proxy rotation and failure tracking

```typescript
interface ProxyManager {
  getNextProxy(): ProxyConfig
  markProxyFailed(proxy: ProxyConfig): void
  forceRotation(): void
  hasAvailableProxies(): boolean
}

class RoundRobinProxyManager implements ProxyManager {
  private proxies: ProxyConfig[]
  private currentIndex: number
  private requestCount: number
  private readonly FORCE_ROTATION_THRESHOLD = 14
}
```

### 3. Browser Pool

**Responsibility**: Manage browser contexts with optimized settings

```typescript
interface BrowserPool {
  createContext(proxy: ProxyConfig): Promise<BrowserContext>
  closeContext(context: BrowserContext): Promise<void>
}

interface BrowserOptions {
  headless: boolean
  blockResources: string[]
  timeout: number
}
```

### 4. Scraper Engine

**Responsibility**: Orchestrate the scraping process with concurrency control

```typescript
interface ScraperEngine {
  scrapeUrls(urls: string[], concurrency: number): Promise<ScrapedData[]>
  scrapeUrl(url: string, proxy: ProxyConfig, retryCount: number): Promise<ScrapedData>
}

interface ScraperOptions {
  maxRetries: number
  timeout: number
  concurrency: number
}
```

### 5. Data Extractor

**Responsibility**: Extract metadata from TikTok pages and user profiles

```typescript
interface DataExtractor {
  extractMetadata(page: Page): Promise<VideoMetadata>
  extractProfileData(page: Page, username: string): Promise<ProfileData>
}

interface VideoMetadata {
  video_url: string
  caption: string
  hashtags: string
  likes: number
  comments_count: number
  share_count: number
  username: string
  upload_date: string
  thumbnail_url: string
  email: string
  instagram_link: string
  youtube_link: string
  twitter_link: string
  other_links: string
}

interface ProfileData {
  email: string
  instagram_link: string
  youtube_link: string
  twitter_link: string
  other_links: string
}
```

### 6. CSV Writer

**Responsibility**: Write results to CSV with proper escaping

```typescript
interface CSVWriter {
  writeHeader(): void
  writeRow(data: VideoMetadata): void
  close(): void
}
```

## Data Models

### ProxyConfig
```typescript
{
  ip: string          // IP address of proxy server
  port: number        // Port number
  username: string    // Authentication username
  password: string    // Authentication password
}
```

### VideoMetadata
```typescript
{
  video_url: string        // Original TikTok URL
  caption: string          // Video caption/description
  hashtags: string         // Semicolon-separated hashtags (#fun;#dance)
  likes: number            // Like count
  comments_count: number   // Comment count
  share_count: number      // Share count
  username: string         // Creator username
  upload_date: string      // Upload date (ISO format)
  thumbnail_url: string    // Thumbnail image URL
  email: string            // Email from profile bio (empty if not found)
  instagram_link: string   // Instagram link from profile (empty if not found)
  youtube_link: string     // YouTube link from profile (empty if not found)
  twitter_link: string     // Twitter/X link from profile (empty if not found)
  other_links: string      // Semicolon-separated other social links
}
```

### ProfileData
```typescript
{
  email: string            // Email address extracted from bio
  instagram_link: string   // Instagram profile URL
  youtube_link: string     // YouTube channel URL
  twitter_link: string     // Twitter/X profile URL
  other_links: string      // Semicolon-separated other social media links
}
```

### ScrapingResult
```typescript
{
  success: boolean
  data?: VideoMetadata
  error?: string
  url: string
  proxyUsed: string
  retryCount: number
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Configuration file loading completeness
*For any* valid urls.txt and proxies.txt files with content, loading the configuration should successfully parse all valid entries and return them in the configuration object.
**Validates: Requirements 1.1, 2.1**

### Property 2: Proxy format parsing correctness
*For any* string in the format IP:PORT:USERNAME:PASSWORD, parsing should produce a ProxyConfig object with all four fields correctly extracted.
**Validates: Requirements 2.2**

### Property 3: Malformed input skipping
*For any* list of inputs (URLs or proxies) containing both valid and malformed entries, processing should skip malformed entries and successfully process all valid entries.
**Validates: Requirements 1.4, 2.4**

### Property 4: Complete metadata extraction
*For any* successfully scraped TikTok page, the extracted VideoMetadata object should contain all fourteen required fields: video_url, caption, hashtags, likes, comments_count, share_count, username, upload_date, thumbnail_url, email, instagram_link, youtube_link, twitter_link, and other_links.
**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 11.2, 11.3, 11.4, 11.5, 11.6**

### Property 5: Browser resource blocking
*For any* browser context created by the system, the configuration should have resource blocking enabled for images, media, fonts, and stylesheets.
**Validates: Requirements 4.1, 4.2, 4.3, 4.4**

### Property 6: Timeout enforcement
*For any* URL scraping operation, the execution time should not exceed 8 seconds.
**Validates: Requirements 4.6**

### Property 7: Resource cleanup
*For any* completed scraping operation (success or failure), all browser contexts and pages should be closed immediately after extraction.
**Validates: Requirements 4.7, 7.3**

### Property 8: Retry with proxy rotation
*For any* URL that fails on first attempt, the system should retry exactly once using a different proxy, and if it fails again, skip the URL and continue processing.
**Validates: Requirements 5.1, 5.2**

### Property 9: Proxy rotation on failure
*For any* proxy that encounters a failure or captcha, the system should immediately switch to the next available proxy in the rotation.
**Validates: Requirements 5.3, 6.3**

### Property 10: Consecutive proxy rotation
*For any* sequence of URL requests, each request should use a different proxy than the previous request.
**Validates: Requirements 6.1**

### Property 11: Round-robin proxy cycling
*For any* list of N proxies, after processing N requests, all proxies should have been used at least once.
**Validates: Requirements 6.4**

### Property 12: Essential logging information
*For any* scraping operation, the log output should contain the URL processed, the proxy used, and the success or failure status.
**Validates: Requirements 7.2**

### Property 13: CSV output structure and completeness
*For any* scraping session, the output.csv file should contain a header row with all fourteen required columns, and should contain rows only for successfully scraped URLs (failed URLs should be omitted).
**Validates: Requirements 8.1, 8.2, 8.5**

### Property 18: Profile navigation and extraction
*For any* TikTok video URL with a valid username, the system should navigate to the user's profile page and attempt to extract contact information and social media links.
**Validates: Requirements 11.1**

### Property 19: Email extraction from bio
*For any* profile bio text containing an email pattern (text@domain.com), the system should successfully extract and return the email address.
**Validates: Requirements 11.2**

### Property 20: Social media link extraction
*For any* profile containing Instagram, YouTube, or Twitter links, the system should extract and categorize each link correctly into its respective field.
**Validates: Requirements 11.3, 11.4, 11.5**

### Property 21: Graceful profile extraction failure
*For any* profile extraction that fails or times out, the system should continue with video metadata extraction and populate profile fields with empty strings.
**Validates: Requirements 11.7, 11.8**

### Property 14: Hashtag formatting
*For any* VideoMetadata with multiple hashtags, the hashtags field should contain semicolon separators between hashtags.
**Validates: Requirements 8.3**

### Property 22: Social media link formatting
*For any* ProfileData with multiple other social media links, the other_links field should contain semicolon separators between links.
**Validates: Requirements 8.4**

### Property 15: CSV serialization round-trip
*For any* VideoMetadata object, writing it to CSV and then parsing it back should produce an equivalent object with all fields preserved, including fields containing commas or quotes.
**Validates: Requirements 8.6**

### Property 16: Concurrent processing capability
*For any* list of URLs with concurrency enabled, multiple URLs should be processed simultaneously, reducing total execution time compared to sequential processing.
**Validates: Requirements 9.1**

### Property 17: Thread-safe CSV writing
*For any* concurrent scraping operations, all successfully scraped results should appear in the output.csv file with no data corruption or missing records.
**Validates: Requirements 9.3**

## Error Handling

### Error Categories

1. **Configuration Errors**
   - Missing or empty urls.txt or proxies.txt
   - Malformed proxy entries
   - Invalid file permissions
   - Action: Log error, terminate gracefully with exit code 1

2. **Network Errors**
   - Proxy connection failures
   - Timeout errors
   - DNS resolution failures
   - Action: Switch proxy, retry once, then skip URL

3. **Extraction Errors**
   - Missing DOM elements
   - Unexpected page structure
   - JavaScript execution failures
   - Action: Log warning, retry once with different proxy, then skip URL

4. **Resource Exhaustion**
   - All proxies exhausted
   - Memory limits reached
   - Action: Log error, save partial results, terminate gracefully

### Error Logging Format

```
[TIMESTAMP] [LEVEL] [COMPONENT] Message
Example: [2024-01-15T10:30:45Z] [ERROR] [ProxyManager] All proxies exhausted
```

### Retry Strategy

- Maximum 1 retry per URL
- Always use different proxy on retry
- Exponential backoff not needed (fail-fast approach)
- Skip URL after 2 total failures

## Testing Strategy

### Unit Testing

The system will use **Vitest** as the testing framework for its speed and modern features.

**Unit Test Coverage:**

1. **ConfigLoader Tests**
   - Test loading valid urls.txt and proxies.txt files
   - Test handling of missing files (edge case)
   - Test handling of empty files (edge case)
   - Test malformed proxy format parsing

2. **ProxyManager Tests**
   - Test round-robin rotation logic
   - Test force rotation after 14 requests (example test)
   - Test proxy failure marking
   - Test exhaustion detection (edge case)

3. **DataExtractor Tests**
   - Test extraction with mock page data
   - Test handling of missing fields
   - Test hashtag formatting with semicolons

4. **CSVWriter Tests**
   - Test CSV escaping for special characters
   - Test header generation
   - Test row writing

### Property-Based Testing

The system will use **fast-check** as the property-based testing library for JavaScript/TypeScript.

**Configuration:**
- Minimum 100 iterations per property test
- Use custom generators for TikTok URLs, proxy configs, and metadata

**Property Test Coverage:**

Each correctness property listed above will be implemented as a property-based test with the following tagging format:

```typescript
// **Feature: tiktok-bulk-scraper, Property 1: Configuration file loading completeness**
test('property: configuration loading completeness', () => {
  fc.assert(
    fc.property(
      fc.array(fc.webUrl()),
      fc.array(proxyConfigGenerator()),
      (urls, proxies) => {
        // Test implementation
      }
    ),
    { numRuns: 100 }
  );
});
```

**Custom Generators Needed:**
- `proxyConfigGenerator()`: Generates valid proxy configurations
- `videoMetadataGenerator()`: Generates complete VideoMetadata objects
- `tiktokUrlGenerator()`: Generates valid TikTok URL patterns
- `malformedInputGenerator()`: Generates invalid inputs for error testing

### Integration Testing

1. **End-to-End Test with Mock TikTok Pages**
   - Create local HTML files mimicking TikTok structure
   - Test full pipeline from input files to CSV output
   - Verify proxy rotation and retry logic

2. **Concurrency Test**
   - Process 50+ URLs concurrently
   - Verify no race conditions in CSV writing
   - Verify proxy rotation works correctly under load

## Performance Targets

- **Throughput**: Process 100 URLs in under 10 minutes (with 3 concurrent workers)
- **Memory**: Stay under 500MB RAM usage
- **Timeout**: 6-8 seconds per URL maximum
- **Success Rate**: 80%+ success rate with valid proxies and URLs

## Implementation Notes

### Playwright Configuration

```typescript
const browser = await playwright.chromium.launch({
  headless: true,
  args: ['--disable-dev-shm-usage', '--no-sandbox']
});

const context = await browser.newContext({
  proxy: {
    server: `http://${proxy.ip}:${proxy.port}`,
    username: proxy.username,
    password: proxy.password
  },
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
});

// Block resources
await context.route('**/*', (route) => {
  const resourceType = route.request().resourceType();
  if (['image', 'media', 'font', 'stylesheet'].includes(resourceType)) {
    route.abort();
  } else {
    route.continue();
  }
});
```

### Concurrency Control

Use a worker pool pattern with configurable concurrency (default: 3 workers):

```typescript
async function processWithConcurrency(urls: string[], concurrency: number) {
  const results = [];
  const queue = [...urls];
  
  const workers = Array(concurrency).fill(null).map(async () => {
    while (queue.length > 0) {
      const url = queue.shift();
      if (url) {
        const result = await scrapeUrl(url);
        results.push(result);
      }
    }
  });
  
  await Promise.all(workers);
  return results;
}
```

### TikTok Selector Strategy

Target these selectors (subject to change as TikTok updates):
- Video container: `[data-e2e="browse-video"]` or `#main-content-video`
- Caption: `[data-e2e="video-desc"]`
- Stats: `[data-e2e="like-count"]`, `[data-e2e="comment-count"]`, `[data-e2e="share-count"]`
- Username: `[data-e2e="video-author-uniqueid"]`
- Hashtags: Extract from caption or `a[href*="/tag/"]`

**Profile Page Selectors:**
- Bio/Description: `[data-e2e="user-bio"]` or `h2[data-e2e="user-subtitle"]`
- Social links: `a[href*="instagram.com"]`, `a[href*="youtube.com"]`, `a[href*="twitter.com"]`, `a[href*="x.com"]`
- Email pattern: Regex `/[\w\.-]+@[\w\.-]+\.\w+/g` applied to bio text

**Profile Extraction Strategy:**
1. After extracting video metadata, construct profile URL: `https://www.tiktok.com/@{username}`
2. Navigate to profile page with same proxy and timeout settings
3. Extract bio text and search for email patterns
4. Query all anchor tags and filter by social media domains
5. Categorize links into instagram_link, youtube_link, twitter_link, or other_links
6. If profile navigation fails or times out, populate fields with empty strings and continue

**Note**: Selectors should be configurable and easy to update as TikTok's DOM structure changes.

## Dependencies

- **playwright**: ^1.40.0 - Browser automation
- **csv-writer**: ^1.6.0 - CSV file generation
- **vitest**: ^1.0.0 - Unit testing framework
- **fast-check**: ^3.15.0 - Property-based testing library
- **typescript**: ^5.3.0 - Type safety
- **pino**: ^8.17.0 - Fast, minimal logging

## Deployment Considerations

- Run on Node.js 18+ for optimal performance
- Ensure sufficient disk space for Playwright browser binaries (~500MB)
- Configure system to allow multiple concurrent browser instances
- Consider running in Docker container for isolation
- Monitor proxy health and rotation effectiveness
