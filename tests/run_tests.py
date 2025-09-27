#!/usr/bin/env python3
"""
FsocietyDDoS Test Runner
Comprehensive test execution and reporting system
"""

import os
import sys
import time
import json
import argparse
import subprocess
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import with error handling for optional dependencies
try:
    from performance_benchmark import PerformanceBenchmark, BenchmarkConfig
    PERFORMANCE_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Performance benchmark not available: {e}")
    PERFORMANCE_AVAILABLE = False
    PerformanceBenchmark = None
    BenchmarkConfig = None

try:
    from stress_test import StressTestController, StressTestConfig
    STRESS_TEST_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Stress test not available: {e}")
    STRESS_TEST_AVAILABLE = False
    StressTestController = None
    StressTestConfig = None

@dataclass
class TestSuite:
    """Test suite configuration"""
    name: str
    description: str
    tests: List[str]
    enabled: bool = True
    timeout: int = 300  # 5 minutes default
    parallel: bool = False
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class TestResult:
    """Individual test result"""
    name: str
    status: str  # 'passed', 'failed', 'skipped', 'timeout'
    duration: float
    output: str
    error: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class TestRunner:
    """Comprehensive test runner"""
    
    def __init__(self, output_dir: str = "test_results"):
        self.output_dir = output_dir
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Define test suites
        self.test_suites = {
            'unit': TestSuite(
                name="Unit Tests",
                description="Basic functionality tests",
                tests=[
                    'test_config_validation',
                    'test_memory_manager',
                    'test_buffer_manager',
                    'test_async_engine',
                    'test_attack_methods'
                ],
                timeout=60,
                parallel=True
            ),
            'integration': TestSuite(
                name="Integration Tests",
                description="Component integration tests",
                tests=[
                    'test_async_integration',
                    'test_memory_integration',
                    'test_attack_pipeline',
                    'test_resource_management'
                ],
                timeout=120,
                dependencies=['unit']
            ),
            'performance': TestSuite(
                name="Performance Tests",
                description="Performance and benchmark tests",
                tests=[
                    'test_performance_benchmark',
                    'test_concurrency_scaling',
                    'test_memory_efficiency',
                    'test_network_throughput'
                ],
                timeout=300,
                dependencies=['unit', 'integration']
            ),
            'stress': TestSuite(
                name="Stress Tests",
                description="System stress and limit tests",
                tests=[
                    'test_stress_basic',
                    'test_stress_extended',
                    'test_resource_limits',
                    'test_failure_recovery'
                ],
                timeout=600,
                dependencies=['performance']
            ),
            'security': TestSuite(
                name="Security Tests",
                description="Security and safety tests",
                tests=[
                    'test_input_validation',
                    'test_resource_protection',
                    'test_rate_limiting',
                    'test_safe_shutdown'
                ],
                timeout=180
            )
        }
    
    def run_all_tests(self, target_url: str = "http://httpbin.org/get", 
                     suites: List[str] = None, 
                     parallel: bool = False) -> Dict[str, Any]:
        """Run all or specified test suites"""
        print(f"[TEST RUNNER] Starting comprehensive test execution")
        print(f"[TEST RUNNER] Target URL: {target_url}")
        print(f"[TEST RUNNER] Output Directory: {self.output_dir}")
        
        self.start_time = time.time()
        
        # Determine which suites to run
        if suites is None:
            suites = list(self.test_suites.keys())
        
        # Validate and order suites based on dependencies
        ordered_suites = self._order_suites_by_dependencies(suites)
        
        try:
            # Run each test suite
            for suite_name in ordered_suites:
                if suite_name not in self.test_suites:
                    print(f"[WARNING] Unknown test suite: {suite_name}")
                    continue
                
                suite = self.test_suites[suite_name]
                if not suite.enabled:
                    print(f"[SKIP] Test suite disabled: {suite_name}")
                    continue
                
                print(f"\n[SUITE] Running {suite.name}: {suite.description}")
                self._run_test_suite(suite, target_url, parallel)
            
            # Generate final report
            report = self._generate_final_report()
            
            return report
            
        except Exception as e:
            print(f"[ERROR] Test execution failed: {e}")
            return {"error": str(e)}
        
        finally:
            self.end_time = time.time()
    
    def _order_suites_by_dependencies(self, suites: List[str]) -> List[str]:
        """Order test suites based on dependencies"""
        ordered = []
        remaining = set(suites)
        
        while remaining:
            # Find suites with no unmet dependencies
            ready = []
            for suite_name in remaining:
                suite = self.test_suites[suite_name]
                if all(dep in ordered or dep not in suites for dep in suite.dependencies):
                    ready.append(suite_name)
            
            if not ready:
                # Circular dependency or missing dependency
                print(f"[WARNING] Circular or missing dependencies, adding remaining: {remaining}")
                ordered.extend(remaining)
                break
            
            # Add ready suites
            for suite_name in ready:
                ordered.append(suite_name)
                remaining.remove(suite_name)
        
        return ordered
    
    def _run_test_suite(self, suite: TestSuite, target_url: str, force_parallel: bool = False):
        """Run a specific test suite"""
        suite_start_time = time.time()
        suite_results = []
        
        # Determine execution mode
        run_parallel = suite.parallel or force_parallel
        
        if run_parallel and len(suite.tests) > 1:
            # Run tests in parallel
            threads = []
            results_lock = threading.Lock()
            
            for test_name in suite.tests:
                thread = threading.Thread(
                    target=self._run_single_test_threaded,
                    args=(test_name, target_url, suite.timeout, suite_results, results_lock)
                )
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join()
        else:
            # Run tests sequentially
            for test_name in suite.tests:
                result = self._run_single_test(test_name, target_url, suite.timeout)
                suite_results.append(result)
        
        # Add results to main results
        self.results.extend(suite_results)
        
        # Print suite summary
        suite_duration = time.time() - suite_start_time
        passed = sum(1 for r in suite_results if r.status == 'passed')
        failed = sum(1 for r in suite_results if r.status == 'failed')
        skipped = sum(1 for r in suite_results if r.status == 'skipped')
        
        print(f"[SUITE COMPLETE] {suite.name}: {passed} passed, {failed} failed, {skipped} skipped ({suite_duration:.1f}s)")
    
    def _run_single_test_threaded(self, test_name: str, target_url: str, timeout: int, 
                                 results: List[TestResult], results_lock: threading.Lock):
        """Run single test in thread-safe manner"""
        result = self._run_single_test(test_name, target_url, timeout)
        
        with results_lock:
            results.append(result)
    
    def _run_single_test(self, test_name: str, target_url: str, timeout: int) -> TestResult:
        """Run a single test"""
        print(f"[TEST] Running {test_name}...")
        start_time = time.time()
        
        try:
            # Route to appropriate test method
            if hasattr(self, f'_{test_name}'):
                method = getattr(self, f'_{test_name}')
                output, metrics = method(target_url, timeout)
                
                duration = time.time() - start_time
                result = TestResult(
                    name=test_name,
                    status='passed',
                    duration=duration,
                    output=output,
                    metrics=metrics
                )
                
                print(f"[PASS] {test_name} ({duration:.1f}s)")
                return result
            
            else:
                # Test method not implemented
                duration = time.time() - start_time
                result = TestResult(
                    name=test_name,
                    status='skipped',
                    duration=duration,
                    output=f"Test method _{test_name} not implemented",
                    error="Not implemented"
                )
                
                print(f"[SKIP] {test_name} - Not implemented")
                return result
        
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(
                name=test_name,
                status='failed',
                duration=duration,
                output="",
                error=str(e)
            )
            
            print(f"[FAIL] {test_name} - {e}")
            return result
    
    # Test implementations
    def _test_config_validation(self, target_url: str, timeout: int) -> tuple:
        """Test configuration validation"""
        output = []
        metrics = {}
        
        # Test valid configuration
        try:
            from core.config import CONFIG
            output.append("+ Configuration loaded successfully")
            metrics['config_keys'] = len(CONFIG)
        except Exception as e:
            raise Exception(f"Failed to load configuration: {e}")
        
        # Test target URL validation
        import urllib.parse
        parsed = urllib.parse.urlparse(target_url)
        if not parsed.scheme or not parsed.netloc:
            raise Exception(f"Invalid target URL: {target_url}")
        
        output.append("+ Target URL validation passed")
        
        return "\n".join(output), metrics
    
    def _test_memory_manager(self, target_url: str, timeout: int) -> tuple:
        """Test memory manager functionality"""
        output = []
        metrics = {}
        
        try:
            from core.memory_manager import MemoryManager
            
            # Test memory manager initialization
            manager = MemoryManager()
            output.append("+ Memory manager initialized")
            
            # Test memory optimization
            initial_memory = manager.get_memory_usage()
            manager.optimize_memory()
            optimized_memory = manager.get_memory_usage()
            
            # Convert dict to string representation for output
            initial_str = str(initial_memory.get('total_allocated', 0))
            optimized_str = str(optimized_memory.get('total_allocated', 0))
            
            output.append(f"+ Memory optimization: {initial_str} -> {optimized_str}")
            metrics['memory_optimization'] = initial_memory
            
            # Test memory monitoring
            stats = manager.get_stats()
            output.append(f"+ Memory stats collected: {len(stats)} metrics")
            metrics['memory_stats'] = stats
            
        except Exception as e:
            raise Exception(f"Memory manager test failed: {e}")
        
        return "\n".join(output), metrics
    
    def _test_buffer_manager(self, target_url: str, timeout: int) -> tuple:
        """Test buffer manager functionality"""
        output = []
        metrics = {}
        
        try:
            from core.memory_manager import BufferManager
            
            # Test buffer manager initialization
            manager = BufferManager()
            output.append("+ Buffer manager initialized")
            
            # Test buffer allocation
            buffer_size = 1024 * 1024  # 1MB
            buffer = manager.allocate_buffer(buffer_size)
            output.append(f"+ Buffer allocated: {len(buffer)} bytes")
            metrics['buffer_size'] = len(buffer)
            
            # Test buffer pool
            pool_size = manager.get_pool_size()
            output.append(f"+ Buffer pool size: {pool_size}")
            metrics['pool_size'] = pool_size
            
        except Exception as e:
            raise Exception(f"Buffer manager test failed: {e}")
        
        return "\n".join(output), metrics
    
    def _test_async_engine(self, target_url: str, timeout: int) -> tuple:
        """Test async engine functionality"""
        output = []
        metrics = {}
        
        try:
            from core.async_engine import initialize_async_engine, cleanup_async_engine
            
            # Test async engine initialization
            engine = initialize_async_engine()
            output.append("+ Async engine initialized")
            
            # Test concurrency calculation
            optimal_concurrency = engine.get_optimal_concurrency()
            output.append(f"+ Optimal concurrency calculated: {optimal_concurrency}")
            metrics['optimal_concurrency'] = optimal_concurrency
            
            # Test cleanup
            cleanup_async_engine()
            output.append("+ Async engine cleanup completed")
            
        except Exception as e:
            raise Exception(f"Async engine test failed: {e}")
        
        return "\n".join(output), metrics
    
    def _test_performance_benchmark(self, target_url: str, timeout: int) -> tuple:
        """Test performance benchmark system"""
        output = []
        metrics = {}
        
        if not PERFORMANCE_AVAILABLE:
            raise Exception("Performance benchmark not available - missing dependencies")
        
        try:
            # Create benchmark configuration
            config = BenchmarkConfig(
                target_url=target_url,
                duration=30,  # Short test
                max_requests=1000,
                concurrency_levels=[10, 50],
                output_dir="test_benchmark_results"
            )
            
            # Run benchmark
            benchmark = PerformanceBenchmark(config)
            results = benchmark.run_full_benchmark()
            
            output.append("+ Performance benchmark completed")
            output.append(f"+ Peak RPS: {results.get('peak_rps', 0):.1f}")
            output.append(f"+ Average response time: {results.get('avg_response_time', 0):.1f}ms")
            
            metrics.update(results)
            
        except Exception as e:
            raise Exception(f"Performance benchmark test failed: {e}")
        
        return "\n".join(output), metrics
    
    def _test_stress_basic(self, target_url: str, timeout: int) -> tuple:
        """Test basic stress testing functionality"""
        output = []
        metrics = {}
        
        if not STRESS_TEST_AVAILABLE:
            raise Exception("Stress test not available - missing dependencies")
        
        try:
            # Create stress test configuration
            config = StressTestConfig(
                target_url=target_url,
                max_duration=60,  # 1 minute test
                max_concurrency=500,
                ramp_up_time=20,
                ramp_down_time=10,
                enable_auto_scaling=True,
                enable_failure_recovery=True
            )
            
            # Run stress test
            controller = StressTestController(config)
            results = controller.run_stress_test()
            
            output.append("+ Basic stress test completed")
            output.append(f"+ Max concurrency achieved: {results['summary']['max_connections']}")
            output.append(f"+ Max CPU usage: {results['summary']['max_cpu_usage']:.1f}%")
            
            metrics.update(results['summary'])
            
        except Exception as e:
            raise Exception(f"Basic stress test failed: {e}")
        
        return "\n".join(output), metrics
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        total_duration = self.end_time - self.start_time if self.start_time and self.end_time else 0
        
        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == 'passed')
        failed_tests = sum(1 for r in self.results if r.status == 'failed')
        skipped_tests = sum(1 for r in self.results if r.status == 'skipped')
        
        # Group results by suite
        suite_results = {}
        for result in self.results:
            # Determine suite based on test name
            suite_name = self._get_suite_for_test(result.name)
            if suite_name not in suite_results:
                suite_results[suite_name] = []
            suite_results[suite_name].append(result)
        
        # Create report
        report = {
            'summary': {
                'total_duration': total_duration,
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'skipped_tests': skipped_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Convert TestResult objects to dict for JSON serialization
        serializable_results = []
        for result in self.results:
            result_dict = {
                'name': result.name,
                'status': result.status,
                'duration': result.duration,
                'output': result.output,
                'error': result.error,
                'metrics': result.metrics if result.metrics else {},
                'timestamp': result.timestamp
            }
            serializable_results.append(result_dict)
        
        # Convert suite results to serializable format
        serializable_suite_results = {}
        for suite_name, results in suite_results.items():
            serializable_suite_results[suite_name] = [
                {
                    'name': r.name,
                    'status': r.status,
                    'duration': r.duration,
                    'output': r.output,
                    'error': r.error,
                    'metrics': r.metrics if r.metrics else {},
                    'timestamp': r.timestamp
                } for r in results
            ]
        
        # Update report with serializable results
        report['suite_results'] = serializable_suite_results
        report['detailed_results'] = serializable_results
        report['failed_tests'] = [r for r in serializable_results if r['status'] == 'failed']
        
        # Save report
        report_file = os.path.join(self.output_dir, f"test_report_{int(time.time())}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Generate HTML report
        self._generate_html_report(report, report_file.replace('.json', '.html'))
        
        # Print summary
        print(f"\n[FINAL REPORT]")
        print(f"Total Duration: {total_duration:.1f}s")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Skipped: {skipped_tests}")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"Report saved to: {report_file}")
        
        return report
    
    def _get_suite_for_test(self, test_name: str) -> str:
        """Determine which suite a test belongs to"""
        for suite_name, suite in self.test_suites.items():
            if test_name in suite.tests:
                return suite_name
        return 'unknown'
    
    def _generate_html_report(self, report: Dict[str, Any], output_file: str):
        """Generate HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>FsocietyDDoS Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ background: #ecf0f1; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .suite {{ margin: 20px 0; border: 1px solid #bdc3c7; border-radius: 5px; }}
        .suite-header {{ background: #34495e; color: white; padding: 10px; }}
        .test-result {{ padding: 10px; border-bottom: 1px solid #ecf0f1; }}
        .passed {{ background: #d5f4e6; }}
        .failed {{ background: #f8d7da; }}
        .skipped {{ background: #fff3cd; }}
        .metrics {{ font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>FsocietyDDoS Test Report</h1>
        <p>Generated: {report['summary']['timestamp']}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Duration:</strong> {report['summary']['total_duration']:.1f}s</p>
        <p><strong>Total Tests:</strong> {report['summary']['total_tests']}</p>
        <p><strong>Passed:</strong> {report['summary']['passed_tests']}</p>
        <p><strong>Failed:</strong> {report['summary']['failed_tests']}</p>
        <p><strong>Skipped:</strong> {report['summary']['skipped_tests']}</p>
        <p><strong>Success Rate:</strong> {report['summary']['success_rate']:.1f}%</p>
    </div>
"""
        
        # Add suite results
        for suite_name, results in report['suite_results'].items():
            html_content += f"""
    <div class="suite">
        <div class="suite-header">
            <h3>{suite_name.title()} Tests</h3>
        </div>
"""
            
            for result in results:
                status_class = result['status']
                html_content += f"""
        <div class="test-result {status_class}">
            <h4>{result['name']}</h4>
            <p><strong>Status:</strong> {result['status'].upper()}</p>
            <p><strong>Duration:</strong> {result['duration']:.2f}s</p>
            <p><strong>Output:</strong></p>
            <pre>{result['output']}</pre>
"""
                
                if result['error']:
                    html_content += f"<p><strong>Error:</strong> {result['error']}</p>"
                
                if result['metrics']:
                    html_content += f"<div class='metrics'><strong>Metrics:</strong> {json.dumps(result['metrics'], indent=2)}</div>"
                
                html_content += "</div>"
            
            html_content += "</div>"
        
        html_content += """
</body>
</html>
"""
        
        with open(output_file, 'w') as f:
            f.write(html_content)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="FsocietyDDoS Test Runner")
    parser.add_argument("--target", default="http://httpbin.org/get", help="Target URL for tests")
    parser.add_argument("--suites", nargs='+', help="Test suites to run", 
                       choices=['unit', 'integration', 'performance', 'stress', 'security'])
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel where possible")
    parser.add_argument("--output-dir", default="test_results", help="Output directory for results")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = TestRunner(output_dir=args.output_dir)
    
    # Run tests
    results = runner.run_all_tests(
        target_url=args.target,
        suites=args.suites,
        parallel=args.parallel
    )
    
    # Exit with appropriate code
    if results.get('summary', {}).get('failed_tests', 0) > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()