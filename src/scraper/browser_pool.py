"""Browser pool for managing Playwright browsers with optimized settings."""

from playwright.async_api import async_playwright, Browser, BrowserContext
from src.types import ProxyConfig, BrowserOptions


class BrowserPool:
    """Manages Playwright browser instances with resource blocking."""
    
    def __init__(self, options: BrowserOptions = None):
        """
        Initialize browser pool.
        
        Args:
            options: Browser configuration options
        """
        self.options = options or BrowserOptions()
        self.playwright = None
        self.browser: Browser = None
    
    async def initialize(self):
        """Initialize Playwright and browser."""
        self.playwright = await async_playwright().start()
        # Launch with a dummy global proxy to allow per-context proxies
        self.browser = await self.playwright.chromium.launch(
            headless=self.options.headless,
            args=['--disable-dev-shm-usage', '--no-sandbox'],
            proxy={"server": "http://per-context"}  # Dummy proxy for per-context override
        )
    
    async def create_context(self, proxy: ProxyConfig) -> BrowserContext:
        """
        Create browser context with proxy and resource blocking.
        
        Args:
            proxy: Proxy configuration
            
        Returns:
            Browser context with optimized settings
        """
        if not self.browser:
            await self.initialize()
        
        # Create context with proxy
        context = await self.browser.new_context(
            proxy={
                "server": f"http://{proxy.ip}:{proxy.port}",
                "username": proxy.username,
                "password": proxy.password
            },
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        # Set timeout
        context.set_default_timeout(self.options.timeout)
        
        # Aggressively block resources for maximum speed
        async def block_resources(route):
            resource_type = route.request.resource_type
            url = route.request.url
            
            # Block all unnecessary resources
            if resource_type in self.options.block_resources:
                await route.abort()
            # Also block tracking, analytics, ads
            elif any(x in url for x in ['analytics', 'tracking', 'ads', 'doubleclick', 'facebook.com/tr']):
                await route.abort()
            else:
                await route.continue_()
        
        await context.route("**/*", block_resources)
        
        return context
    
    async def close_context(self, context: BrowserContext) -> None:
        """
        Close browser context.
        
        Args:
            context: Browser context to close
        """
        await context.close()
    
    async def close(self) -> None:
        """Close browser and playwright."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
