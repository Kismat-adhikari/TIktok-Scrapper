"""Unit tests for ProxyManager."""

import pytest
from src.proxy import RoundRobinProxyManager
from src.types import ProxyConfig, ResourceExhaustionError


class TestRoundRobinProxyManager:
    """Unit tests for RoundRobinProxyManager class."""
    
    def test_force_rotation_after_14_requests(self):
        """Test force rotation after 14 requests (example test)."""
        proxies = [
            ProxyConfig(ip="1.1.1.1", port=8080, username="user1", password="pass1"),
            ProxyConfig(ip="2.2.2.2", port=8080, username="user2", password="pass2"),
        ]
        manager = RoundRobinProxyManager(proxies)
        
        # Get 14 proxies
        used_proxies = []
        for _ in range(14):
            proxy = manager.get_next_proxy()
            used_proxies.append(proxy)
        
        # After 14 requests, rotation should have occurred
        # The 15th request should trigger force rotation
        proxy_15 = manager.get_next_proxy()
        
        # Verify rotation happened (request count should be 15)
        assert manager.request_count == 15
    
    def test_proxy_exhaustion_detection(self):
        """Test exhaustion detection (edge case)."""
        proxies = [
            ProxyConfig(ip="1.1.1.1", port=8080, username="user1", password="pass1"),
            ProxyConfig(ip="2.2.2.2", port=8080, username="user2", password="pass2"),
        ]
        manager = RoundRobinProxyManager(proxies)
        
        # Mark all proxies as failed
        for proxy in proxies:
            manager.mark_proxy_failed(proxy)
        
        # Should raise ResourceExhaustionError
        with pytest.raises(ResourceExhaustionError, match="All proxies have failed"):
            manager.get_next_proxy()
    
    def test_no_proxies_initialization(self):
        """Test initialization with no proxies."""
        with pytest.raises(ResourceExhaustionError, match="No proxies available"):
            RoundRobinProxyManager([])
    
    def test_has_available_proxies(self):
        """Test has_available_proxies method."""
        proxies = [
            ProxyConfig(ip="1.1.1.1", port=8080, username="user1", password="pass1"),
            ProxyConfig(ip="2.2.2.2", port=8080, username="user2", password="pass2"),
        ]
        manager = RoundRobinProxyManager(proxies)
        
        # Initially all proxies available
        assert manager.has_available_proxies()
        
        # Mark one as failed
        manager.mark_proxy_failed(proxies[0])
        assert manager.has_available_proxies()
        
        # Mark all as failed
        manager.mark_proxy_failed(proxies[1])
        assert not manager.has_available_proxies()
    
    def test_force_rotation_method(self):
        """Test force_rotation method."""
        proxies = [
            ProxyConfig(ip="1.1.1.1", port=8080, username="user1", password="pass1"),
            ProxyConfig(ip="2.2.2.2", port=8080, username="user2", password="pass2"),
            ProxyConfig(ip="3.3.3.3", port=8080, username="user3", password="pass3"),
        ]
        manager = RoundRobinProxyManager(proxies)
        
        # Get first proxy
        first = manager.get_next_proxy()
        
        # Force rotation
        manager.force_rotation()
        
        # Next proxy should be different
        next_proxy = manager.get_next_proxy()
        assert first.ip != next_proxy.ip
