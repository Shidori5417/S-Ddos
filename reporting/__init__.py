"""
Reporting Module
Advanced logging, reporting, and analytics system
"""

from .advanced_logger import (
    LogLevel,
    ReportFormat,
    LoggingConfig,
    LogEntry,
    LogEncryption,
    DatabaseLogger,
    LogAnalyzer,
    ReportGenerator,
    AdvancedLogger,
    get_advanced_logger
)

__all__ = [
    'LogLevel',
    'ReportFormat',
    'LoggingConfig',
    'LogEntry',
    'LogEncryption',
    'DatabaseLogger',
    'LogAnalyzer',
    'ReportGenerator',
    'AdvancedLogger',
    'get_advanced_logger',
    'list_reporting_features'
]


def list_reporting_features() -> dict:
    """
    List all available reporting and logging features
    
    Returns:
        dict: Available features and their descriptions
    """
    return {
        'advanced_logging': {
            'description': 'Comprehensive logging system with multiple outputs',
            'features': [
                'Multi-level logging (TRACE to CRITICAL)',
                'Special attack and security log levels',
                'Async logging for performance',
                'Log encryption and security',
                'Structured log entries with metadata'
            ]
        },
        'database_logging': {
            'description': 'SQLite-based log storage and querying',
            'features': [
                'Structured log storage',
                'Advanced querying capabilities',
                'Automatic log retention',
                'Performance optimized indexes',
                'Log correlation support'
            ]
        },
        'log_analysis': {
            'description': 'Intelligent log analysis and pattern detection',
            'features': [
                'Attack pattern analysis',
                'Anomaly detection',
                'Threat intelligence generation',
                'Statistical analysis',
                'Predictive insights'
            ]
        },
        'report_generation': {
            'description': 'Comprehensive report generation in multiple formats',
            'features': [
                'JSON, CSV, HTML, PDF reports',
                'Automated report scheduling',
                'Attack analysis reports',
                'Security incident reports',
                'Performance reports'
            ]
        },
        'real_time_monitoring': {
            'description': 'Real-time log monitoring and alerting',
            'features': [
                'Live log streaming',
                'Threshold-based alerts',
                'Real-time dashboards',
                'Event correlation',
                'Instant notifications'
            ]
        },
        'security_features': {
            'description': 'Security-focused logging capabilities',
            'features': [
                'Log encryption',
                'Sensitive data hashing',
                'IP anonymization',
                'Audit trails',
                'Tamper detection'
            ]
        },
        'analytics_engine': {
            'description': 'Advanced analytics and intelligence',
            'features': [
                'Attack effectiveness analysis',
                'Target profiling',
                'Traffic pattern analysis',
                'Performance metrics',
                'Trend analysis'
            ]
        }
    }