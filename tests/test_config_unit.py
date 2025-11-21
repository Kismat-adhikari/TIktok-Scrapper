"""Unit tests for ConfigLoader."""

import pytest
import tempfile
from pathlib import Path
from src.config import ConfigLoader
from src.types import ConfigurationError, Config


class TestConfigLoader:
    """Unit tests for ConfigLoader class."""
    
    @pytest.mark.asyncio
    async def test_load_urls_missing_file(self):
        """Test handling of missing URLs file (edge case)."""
        loader = ConfigLoader()
        
        with pytest.raises(ConfigurationError, match="URLs file not found"):
            await loader.load_urls("nonexistent_file.txt")
    
    @pytest.mark.asyncio
    async def test_load_urls_empty_file(self):
        """Test handling of empty URLs file (edge case)."""
        loader = ConfigLoader()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            urls_file = Path(tmpdir) / 'empty.txt'
            urls_file.write_text("")
            
            with pytest.raises(ConfigurationError, match="URLs file is empty"):
                await loader.load_urls(str(urls_file))
    
    @pytest.mark.asyncio
    async def test_load_proxies_missing_file(self):
        """Test handling of missing proxies file (edge case)."""
        loader = ConfigLoader()
        
        with pytest.raises(ConfigurationError, match="Proxies file not found"):
            await loader.load_proxies("nonexistent_file.txt")
    
    @pytest.mark.asyncio
    async def test_load_proxies_empty_file(self):
        """Test handling of empty proxies file (edge case)."""
        loader = ConfigLoader()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            proxies_file = Path(tmpdir) / 'empty.txt'
            proxies_file.write_text("")
            
            with pytest.raises(ConfigurationError, match="No valid proxies found"):
                await loader.load_proxies(str(proxies_file))
    
    def test_parse_proxy_malformed_format(self):
        """Test malformed proxy format parsing."""
        loader = ConfigLoader()
        
        # Too few parts
        with pytest.raises(ValueError, match="Invalid proxy format"):
            loader._parse_proxy_line("1.2.3.4:8080:user")
        
        # Too many parts
        with pytest.raises(ValueError, match="Invalid proxy format"):
            loader._parse_proxy_line("1.2.3.4:8080:user:pass:extra")
        
        # Invalid port
        with pytest.raises(ValueError, match="Invalid port"):
            loader._parse_proxy_line("1.2.3.4:abc:user:pass")
        
        # Port out of range
        with pytest.raises(ValueError, match="Invalid port number"):
            loader._parse_proxy_line("1.2.3.4:99999:user:pass")
        
        # Empty username
        with pytest.raises(ValueError, match="Username cannot be empty"):
            loader._parse_proxy_line("1.2.3.4:8080::pass")
        
        # Empty password
        with pytest.raises(ValueError, match="Password cannot be empty"):
            loader._parse_proxy_line("1.2.3.4:8080:user:")
    
    def test_validate_config_empty_urls(self):
        """Test validation with empty URLs."""
        loader = ConfigLoader()
        config = Config(urls=[], proxies=[])
        
        result = loader.validate_config(config)
        
        assert not result.valid
        assert "No URLs provided" in result.errors
    
    def test_validate_config_invalid_url_format(self):
        """Test validation with invalid URL format."""
        loader = ConfigLoader()
        config = Config(
            urls=["not-a-url", "http://valid.com"],
            proxies=[]
        )
        
        result = loader.validate_config(config)
        
        assert not result.valid
        assert any("Invalid URL format" in err for err in result.errors)
    
    def test_validate_config_empty_proxies(self):
        """Test validation with empty proxies."""
        loader = ConfigLoader()
        config = Config(urls=["http://test.com"], proxies=[])
        
        result = loader.validate_config(config)
        
        assert not result.valid
        assert "No proxies provided" in result.errors
    
    @pytest.mark.asyncio
    async def test_load_urls_skips_comments(self):
        """Test that comments and empty lines are skipped."""
        loader = ConfigLoader()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            urls_file = Path(tmpdir) / 'urls.txt'
            urls_file.write_text(
                "# This is a comment\n"
                "http://example.com\n"
                "\n"
                "# Another comment\n"
                "https://test.com\n"
            )
            
            urls = await loader.load_urls(str(urls_file))
            
            assert len(urls) == 2
            assert urls[0] == "http://example.com"
            assert urls[1] == "https://test.com"
    
    @pytest.mark.asyncio
    async def test_load_proxies_skips_comments(self):
        """Test that comments and empty lines are skipped in proxies."""
        loader = ConfigLoader()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            proxies_file = Path(tmpdir) / 'proxies.txt'
            proxies_file.write_text(
                "# Proxy list\n"
                "1.2.3.4:8080:user1:pass1\n"
                "\n"
                "5.6.7.8:9090:user2:pass2\n"
            )
            
            proxies = await loader.load_proxies(str(proxies_file))
            
            assert len(proxies) == 2
            assert proxies[0].ip == "1.2.3.4"
            assert proxies[1].ip == "5.6.7.8"
