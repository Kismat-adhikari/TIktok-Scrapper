"""Type definitions and data classes for the TikTok scraper."""

from dataclasses import dataclass
from typing import Optional, Protocol
from playwright.async_api import BrowserContext, Page


# ============================================================================
# Configuration Types
# ============================================================================

@dataclass
class ProxyConfig:
    """Proxy server configuration."""
    ip: str
    port: int
    username: str
    password: str

    def to_url(self) -> str:
        """Convert proxy config to URL format."""
        return f"http://{self.username}:{self.password}@{self.ip}:{self.port}"


@dataclass
class Config:
    """Application configuration."""
    urls: list[str]
    proxies: list[ProxyConfig]


@dataclass
class ValidationResult:
    """Result of configuration validation."""
    valid: bool
    errors: list[str]


# ============================================================================
# Metadata Types
# ============================================================================

@dataclass
class ProfileData:
    """TikTok user profile data."""
    bio: str = ""
    email: str = ""
    instagram_link: str = ""
    youtube_link: str = ""
    twitter_link: str = ""
    other_links: str = ""  # Semicolon-separated


@dataclass
class VideoMetadata:
    """TikTok video metadata."""
    video_url: str
    caption: str
    hashtags: str  # Semicolon-separated
    likes: int
    comments_count: int
    share_count: int
    username: str
    upload_date: str
    thumbnail_url: str
    bio: str = ""
    email: str = ""
    instagram_link: str = ""
    youtube_link: str = ""
    twitter_link: str = ""
    other_links: str = ""  # Semicolon-separated


# ============================================================================
# Scraping Result Types
# ============================================================================

@dataclass
class ScrapingResult:
    """Result of a scraping operation."""
    success: bool
    url: str
    proxy_used: str
    retry_count: int
    data: Optional[VideoMetadata] = None
    error: Optional[str] = None


# ============================================================================
# Options Types
# ============================================================================

@dataclass
class BrowserOptions:
    """Browser configuration options."""
    headless: bool = True
    block_resources: list[str] = None
    timeout: int = 8000  # milliseconds

    def __post_init__(self):
        if self.block_resources is None:
            # Block everything except HTML and scripts for maximum speed
            self.block_resources = ['image', 'media', 'font', 'stylesheet', 'other', 'texttrack', 'eventsource', 'websocket', 'manifest']


@dataclass
class ScraperOptions:
    """Scraper engine options."""
    max_retries: int = 1
    timeout: int = 15000  # milliseconds - increased for reliability
    concurrency: int = 10  # Increased default


# ============================================================================
# Component Protocols (Interfaces)
# ============================================================================

class IConfigLoader(Protocol):
    """Interface for configuration loader."""
    
    async def load_urls(self, file_path: str) -> list[str]:
        """Load URLs from file."""
        ...
    
    async def load_proxies(self, file_path: str) -> list[ProxyConfig]:
        """Load proxy configurations from file."""
        ...
    
    def validate_config(self, config: Config) -> ValidationResult:
        """Validate configuration."""
        ...


class IProxyManager(Protocol):
    """Interface for proxy manager."""
    
    def get_next_proxy(self) -> ProxyConfig:
        """Get next proxy in rotation."""
        ...
    
    def mark_proxy_failed(self, proxy: ProxyConfig) -> None:
        """Mark a proxy as failed."""
        ...
    
    def force_rotation(self) -> None:
        """Force proxy rotation."""
        ...
    
    def has_available_proxies(self) -> bool:
        """Check if proxies are available."""
        ...


class IBrowserPool(Protocol):
    """Interface for browser pool."""
    
    async def create_context(self, proxy: ProxyConfig) -> BrowserContext:
        """Create browser context with proxy."""
        ...
    
    async def close_context(self, context: BrowserContext) -> None:
        """Close browser context."""
        ...
    
    async def close(self) -> None:
        """Close browser pool."""
        ...


class IDataExtractor(Protocol):
    """Interface for data extractor."""
    
    async def extract_metadata(self, page: Page, url: str) -> VideoMetadata:
        """Extract metadata from page."""
        ...
    
    async def extract_profile_data(self, page: Page, username: str) -> ProfileData:
        """Extract profile data from user page."""
        ...


class ICSVWriter(Protocol):
    """Interface for CSV writer."""
    
    async def write_header(self) -> None:
        """Write CSV header."""
        ...
    
    async def write_row(self, data: VideoMetadata) -> None:
        """Write data row to CSV."""
        ...
    
    async def close(self) -> None:
        """Close CSV writer."""
        ...


class IScraperEngine(Protocol):
    """Interface for scraper engine."""
    
    async def scrape_urls(self, urls: list[str], concurrency: int) -> list[ScrapingResult]:
        """Scrape multiple URLs with concurrency."""
        ...
    
    async def scrape_url(self, url: str, proxy: ProxyConfig, retry_count: int) -> ScrapingResult:
        """Scrape single URL."""
        ...


# ============================================================================
# Error Types
# ============================================================================

class ConfigurationError(Exception):
    """Configuration-related errors."""
    pass


class NetworkError(Exception):
    """Network-related errors."""
    pass


class ExtractionError(Exception):
    """Data extraction errors."""
    pass


class ResourceExhaustionError(Exception):
    """Resource exhaustion errors."""
    pass
