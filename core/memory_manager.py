"""
High-Performance Memory and Buffer Management System
Optimized for 10 Gbps network and multi-core processing
"""

import os
import gc
import mmap
import threading
import queue
import psutil
from typing import Dict, List, Optional, Any
from collections import deque
import weakref
import ctypes
from ctypes import wintypes

class HighPerformanceMemoryPool:
    """Memory pool for high-performance request handling - Set to 8GB"""
    
    def __init__(self, pool_size: int = 8 * 1024 * 1024 * 1024):  # 8GB default
        self.pool_size = pool_size
        self.chunk_size = 128 * 1024  # 128KB chunks (increased from 64KB)
        self.available_chunks = queue.Queue()
        self.allocated_chunks = weakref.WeakSet()
        self.lock = threading.RLock()
        
        # Pre-allocate memory pool
        self._initialize_pool()
        
        # Memory statistics
        self.stats = {
            'total_allocated': 0,
            'peak_usage': 0,
            'allocations': 0,
            'deallocations': 0,
            'pool_hits': 0,
            'pool_misses': 0
        }
    
    def _initialize_pool(self):
        """Initialize memory pool with pre-allocated chunks"""
        num_chunks = self.pool_size // self.chunk_size
        
        try:
            # Pre-allocate chunks
            for _ in range(num_chunks):
                chunk = bytearray(self.chunk_size)
                self.available_chunks.put(chunk)
                
            print(f"✅ Memory pool initialized: {num_chunks} chunks of {self.chunk_size} bytes")
            
        except MemoryError:
            print(f"⚠️  Warning: Could not allocate full memory pool, using system memory")
    
    def get_chunk(self, size: int = None) -> bytearray:
        """Get a memory chunk from the pool"""
        if size is None:
            size = self.chunk_size
            
        with self.lock:
            try:
                if size <= self.chunk_size and not self.available_chunks.empty():
                    chunk = self.available_chunks.get_nowait()
                    self.allocated_chunks.add(chunk)
                    self.stats['pool_hits'] += 1
                    self.stats['allocations'] += 1
                    return chunk
                else:
                    # Fallback to system allocation
                    chunk = bytearray(size)
                    self.stats['pool_misses'] += 1
                    self.stats['allocations'] += 1
                    return chunk
                    
            except queue.Empty:
                # Pool exhausted, allocate from system
                chunk = bytearray(size)
                self.stats['pool_misses'] += 1
                self.stats['allocations'] += 1
                return chunk
    
    def return_chunk(self, chunk: bytearray):
        """Return a chunk to the pool"""
        if len(chunk) == self.chunk_size:
            with self.lock:
                # Clear the chunk
                chunk[:] = b'\x00' * len(chunk)
                
                try:
                    self.available_chunks.put_nowait(chunk)
                    self.stats['deallocations'] += 1
                except queue.Full:
                    # Pool is full, let GC handle it
                    pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory pool statistics"""
        with self.lock:
            current_usage = (self.stats['allocations'] - self.stats['deallocations']) * self.chunk_size
            self.stats['peak_usage'] = max(self.stats['peak_usage'], current_usage)
            return self.stats.copy()
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics - compatibility method"""
        return self.get_stats()
    
    def get_pool_size(self) -> int:
        """Get pool size - compatibility method"""
        return self.pool_size
    
    def optimize_memory(self):
        """Optimize memory - compatibility method"""
        # Trigger garbage collection
        gc.collect()
        
        # Clear unused chunks
        with self.lock:
            # Force cleanup of weak references
            self.allocated_chunks.clear()
    
    def cleanup(self):
        """Cleanup memory pool - compatibility method"""
        self.optimize_memory()

class BufferManager:
    """High-performance buffer management for network operations - Enhanced capacity"""
    
    def __init__(self, buffer_sizes: List[int] = None):
        if buffer_sizes is None:
            # Increased buffer sizes for better performance
            buffer_sizes = [2048, 8192, 16384, 32768, 65536, 131072, 262144]  # Up to 256KB buffers
            
        self.buffer_pools = {}
        self.lock = threading.RLock()
        
        # Initialize buffer pools for different sizes
        for size in buffer_sizes:
            self.buffer_pools[size] = {
                'available': deque(),
                'allocated': weakref.WeakSet(),
                'stats': {'hits': 0, 'misses': 0, 'allocations': 0}
            }
            
            # Pre-allocate more buffers for better performance
            buffer_count = 500 if size <= 65536 else 200  # More buffers for smaller sizes
            for _ in range(buffer_count):
                buffer = bytearray(size)
                self.buffer_pools[size]['available'].append(buffer)
    
    def get_buffer(self, min_size: int) -> bytearray:
        """Get an appropriately sized buffer"""
        # Find the smallest buffer that fits
        suitable_size = None
        for size in sorted(self.buffer_pools.keys()):
            if size >= min_size:
                suitable_size = size
                break
        
        if suitable_size is None:
            # Need a larger buffer than available, allocate directly
            return bytearray(min_size)
        
        with self.lock:
            pool = self.buffer_pools[suitable_size]
            
            if pool['available']:
                buffer = pool['available'].popleft()
                pool['allocated'].add(buffer)
                pool['stats']['hits'] += 1
                pool['stats']['allocations'] += 1
                return buffer
            else:
                # Pool exhausted, allocate new
                buffer = bytearray(suitable_size)
                pool['stats']['misses'] += 1
                pool['stats']['allocations'] += 1
                return buffer
    
    def return_buffer(self, buffer: bytearray):
        """Return buffer to appropriate pool"""
        size = len(buffer)
        
        if size in self.buffer_pools:
            with self.lock:
                pool = self.buffer_pools[size]
                
                # Clear buffer
                buffer[:] = b'\x00' * len(buffer)
                
                # Return to pool if not full
                if len(pool['available']) < 200:  # Max 200 buffers per pool
                    pool['available'].append(buffer)
    
    def allocate_buffer(self, size: int) -> bytearray:
        """Allocate buffer - compatibility method"""
        return self.get_buffer(size)
    
    def deallocate_buffer(self, buffer: bytearray):
        """Deallocate buffer - compatibility method"""
        return self.return_buffer(buffer)
    
    def get_pool_size(self) -> int:
        """Get pool size - compatibility method"""
        return len(self.buffer_pools)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get buffer pool statistics"""
        with self.lock:
            stats = {}
            for size, pool in self.buffer_pools.items():
                stats[f'buffer_{size}'] = {
                    'available': len(pool['available']),
                    'allocated': len(pool['allocated']),
                    'hits': pool['stats']['hits'],
                    'misses': pool['stats']['misses'],
                    'allocations': pool['stats']['allocations']
                }
            return stats

class MemoryOptimizer:
    """System memory optimization for high-performance operations"""
    
    def __init__(self):
        self.original_gc_thresholds = gc.get_threshold()
        self.optimization_applied = False
    
    def optimize_for_performance(self):
        """Apply memory optimizations for high performance"""
        try:
            # Disable garbage collection during high-performance operations
            gc.disable()
            
            # Set aggressive GC thresholds when enabled
            gc.set_threshold(10000, 100, 100)
            
            # Force immediate garbage collection
            gc.collect()
            
            # Try to optimize system memory settings (Windows specific)
            if os.name == 'nt':
                self._optimize_windows_memory()
            
            self.optimization_applied = True
            print("✅ Memory optimizations applied for high performance")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not apply all memory optimizations: {e}")
    
    def _optimize_windows_memory(self):
        """Windows-specific memory optimizations"""
        try:
            # Increase working set size
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetCurrentProcess()
            
            # Set working set size (min: 1GB, max: 4GB)
            min_size = 1024 * 1024 * 1024  # 1GB
            max_size = 4 * 1024 * 1024 * 1024  # 4GB
            
            kernel32.SetProcessWorkingSetSize(handle, min_size, max_size)
            
        except Exception as e:
            print(f"⚠️  Could not optimize Windows memory settings: {e}")
    
    def restore_defaults(self):
        """Restore original memory settings"""
        if self.optimization_applied:
            # Re-enable garbage collection
            gc.enable()
            
            # Restore original GC thresholds
            gc.set_threshold(*self.original_gc_thresholds)
            
            # Force cleanup
            gc.collect()
            
            self.optimization_applied = False
            print("✅ Memory settings restored to defaults")
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get current memory usage information"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss,  # Resident Set Size
            'vms': memory_info.vms,  # Virtual Memory Size
            'percent': process.memory_percent(),
            'available': psutil.virtual_memory().available,
            'total': psutil.virtual_memory().total,
            'gc_enabled': gc.isenabled(),
            'gc_counts': gc.get_count(),
            'gc_thresholds': gc.get_threshold()
        }

class RequestDataCache:
    """Cache for pre-built request data to reduce allocation overhead"""
    
    def __init__(self, cache_size: int = 10000):
        self.cache_size = cache_size
        self.cache = deque(maxlen=cache_size)
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    def get_request_data(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Get cached request data or create new"""
        with self.lock:
            # Try to find matching template in cache
            for cached_data in self.cache:
                if self._templates_match(cached_data['template'], template):
                    self.stats['hits'] += 1
                    return cached_data['data'].copy()
            
            # Not found in cache, create new
            request_data = self._create_request_data(template)
            
            # Add to cache
            if len(self.cache) >= self.cache_size:
                self.stats['evictions'] += 1
            
            self.cache.append({
                'template': template.copy(),
                'data': request_data.copy()
            })
            
            self.stats['misses'] += 1
            return request_data
    
    def _templates_match(self, template1: Dict[str, Any], template2: Dict[str, Any]) -> bool:
        """Check if two templates match"""
        # Simple comparison - can be enhanced for more complex matching
        return template1.get('method') == template2.get('method') and \
               template1.get('content_type') == template2.get('content_type')
    
    def _create_request_data(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Create request data from template"""
        return {
            'headers': template.get('headers', {}),
            'data': template.get('data', ''),
            'params': template.get('params', {}),
            'timeout': template.get('timeout', (1, 3)),
            'allow_redirects': template.get('allow_redirects', False),
            'verify': template.get('verify', False)
        }
    
    def clear_cache(self):
        """Clear the cache"""
        with self.lock:
            self.cache.clear()
            self.stats = {'hits': 0, 'misses': 0, 'evictions': 0}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            hit_rate = self.stats['hits'] / (self.stats['hits'] + self.stats['misses']) if (self.stats['hits'] + self.stats['misses']) > 0 else 0
            return {
                **self.stats,
                'cache_size': len(self.cache),
                'hit_rate': hit_rate
            }

# Global instances
memory_pool = HighPerformanceMemoryPool()
buffer_manager = BufferManager()
memory_optimizer = MemoryOptimizer()
request_cache = RequestDataCache()

# For backward compatibility
MemoryManager = HighPerformanceMemoryPool

def initialize_memory_optimizations():
    """Initialize all memory optimizations"""
    print("🚀 Initializing high-performance memory optimizations...")
    memory_optimizer.optimize_for_performance()
    print("✅ Memory optimizations ready")

def cleanup_memory_optimizations():
    """Cleanup memory optimizations"""
    print("🧹 Cleaning up memory optimizations...")
    memory_optimizer.restore_defaults()
    request_cache.clear_cache()
    gc.collect()
    print("✅ Memory cleanup completed")

def get_memory_stats() -> Dict[str, Any]:
    """Get comprehensive memory statistics"""
    return {
        'memory_pool': memory_pool.get_stats(),
        'buffer_manager': buffer_manager.get_stats(),
        'memory_info': memory_optimizer.get_memory_info(),
        'request_cache': request_cache.get_stats()
    }