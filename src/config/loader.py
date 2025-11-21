"""Configuration loader for reading URLs and proxy configurations."""

import os
from pathlib import Path
from typing import List

from src.types import Config, ProxyConfig, ValidationResult, ConfigurationError


class ConfigLoader:
    """Loads and validates configuration from input files."""

    async def load_urls(self, file_path: str) -> List[str]:
        """
        Load URLs from a text file.
        
        Args:
            file_path: Path to the URLs file
            
        Returns:
            List of URLs (excluding comments and empty lines)
            
        Raises:
            ConfigurationError: If file is missing or empty
        """
        path = Path(file_path)
        
        if not path.exists():
            raise ConfigurationError(f"URLs file not found: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            raise ConfigurationError(f"Failed to read URLs file: {e}")
        
        # Filter out comments and empty lines
        urls = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)
        
        if not urls:
            raise ConfigurationError(f"URLs file is empty: {file_path}")
        
        return urls

    async def load_proxies(self, file_path: str) -> List[ProxyConfig]:
        """
        Load proxy configurations from a text file.
        Expected format: IP:PORT:USERNAME:PASSWORD
        
        Args:
            file_path: Path to the proxies file
            
        Returns:
            List of ProxyConfig objects
            
        Raises:
            ConfigurationError: If file is missing or empty
        """
        path = Path(file_path)
        
        if not path.exists():
            raise ConfigurationError(f"Proxies file not found: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            raise ConfigurationError(f"Failed to read proxies file: {e}")
        
        # Parse proxy configurations
        proxies = []
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            try:
                proxy = self._parse_proxy_line(line)
                proxies.append(proxy)
            except ValueError as e:
                # Skip malformed entries but log warning
                print(f"Warning: Skipping malformed proxy on line {line_num}: {e}")
                continue
        
        if not proxies:
            raise ConfigurationError(f"No valid proxies found in: {file_path}")
        
        return proxies

    def _parse_proxy_line(self, line: str) -> ProxyConfig:
        """
        Parse a single proxy line in IP:PORT:USERNAME:PASSWORD format.
        
        Args:
            line: Proxy configuration line
            
        Returns:
            ProxyConfig object
            
        Raises:
            ValueError: If line format is invalid
        """
        parts = line.split(':')
        
        if len(parts) != 4:
            raise ValueError(
                f"Invalid proxy format. Expected IP:PORT:USERNAME:PASSWORD, got: {line}"
            )
        
        ip, port_str, username, password = parts
        
        # Validate IP (basic check)
        if not ip or not all(c.isdigit() or c == '.' for c in ip):
            raise ValueError(f"Invalid IP address: {ip}")
        
        # Validate and parse port
        try:
            port = int(port_str)
            if not (1 <= port <= 65535):
                raise ValueError(f"Port must be between 1 and 65535, got: {port}")
        except ValueError:
            raise ValueError(f"Invalid port number: {port_str}")
        
        # Validate username and password are not empty
        if not username:
            raise ValueError("Username cannot be empty")
        if not password:
            raise ValueError("Password cannot be empty")
        
        return ProxyConfig(
            ip=ip,
            port=port,
            username=username,
            password=password
        )

    def validate_config(self, config: Config) -> ValidationResult:
        """
        Validate the loaded configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            ValidationResult with validation status and any errors
        """
        errors = []
        
        # Validate URLs
        if not config.urls:
            errors.append("No URLs provided")
        else:
            for i, url in enumerate(config.urls):
                if not url.strip():
                    errors.append(f"Empty URL at index {i}")
                elif not url.startswith(('http://', 'https://')):
                    errors.append(f"Invalid URL format at index {i}: {url}")
        
        # Validate proxies
        if not config.proxies:
            errors.append("No proxies provided")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors
        )
