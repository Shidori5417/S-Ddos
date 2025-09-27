"""
Advanced Logging and Reporting System
Comprehensive logging, reporting, and analytics for DDoS operations
"""

import logging
import json
import csv
import sqlite3
import threading
import time
import os
import gzip
import shutil
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import hashlib
import base64
from collections import defaultdict, deque
import statistics

from core.logger import logger


class LogLevel(Enum):
    """Enhanced log levels"""
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    ATTACK = 60  # Special level for attack operations
    SECURITY = 70  # Special level for security events


class ReportFormat(Enum):
    """Report output formats"""
    JSON = "json"
    CSV = "csv"
    HTML = "html"
    PDF = "pdf"
    XML = "xml"
    SQLITE = "sqlite"


@dataclass
class LoggingConfig:
    """Configuration for advanced logging"""
    # Basic Settings
    log_level: LogLevel = LogLevel.INFO
    log_to_file: bool = True
    log_to_console: bool = True
    log_to_database: bool = True
    
    # File Settings
    log_directory: str = "logs"
    log_filename: str = "fsociety_ddos.log"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    backup_count: int = 10
    compress_backups: bool = True
    
    # Database Settings
    database_path: str = "logs/attack_logs.db"
    database_retention_days: int = 30
    
    # Security Settings
    encrypt_logs: bool = True
    hash_sensitive_data: bool = True
    anonymize_ips: bool = False
    
    # Performance Settings
    async_logging: bool = True
    buffer_size: int = 1000
    flush_interval: float = 5.0  # seconds
    
    # Reporting Settings
    enable_reports: bool = True
    report_directory: str = "reports"
    auto_report_interval: int = 3600  # seconds (1 hour)
    
    # Advanced Features
    enable_analytics: bool = True
    enable_real_time_monitoring: bool = True
    enable_log_correlation: bool = True
    enable_threat_detection: bool = True


@dataclass
class LogEntry:
    """Enhanced log entry structure"""
    timestamp: datetime
    level: LogLevel
    message: str
    category: str
    source: str
    thread_id: int
    process_id: int
    
    # Attack-specific fields
    target_ip: Optional[str] = None
    target_port: Optional[int] = None
    attack_type: Optional[str] = None
    packets_sent: Optional[int] = None
    bytes_sent: Optional[int] = None
    
    # Security fields
    user_agent: Optional[str] = None
    source_ip: Optional[str] = None
    session_id: Optional[str] = None
    
    # Performance fields
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    network_usage: Optional[float] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    correlation_id: Optional[str] = None


class LogEncryption:
    """Log encryption and security"""
    
    def __init__(self, key: Optional[bytes] = None):
        self.key = key or self._generate_key()
    
    def _generate_key(self) -> bytes:
        """Generate encryption key"""
        return os.urandom(32)  # 256-bit key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt log data"""
        try:
            from cryptography.fernet import Fernet
            
            # Use base64 encoded key for Fernet
            key = base64.urlsafe_b64encode(self.key[:32])
            fernet = Fernet(key)
            
            encrypted = fernet.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        except ImportError:
            # Fallback to simple base64 encoding if cryptography not available
            return base64.b64encode(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt log data"""
        try:
            from cryptography.fernet import Fernet
            
            key = base64.urlsafe_b64encode(self.key[:32])
            fernet = Fernet(key)
            
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except ImportError:
            # Fallback to simple base64 decoding
            return base64.b64decode(encrypted_data.encode()).decode()
    
    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data"""
        return hashlib.sha256(data.encode()).hexdigest()


class DatabaseLogger:
    """Database logging backend"""
    
    def __init__(self, config: LoggingConfig):
        self.config = config
        self.db_path = config.database_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS log_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    category TEXT,
                    source TEXT,
                    thread_id INTEGER,
                    process_id INTEGER,
                    target_ip TEXT,
                    target_port INTEGER,
                    attack_type TEXT,
                    packets_sent INTEGER,
                    bytes_sent INTEGER,
                    user_agent TEXT,
                    source_ip TEXT,
                    session_id TEXT,
                    cpu_usage REAL,
                    memory_usage REAL,
                    network_usage REAL,
                    metadata TEXT,
                    tags TEXT,
                    correlation_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON log_entries(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_level ON log_entries(level)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON log_entries(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_attack_type ON log_entries(attack_type)")
    
    def log_entry(self, entry: LogEntry):
        """Log entry to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO log_entries (
                        timestamp, level, message, category, source, thread_id, process_id,
                        target_ip, target_port, attack_type, packets_sent, bytes_sent,
                        user_agent, source_ip, session_id, cpu_usage, memory_usage, network_usage,
                        metadata, tags, correlation_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.timestamp.isoformat(),
                    entry.level.name,
                    entry.message,
                    entry.category,
                    entry.source,
                    entry.thread_id,
                    entry.process_id,
                    entry.target_ip,
                    entry.target_port,
                    entry.attack_type,
                    entry.packets_sent,
                    entry.bytes_sent,
                    entry.user_agent,
                    entry.source_ip,
                    entry.session_id,
                    entry.cpu_usage,
                    entry.memory_usage,
                    entry.network_usage,
                    json.dumps(entry.metadata),
                    json.dumps(entry.tags),
                    entry.correlation_id
                ))
        except Exception as e:
            logger.error(f"Database logging error: {e}")
    
    def query_logs(self, 
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   level: Optional[LogLevel] = None,
                   category: Optional[str] = None,
                   limit: int = 1000) -> List[Dict[str, Any]]:
        """Query log entries"""
        query = "SELECT * FROM log_entries WHERE 1=1"
        params = []
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        if level:
            query += " AND level = ?"
            params.append(level.name)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Database query error: {e}")
            return []
    
    def cleanup_old_logs(self):
        """Clean up old log entries"""
        cutoff_date = datetime.now() - timedelta(days=self.config.database_retention_days)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM log_entries WHERE timestamp < ?",
                    (cutoff_date.isoformat(),)
                )
                deleted_count = cursor.rowcount
                logger.info(f"Cleaned up {deleted_count} old log entries")
        except Exception as e:
            logger.error(f"Log cleanup error: {e}")


class LogAnalyzer:
    """Log analysis and correlation"""
    
    def __init__(self, config: LoggingConfig):
        self.config = config
        self.db_logger = DatabaseLogger(config)
        
    def analyze_attack_patterns(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze attack patterns"""
        start_time = datetime.now() - timedelta(hours=hours)
        logs = self.db_logger.query_logs(start_time=start_time, limit=10000)
        
        # Filter attack logs
        attack_logs = [log for log in logs if log.get('attack_type')]
        
        if not attack_logs:
            return {'message': 'No attack data found'}
        
        # Analyze patterns
        attack_types = defaultdict(int)
        target_ips = defaultdict(int)
        hourly_distribution = defaultdict(int)
        
        total_packets = 0
        total_bytes = 0
        
        for log in attack_logs:
            # Attack type distribution
            if log.get('attack_type'):
                attack_types[log['attack_type']] += 1
            
            # Target IP distribution
            if log.get('target_ip'):
                target_ips[log['target_ip']] += 1
            
            # Hourly distribution
            timestamp = datetime.fromisoformat(log['timestamp'])
            hour_key = timestamp.strftime('%Y-%m-%d %H:00')
            hourly_distribution[hour_key] += 1
            
            # Traffic statistics
            if log.get('packets_sent'):
                total_packets += log['packets_sent']
            if log.get('bytes_sent'):
                total_bytes += log['bytes_sent']
        
        return {
            'analysis_period': f"{hours} hours",
            'total_attack_events': len(attack_logs),
            'attack_type_distribution': dict(attack_types),
            'top_targets': dict(sorted(target_ips.items(), key=lambda x: x[1], reverse=True)[:10]),
            'hourly_distribution': dict(hourly_distribution),
            'traffic_statistics': {
                'total_packets_sent': total_packets,
                'total_bytes_sent': total_bytes,
                'average_packets_per_event': total_packets / len(attack_logs) if attack_logs else 0,
                'average_bytes_per_event': total_bytes / len(attack_logs) if attack_logs else 0
            }
        }
    
    def detect_anomalies(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Detect anomalies in log data"""
        start_time = datetime.now() - timedelta(hours=hours)
        logs = self.db_logger.query_logs(start_time=start_time, limit=10000)
        
        anomalies = []
        
        # Check for unusual error rates
        error_logs = [log for log in logs if log.get('level') in ['ERROR', 'CRITICAL']]
        error_rate = len(error_logs) / len(logs) if logs else 0
        
        if error_rate > 0.1:  # More than 10% errors
            anomalies.append({
                'type': 'high_error_rate',
                'severity': 'high',
                'description': f"High error rate detected: {error_rate:.2%}",
                'count': len(error_logs)
            })
        
        # Check for unusual attack patterns
        attack_logs = [log for log in logs if log.get('attack_type')]
        if attack_logs:
            # Check for rapid attack bursts
            attack_times = [datetime.fromisoformat(log['timestamp']) for log in attack_logs]
            attack_times.sort()
            
            # Look for periods with many attacks in short time
            for i in range(len(attack_times) - 10):
                time_window = attack_times[i + 9] - attack_times[i]
                if time_window.total_seconds() < 60:  # 10 attacks in less than 1 minute
                    anomalies.append({
                        'type': 'attack_burst',
                        'severity': 'medium',
                        'description': f"Attack burst detected: 10 attacks in {time_window.total_seconds():.1f} seconds",
                        'timestamp': attack_times[i].isoformat()
                    })
        
        return anomalies
    
    def generate_threat_intelligence(self) -> Dict[str, Any]:
        """Generate threat intelligence report"""
        # Analyze last 7 days
        start_time = datetime.now() - timedelta(days=7)
        logs = self.db_logger.query_logs(start_time=start_time, limit=50000)
        
        # Extract threat indicators
        threat_ips = set()
        attack_vectors = defaultdict(int)
        
        for log in logs:
            if log.get('target_ip'):
                threat_ips.add(log['target_ip'])
            if log.get('attack_type'):
                attack_vectors[log['attack_type']] += 1
        
        return {
            'report_generated': datetime.now().isoformat(),
            'analysis_period': '7 days',
            'threat_indicators': {
                'targeted_ips': list(threat_ips),
                'attack_vectors': dict(attack_vectors),
                'total_threats': len(threat_ips)
            },
            'recommendations': self._generate_recommendations(attack_vectors)
        }
    
    def _generate_recommendations(self, attack_vectors: Dict[str, int]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if attack_vectors.get('UDP_FLOOD', 0) > 100:
            recommendations.append("Consider implementing UDP flood protection")
        
        if attack_vectors.get('SYN_FLOOD', 0) > 100:
            recommendations.append("Enable SYN flood protection on target systems")
        
        if attack_vectors.get('HTTP_FLOOD', 0) > 50:
            recommendations.append("Implement rate limiting and WAF protection")
        
        if len(attack_vectors) > 5:
            recommendations.append("Multi-vector attack detected - implement comprehensive DDoS protection")
        
        return recommendations


class ReportGenerator:
    """Advanced report generation"""
    
    def __init__(self, config: LoggingConfig):
        self.config = config
        self.db_logger = DatabaseLogger(config)
        self.analyzer = LogAnalyzer(config)
        
        # Ensure report directory exists
        os.makedirs(config.report_directory, exist_ok=True)
    
    def generate_attack_report(self, 
                             format_type: ReportFormat = ReportFormat.JSON,
                             hours: int = 24) -> str:
        """Generate comprehensive attack report"""
        
        # Gather data
        analysis = self.analyzer.analyze_attack_patterns(hours)
        anomalies = self.analyzer.detect_anomalies(hours)
        threat_intel = self.analyzer.generate_threat_intelligence()
        
        report_data = {
            'report_type': 'attack_analysis',
            'generated_at': datetime.now().isoformat(),
            'analysis_period_hours': hours,
            'attack_analysis': analysis,
            'anomalies_detected': anomalies,
            'threat_intelligence': threat_intel
        }
        
        # Generate report in requested format
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"attack_report_{timestamp}.{format_type.value}"
        filepath = os.path.join(self.config.report_directory, filename)
        
        if format_type == ReportFormat.JSON:
            self._generate_json_report(report_data, filepath)
        elif format_type == ReportFormat.CSV:
            self._generate_csv_report(report_data, filepath)
        elif format_type == ReportFormat.HTML:
            self._generate_html_report(report_data, filepath)
        
        logger.info(f"Attack report generated: {filepath}")
        return filepath
    
    def _generate_json_report(self, data: Dict[str, Any], filepath: str):
        """Generate JSON report"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _generate_csv_report(self, data: Dict[str, Any], filepath: str):
        """Generate CSV report"""
        # Extract attack events for CSV
        start_time = datetime.now() - timedelta(hours=data['analysis_period_hours'])
        logs = self.db_logger.query_logs(start_time=start_time, limit=10000)
        attack_logs = [log for log in logs if log.get('attack_type')]
        
        with open(filepath, 'w', newline='') as f:
            if attack_logs:
                writer = csv.DictWriter(f, fieldnames=attack_logs[0].keys())
                writer.writeheader()
                writer.writerows(attack_logs)
    
    def _generate_html_report(self, data: Dict[str, Any], filepath: str):
        """Generate HTML report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>FsocietyDDoS Attack Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .anomaly {{ background-color: #f8d7da; padding: 10px; margin: 5px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>FsocietyDDoS Attack Report</h1>
                <p>Generated: {data['generated_at']}</p>
                <p>Analysis Period: {data['analysis_period_hours']} hours</p>
            </div>
            
            <div class="section">
                <h2>Attack Analysis</h2>
                <p>Total Attack Events: {data['attack_analysis'].get('total_attack_events', 0)}</p>
                <h3>Attack Type Distribution</h3>
                <table>
                    <tr><th>Attack Type</th><th>Count</th></tr>
        """
        
        # Add attack type distribution
        for attack_type, count in data['attack_analysis'].get('attack_type_distribution', {}).items():
            html_content += f"<tr><td>{attack_type}</td><td>{count}</td></tr>"
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>Anomalies Detected</h2>
        """
        
        # Add anomalies
        for anomaly in data['anomalies_detected']:
            html_content += f"""
                <div class="anomaly">
                    <strong>{anomaly['type']}</strong> (Severity: {anomaly['severity']})<br>
                    {anomaly['description']}
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        with open(filepath, 'w') as f:
            f.write(html_content)


class AdvancedLogger:
    """Main advanced logging system"""
    
    def __init__(self, config: LoggingConfig = None):
        self.config = config or LoggingConfig()
        
        # Initialize components
        self.encryption = LogEncryption() if self.config.encrypt_logs else None
        self.db_logger = DatabaseLogger(self.config) if self.config.log_to_database else None
        self.report_generator = ReportGenerator(self.config) if self.config.enable_reports else None
        
        # Logging buffer for async logging
        self.log_buffer = deque(maxlen=self.config.buffer_size)
        self.buffer_lock = threading.Lock()
        
        # Setup file logging
        self._setup_file_logging()
        
        # Start background tasks
        if self.config.async_logging:
            self._start_async_logging()
        
        if self.config.enable_reports and self.config.auto_report_interval > 0:
            self._start_auto_reporting()
    
    def _setup_file_logging(self):
        """Setup file logging"""
        if not self.config.log_to_file:
            return
        
        os.makedirs(self.config.log_directory, exist_ok=True)
        
        # Configure rotating file handler
        from logging.handlers import RotatingFileHandler
        
        log_path = os.path.join(self.config.log_directory, self.config.log_filename)
        
        handler = RotatingFileHandler(
            log_path,
            maxBytes=self.config.max_file_size,
            backupCount=self.config.backup_count
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
    
    def _start_async_logging(self):
        """Start async logging thread"""
        def async_log_worker():
            while True:
                try:
                    if self.log_buffer:
                        with self.buffer_lock:
                            entries_to_process = list(self.log_buffer)
                            self.log_buffer.clear()
                        
                        # Process buffered entries
                        for entry in entries_to_process:
                            self._write_log_entry(entry)
                    
                    time.sleep(self.config.flush_interval)
                except Exception as e:
                    logger.error(f"Async logging error: {e}")
        
        thread = threading.Thread(target=async_log_worker)
        thread.daemon = True
        thread.start()
    
    def _start_auto_reporting(self):
        """Start automatic report generation"""
        def auto_report_worker():
            while True:
                try:
                    time.sleep(self.config.auto_report_interval)
                    if self.report_generator:
                        self.report_generator.generate_attack_report()
                except Exception as e:
                    logger.error(f"Auto reporting error: {e}")
        
        thread = threading.Thread(target=auto_report_worker)
        thread.daemon = True
        thread.start()
    
    def log_attack_event(self,
                        message: str,
                        attack_type: str,
                        target_ip: str,
                        target_port: Optional[int] = None,
                        packets_sent: Optional[int] = None,
                        bytes_sent: Optional[int] = None,
                        **kwargs):
        """Log attack event"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ATTACK,
            message=message,
            category="attack",
            source="ddos_engine",
            thread_id=threading.get_ident(),
            process_id=os.getpid(),
            target_ip=target_ip,
            target_port=target_port,
            attack_type=attack_type,
            packets_sent=packets_sent,
            bytes_sent=bytes_sent,
            **kwargs
        )
        
        self._add_log_entry(entry)
    
    def log_security_event(self,
                          message: str,
                          event_type: str,
                          source_ip: Optional[str] = None,
                          **kwargs):
        """Log security event"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.SECURITY,
            message=message,
            category="security",
            source="security_system",
            thread_id=threading.get_ident(),
            process_id=os.getpid(),
            source_ip=source_ip,
            metadata={'event_type': event_type},
            **kwargs
        )
        
        self._add_log_entry(entry)
    
    def _add_log_entry(self, entry: LogEntry):
        """Add log entry to buffer or process immediately"""
        if self.config.async_logging:
            with self.buffer_lock:
                self.log_buffer.append(entry)
        else:
            self._write_log_entry(entry)
    
    def _write_log_entry(self, entry: LogEntry):
        """Write log entry to all configured outputs"""
        # Console logging
        if self.config.log_to_console:
            print(f"[{entry.timestamp}] {entry.level.name}: {entry.message}")
        
        # File logging
        if self.config.log_to_file:
            log_message = f"{entry.timestamp} - {entry.level.name} - {entry.category} - {entry.message}"
            
            if self.encryption:
                log_message = self.encryption.encrypt_data(log_message)
            
            logger.log(entry.level.value, log_message)
        
        # Database logging
        if self.db_logger:
            self.db_logger.log_entry(entry)
    
    def generate_report(self, format_type: ReportFormat = ReportFormat.JSON, hours: int = 24) -> str:
        """Generate comprehensive report"""
        if not self.report_generator:
            raise ValueError("Reporting not enabled")
        
        return self.report_generator.generate_attack_report(format_type, hours)
    
    def get_attack_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get attack statistics"""
        if not self.db_logger:
            return {}
        
        analyzer = LogAnalyzer(self.config)
        return analyzer.analyze_attack_patterns(hours)
    
    def cleanup_logs(self):
        """Clean up old logs"""
        if self.db_logger:
            self.db_logger.cleanup_old_logs()
        
        # Compress old log files
        if self.config.compress_backups:
            self._compress_old_logs()
    
    def _compress_old_logs(self):
        """Compress old log files"""
        log_dir = Path(self.config.log_directory)
        
        for log_file in log_dir.glob("*.log.*"):
            if not log_file.name.endswith('.gz'):
                compressed_file = log_file.with_suffix(log_file.suffix + '.gz')
                
                with open(log_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                log_file.unlink()  # Remove original file
                logger.debug(f"Compressed log file: {compressed_file}")


# Global advanced logger instance
advanced_logger = None


def get_advanced_logger(config: LoggingConfig = None) -> AdvancedLogger:
    """Get global advanced logger instance"""
    global advanced_logger
    
    if advanced_logger is None:
        advanced_logger = AdvancedLogger(config)
    
    return advanced_logger