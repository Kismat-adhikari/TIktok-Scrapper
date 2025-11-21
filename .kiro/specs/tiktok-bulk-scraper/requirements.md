# Requirements Document

## Introduction

This document specifies the requirements for a high-speed TikTok metadata scraper designed to extract video information from bulk URLs without authentication, API keys, or video downloads. The system prioritizes speed, low resource usage, and efficient proxy rotation to handle large-scale scraping operations.

## Glossary

- **Scraper**: The automated system that extracts metadata from TikTok video URLs
- **Metadata**: Information about TikTok videos including captions, statistics, and user details
- **Proxy**: An intermediary server used to route requests and avoid rate limiting
- **Headless Mode**: Browser operation without a visible user interface
- **DOM**: Document Object Model, the tree structure of HTML elements
- **CSV**: Comma-Separated Values file format for tabular data output

## Requirements

### Requirement 1

**User Story:** As a data analyst, I want to provide bulk TikTok URLs in a text file, so that I can process multiple videos without manual input.

#### Acceptance Criteria

1. WHEN the Scraper starts THEN the Scraper SHALL read all URLs from a file named urls.txt
2. WHEN the urls.txt file contains multiple URLs THEN the Scraper SHALL process each URL sequentially or in parallel
3. WHEN the urls.txt file is missing or empty THEN the Scraper SHALL report an error and terminate gracefully
4. WHEN a URL in urls.txt is malformed THEN the Scraper SHALL skip that URL and continue processing remaining URLs

### Requirement 2

**User Story:** As a data analyst, I want to configure proxies in a standardized format, so that I can rotate through multiple proxy servers to avoid rate limiting.

#### Acceptance Criteria

1. WHEN the Scraper starts THEN the Scraper SHALL load proxy configurations from a file named proxies.txt
2. WHEN proxies.txt contains proxy entries THEN each entry SHALL follow the format IP:PORT:USERNAME:PASSWORD
3. WHEN proxies.txt is missing or empty THEN the Scraper SHALL report an error and terminate gracefully
4. WHEN a proxy entry is malformed THEN the Scraper SHALL skip that proxy and continue with remaining proxies

### Requirement 3

**User Story:** As a data analyst, I want to extract specific metadata fields from TikTok videos, so that I can analyze video performance and content.

#### Acceptance Criteria

1. WHEN the Scraper processes a TikTok URL THEN the Scraper SHALL extract the video_url field
2. WHEN the Scraper processes a TikTok URL THEN the Scraper SHALL extract the caption field
3. WHEN the Scraper processes a TikTok URL THEN the Scraper SHALL extract hashtags as a semicolon-separated string
4. WHEN the Scraper processes a TikTok URL THEN the Scraper SHALL extract the likes count field
5. WHEN the Scraper processes a TikTok URL THEN the Scraper SHALL extract the comments_count field
6. WHEN the Scraper processes a TikTok URL THEN the Scraper SHALL extract the share_count field
7. WHEN the Scraper processes a TikTok URL THEN the Scraper SHALL extract the username field
8. WHEN the Scraper processes a TikTok URL THEN the Scraper SHALL extract the upload_date field
9. WHEN the Scraper processes a TikTok URL THEN the Scraper SHALL extract the thumbnail_url field

### Requirement 11

**User Story:** As a data analyst, I want to extract contact information and social media links from user profiles, so that I can identify creators with public contact details for outreach purposes.

#### Acceptance Criteria

1. WHEN the Scraper processes a TikTok URL THEN the Scraper SHALL navigate to the user's profile page
2. WHEN the Scraper visits a user profile THEN the Scraper SHALL extract email addresses if present in the bio or description
3. WHEN the Scraper visits a user profile THEN the Scraper SHALL extract Instagram links if present
4. WHEN the Scraper visits a user profile THEN the Scraper SHALL extract YouTube links if present
5. WHEN the Scraper visits a user profile THEN the Scraper SHALL extract Twitter links if present
6. WHEN the Scraper visits a user profile THEN the Scraper SHALL extract other social media links if present
7. WHEN no contact information is found THEN the Scraper SHALL record empty values for those fields
8. WHEN profile extraction fails THEN the Scraper SHALL continue with video metadata and leave profile fields empty

### Requirement 4

**User Story:** As a data analyst, I want the scraper to operate at maximum speed, so that I can process large volumes of URLs efficiently.

#### Acceptance Criteria

1. WHEN the Scraper launches a browser THEN the Scraper SHALL disable image loading to reduce bandwidth and processing time
2. WHEN the Scraper launches a browser THEN the Scraper SHALL disable media loading to reduce bandwidth and processing time
3. WHEN the Scraper launches a browser THEN the Scraper SHALL disable font loading to reduce bandwidth and processing time
4. WHEN the Scraper launches a browser THEN the Scraper SHALL disable stylesheet loading to reduce bandwidth and processing time
5. WHEN the Scraper loads a TikTok page THEN the Scraper SHALL wait only for the video container element and not the full page load
6. WHEN the Scraper processes a single URL THEN the Scraper SHALL enforce a timeout of 6 to 8 seconds maximum
7. WHEN the Scraper completes extraction from a URL THEN the Scraper SHALL close the browser tab immediately

### Requirement 5

**User Story:** As a data analyst, I want the scraper to handle failures gracefully, so that temporary issues do not stop the entire scraping operation.

#### Acceptance Criteria

1. WHEN a URL fails to load or extract data THEN the Scraper SHALL retry that URL once with a different proxy
2. WHEN a URL fails twice THEN the Scraper SHALL skip that URL and continue processing remaining URLs
3. WHEN a proxy fails or returns a captcha THEN the Scraper SHALL switch to the next available proxy
4. WHEN all proxies are exhausted THEN the Scraper SHALL report an error and terminate

### Requirement 6

**User Story:** As a data analyst, I want intelligent proxy rotation, so that I can avoid detection and rate limiting from TikTok servers.

#### Acceptance Criteria

1. WHEN the Scraper processes a URL THEN the Scraper SHALL rotate to a different proxy for each request
2. WHEN the Scraper has processed 14 URLs THEN the Scraper SHALL force a proxy rotation regardless of success status
3. WHEN a proxy encounters a failure or captcha THEN the Scraper SHALL immediately switch to the next proxy in the list
4. WHEN the Scraper rotates proxies THEN the Scraper SHALL cycle through all available proxies from proxies.txt

### Requirement 7

**User Story:** As a data analyst, I want minimal resource usage during scraping, so that I can run the scraper on standard hardware without performance degradation.

#### Acceptance Criteria

1. WHEN the Scraper extracts metadata THEN the Scraper SHALL use minimal DOM queries to locate required elements
2. WHEN the Scraper operates THEN the Scraper SHALL log only essential information including URL processed, proxy used, and success or failure status
3. WHEN the Scraper processes multiple URLs THEN the Scraper SHALL manage memory efficiently by closing resources immediately after use

### Requirement 8

**User Story:** As a data analyst, I want scraped data exported to CSV format, so that I can easily import the results into analysis tools.

#### Acceptance Criteria

1. WHEN the Scraper completes processing THEN the Scraper SHALL save results to a file named output.csv
2. WHEN the Scraper writes to output.csv THEN the file SHALL contain columns: video_url, caption, hashtags, likes, comments_count, share_count, username, upload_date, thumbnail_url, email, instagram_link, youtube_link, twitter_link, other_links
3. WHEN the Scraper writes hashtags to output.csv THEN hashtags SHALL be separated by semicolons
4. WHEN the Scraper writes multiple social media links to output.csv THEN links SHALL be separated by semicolons
5. WHEN a URL fails twice THEN the Scraper SHALL omit that URL from output.csv
6. WHEN the Scraper writes to output.csv THEN the file SHALL use proper CSV escaping for fields containing commas or quotes

### Requirement 9

**User Story:** As a data analyst, I want the scraper to support concurrent processing, so that I can maximize throughput when processing large URL lists.

#### Acceptance Criteria

1. WHEN the Scraper processes URLs THEN the Scraper SHALL support processing multiple URLs in parallel
2. WHEN the Scraper runs concurrent operations THEN the Scraper SHALL maintain proxy rotation rules across all parallel requests
3. WHEN the Scraper runs concurrent operations THEN the Scraper SHALL ensure thread-safe writing to output.csv

### Requirement 10

**User Story:** As a data analyst, I want the scraper to exclude unnecessary features, so that the system remains lightweight and focused on core functionality.

#### Acceptance Criteria

1. THE Scraper SHALL NOT implement login or authentication functionality
2. THE Scraper SHALL NOT download video files
3. THE Scraper SHALL NOT implement captcha solving mechanisms
4. THE Scraper SHALL NOT require API keys for operation
5. THE Scraper SHALL NOT scrape individual comments from videos
6. THE Scraper SHALL NOT implement browser fingerprint spoofing
