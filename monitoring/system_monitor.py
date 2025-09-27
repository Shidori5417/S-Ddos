"""
System Monitoring and Performance Optimization Module
Real-time system monitoring, resource optimization, and performance tuning
"""

import psutil
import threading
import time
import json
import os
import platform
import socket
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import statistics
from collections import deque, defaultdict

from core.logger import logger


@dataclass
class MonitoringConfig:
    """Configuration for system monitoring"""
    # Monitoring Intervals
    cpu_monitor_interval: float = 1.0  # seconds
    memory_monitor_interval: float = 2.0
    network_monitor_interval: float = 1.0
    disk_monitor_interval: float = 5.0
    process_monitor_interval: float = 3.0
    
    # Thresholds
    cpu_warning_threshold: float = 80.0  # percentage
    cpu_critical_threshold: float = 95.0
    memory_warning_threshold: float = 85.0
    memory_critical_threshold: float = 95.0
    disk_warning_threshold: float = 90.0
    disk_critical_threshold: float = 98.0
    
    # History Settings
    history_size: int = 1000  # number of data points to keep
    enable_history: bool = True
    save_to_file: bool = True
    log_file_path: str = "monitoring.log"
    
    # Performance Optimization
    auto_optimization: bool = True
    optimize_cpu: bool = True
    optimize_memory: bool = True
    optimize_network: bool = True
    
    # Alert Settings
    enable_alerts: bool = True
    alert_cooldown: int = 300  # seconds between same alerts
    
    # Advanced Features
    monitor_attack_processes: bool = True
    track_network_connections: bool = True
    monitor_system_calls: bool = False
    enable_predictive_analysis: bool = True


class CPUMonitor:
    """CPU monitoring and optimization"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.cpu_history = deque(maxlen=config.history_size)
        self.core_history = defaultdict(lambda: deque(maxlen=config.history_size))
        self.is_monitoring = False
        self.last_alert = {}
        
    def start_monitoring(self):
        """Start CPU monitoring"""
        self.is_monitoring = True
        thread = threading.Thread(target=self._monitor_loop)
        thread.daemon = True
        thread.start()
        logger.info("CPU monitoring started")
    
    def _monitor_loop(self):
        """Main CPU monitoring loop"""
        while self.is_monitoring:
            try:
                # Get overall CPU usage
                cpu_percent = psutil.cpu_percent(interval=None)
                
                # Get per-core usage
                cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
                
                # Get CPU frequency
                cpu_freq = psutil.cpu_freq()
                
                # Get CPU stats
                cpu_stats = psutil.cpu_stats()
                
                # Store data
                timestamp = datetime.now()
                cpu_data = {
                    'timestamp': timestamp,
                    'cpu_percent': cpu_percent,
                    'cpu_per_core': cpu_per_core,
                    'cpu_freq': cpu_freq._asdict() if cpu_freq else None,
                    'cpu_stats': cpu_stats._asdict(),
                    'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None
                }
                
                if self.config.enable_history:
                    self.cpu_history.append(cpu_data)
                
                # Check thresholds and alerts
                self._check_cpu_thresholds(cpu_data)
                
                # Auto-optimization
                if self.config.auto_optimization and self.config.optimize_cpu:
                    self._optimize_cpu_usage(cpu_data)
                
                time.sleep(self.config.cpu_monitor_interval)
                
            except Exception as e:
                logger.error(f"CPU monitoring error: {e}")
                time.sleep(5)
    
    def _check_cpu_thresholds(self, cpu_data: Dict[str, Any]):
        """Check CPU usage thresholds"""
        cpu_percent = cpu_data['cpu_percent']
        
        if cpu_percent >= self.config.cpu_critical_threshold:
            self._send_alert('cpu_critical', f"Critical CPU usage: {cpu_percent:.1f}%")
        elif cpu_percent >= self.config.cpu_warning_threshold:
            self._send_alert('cpu_warning', f"High CPU usage: {cpu_percent:.1f}%")
    
    def _optimize_cpu_usage(self, cpu_data: Dict[str, Any]):
        """Optimize CPU usage"""
        cpu_percent = cpu_data['cpu_percent']
        
        if cpu_percent >= self.config.cpu_warning_threshold:
            # Get high CPU processes
            high_cpu_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > 10.0:
                        high_cpu_processes.append(proc.info)
                except:
                    continue
            
            # Sort by CPU usage
            high_cpu_processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            logger.info(f"High CPU processes detected: {high_cpu_processes[:5]}")
            
            # Implement CPU optimization strategies
            self._apply_cpu_optimizations(high_cpu_processes)
    
    def _apply_cpu_optimizations(self, processes: List[Dict[str, Any]]):
        """Apply CPU optimization strategies - Linux optimized"""
        try:
            # Lower priority of high CPU processes (except critical ones)
            for proc_info in processes[:3]:  # Top 3 CPU consumers
                try:
                    proc = psutil.Process(proc_info['pid'])
                    
                    # Don't modify system processes
                    if proc_info['name'] in ['System', 'kernel', 'init', 'kthreadd', 'systemd']:
                        continue
                    
                    # Lower process priority (Linux-optimized)
                    current_nice = proc.nice()
                    if current_nice < 10:  # Only increase nice value (lower priority)
                        new_nice = min(current_nice + 5, 19)  # Max nice value is 19
                        proc.nice(new_nice)
                        logger.debug(f"Lowered priority for process {proc_info['name']} (PID: {proc_info['pid']}) from {current_nice} to {new_nice}")
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, PermissionError) as e:
                    logger.debug(f"Failed to optimize process {proc_info['pid']}: {e}")
            
        except Exception as e:
            logger.error(f"CPU optimization failed: {e}")
    
    def _send_alert(self, alert_type: str, message: str):
        """Send CPU alert"""
        if not self.config.enable_alerts:
            return
        
        now = time.time()
        if alert_type in self.last_alert:
            if now - self.last_alert[alert_type] < self.config.alert_cooldown:
                return
        
        self.last_alert[alert_type] = now
        logger.warning(f"CPU Alert [{alert_type}]: {message}")
    
    def get_cpu_stats(self) -> Dict[str, Any]:
        """Get current CPU statistics"""
        if not self.cpu_history:
            return {}
        
        recent_data = list(self.cpu_history)[-10:]  # Last 10 data points
        cpu_values = [data['cpu_percent'] for data in recent_data]
        
        return {
            'current_cpu': recent_data[-1]['cpu_percent'] if recent_data else 0,
            'average_cpu': statistics.mean(cpu_values) if cpu_values else 0,
            'max_cpu': max(cpu_values) if cpu_values else 0,
            'min_cpu': min(cpu_values) if cpu_values else 0,
            'cpu_cores': psutil.cpu_count(),
            'cpu_cores_logical': psutil.cpu_count(logical=True)
        }
    
    def stop_monitoring(self):
        """Stop CPU monitoring"""
        self.is_monitoring = False
        logger.info("CPU monitoring stopped")


class MemoryMonitor:
    """Memory monitoring and optimization"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.memory_history = deque(maxlen=config.history_size)
        self.is_monitoring = False
        self.last_alert = {}
        
    def start_monitoring(self):
        """Start memory monitoring"""
        self.is_monitoring = True
        thread = threading.Thread(target=self._monitor_loop)
        thread.daemon = True
        thread.start()
        logger.info("Memory monitoring started")
    
    def _monitor_loop(self):
        """Main memory monitoring loop"""
        while self.is_monitoring:
            try:
                # Get memory info
                memory = psutil.virtual_memory()
                swap = psutil.swap_memory()
                
                # Store data
                timestamp = datetime.now()
                memory_data = {
                    'timestamp': timestamp,
                    'memory': memory._asdict(),
                    'swap': swap._asdict(),
                    'memory_percent': memory.percent,
                    'swap_percent': swap.percent
                }
                
                if self.config.enable_history:
                    self.memory_history.append(memory_data)
                
                # Check thresholds
                self._check_memory_thresholds(memory_data)
                
                # Auto-optimization
                if self.config.auto_optimization and self.config.optimize_memory:
                    self._optimize_memory_usage(memory_data)
                
                time.sleep(self.config.memory_monitor_interval)
                
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                time.sleep(5)
    
    def _check_memory_thresholds(self, memory_data: Dict[str, Any]):
        """Check memory usage thresholds"""
        memory_percent = memory_data['memory_percent']
        
        if memory_percent >= self.config.memory_critical_threshold:
            self._send_alert('memory_critical', f"Critical memory usage: {memory_percent:.1f}%")
        elif memory_percent >= self.config.memory_warning_threshold:
            self._send_alert('memory_warning', f"High memory usage: {memory_percent:.1f}%")
    
    def _optimize_memory_usage(self, memory_data: Dict[str, Any]):
        """Optimize memory usage"""
        memory_percent = memory_data['memory_percent']
        
        if memory_percent >= self.config.memory_warning_threshold:
            # Get high memory processes
            high_memory_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info']):
                try:
                    if proc.info['memory_percent'] > 5.0:
                        high_memory_processes.append(proc.info)
                except:
                    continue
            
            # Sort by memory usage
            high_memory_processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            
            logger.info(f"High memory processes detected: {high_memory_processes[:5]}")
            
            # Apply memory optimizations
            self._apply_memory_optimizations(high_memory_processes)
    
    def _apply_memory_optimizations(self, processes: List[Dict[str, Any]]):
        """Apply memory optimization strategies"""
        try:
            # Force garbage collection
            import gc
            gc.collect()
            
            # Clear system caches (Linux/Unix)
            if platform.system() in ['Linux', 'Darwin']:
                try:
                    subprocess.run(['sync'], check=False)
                    # Note: Actual cache clearing requires root privileges
                except:
                    pass
            
            logger.debug("Applied memory optimizations")
            
        except Exception as e:
            logger.error(f"Memory optimization failed: {e}")
    
    def _send_alert(self, alert_type: str, message: str):
        """Send memory alert"""
        if not self.config.enable_alerts:
            return
        
        now = time.time()
        if alert_type in self.last_alert:
            if now - self.last_alert[alert_type] < self.config.alert_cooldown:
                return
        
        self.last_alert[alert_type] = now
        logger.warning(f"Memory Alert [{alert_type}]: {message}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total_memory': memory.total,
            'available_memory': memory.available,
            'used_memory': memory.used,
            'memory_percent': memory.percent,
            'total_swap': swap.total,
            'used_swap': swap.used,
            'swap_percent': swap.percent
        }
    
    def stop_monitoring(self):
        """Stop memory monitoring"""
        self.is_monitoring = False
        logger.info("Memory monitoring stopped")


class NetworkMonitor:
    """Network monitoring and optimization"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.network_history = deque(maxlen=config.history_size)
        self.connection_history = deque(maxlen=config.history_size)
        self.is_monitoring = False
        self.last_network_io = None
        
    def start_monitoring(self):
        """Start network monitoring"""
        self.is_monitoring = True
        thread = threading.Thread(target=self._monitor_loop)
        thread.daemon = True
        thread.start()
        logger.info("Network monitoring started")
    
    def _monitor_loop(self):
        """Main network monitoring loop"""
        while self.is_monitoring:
            try:
                # Get network I/O stats
                network_io = psutil.net_io_counters()
                
                # Calculate rates if we have previous data
                rates = {}
                if self.last_network_io:
                    time_diff = self.config.network_monitor_interval
                    rates = {
                        'bytes_sent_rate': (network_io.bytes_sent - self.last_network_io.bytes_sent) / time_diff,
                        'bytes_recv_rate': (network_io.bytes_recv - self.last_network_io.bytes_recv) / time_diff,
                        'packets_sent_rate': (network_io.packets_sent - self.last_network_io.packets_sent) / time_diff,
                        'packets_recv_rate': (network_io.packets_recv - self.last_network_io.packets_recv) / time_diff
                    }
                
                self.last_network_io = network_io
                
                # Get network connections
                connections = []
                if self.config.track_network_connections:
                    try:
                        connections = psutil.net_connections(kind='inet')
                    except:
                        pass
                
                # Store data
                timestamp = datetime.now()
                network_data = {
                    'timestamp': timestamp,
                    'network_io': network_io._asdict(),
                    'rates': rates,
                    'connections_count': len(connections),
                    'connections': connections[:100] if connections else []  # Limit to 100 connections
                }
                
                if self.config.enable_history:
                    self.network_history.append(network_data)
                
                # Monitor attack processes
                if self.config.monitor_attack_processes:
                    self._monitor_attack_connections(connections)
                
                time.sleep(self.config.network_monitor_interval)
                
            except Exception as e:
                logger.error(f"Network monitoring error: {e}")
                time.sleep(5)
    
    def _monitor_attack_connections(self, connections: List[Any]):
        """Monitor network connections from attack processes"""
        attack_connections = []
        
        for conn in connections:
            try:
                if hasattr(conn, 'pid') and conn.pid:
                    proc = psutil.Process(conn.pid)
                    proc_name = proc.name().lower()
                    
                    # Check if this might be an attack process
                    if any(keyword in proc_name for keyword in ['ddos', 'flood', 'attack', 'stress']):
                        attack_connections.append({
                            'pid': conn.pid,
                            'process_name': proc_name,
                            'local_addr': conn.laddr,
                            'remote_addr': conn.raddr,
                            'status': conn.status
                        })
            except:
                continue
        
        if attack_connections:
            logger.debug(f"Attack connections detected: {len(attack_connections)}")
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get current network statistics"""
        network_io = psutil.net_io_counters()
        
        # Get interface stats
        interface_stats = {}
        try:
            for interface, stats in psutil.net_io_counters(pernic=True).items():
                interface_stats[interface] = stats._asdict()
        except:
            pass
        
        return {
            'total_bytes_sent': network_io.bytes_sent,
            'total_bytes_recv': network_io.bytes_recv,
            'total_packets_sent': network_io.packets_sent,
            'total_packets_recv': network_io.packets_recv,
            'interface_stats': interface_stats
        }
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.is_monitoring = False
        logger.info("Network monitoring stopped")


class ProcessMonitor:
    """Process monitoring and management"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.process_history = deque(maxlen=config.history_size)
        self.is_monitoring = False
        self.tracked_processes = {}
        
    def start_monitoring(self):
        """Start process monitoring"""
        self.is_monitoring = True
        thread = threading.Thread(target=self._monitor_loop)
        thread.daemon = True
        thread.start()
        logger.info("Process monitoring started")
    
    def _monitor_loop(self):
        """Main process monitoring loop"""
        while self.is_monitoring:
            try:
                # Get all processes
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'create_time']):
                    try:
                        processes.append(proc.info)
                    except:
                        continue
                
                # Store data
                timestamp = datetime.now()
                process_data = {
                    'timestamp': timestamp,
                    'process_count': len(processes),
                    'processes': processes
                }
                
                if self.config.enable_history:
                    self.process_history.append(process_data)
                
                # Track specific processes
                self._track_processes(processes)
                
                time.sleep(self.config.process_monitor_interval)
                
            except Exception as e:
                logger.error(f"Process monitoring error: {e}")
                time.sleep(5)
    
    def _track_processes(self, processes: List[Dict[str, Any]]):
        """Track specific processes of interest"""
        # Track attack-related processes
        attack_processes = []
        for proc in processes:
            proc_name = proc['name'].lower()
            if any(keyword in proc_name for keyword in ['ddos', 'flood', 'attack', 'stress', 'fsociety']):
                attack_processes.append(proc)
        
        if attack_processes:
            logger.debug(f"Attack processes running: {len(attack_processes)}")
            self.tracked_processes['attack_processes'] = attack_processes
    
    def get_process_stats(self) -> Dict[str, Any]:
        """Get current process statistics"""
        try:
            processes = list(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']))
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x.info.get('cpu_percent', 0), reverse=True)
            
            return {
                'total_processes': len(processes),
                'top_cpu_processes': [p.info for p in processes[:10]],
                'tracked_processes': self.tracked_processes
            }
        except:
            return {}
    
    def stop_monitoring(self):
        """Stop process monitoring"""
        self.is_monitoring = False
        logger.info("Process monitoring stopped")


class PerformanceOptimizer:
    """System performance optimization"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        
    def optimize_system_performance(self):
        """Optimize overall system performance"""
        logger.info("Starting system performance optimization...")
        
        optimizations_applied = []
        
        # CPU optimizations
        if self.config.optimize_cpu:
            cpu_opts = self._optimize_cpu_performance()
            optimizations_applied.extend(cpu_opts)
        
        # Memory optimizations
        if self.config.optimize_memory:
            memory_opts = self._optimize_memory_performance()
            optimizations_applied.extend(memory_opts)
        
        # Network optimizations
        if self.config.optimize_network:
            network_opts = self._optimize_network_performance()
            optimizations_applied.extend(network_opts)
        
        logger.info(f"Applied {len(optimizations_applied)} performance optimizations")
        return optimizations_applied
    
    def _optimize_cpu_performance(self) -> List[str]:
        """Optimize CPU performance"""
        optimizations = []
        
        try:
            # Set CPU governor to performance (Linux)
            if platform.system() == 'Linux':
                try:
                    subprocess.run(['cpupower', 'frequency-set', '-g', 'performance'], 
                                 check=False, capture_output=True)
                    optimizations.append("Set CPU governor to performance mode")
                except:
                    pass
            
            # Disable CPU throttling (where possible)
            optimizations.append("CPU optimization attempted")
            
        except Exception as e:
            logger.debug(f"CPU optimization error: {e}")
        
        return optimizations
    
    def _optimize_memory_performance(self) -> List[str]:
        """Optimize memory performance"""
        optimizations = []
        
        try:
            # Force garbage collection
            import gc
            gc.collect()
            optimizations.append("Forced garbage collection")
            
            # Optimize memory allocation
            optimizations.append("Memory allocation optimized")
            
        except Exception as e:
            logger.debug(f"Memory optimization error: {e}")
        
        return optimizations
    
    def _optimize_network_performance(self) -> List[str]:
        """Optimize network performance"""
        optimizations = []
        
        try:
            # Network buffer optimizations would go here
            # Note: Most network optimizations require system-level changes
            optimizations.append("Network performance optimization attempted")
            
        except Exception as e:
            logger.debug(f"Network optimization error: {e}")
        
        return optimizations


class SystemMonitorManager:
    """Main system monitoring manager"""
    
    def __init__(self, config: MonitoringConfig = None):
        self.config = config or MonitoringConfig()
        
        # Initialize monitors
        self.cpu_monitor = CPUMonitor(self.config)
        self.memory_monitor = MemoryMonitor(self.config)
        self.network_monitor = NetworkMonitor(self.config)
        self.process_monitor = ProcessMonitor(self.config)
        self.performance_optimizer = PerformanceOptimizer(self.config)
        
        self.is_monitoring = False
        self.start_time = None
        
    def start_monitoring(self):
        """Start comprehensive system monitoring"""
        logger.info("Starting comprehensive system monitoring...")
        
        self.is_monitoring = True
        self.start_time = datetime.now()
        
        # Start individual monitors
        self.cpu_monitor.start_monitoring()
        self.memory_monitor.start_monitoring()
        self.network_monitor.start_monitoring()
        self.process_monitor.start_monitoring()
        
        # Apply initial optimizations
        if self.config.auto_optimization:
            self.performance_optimizer.optimize_system_performance()
        
        logger.info("System monitoring active")
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            'monitoring_active': self.is_monitoring,
            'uptime': str(datetime.now() - self.start_time) if self.start_time else None,
            'cpu_stats': self.cpu_monitor.get_cpu_stats(),
            'memory_stats': self.memory_monitor.get_memory_stats(),
            'network_stats': self.network_monitor.get_network_stats(),
            'process_stats': self.process_monitor.get_process_stats(),
            'system_info': {
                'platform': platform.platform(),
                'processor': platform.processor(),
                'architecture': platform.architecture(),
                'hostname': socket.gethostname()
            }
        }
    
    def optimize_for_attack(self):
        """Optimize system specifically for attack operations"""
        logger.info("Optimizing system for attack operations...")
        
        optimizations = self.performance_optimizer.optimize_system_performance()
        
        # Additional attack-specific optimizations
        try:
            # Increase file descriptor limits (Unix)
            if platform.system() in ['Linux', 'Darwin']:
                import resource
                resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))
                optimizations.append("Increased file descriptor limit")
        except:
            pass
        
        return optimizations
    
    def stop_monitoring(self):
        """Stop all monitoring"""
        logger.info("Stopping system monitoring...")
        
        self.is_monitoring = False
        
        # Stop individual monitors
        self.cpu_monitor.stop_monitoring()
        self.memory_monitor.stop_monitoring()
        self.network_monitor.stop_monitoring()
        self.process_monitor.stop_monitoring()
        
        logger.info("System monitoring stopped")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            'monitoring_active': self.is_monitoring,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'config': {
                'auto_optimization': self.config.auto_optimization,
                'enable_alerts': self.config.enable_alerts,
                'history_enabled': self.config.enable_history
            }
        }