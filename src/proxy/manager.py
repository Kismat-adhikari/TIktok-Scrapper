"""Proxy manager with round-robin rotation logic."""

from typing import List, Set
from src.types import ProxyConfig, ResourceExhaustionError


class RoundRobinProxyManager:
    """Manages proxy rotation using round-robin strategy with forced rotation."""
    
    FORCE_ROTATION_THRESHOLD = 14
    
    def __init__(self, proxies: List[ProxyConfig]):
        """
        Initialize proxy manager.
        
        Args:
            proxies: List of proxy configurations
            
        Raises:
            ResourceExhaustionError: If no proxies provided
        """
        if not proxies:
            raise ResourceExhaustionError("No proxies available")
        
        self.proxies = proxies
        self.current_index = 0
        self.request_count = 0
        self.failed_proxies: Set[str] = set()
    
    def get_next_proxy(self) -> ProxyConfig:
        """
        Get next proxy in rotation.
        
        Returns:
            Next proxy configuration
            
        Raises:
            ResourceExhaustionError: If all proxies have failed
        """
        if not self.has_available_proxies():
            raise ResourceExhaustionError("All proxies have failed")
        
        # Force rotation every 14 requests
        if self.request_count > 0 and self.request_count % self.FORCE_ROTATION_THRESHOLD == 0:
            self.force_rotation()
        
        # Find next available proxy (skip failed ones)
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.current_index]
            proxy_key = self._get_proxy_key(proxy)
            
            # Move to next proxy for next call
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            # Skip failed proxies
            if proxy_key not in self.failed_proxies:
                self.request_count += 1
                return proxy
            
            attempts += 1
        
        raise ResourceExhaustionError("All proxies have failed")
    
    def mark_proxy_failed(self, proxy: ProxyConfig) -> None:
        """
        Mark a proxy as failed.
        
        Args:
            proxy: Proxy configuration to mark as failed
        """
        proxy_key = self._get_proxy_key(proxy)
        self.failed_proxies.add(proxy_key)
    
    def force_rotation(self) -> None:
        """Force rotation to next proxy."""
        self.current_index = (self.current_index + 1) % len(self.proxies)
    
    def has_available_proxies(self) -> bool:
        """
        Check if there are available proxies.
        
        Returns:
            True if at least one proxy is not failed
        """
        return len(self.failed_proxies) < len(self.proxies)
    
    def _get_proxy_key(self, proxy: ProxyConfig) -> str:
        """
        Get unique key for proxy.
        
        Args:
            proxy: Proxy configuration
            
        Returns:
            Unique string key for proxy
        """
        return f"{proxy.ip}:{proxy.port}"
