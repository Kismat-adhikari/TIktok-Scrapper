"""Property-based tests for proxy manager."""

import pytest
from hypothesis import given, strategies as st, settings
from src.proxy import RoundRobinProxyManager
from src.types import ProxyConfig


@st.composite
def proxy_list_strategy(draw):
    """Generate list of unique proxy configs with simple sequential IPs."""
    count = draw(st.integers(min_value=2, max_value=5))
    proxies = []
    for i in range(count):
        proxy = ProxyConfig(
            ip=f"1.1.1.{i+1}",  # Simple sequential IPs
            port=8080 + i,  # Sequential ports
            username=f"user{i}",
            password=f"pass{i}"
        )
        proxies.append(proxy)
    return proxies


# **Feature: tiktok-bulk-scraper, Property 10: Consecutive proxy rotation**
@given(proxies=proxy_list_strategy())
@settings(max_examples=50)
def test_property_consecutive_proxy_rotation(proxies):
    """
    Property 10: Consecutive proxy rotation
    For any sequence of URL requests, each request should use a different 
    proxy than the previous request.
    
    Validates: Requirements 6.1
    """
    manager = RoundRobinProxyManager(proxies)
    
    # Get multiple proxies
    num_requests = min(len(proxies) * 2, 20)
    used_proxies = []
    
    for _ in range(num_requests):
        proxy = manager.get_next_proxy()
        used_proxies.append(proxy)
    
    # Property: Consecutive proxies should be different (when we have more than 1 proxy)
    if len(proxies) > 1:
        for i in range(len(used_proxies) - 1):
            current = used_proxies[i]
            next_proxy = used_proxies[i + 1]
            assert current.ip != next_proxy.ip or current.port != next_proxy.port, \
                "Consecutive proxies should be different"


# **Feature: tiktok-bulk-scraper, Property 11: Round-robin proxy cycling**
@given(proxies=proxy_list_strategy())
@settings(max_examples=50)
def test_property_round_robin_proxy_cycling(proxies):
    """
    Property 11: Round-robin proxy cycling
    For any list of N proxies, after processing N requests, all proxies 
    should have been used at least once.
    
    Validates: Requirements 6.4
    """
    manager = RoundRobinProxyManager(proxies)
    
    # Get N proxies
    used_proxies = []
    for _ in range(len(proxies)):
        proxy = manager.get_next_proxy()
        used_proxies.append(proxy)
    
    # Property: All proxies should have been used
    used_proxy_keys = {f"{p.ip}:{p.port}" for p in used_proxies}
    all_proxy_keys = {f"{p.ip}:{p.port}" for p in proxies}
    
    assert used_proxy_keys == all_proxy_keys, \
        "All proxies should be used after N requests"


# **Feature: tiktok-bulk-scraper, Property 9: Proxy rotation on failure**
@given(proxies=proxy_list_strategy())
@settings(max_examples=50)
def test_property_proxy_rotation_on_failure(proxies):
    """
    Property 9: Proxy rotation on failure
    For any proxy that encounters a failure or captcha, the system should 
    immediately switch to the next available proxy in the rotation.
    
    Validates: Requirements 5.3, 6.3
    """
    if len(proxies) < 2:
        return  # Need at least 2 proxies to test rotation
    
    manager = RoundRobinProxyManager(proxies)
    
    # Get first proxy
    first_proxy = manager.get_next_proxy()
    
    # Mark it as failed
    manager.mark_proxy_failed(first_proxy)
    
    # Get next proxy
    second_proxy = manager.get_next_proxy()
    
    # Property: Second proxy should be different from failed proxy
    assert first_proxy.ip != second_proxy.ip or first_proxy.port != second_proxy.port, \
        "Should switch to different proxy after failure"
    
    # Property: Failed proxy should not be returned again
    for _ in range(len(proxies) * 2):
        proxy = manager.get_next_proxy()
        assert proxy.ip != first_proxy.ip or proxy.port != first_proxy.port, \
            "Failed proxy should not be used again"
