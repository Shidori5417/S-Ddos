"""
Monitoring Module
Comprehensive system monitoring, performance optimization, and resource management
"""

from .system_monitor import (
    MonitoringConfig,
    CPUMonitor,
    MemoryMonitor,
    NetworkMonitor,
    ProcessMonitor,
    PerformanceOptimizer,
    SystemMonitorManager
)

__all__ = [
    'MonitoringConfig',
    'CPUMonitor',
    'MemoryMonitor',
    'NetworkMonitor',
    'ProcessMonitor',
    'PerformanceOptimizer',
    'SystemMonitorManager',
    'get_system_monitor',
    'list_monitoring_features'
]

# Monitoring systems registry
MONITORING_SYSTEMS = {
    'cpu_monitor': CPUMonitor,
    'memory_monitor': MemoryMonitor,
    'network_monitor': NetworkMonitor,
    'process_monitor': ProcessMonitor,
    'performance_optimizer': PerformanceOptimizer,
    'system_monitor_manager': SystemMonitorManager
}


def get_system_monitor(config: MonitoringConfig = None) -> SystemMonitorManager:
    """
    Get a configured system monitor manager
    
    Args:
        config: Monitoring configuration
        
    Returns:
        SystemMonitorManager: Configured system monitor
    """
    return SystemMonitorManager(config)


def list_monitoring_features() -> dict:
    """
    List all available monitoring features
    
    Returns:
        dict: Available monitoring features and their descriptions
    """
    return {
        'cpu_monitoring': {
            'description': 'Real-time CPU usage monitoring and optimization',
            'features': [
                'Per-core CPU monitoring',
                'CPU frequency tracking',
                'Process CPU usage analysis',
                'Automatic CPU optimization',
                'CPU threshold alerts'
            ]
        },
        'memory_monitoring': {
            'description': 'Memory usage monitoring and optimization',
            'features': [
                'RAM usage tracking',
                'Swap usage monitoring',
                'Memory leak detection',
                'Automatic garbage collection',
                'Memory threshold alerts'
            ]
        },
        'network_monitoring': {
            'description': 'Network activity monitoring and analysis',
            'features': [
                'Network I/O statistics',
                'Connection tracking',
                'Bandwidth monitoring',
                'Attack connection detection',
                'Network performance optimization'
            ]
        },
        'process_monitoring': {
            'description': 'Process tracking and management',
            'features': [
                'Process resource usage',
                'Attack process detection',
                'Process lifecycle tracking',
                'Resource optimization',
                'Process priority management'
            ]
        },
        'performance_optimization': {
            'description': 'System performance optimization',
            'features': [
                'Automatic performance tuning',
                'Resource allocation optimization',
                'System configuration optimization',
                'Attack-specific optimizations',
                'Real-time performance adjustments'
            ]
        },
        'alerting_system': {
            'description': 'Intelligent alerting and notifications',
            'features': [
                'Threshold-based alerts',
                'Predictive analysis',
                'Alert cooldown management',
                'Multi-level alert severity',
                'Custom alert conditions'
            ]
        }
    }