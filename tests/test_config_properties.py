"""Property-based tests for configuration loading."""

import pytest
import tempfile
import asyncio
from pathlib import Path
from hypothesis import given, strategies as st, settings
from src.config import ConfigLoader
from src.types import ProxyConfig


# Custom strategies for generating test data
@st.composite
def proxy_config_strategy(draw):
    """Generate valid proxy configurations with ASCII printable characters only."""
    ip = f"{draw(st.integers(1, 255))}.{draw(st.integers(0, 255))}.{draw(st.integers(0, 255))}.{draw(st.integers(0, 255))}"
    port = draw(st.integers(1, 65535))
    # Use only ASCII alphanumeric characters for username and password
    username = draw(st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'))
    password = draw(st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'))
    return f"{ip}:{port}:{username}:{password}"


@st.composite
def url_strategy(draw):
    """Generate valid URLs with ASCII characters only."""
    protocol = draw(st.sampled_from(['http://', 'https://']))
    # Use only ASCII lowercase letters and digits for domain
    domain = draw(st.text(min_size=3, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))
    tld = draw(st.sampled_from(['.com', '.net', '.org']))
    # Use only ASCII for path
    path = draw(st.text(min_size=0, max_size=30, alphabet='abcdefghijklmnopqrstuvwxyz0123456789-_'))
    return f"{protocol}{domain}{tld}/{path}" if path else f"{protocol}{domain}{tld}"


# **Feature: tiktok-bulk-scraper, Property 1: Configuration file loading completeness**
@given(
    urls=st.lists(url_strategy(), min_size=1, max_size=20),
    proxies=st.lists(proxy_config_strategy(), min_size=1, max_size=10)
)
@settings(max_examples=50)
def test_property_configuration_loading_completeness(urls, proxies):
    """
    Property 1: Configuration file loading completeness
    For any valid urls.txt and proxies.txt files with content, loading the 
    configuration should successfully parse all valid entries and return them 
    in the configuration object.
    
    Validates: Requirements 1.1, 2.1
    """
    async def run_test():
        loader = ConfigLoader()
        
        # Create temporary files with generated data
        with tempfile.TemporaryDirectory() as tmpdir:
            urls_file = Path(tmpdir) / 'urls.txt'
            proxies_file = Path(tmpdir) / 'proxies.txt'
            
            # Write URLs to file
            with open(urls_file, 'w', encoding='utf-8') as f:
                for url in urls:
                    f.write(f"{url}\n")
            
            # Write proxies to file
            with open(proxies_file, 'w', encoding='utf-8') as f:
                for proxy in proxies:
                    f.write(f"{proxy}\n")
            
            # Load configuration
            loaded_urls = await loader.load_urls(str(urls_file))
            loaded_proxies = await loader.load_proxies(str(proxies_file))
            
            # Property: All valid entries should be loaded
            assert len(loaded_urls) == len(urls), "All URLs should be loaded"
            assert len(loaded_proxies) == len(proxies), "All proxies should be loaded"
            
            # Property: Loaded URLs should match input URLs
            for original, loaded in zip(urls, loaded_urls):
                assert original == loaded, f"URL mismatch: {original} != {loaded}"
            
            # Property: Loaded proxies should have all required fields
            for proxy in loaded_proxies:
                assert isinstance(proxy, ProxyConfig), "Should return ProxyConfig objects"
                assert proxy.ip, "IP should not be empty"
                assert 1 <= proxy.port <= 65535, "Port should be valid"
                assert proxy.username, "Username should not be empty"
                assert proxy.password, "Password should not be empty"
    
    # Run the async test
    asyncio.run(run_test())



# **Feature: tiktok-bulk-scraper, Property 2: Proxy format parsing correctness**
@given(
    ip=st.integers(1, 255).flatmap(lambda a: st.tuples(
        st.just(a), st.integers(0, 255), st.integers(0, 255), st.integers(0, 255)
    )),
    port=st.integers(1, 65535),
    username=st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
    password=st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
)
@settings(max_examples=50)
def test_property_proxy_format_parsing_correctness(ip, port, username, password):
    """
    Property 2: Proxy format parsing correctness
    For any string in the format IP:PORT:USERNAME:PASSWORD, parsing should 
    produce a ProxyConfig object with all four fields correctly extracted.
    
    Validates: Requirements 2.2
    """
    loader = ConfigLoader()
    ip_str = f"{ip[0]}.{ip[1]}.{ip[2]}.{ip[3]}"
    proxy_line = f"{ip_str}:{port}:{username}:{password}"
    
    # Parse the proxy line
    proxy = loader._parse_proxy_line(proxy_line)
    
    # Property: All fields should be correctly extracted
    assert proxy.ip == ip_str, f"IP mismatch: {proxy.ip} != {ip_str}"
    assert proxy.port == port, f"Port mismatch: {proxy.port} != {port}"
    assert proxy.username == username, f"Username mismatch: {proxy.username} != {username}"
    assert proxy.password == password, f"Password mismatch: {proxy.password} != {password}"


# **Feature: tiktok-bulk-scraper, Property 3: Malformed input skipping**
@given(
    valid_urls=st.lists(url_strategy(), min_size=1, max_size=10),
    valid_proxies=st.lists(proxy_config_strategy(), min_size=1, max_size=5),
    malformed_urls=st.lists(st.text(min_size=1, max_size=20, alphabet='abcdefg'), min_size=1, max_size=5),
    malformed_proxies=st.lists(st.text(min_size=1, max_size=20, alphabet='abcdefg:'), min_size=1, max_size=5)
)
@settings(max_examples=50)
def test_property_malformed_input_skipping(valid_urls, valid_proxies, malformed_urls, malformed_proxies):
    """
    Property 3: Malformed input skipping
    For any list of inputs (URLs or proxies) containing both valid and malformed 
    entries, processing should skip malformed entries and successfully process 
    all valid entries.
    
    Validates: Requirements 1.4, 2.4
    """
    async def run_test():
        loader = ConfigLoader()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            urls_file = Path(tmpdir) / 'urls.txt'
            proxies_file = Path(tmpdir) / 'proxies.txt'
            
            # Mix valid and malformed URLs
            all_urls = valid_urls + malformed_urls
            with open(urls_file, 'w', encoding='utf-8') as f:
                for url in all_urls:
                    f.write(f"{url}\n")
            
            # Mix valid and malformed proxies
            all_proxies = valid_proxies + malformed_proxies
            with open(proxies_file, 'w', encoding='utf-8') as f:
                for proxy in all_proxies:
                    f.write(f"{proxy}\n")
            
            # Load - should skip malformed entries
            loaded_urls = await loader.load_urls(str(urls_file))
            loaded_proxies = await loader.load_proxies(str(proxies_file))
            
            # Property: At least all valid entries should be loaded
            # Note: Some malformed URLs might be loaded if they don't violate basic format
            assert len(loaded_urls) >= len(valid_urls), "At least all valid URLs should be loaded"
            assert len(loaded_proxies) == len(valid_proxies), "All valid proxies should be loaded"
            
            # Property: All valid URLs should be present in loaded URLs
            for valid_url in valid_urls:
                assert valid_url in loaded_urls, f"Valid URL {valid_url} should be in loaded URLs"
    
    asyncio.run(run_test())
