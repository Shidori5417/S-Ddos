#!/usr/bin/env python3
"""
FsocietyDDoS Performance Benchmark System
Advanced performance testing and monitoring for DDoS attacks
"""

import asyncio
import time
import threading
import psutil
import statistics
import json
import csv
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
import numpy as np
import requests
import aiohttp
import gc
import sys
import traceback

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fsociety_ddos import HighPerformanceAttackThreadCLI
from async_attack_methods import HighPerformanceAsyncAttacker
from core.memory_manager import MemoryManager, BufferManager

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: float
    requests_per_second: float
    response_time_avg: float
    response_time_min: float
    response_time_max: float
    response_time_p95: float
    response_time_p99: float
    success_rate: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    network_sent: int
    network_received: int
    active_connections: int
    failed_connections: int
    bytes_sent: int
    bytes_received: int
    thread_count: int
    async_tasks: int

@dataclass
class BenchmarkConfig:
    """Benchmark configuration"""
    target_url: str
    duration: int = 60  # seconds
    max_requests: int = 100000
    concurrency_levels: List[int] = None
    test_types: List[str] = None
    warmup_time: int = 10
    cooldown_time: int = 5
    output_dir: str = "benchmark_results"
    enable_async: bool = True
    enable_threading: bool = True
    memory_limit: int = 8 * 1024 * 1024 * 1024  # 8GB
    
    def __post_init__(self):
        if self.concurrency_levels is None:
            self.concurrency_levels = [10, 50, 100, 200, 500, 1000]
        if self.test_types is None:
            self.test_types = ["http_flood", "async_flood", "mixed_load"]

class PerformanceBenchmark:
    """Advanced performance benchmark system"""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.metrics_history: List[PerformanceMetrics] = []
        self.test_results: Dict[str, Any] = {}
        self.memory_manager = MemoryManager()
        self.buffer_manager = BufferManager()
        self.start_time = None
        self.end_time = None
        self.baseline_metrics = None
        
        # Create output directory
        os.makedirs(config.output_dir, exist_ok=True)
        
        # Initialize monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        
    def run_full_benchmark(self) -> Dict[str, Any]:
        """Run complete benchmark suite"""
        print(f"[BENCHMARK] Starting comprehensive performance benchmark")
        print(f"[BENCHMARK] Target: {self.config.target_url}")
        print(f"[BENCHMARK] Duration: {self.config.duration}s per test")
        print(f"[BENCHMARK] Concurrency levels: {self.config.concurrency_levels}")
        
        self.start_time = time.time()
        
        try:
            # Collect baseline metrics
            self._collect_baseline_metrics()
            
            # Run different test types
            for test_type in self.config.test_types:
                print(f"\n[BENCHMARK] Running {test_type} tests...")
                self.test_results[test_type] = self._run_test_suite(test_type)
                
                # Cooldown between test types
                if test_type != self.config.test_types[-1]:
                    print(f"[BENCHMARK] Cooldown for {self.config.cooldown_time}s...")
                    time.sleep(self.config.cooldown_time)
            
            # Generate comprehensive report
            self._generate_comprehensive_report()
            
            # Create visualizations
            self._create_performance_charts()
            
            self.end_time = time.time()
            total_time = self.end_time - self.start_time
            
            print(f"\n[BENCHMARK] Benchmark completed in {total_time:.2f}s")
            print(f"[BENCHMARK] Results saved to: {self.config.output_dir}")
            
            return self.test_results
            
        except Exception as e:
            print(f"[ERROR] Benchmark failed: {e}")
            traceback.print_exc()
            return {}
    
    def _collect_baseline_metrics(self):
        """Collect baseline system metrics"""
        print("[BENCHMARK] Collecting baseline metrics...")
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        network = psutil.net_io_counters()
        
        self.baseline_metrics = {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'memory_available': memory.available,
            'network_sent': network.bytes_sent,
            'network_received': network.bytes_recv,
            'timestamp': time.time()
        }
        
        print(f"[BASELINE] CPU: {cpu_percent:.1f}%, Memory: {memory.percent:.1f}%")
    
    def _run_test_suite(self, test_type: str) -> Dict[str, Any]:
        """Run test suite for specific test type"""
        suite_results = {}
        
        for concurrency in self.config.concurrency_levels:
            print(f"[TEST] {test_type} with {concurrency} concurrent connections...")
            
            # Start monitoring
            self._start_monitoring()
            
            try:
                # Warmup
                print(f"[WARMUP] {self.config.warmup_time}s warmup...")
                time.sleep(self.config.warmup_time)
                
                # Run actual test
                test_result = self._run_single_test(test_type, concurrency)
                suite_results[f"concurrency_{concurrency}"] = test_result
                
                # Stop monitoring
                self._stop_monitoring()
                
                # Process metrics
                test_metrics = self._process_metrics()
                suite_results[f"concurrency_{concurrency}"]["metrics"] = test_metrics
                
                print(f"[RESULT] RPS: {test_metrics['avg_rps']:.2f}, "
                      f"Response Time: {test_metrics['avg_response_time']:.2f}ms, "
                      f"Success Rate: {test_metrics['success_rate']:.2f}%")
                
            except Exception as e:
                print(f"[ERROR] Test failed for {test_type} with {concurrency} concurrency: {e}")
                suite_results[f"concurrency_{concurrency}"] = {"error": str(e)}
            
            # Cleanup between tests
            gc.collect()
            time.sleep(2)
        
        return suite_results
    
    def _run_single_test(self, test_type: str, concurrency: int) -> Dict[str, Any]:
        """Run single performance test"""
        if test_type == "http_flood":
            return self._run_http_flood_test(concurrency)
        elif test_type == "async_flood":
            return self._run_async_flood_test(concurrency)
        elif test_type == "mixed_load":
            return self._run_mixed_load_test(concurrency)
        else:
            raise ValueError(f"Unknown test type: {test_type}")
    
    def _run_http_flood_test(self, concurrency: int) -> Dict[str, Any]:
        """Run HTTP flood test using threading"""
        results = {
            'test_type': 'http_flood',
            'concurrency': concurrency,
            'start_time': time.time(),
            'requests_sent': 0,
            'requests_successful': 0,
            'requests_failed': 0,
            'response_times': [],
            'errors': []
        }
        
        # Create attack instance
        attacker = HighPerformanceAttackThreadCLI(
            target=self.config.target_url,
            num_requests=self.config.max_requests,
            method="GET",
            concurrency=concurrency
        )
        
        # Run attack for specified duration
        attack_thread = threading.Thread(target=attacker.run)
        attack_thread.start()
        
        time.sleep(self.config.duration)
        
        # Stop attack
        attacker.stop()
        attack_thread.join(timeout=10)
        
        results['end_time'] = time.time()
        results['duration'] = results['end_time'] - results['start_time']
        
        # Get statistics from attacker
        if hasattr(attacker, 'stats_manager'):
            stats = attacker.stats_manager.get_summary()
            results.update({
                'requests_sent': stats.get('total_requests', 0),
                'requests_successful': stats.get('successful_requests', 0),
                'requests_failed': stats.get('failed_requests', 0),
                'avg_response_time': stats.get('avg_response_time', 0),
                'min_response_time': stats.get('min_response_time', 0),
                'max_response_time': stats.get('max_response_time', 0)
            })
        
        return results
    
    def _run_async_flood_test(self, concurrency: int) -> Dict[str, Any]:
        """Run async flood test"""
        results = {
            'test_type': 'async_flood',
            'concurrency': concurrency,
            'start_time': time.time(),
            'requests_sent': 0,
            'requests_successful': 0,
            'requests_failed': 0,
            'response_times': [],
            'errors': []
        }
        
        async def run_async_test():
            attacker = HighPerformanceAsyncAttacker(
                target_url=self.config.target_url,
                concurrency=concurrency,
                duration=self.config.duration
            )
            
            await attacker.initialize()
            
            try:
                attack_result = await attacker.run_attack()
                results.update({
                    'requests_sent': attack_result.total_requests,
                    'requests_successful': attack_result.successful_requests,
                    'requests_failed': attack_result.failed_requests,
                    'avg_response_time': attack_result.avg_response_time,
                    'min_response_time': attack_result.min_response_time,
                    'max_response_time': attack_result.max_response_time,
                    'response_times': attack_result.response_times
                })
            finally:
                await attacker.cleanup()
        
        # Run async test
        asyncio.run(run_async_test())
        
        results['end_time'] = time.time()
        results['duration'] = results['end_time'] - results['start_time']
        
        return results
    
    def _run_mixed_load_test(self, concurrency: int) -> Dict[str, Any]:
        """Run mixed load test (threading + async)"""
        results = {
            'test_type': 'mixed_load',
            'concurrency': concurrency,
            'start_time': time.time(),
            'threading_results': {},
            'async_results': {}
        }
        
        # Split concurrency between threading and async
        thread_concurrency = concurrency // 2
        async_concurrency = concurrency - thread_concurrency
        
        # Run both tests simultaneously
        thread_future = None
        async_future = None
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Start threading test
            thread_future = executor.submit(
                self._run_http_flood_test, thread_concurrency
            )
            
            # Start async test
            async_future = executor.submit(
                self._run_async_flood_test, async_concurrency
            )
            
            # Wait for completion
            results['threading_results'] = thread_future.result()
            results['async_results'] = async_future.result()
        
        results['end_time'] = time.time()
        results['duration'] = results['end_time'] - results['start_time']
        
        # Combine results
        total_requests = (results['threading_results'].get('requests_sent', 0) + 
                         results['async_results'].get('requests_sent', 0))
        total_successful = (results['threading_results'].get('requests_successful', 0) + 
                           results['async_results'].get('requests_successful', 0))
        
        results['combined_rps'] = total_requests / results['duration'] if results['duration'] > 0 else 0
        results['combined_success_rate'] = (total_successful / total_requests * 100) if total_requests > 0 else 0
        
        return results
    
    def _start_monitoring(self):
        """Start system monitoring"""
        self.monitoring_active = True
        self.metrics_history.clear()
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.start()
    
    def _stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitoring_loop(self):
        """Monitoring loop for collecting metrics"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                network = psutil.net_io_counters()
                
                # Create metrics object
                metrics = PerformanceMetrics(
                    timestamp=time.time(),
                    requests_per_second=0,  # Will be calculated later
                    response_time_avg=0,
                    response_time_min=0,
                    response_time_max=0,
                    response_time_p95=0,
                    response_time_p99=0,
                    success_rate=0,
                    error_rate=0,
                    cpu_usage=cpu_percent,
                    memory_usage=memory.percent,
                    network_sent=network.bytes_sent,
                    network_received=network.bytes_recv,
                    active_connections=0,
                    failed_connections=0,
                    bytes_sent=0,
                    bytes_received=0,
                    thread_count=threading.active_count(),
                    async_tasks=0
                )
                
                self.metrics_history.append(metrics)
                
            except Exception as e:
                print(f"[WARNING] Monitoring error: {e}")
            
            time.sleep(0.5)  # Collect metrics every 500ms
    
    def _process_metrics(self) -> Dict[str, Any]:
        """Process collected metrics"""
        if not self.metrics_history:
            return {}
        
        # Calculate averages and statistics
        cpu_values = [m.cpu_usage for m in self.metrics_history]
        memory_values = [m.memory_usage for m in self.metrics_history]
        
        return {
            'avg_cpu_usage': statistics.mean(cpu_values),
            'max_cpu_usage': max(cpu_values),
            'avg_memory_usage': statistics.mean(memory_values),
            'max_memory_usage': max(memory_values),
            'avg_rps': 0,  # Will be calculated from test results
            'avg_response_time': 0,
            'success_rate': 0,
            'total_metrics_collected': len(self.metrics_history)
        }
    
    def _generate_comprehensive_report(self):
        """Generate comprehensive benchmark report"""
        report_file = os.path.join(self.config.output_dir, f"benchmark_report_{int(time.time())}.json")
        
        report = {
            'benchmark_config': asdict(self.config),
            'baseline_metrics': self.baseline_metrics,
            'test_results': self.test_results,
            'summary': self._generate_summary(),
            'recommendations': self._generate_recommendations(),
            'timestamp': datetime.now().isoformat(),
            'total_duration': self.end_time - self.start_time if self.end_time and self.start_time else 0
        }
        
        # Save JSON report
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate CSV report
        self._generate_csv_report()
        
        # Generate text summary
        self._generate_text_summary()
        
        print(f"[REPORT] Comprehensive report saved to: {report_file}")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate performance summary"""
        summary = {
            'best_performance': {},
            'worst_performance': {},
            'optimal_concurrency': {},
            'resource_usage': {}
        }
        
        # Analyze results for each test type
        for test_type, results in self.test_results.items():
            best_rps = 0
            best_config = None
            
            for config_name, result in results.items():
                if isinstance(result, dict) and 'error' not in result:
                    # Calculate RPS
                    duration = result.get('duration', 1)
                    requests = result.get('requests_sent', 0)
                    rps = requests / duration if duration > 0 else 0
                    
                    if rps > best_rps:
                        best_rps = rps
                        best_config = config_name
            
            if best_config:
                summary['best_performance'][test_type] = {
                    'configuration': best_config,
                    'rps': best_rps,
                    'result': results[best_config]
                }
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Analyze CPU usage
        if self.baseline_metrics and self.baseline_metrics['cpu_usage'] > 80:
            recommendations.append("High baseline CPU usage detected. Consider reducing background processes.")
        
        # Analyze memory usage
        if self.baseline_metrics and self.baseline_metrics['memory_usage'] > 80:
            recommendations.append("High memory usage detected. Consider increasing available RAM or reducing memory-intensive applications.")
        
        # Analyze test results
        for test_type, results in self.test_results.items():
            success_rates = []
            for config_name, result in results.items():
                if isinstance(result, dict) and 'error' not in result:
                    total_requests = result.get('requests_sent', 0)
                    successful_requests = result.get('requests_successful', 0)
                    if total_requests > 0:
                        success_rate = (successful_requests / total_requests) * 100
                        success_rates.append(success_rate)
            
            if success_rates and statistics.mean(success_rates) < 90:
                recommendations.append(f"Low success rate for {test_type}. Consider reducing concurrency or improving target server capacity.")
        
        return recommendations
    
    def _generate_csv_report(self):
        """Generate CSV report for easy analysis"""
        csv_file = os.path.join(self.config.output_dir, f"benchmark_data_{int(time.time())}.csv")
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Test Type', 'Concurrency', 'Duration', 'Requests Sent', 
                'Requests Successful', 'Requests Failed', 'RPS', 'Success Rate',
                'Avg Response Time', 'Min Response Time', 'Max Response Time'
            ])
            
            # Write data
            for test_type, results in self.test_results.items():
                for config_name, result in results.items():
                    if isinstance(result, dict) and 'error' not in result:
                        concurrency = result.get('concurrency', 0)
                        duration = result.get('duration', 0)
                        requests_sent = result.get('requests_sent', 0)
                        requests_successful = result.get('requests_successful', 0)
                        requests_failed = result.get('requests_failed', 0)
                        rps = requests_sent / duration if duration > 0 else 0
                        success_rate = (requests_successful / requests_sent * 100) if requests_sent > 0 else 0
                        
                        writer.writerow([
                            test_type, concurrency, duration, requests_sent,
                            requests_successful, requests_failed, rps, success_rate,
                            result.get('avg_response_time', 0),
                            result.get('min_response_time', 0),
                            result.get('max_response_time', 0)
                        ])
    
    def _generate_text_summary(self):
        """Generate human-readable text summary"""
        summary_file = os.path.join(self.config.output_dir, f"benchmark_summary_{int(time.time())}.txt")
        
        with open(summary_file, 'w') as f:
            f.write("FsocietyDDoS Performance Benchmark Report\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Target URL: {self.config.target_url}\n")
            f.write(f"Test Duration: {self.config.duration} seconds per test\n")
            f.write(f"Concurrency Levels: {self.config.concurrency_levels}\n")
            f.write(f"Test Types: {self.config.test_types}\n\n")
            
            # Baseline metrics
            if self.baseline_metrics:
                f.write("Baseline System Metrics:\n")
                f.write(f"  CPU Usage: {self.baseline_metrics['cpu_usage']:.1f}%\n")
                f.write(f"  Memory Usage: {self.baseline_metrics['memory_usage']:.1f}%\n\n")
            
            # Test results summary
            f.write("Test Results Summary:\n")
            for test_type, results in self.test_results.items():
                f.write(f"\n{test_type.upper()}:\n")
                for config_name, result in results.items():
                    if isinstance(result, dict) and 'error' not in result:
                        concurrency = result.get('concurrency', 0)
                        duration = result.get('duration', 0)
                        requests_sent = result.get('requests_sent', 0)
                        rps = requests_sent / duration if duration > 0 else 0
                        success_rate = (result.get('requests_successful', 0) / requests_sent * 100) if requests_sent > 0 else 0
                        
                        f.write(f"  Concurrency {concurrency}: {rps:.2f} RPS, {success_rate:.1f}% success\n")
            
            # Recommendations
            recommendations = self._generate_recommendations()
            if recommendations:
                f.write("\nRecommendations:\n")
                for i, rec in enumerate(recommendations, 1):
                    f.write(f"  {i}. {rec}\n")
    
    def _create_performance_charts(self):
        """Create performance visualization charts"""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            # Create charts for each test type
            for test_type, results in self.test_results.items():
                self._create_test_type_chart(test_type, results)
            
            # Create comparison chart
            self._create_comparison_chart()
            
        except ImportError:
            print("[WARNING] matplotlib not available. Skipping chart generation.")
        except Exception as e:
            print(f"[WARNING] Chart generation failed: {e}")
    
    def _create_test_type_chart(self, test_type: str, results: Dict[str, Any]):
        """Create chart for specific test type"""
        concurrency_levels = []
        rps_values = []
        success_rates = []
        
        for config_name, result in results.items():
            if isinstance(result, dict) and 'error' not in result:
                concurrency = result.get('concurrency', 0)
                duration = result.get('duration', 0)
                requests_sent = result.get('requests_sent', 0)
                requests_successful = result.get('requests_successful', 0)
                
                rps = requests_sent / duration if duration > 0 else 0
                success_rate = (requests_successful / requests_sent * 100) if requests_sent > 0 else 0
                
                concurrency_levels.append(concurrency)
                rps_values.append(rps)
                success_rates.append(success_rate)
        
        if not concurrency_levels:
            return
        
        # Create subplot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # RPS chart
        ax1.plot(concurrency_levels, rps_values, 'b-o', linewidth=2, markersize=6)
        ax1.set_xlabel('Concurrency Level')
        ax1.set_ylabel('Requests Per Second')
        ax1.set_title(f'{test_type.upper()} - Requests Per Second vs Concurrency')
        ax1.grid(True, alpha=0.3)
        
        # Success rate chart
        ax2.plot(concurrency_levels, success_rates, 'g-s', linewidth=2, markersize=6)
        ax2.set_xlabel('Concurrency Level')
        ax2.set_ylabel('Success Rate (%)')
        ax2.set_title(f'{test_type.upper()} - Success Rate vs Concurrency')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 105)
        
        plt.tight_layout()
        
        # Save chart
        chart_file = os.path.join(self.config.output_dir, f"{test_type}_performance_chart.png")
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"[CHART] {test_type} performance chart saved to: {chart_file}")
    
    def _create_comparison_chart(self):
        """Create comparison chart for all test types"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        
        for i, (test_type, results) in enumerate(self.test_results.items()):
            concurrency_levels = []
            rps_values = []
            
            for config_name, result in results.items():
                if isinstance(result, dict) and 'error' not in result:
                    concurrency = result.get('concurrency', 0)
                    duration = result.get('duration', 0)
                    requests_sent = result.get('requests_sent', 0)
                    
                    rps = requests_sent / duration if duration > 0 else 0
                    
                    concurrency_levels.append(concurrency)
                    rps_values.append(rps)
            
            if concurrency_levels:
                color = colors[i % len(colors)]
                ax.plot(concurrency_levels, rps_values, f'{color}-o', 
                       linewidth=2, markersize=6, label=test_type.upper())
        
        ax.set_xlabel('Concurrency Level')
        ax.set_ylabel('Requests Per Second')
        ax.set_title('Performance Comparison - All Test Types')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Save comparison chart
        chart_file = os.path.join(self.config.output_dir, "performance_comparison.png")
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"[CHART] Performance comparison chart saved to: {chart_file}")

def run_benchmark_suite(target_url: str, **kwargs) -> Dict[str, Any]:
    """Run complete benchmark suite"""
    config = BenchmarkConfig(target_url=target_url, **kwargs)
    benchmark = PerformanceBenchmark(config)
    return benchmark.run_full_benchmark()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="FsocietyDDoS Performance Benchmark")
    parser.add_argument("target", help="Target URL for benchmark")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    parser.add_argument("--max-requests", type=int, default=100000, help="Maximum requests per test")
    parser.add_argument("--concurrency", nargs='+', type=int, default=[10, 50, 100, 200, 500, 1000], 
                       help="Concurrency levels to test")
    parser.add_argument("--output-dir", default="benchmark_results", help="Output directory")
    parser.add_argument("--warmup", type=int, default=10, help="Warmup time in seconds")
    parser.add_argument("--cooldown", type=int, default=5, help="Cooldown time in seconds")
    
    args = parser.parse_args()
    
    # Run benchmark
    config = BenchmarkConfig(
        target_url=args.target,
        duration=args.duration,
        max_requests=args.max_requests,
        concurrency_levels=args.concurrency,
        output_dir=args.output_dir,
        warmup_time=args.warmup,
        cooldown_time=args.cooldown
    )
    
    benchmark = PerformanceBenchmark(config)
    results = benchmark.run_full_benchmark()
    
    print("\n[BENCHMARK] Benchmark completed successfully!")
    print(f"[BENCHMARK] Check results in: {args.output_dir}")