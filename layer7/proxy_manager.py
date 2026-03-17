"""
Proxy Management System for Layer 7 Attacks
"""

import asyncio
import aiohttp
import random
import time
import threading
import warnings
import urllib3
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.logger import logger
from core.utils import NetworkUtils, ValidationUtils


@dataclass
class ProxyInfo:
    """Proxy information container"""
    host: str
    port: int
    protocol: str  # http, https, socks4, socks5
    username: Optional[str] = None
    password: Optional[str] = None
    response_time: Optional[float] = None
    success_rate: float = 0.0
    last_tested: Optional[float] = None
    is_working: bool = False
    country: Optional[str] = None
    anonymity: Optional[str] = None  # transparent, anonymous, elite
    
    @property
    def url(self) -> str:
        """Get proxy URL"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"
    
    @property
    def address(self) -> str:
        """Get proxy address"""
        return f"{self.host}:{self.port}"


class ProxyScanner:
    """Scan and collect proxies from various sources - Optimized for speed"""
    
    def __init__(self):
        # Expanded proxy sources for faster collection
        self.sources = [
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://api.proxyscrape.com/v2/?request=get&protocol=http',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
            'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
            'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
            'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt',
            'https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt',
            'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt',
            'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt'
        ]
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0'
        ]
    
    async def scan_proxies(self, max_proxies: int = 5000) -> List[ProxyInfo]:  # Increased from 1000
        """Scan for proxies from multiple sources - High speed mode"""
        logger.info("Starting high-speed proxy scan from multiple sources")
        
        all_proxies = []
        
        # Reduced timeout for faster scanning
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10, connect=5),  # Reduced from 30s to 10s
            headers={'User-Agent': random.choice(self.user_agents)},
            connector=aiohttp.TCPConnector(limit=200, limit_per_host=50)  # Increased connection limits
        ) as session:
            
            tasks = []
            for source in self.sources:
                task = asyncio.create_task(self._scan_source(session, source))
                tasks.append(task)
            
            # Gather results from all sources with faster timeout
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_proxies.extend(result)
                elif isinstance(result, Exception):
                    logger.warning(f"Source scan failed: {result}")
        
        # Remove duplicates and limit
        unique_proxies = self._remove_duplicates(all_proxies)
        limited_proxies = unique_proxies[:max_proxies]
        
        logger.info(f"Collected {len(limited_proxies)} unique proxies in high-speed mode")
        return limited_proxies
    
    async def _scan_source(self, session: aiohttp.ClientSession, source: str) -> List[ProxyInfo]:
        """Scan single proxy source"""
        try:
            logger.debug(f"Scanning proxy source: {source}")
            
            async with session.get(source) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._parse_proxy_list(content)
                else:
                    logger.warning(f"Source returned status {response.status}: {source}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to scan source {source}: {e}")
            return []
    
    def _parse_proxy_list(self, content: str) -> List[ProxyInfo]:
        """Parse proxy list from text content"""
        proxies = []
        
        for line in content.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Try different formats
            proxy_info = self._parse_proxy_line(line)
            if proxy_info:
                proxies.append(proxy_info)
        
        return proxies
    
    def _parse_proxy_line(self, line: str) -> Optional[ProxyInfo]:
        """Parse single proxy line"""
        try:
            # Format: host:port or protocol://host:port
            if '://' in line:
                parsed = urlparse(line)
                protocol = parsed.scheme
                host = parsed.hostname
                port = parsed.port
                username = parsed.username
                password = parsed.password
            else:
                # Simple host:port format
                parts = line.split(':')
                if len(parts) >= 2:
                    host = parts[0].strip()
                    port = int(parts[1].strip())
                    protocol = 'http'  # Default to HTTP
                    username = None
                    password = None
                else:
                    return None
            
            # Validate
            if not host or not port:
                return None
            
            if not ValidationUtils.is_valid_ip(host) and not ValidationUtils.is_valid_hostname(host):
                return None
            
            return ProxyInfo(
                host=host,
                port=port,
                protocol=protocol,
                username=username,
                password=password
            )
            
        except Exception as e:
            logger.debug(f"Failed to parse proxy line '{line}': {e}")
            return None
    
    def _remove_duplicates(self, proxies: List[ProxyInfo]) -> List[ProxyInfo]:
        """Remove duplicate proxies"""
        seen = set()
        unique_proxies = []
        
        for proxy in proxies:
            key = (proxy.host, proxy.port, proxy.protocol)
            if key not in seen:
                seen.add(key)
                unique_proxies.append(proxy)
        
        return unique_proxies


class ProxyTester:
    """Test proxy connectivity and performance - Optimized for high-speed testing"""
    
    def __init__(self):
        # Expanded test URLs for better validation
        self.test_urls = [
            'http://httpbin.org/ip',
            'https://httpbin.org/ip',
            'http://icanhazip.com',
            'https://api.ipify.org',
            'http://checkip.amazonaws.com',
            'https://ipinfo.io/ip',
            'http://ident.me',
            'https://api.myip.com'
        ]
        
        # Optimized settings for speed
        self.timeout = 5  # Reduced from 10 to 5 seconds
        self.max_concurrent = 200  # Increased from 50 to 200
        self.batch_size = 500  # Process in batches for better memory management
    
    async def test_proxies(self, proxies: List[ProxyInfo], 
                          max_concurrent: Optional[int] = None) -> List[ProxyInfo]:
        """Test multiple proxies concurrently with batch processing"""
        if not proxies:
            return []
        
        concurrent_limit = max_concurrent or self.max_concurrent
        logger.info(f"High-speed testing {len(proxies)} proxies with {concurrent_limit} concurrent connections")
        
        working_proxies = []
        
        # Process proxies in batches for better performance
        for i in range(0, len(proxies), self.batch_size):
            batch = proxies[i:i + self.batch_size]
            logger.info(f"Testing batch {i//self.batch_size + 1}/{(len(proxies) + self.batch_size - 1)//self.batch_size}")
            
            # Create semaphore to limit concurrent connections
            semaphore = asyncio.Semaphore(concurrent_limit)
            
            # Test batch of proxies
            tasks = []
            for proxy in batch:
                task = asyncio.create_task(self._test_proxy_with_semaphore(proxy, semaphore))
                tasks.append(task)
            
            # Wait for batch to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter working proxies from this batch
            for result in results:
                if isinstance(result, ProxyInfo) and result.is_working:
                    working_proxies.append(result)
        
        # Sort by response time
        working_proxies.sort(key=lambda p: p.response_time or float('inf'))
        
        logger.info(f"High-speed test completed: {len(working_proxies)} working proxies out of {len(proxies)}")
        return working_proxies
    
    async def _test_proxy_with_semaphore(self, proxy: ProxyInfo, semaphore: asyncio.Semaphore) -> ProxyInfo:
        """Test single proxy with semaphore"""
        async with semaphore:
            return await self._test_proxy(proxy)
    
    async def _test_proxy(self, proxy: ProxyInfo) -> ProxyInfo:
        """Test single proxy"""
        start_time = time.time()
        
        try:
            # Create proxy connector
            if proxy.protocol.lower() in ['http', 'https']:
                connector = aiohttp.TCPConnector()
                proxy_url = proxy.url
            else:
                # For SOCKS proxies, we'd need aiohttp-socks
                logger.debug(f"SOCKS proxy not supported in basic test: {proxy.address}")
                proxy.is_working = False
                return proxy
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            ) as session:
                
                # Test with a simple HTTP request
                test_url = random.choice(self.test_urls)
                
                async with session.get(
                    test_url,
                    proxy=proxy_url if proxy.protocol.lower() in ['http', 'https'] else None
                ) as response:
                    
                    if response.status == 200:
                        response_time = time.time() - start_time
                        proxy.response_time = response_time
                        proxy.is_working = True
                        proxy.last_tested = time.time()
                        proxy.success_rate = 1.0
                        
                        # Try to get response content for additional validation
                        try:
                            content = await response.text()
                            if len(content) > 0:
                                logger.debug(f"Proxy {proxy.address} working - {response_time:.2f}s")
                            else:
                                proxy.is_working = False
                        except:
                            proxy.is_working = False
                    else:
                        proxy.is_working = False
                        
        except Exception as e:
            logger.debug(f"Proxy {proxy.address} failed: {e}")
            proxy.is_working = False
            proxy.last_tested = time.time()
        
        return proxy
    
    def test_proxy_sync(self, proxy: ProxyInfo, test_url: str = None) -> bool:
        """Synchronous proxy test"""
        import requests
        
        try:
            test_url = test_url or 'http://httpbin.org/ip'
            proxies = {
                'http': proxy.url,
                'https': proxy.url
            }
            
            start_time = time.time()
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', urllib3.exceptions.InsecureRequestWarning)
                response = requests.get(
                    test_url,
                    proxies=proxies,
                    timeout=self.timeout,
                    verify=False
                )
            
            if response.status_code == 200:
                proxy.response_time = time.time() - start_time
                proxy.is_working = True
                proxy.last_tested = time.time()
                return True
            
        except Exception as e:
            logger.debug(f"Sync proxy test failed for {proxy.address}: {e}")
        
        proxy.is_working = False
        proxy.last_tested = time.time()
        return False


class ProxyManager:
    """Manage proxy pool for attacks"""
    
    def __init__(self):
        self.proxies: List[ProxyInfo] = []
        self.working_proxies: List[ProxyInfo] = []
        self.failed_proxies: Set[str] = set()
        
        self.scanner = ProxyScanner()
        self.tester = ProxyTester()
        
        self._lock = threading.Lock()
        self._current_index = 0
        
        # Statistics
        self.stats = {
            'total_proxies': 0,
            'working_proxies': 0,
            'failed_proxies': 0,
            'success_rate': 0.0,
            'last_scan': None,
            'last_test': None
        }
    
    async def initialize(self, scan_proxies: bool = True, test_proxies: bool = True):
        """Initialize proxy manager"""
        logger.info("Initializing proxy manager")
        
        if scan_proxies:
            await self.scan_and_load_proxies()
        
        if test_proxies and self.proxies:
            await self.test_all_proxies()
        
        self._update_stats()
    
    async def scan_and_load_proxies(self, max_proxies: int = 5000):
        """Scan and load proxies - High-speed mode"""
        logger.info("Scanning for proxies in high-speed mode")
        
        proxies = await self.scanner.scan_proxies(max_proxies)
        
        with self._lock:
            self.proxies = proxies
            self.stats['last_scan'] = time.time()
        
        logger.info(f"Loaded {len(proxies)} proxies in high-speed mode")
    
    async def test_all_proxies(self):
        """Test all loaded proxies - High-speed mode"""
        if not self.proxies:
            logger.warning("No proxies to test")
            return
        
        logger.info(f"Testing {len(self.proxies)} proxies in high-speed mode")
        
        working_proxies = await self.tester.test_proxies(self.proxies)
        
        with self._lock:
            self.working_proxies = working_proxies
            self.stats['last_test'] = time.time()
        
        logger.info(f"High-speed testing completed: {len(working_proxies)} working proxies found")
        
        self._update_stats()
        logger.info(f"Found {len(working_proxies)} working proxies")
    
    def get_proxy(self, exclude_failed: bool = True) -> Optional[ProxyInfo]:
        """Get next available proxy"""
        with self._lock:
            available_proxies = self.working_proxies if exclude_failed else self.proxies
            
            if not available_proxies:
                return None
            
            # Filter out failed proxies if requested
            if exclude_failed:
                available_proxies = [
                    p for p in available_proxies 
                    if p.address not in self.failed_proxies
                ]
            
            if not available_proxies:
                return None
            
            # Round-robin selection
            proxy = available_proxies[self._current_index % len(available_proxies)]
            self._current_index += 1
            
            return proxy
    
    def get_random_proxy(self, exclude_failed: bool = True) -> Optional[ProxyInfo]:
        """Get random proxy"""
        with self._lock:
            available_proxies = self.working_proxies if exclude_failed else self.proxies
            
            if exclude_failed:
                available_proxies = [
                    p for p in available_proxies 
                    if p.address not in self.failed_proxies
                ]
            
            if not available_proxies:
                return None
            
            return random.choice(available_proxies)
    
    def mark_proxy_failed(self, proxy: ProxyInfo):
        """Mark proxy as failed"""
        with self._lock:
            self.failed_proxies.add(proxy.address)
            proxy.is_working = False
        
        logger.debug(f"Marked proxy as failed: {proxy.address}")
    
    def mark_proxy_working(self, proxy: ProxyInfo):
        """Mark proxy as working"""
        with self._lock:
            self.failed_proxies.discard(proxy.address)
            proxy.is_working = True
        
        logger.debug(f"Marked proxy as working: {proxy.address}")
    
    def get_proxy_stats(self) -> Dict:
        """Get proxy statistics"""
        with self._lock:
            return self.stats.copy()
    
    def clear_failed_proxies(self):
        """Clear failed proxy list"""
        with self._lock:
            self.failed_proxies.clear()
        
        logger.info("Cleared failed proxy list")
    
    def remove_proxy(self, proxy: ProxyInfo):
        """Remove proxy from all lists"""
        with self._lock:
            if proxy in self.proxies:
                self.proxies.remove(proxy)
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
            self.failed_proxies.discard(proxy.address)
        
        self._update_stats()
    
    def add_proxy(self, proxy: ProxyInfo):
        """Add proxy to the pool"""
        with self._lock:
            if proxy not in self.proxies:
                self.proxies.append(proxy)
                if proxy.is_working:
                    self.working_proxies.append(proxy)
        
        self._update_stats()
    
    def _update_stats(self):
        """Update internal statistics"""
        with self._lock:
            self.stats['total_proxies'] = len(self.proxies)
            self.stats['working_proxies'] = len(self.working_proxies)
            self.stats['failed_proxies'] = len(self.failed_proxies)
            
            if self.stats['total_proxies'] > 0:
                self.stats['success_rate'] = (
                    self.stats['working_proxies'] / self.stats['total_proxies']
                ) * 100
            else:
                self.stats['success_rate'] = 0.0
    
    def export_proxies(self, filename: str, working_only: bool = True):
        """Export proxies to file"""
        proxies_to_export = self.working_proxies if working_only else self.proxies
        
        with open(filename, 'w') as f:
            for proxy in proxies_to_export:
                f.write(f"{proxy.address}\n")
        
        logger.info(f"Exported {len(proxies_to_export)} proxies to {filename}")
    
    def import_proxies(self, filename: str):
        """Import proxies from file"""
        try:
            with open(filename, 'r') as f:
                content = f.read()
            
            proxies = self.scanner._parse_proxy_list(content)
            
            with self._lock:
                for proxy in proxies:
                    if proxy not in self.proxies:
                        self.proxies.append(proxy)
            
            self._update_stats()
            logger.info(f"Imported {len(proxies)} proxies from {filename}")
            
        except Exception as e:
            logger.error(f"Failed to import proxies from {filename}: {e}")


# Global proxy manager instance
proxy_manager = ProxyManager()