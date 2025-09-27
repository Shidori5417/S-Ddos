"""
Configuration Settings
Comprehensive configuration management system
"""

import json
import os
import yaml
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import logging


@dataclass
class GlobalConfig:
    """Global application configuration - Enhanced for maximum performance"""
    
    # Application settings
    app_name: str = "FsocietyDDoS"
    version: str = "2.0.0"
    debug_mode: bool = False
    verbose_output: bool = True
    
    # Performance settings - Set to 8GB memory as requested
    max_threads: int = 2000  # Increased from 100 to 2000
    thread_pool_size: int = 1000  # Increased from 50 to 1000
    memory_limit_mb: int = 8192  # Set to 8GB (8192 MB)
    cpu_limit_percent: int = 95  # Increased from 80 to 95%
    
    # Timeout settings - Optimized for faster operations
    connection_timeout: int = 2  # Reduced from 10 to 2
    read_timeout: int = 5  # Reduced from 30 to 5
    operation_timeout: int = 600  # Increased from 300 to 600
    
    # File paths
    config_dir: str = "config"
    logs_dir: str = "logs"
    temp_dir: str = "temp"
    data_dir: str = "data"
    
    # Security settings - Enhanced capabilities
    enable_encryption: bool = True
    encryption_key: Optional[str] = None
    secure_mode: bool = True
    enable_stealth_mode: bool = True
    anti_detection_mode: bool = True
    
    def __post_init__(self):
        """Post-initialization validation"""
        if self.max_threads < 1:
            self.max_threads = 1
        if self.thread_pool_size < 1:
            self.thread_pool_size = 1
        if self.memory_limit_mb < 64:
            self.memory_limit_mb = 64


@dataclass
class AttackConfig:
    """Attack configuration settings - Enhanced for maximum impact"""
    
    # Attack parameters
    attack_type: str = "http_flood"
    attack_layer: str = "layer7"  # layer4 or layer7
    target_url: str = ""
    target_ip: str = ""
    target_port: int = 80
    
    # Basic attack parameters - Significantly increased
    threads: int = 500  # Increased from 50 to 500 threads
    requests_per_second: int = 1000  # Increased from 100 to 1000 RPS
    duration_seconds: int = 300  # Increased from 60 to 300 seconds (5 minutes)
    packet_size: int = 8192  # Increased from 1024 to 8192 bytes
    
    # Request settings (Layer 7)
    http_method: str = "GET"
    user_agents: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    ])
    custom_headers: Dict[str, str] = field(default_factory=dict)
    
    # Protocol settings (Layer 4)
    protocol: str = "tcp"  # tcp, udp, icmp
    source_port_range: tuple = (1024, 65535)
    enable_spoofing: bool = True
    fragment_packets: bool = False
    
    # Proxy settings
    use_proxies: bool = True
    proxy_list: List[str] = field(default_factory=list)
    proxy_rotation: bool = True
    proxy_timeout: int = 10
    
    # Evasion settings
    randomize_headers: bool = True
    randomize_payload: bool = True
    use_ssl: bool = False
    bypass_cloudflare: bool = True
    
    def __post_init__(self):
        """Post-initialization validation"""
        if self.threads < 1:
            self.threads = 1
        if self.requests_per_second < 1:
            self.requests_per_second = 1
        if self.duration_seconds < 1:
            self.duration_seconds = 1
        if self.target_port < 1 or self.target_port > 65535:
            self.target_port = 80


@dataclass
class SecurityConfig:
    """Security and stealth configuration"""
    
    # Stealth settings
    enable_stealth_mode: bool = True
    hide_process: bool = True
    obfuscate_traffic: bool = True
    anti_forensics: bool = True
    
    # Detection avoidance
    avoid_honeypots: bool = True
    evade_ids: bool = True
    evade_waf: bool = True
    randomize_timing: bool = True
    
    # Behavioral evasion
    human_like_behavior: bool = True
    random_delays: bool = True
    delay_range: tuple = (1, 5)
    jitter_factor: float = 0.2
    
    # Network evasion
    rotate_source_ip: bool = True
    spoof_mac_address: bool = True
    randomize_ttl: bool = True
    fragment_threshold: int = 1400
    
    # Anti-analysis
    detect_sandbox: bool = True
    detect_vm: bool = True
    detect_debugger: bool = True
    self_destruct: bool = False
    
    # Encryption settings
    encrypt_payloads: bool = True
    encrypt_communications: bool = True
    encryption_algorithm: str = "AES-256"
    
    def __post_init__(self):
        """Post-initialization validation"""
        if self.jitter_factor < 0 or self.jitter_factor > 1:
            self.jitter_factor = 0.2
        if self.fragment_threshold < 64:
            self.fragment_threshold = 64


@dataclass
class NetworkConfig:
    """Network and connection configuration"""
    
    # Connection settings
    max_connections: int = 1000
    connection_pool_size: int = 100
    keep_alive: bool = True
    tcp_nodelay: bool = True
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_factor: float = 2.0
    
    # Bandwidth settings
    bandwidth_limit_mbps: Optional[int] = None
    rate_limit_requests: Optional[int] = None
    burst_size: int = 10
    
    # DNS settings
    custom_dns_servers: List[str] = field(default_factory=lambda: [
        "8.8.8.8", "8.8.4.4", "1.1.1.1", "1.0.0.1"
    ])
    dns_timeout: int = 5
    
    # Interface settings
    bind_interface: Optional[str] = None
    source_ip_range: Optional[str] = None
    
    # Quality of Service
    dscp_marking: Optional[int] = None
    traffic_class: Optional[int] = None
    
    def __post_init__(self):
        """Post-initialization validation"""
        if self.max_connections < 1:
            self.max_connections = 1
        if self.connection_pool_size < 1:
            self.connection_pool_size = 1
        if self.max_retries < 0:
            self.max_retries = 0


@dataclass
class LoggingConfig:
    """Logging and monitoring configuration"""
    
    # Logging levels
    log_level: str = "INFO"
    console_log_level: str = "INFO"
    file_log_level: str = "DEBUG"
    
    # Log files
    enable_file_logging: bool = True
    log_file_path: str = "logs/fsociety.log"
    max_log_size_mb: int = 100
    backup_count: int = 5
    
    # Log formats
    console_format: str = "%(asctime)s - %(levelname)s - %(message)s"
    file_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    
    # Monitoring
    enable_monitoring: bool = True
    metrics_interval: int = 60
    performance_tracking: bool = True
    
    # Security logging
    log_attacks: bool = True
    log_security_events: bool = True
    sanitize_logs: bool = True
    
    # Remote logging
    enable_remote_logging: bool = False
    remote_log_server: Optional[str] = None
    remote_log_port: int = 514
    
    def __post_init__(self):
        """Post-initialization validation"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_levels:
            self.log_level = "INFO"
        if self.console_log_level not in valid_levels:
            self.console_log_level = "INFO"
        if self.file_log_level not in valid_levels:
            self.file_log_level = "DEBUG"


class ConfigManager:
    """Centralized configuration manager"""
    
    def __init__(self):
        self.global_config = GlobalConfig()
        self.attack_config = AttackConfig()
        self.security_config = SecurityConfig()
        self.network_config = NetworkConfig()
        self.logging_config = LoggingConfig()
        
        self._config_file_path = None
        self._logger = logging.getLogger(__name__)
    
    def load_from_file(self, config_path: str):
        """Load configuration from file"""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.json':
                    data = json.load(f)
                elif config_path.suffix.lower() in ['.yml', '.yaml']:
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
            
            self._load_from_dict(data)
            self._config_file_path = str(config_path)
            self._logger.info(f"Configuration loaded from: {config_path}")
            
        except Exception as e:
            self._logger.error(f"Failed to load configuration: {e}")
            raise
    
    def save_to_file(self, config_path: str, format: str = 'json'):
        """Save configuration to file"""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = self.to_dict()
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                if format.lower() == 'json':
                    json.dump(data, f, indent=2, ensure_ascii=False)
                elif format.lower() in ['yml', 'yaml']:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
                else:
                    raise ValueError(f"Unsupported format: {format}")
            
            self._config_file_path = str(config_path)
            self._logger.info(f"Configuration saved to: {config_path}")
            
        except Exception as e:
            self._logger.error(f"Failed to save configuration: {e}")
            raise
    
    def _load_from_dict(self, data: Dict[str, Any]):
        """Load configuration from dictionary"""
        if 'global' in data:
            self.global_config = GlobalConfig(**data['global'])
        
        if 'attack' in data:
            self.attack_config = AttackConfig(**data['attack'])
        
        if 'security' in data:
            self.security_config = SecurityConfig(**data['security'])
        
        if 'network' in data:
            self.network_config = NetworkConfig(**data['network'])
        
        if 'logging' in data:
            self.logging_config = LoggingConfig(**data['logging'])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'global': asdict(self.global_config),
            'attack': asdict(self.attack_config),
            'security': asdict(self.security_config),
            'network': asdict(self.network_config),
            'logging': asdict(self.logging_config)
        }
    
    def apply_profile(self, profile):
        """Apply configuration profile"""
        if hasattr(profile, 'global_config'):
            self.global_config = profile.global_config
        if hasattr(profile, 'attack_config'):
            self.attack_config = profile.attack_config
        if hasattr(profile, 'security_config'):
            self.security_config = profile.security_config
        if hasattr(profile, 'network_config'):
            self.network_config = profile.network_config
        if hasattr(profile, 'logging_config'):
            self.logging_config = profile.logging_config
    
    def update_config(self, section: str, **kwargs):
        """Update specific configuration section"""
        if section == 'global':
            config = self.global_config
        elif section == 'attack':
            config = self.attack_config
        elif section == 'security':
            config = self.security_config
        elif section == 'network':
            config = self.network_config
        elif section == 'logging':
            config = self.logging_config
        else:
            raise ValueError(f"Unknown configuration section: {section}")
        
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                self._logger.warning(f"Unknown configuration key: {key}")
    
    def get_config(self, section: str):
        """Get specific configuration section"""
        if section == 'global':
            return self.global_config
        elif section == 'attack':
            return self.attack_config
        elif section == 'security':
            return self.security_config
        elif section == 'network':
            return self.network_config
        elif section == 'logging':
            return self.logging_config
        else:
            raise ValueError(f"Unknown configuration section: {section}")
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate global config
        if self.global_config.max_threads > 1000:
            issues.append("Global: max_threads exceeds recommended limit (1000)")
        
        # Validate attack config
        if not self.attack_config.target_url and not self.attack_config.target_ip:
            issues.append("Attack: Either target_url or target_ip must be specified")
        
        if self.attack_config.threads > self.global_config.max_threads:
            issues.append("Attack: threads exceeds global max_threads limit")
        
        # Validate network config
        if self.network_config.max_connections > 10000:
            issues.append("Network: max_connections exceeds recommended limit (10000)")
        
        return issues
    
    def create_directories(self):
        """Create necessary directories"""
        directories = [
            self.global_config.config_dir,
            self.global_config.logs_dir,
            self.global_config.temp_dir,
            self.global_config.data_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def setup_logging(self):
        """Setup logging based on configuration"""
        log_config = self.logging_config
        
        # Create logs directory
        log_path = Path(log_config.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_config.log_level))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_config.console_log_level))
        console_formatter = logging.Formatter(log_config.console_format)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler
        if log_config.enable_file_logging:
            from logging.handlers import RotatingFileHandler
            
            file_handler = RotatingFileHandler(
                log_config.log_file_path,
                maxBytes=log_config.max_log_size_mb * 1024 * 1024,
                backupCount=log_config.backup_count
            )
            file_handler.setLevel(getattr(logging, log_config.file_log_level))
            file_formatter = logging.Formatter(log_config.file_format)
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
    
    def __str__(self):
        """String representation"""
        return f"ConfigManager(file={self._config_file_path})"
    
    def __repr__(self):
        """Detailed representation"""
        return f"ConfigManager(global={self.global_config}, attack={self.attack_config})"