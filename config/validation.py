"""
Configuration Validation
Comprehensive validation system for all configuration settings
"""

import re
import socket
import ipaddress
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse
import logging


class ValidationError(Exception):
    """Configuration validation error"""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(message)


class ConfigValidator:
    """Configuration validator with comprehensive checks"""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        
        # Validation rules
        self.port_range = (1, 65535)
        self.thread_limits = (1, 1000)
        self.timeout_limits = (1, 3600)
        self.memory_limits = (64, 8192)  # MB
        self.rate_limits = (1, 10000)
        
        # Valid protocols
        self.valid_protocols = {'tcp', 'udp', 'icmp'}
        self.valid_http_methods = {'GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH'}
        self.valid_log_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        self.valid_attack_layers = {'layer4', 'layer7'}
        
        # Regex patterns
        self.ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        self.domain_pattern = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$')
        self.url_pattern = re.compile(r'^https?://[^\s/$.?#].[^\s]*$')
    
    def validate_global_config(self, config) -> List[ValidationError]:
        """Validate global configuration"""
        errors = []
        
        try:
            # Thread validation
            if not self._is_in_range(config.max_threads, self.thread_limits):
                errors.append(ValidationError(
                    f"max_threads must be between {self.thread_limits[0]} and {self.thread_limits[1]}",
                    "max_threads", config.max_threads
                ))
            
            if not self._is_in_range(config.thread_pool_size, (1, config.max_threads)):
                errors.append(ValidationError(
                    f"thread_pool_size must be between 1 and {config.max_threads}",
                    "thread_pool_size", config.thread_pool_size
                ))
            
            # Memory validation
            if not self._is_in_range(config.memory_limit_mb, self.memory_limits):
                errors.append(ValidationError(
                    f"memory_limit_mb must be between {self.memory_limits[0]} and {self.memory_limits[1]}",
                    "memory_limit_mb", config.memory_limit_mb
                ))
            
            # CPU validation
            if not self._is_in_range(config.cpu_limit_percent, (1, 100)):
                errors.append(ValidationError(
                    "cpu_limit_percent must be between 1 and 100",
                    "cpu_limit_percent", config.cpu_limit_percent
                ))
            
            # Timeout validation
            timeouts = [
                ('connection_timeout', config.connection_timeout),
                ('read_timeout', config.read_timeout),
                ('operation_timeout', config.operation_timeout)
            ]
            
            for name, value in timeouts:
                if not self._is_in_range(value, self.timeout_limits):
                    errors.append(ValidationError(
                        f"{name} must be between {self.timeout_limits[0]} and {self.timeout_limits[1]}",
                        name, value
                    ))
            
        except Exception as e:
            errors.append(ValidationError(f"Global config validation error: {e}"))
        
        return errors
    
    def validate_attack_config(self, config) -> List[ValidationError]:
        """Validate attack configuration"""
        errors = []
        
        try:
            # Target validation
            if not config.target_url and not config.target_ip:
                errors.append(ValidationError(
                    "Either target_url or target_ip must be specified",
                    "target"
                ))
            
            if config.target_url:
                if not self._is_valid_url(config.target_url):
                    errors.append(ValidationError(
                        "Invalid target URL format",
                        "target_url", config.target_url
                    ))
            
            if config.target_ip:
                if not self._is_valid_ip(config.target_ip):
                    errors.append(ValidationError(
                        "Invalid target IP address",
                        "target_ip", config.target_ip
                    ))
            
            # Port validation
            if not self._is_in_range(config.target_port, self.port_range):
                errors.append(ValidationError(
                    f"target_port must be between {self.port_range[0]} and {self.port_range[1]}",
                    "target_port", config.target_port
                ))
            
            # Thread validation
            if not self._is_in_range(config.threads, self.thread_limits):
                errors.append(ValidationError(
                    f"threads must be between {self.thread_limits[0]} and {self.thread_limits[1]}",
                    "threads", config.threads
                ))
            
            # Rate validation
            if not self._is_in_range(config.requests_per_second, self.rate_limits):
                errors.append(ValidationError(
                    f"requests_per_second must be between {self.rate_limits[0]} and {self.rate_limits[1]}",
                    "requests_per_second", config.requests_per_second
                ))
            
            # Duration validation
            if config.duration_seconds < 1:
                errors.append(ValidationError(
                    "duration_seconds must be at least 1",
                    "duration_seconds", config.duration_seconds
                ))
            
            # Protocol validation
            if config.attack_layer not in self.valid_attack_layers:
                errors.append(ValidationError(
                    f"attack_layer must be one of: {', '.join(self.valid_attack_layers)}",
                    "attack_layer", config.attack_layer
                ))
            
            if config.protocol not in self.valid_protocols:
                errors.append(ValidationError(
                    f"protocol must be one of: {', '.join(self.valid_protocols)}",
                    "protocol", config.protocol
                ))
            
            # HTTP method validation
            if config.http_method not in self.valid_http_methods:
                errors.append(ValidationError(
                    f"http_method must be one of: {', '.join(self.valid_http_methods)}",
                    "http_method", config.http_method
                ))
            
            # Proxy validation
            if config.use_proxies and config.proxy_list:
                for i, proxy in enumerate(config.proxy_list):
                    if not self._is_valid_proxy(proxy):
                        errors.append(ValidationError(
                            f"Invalid proxy format at index {i}",
                            "proxy_list", proxy
                        ))
            
            # Source port range validation
            if len(config.source_port_range) != 2:
                errors.append(ValidationError(
                    "source_port_range must be a tuple of (min_port, max_port)",
                    "source_port_range", config.source_port_range
                ))
            else:
                min_port, max_port = config.source_port_range
                if not self._is_in_range(min_port, self.port_range) or not self._is_in_range(max_port, self.port_range):
                    errors.append(ValidationError(
                        f"source_port_range values must be between {self.port_range[0]} and {self.port_range[1]}",
                        "source_port_range", config.source_port_range
                    ))
                if min_port >= max_port:
                    errors.append(ValidationError(
                        "source_port_range min_port must be less than max_port",
                        "source_port_range", config.source_port_range
                    ))
            
        except Exception as e:
            errors.append(ValidationError(f"Attack config validation error: {e}"))
        
        return errors
    
    def validate_security_config(self, config) -> List[ValidationError]:
        """Validate security configuration"""
        errors = []
        
        try:
            # Delay range validation
            if len(config.delay_range) != 2:
                errors.append(ValidationError(
                    "delay_range must be a tuple of (min_delay, max_delay)",
                    "delay_range", config.delay_range
                ))
            else:
                min_delay, max_delay = config.delay_range
                if min_delay < 0 or max_delay < 0:
                    errors.append(ValidationError(
                        "delay_range values must be non-negative",
                        "delay_range", config.delay_range
                    ))
                if min_delay >= max_delay:
                    errors.append(ValidationError(
                        "delay_range min_delay must be less than max_delay",
                        "delay_range", config.delay_range
                    ))
            
            # Jitter factor validation
            if not self._is_in_range(config.jitter_factor, (0.0, 1.0)):
                errors.append(ValidationError(
                    "jitter_factor must be between 0.0 and 1.0",
                    "jitter_factor", config.jitter_factor
                ))
            
            # Fragment threshold validation
            if config.fragment_threshold < 64 or config.fragment_threshold > 65535:
                errors.append(ValidationError(
                    "fragment_threshold must be between 64 and 65535",
                    "fragment_threshold", config.fragment_threshold
                ))
            
            # Encryption algorithm validation
            valid_algorithms = ['AES-128', 'AES-192', 'AES-256', 'ChaCha20']
            if config.encryption_algorithm not in valid_algorithms:
                errors.append(ValidationError(
                    f"encryption_algorithm must be one of: {', '.join(valid_algorithms)}",
                    "encryption_algorithm", config.encryption_algorithm
                ))
            
        except Exception as e:
            errors.append(ValidationError(f"Security config validation error: {e}"))
        
        return errors
    
    def validate_network_config(self, config) -> List[ValidationError]:
        """Validate network configuration"""
        errors = []
        
        try:
            # Connection validation
            if config.max_connections < 1:
                errors.append(ValidationError(
                    "max_connections must be at least 1",
                    "max_connections", config.max_connections
                ))
            
            if config.connection_pool_size < 1 or config.connection_pool_size > config.max_connections:
                errors.append(ValidationError(
                    f"connection_pool_size must be between 1 and {config.max_connections}",
                    "connection_pool_size", config.connection_pool_size
                ))
            
            # Retry validation
            if config.max_retries < 0:
                errors.append(ValidationError(
                    "max_retries must be non-negative",
                    "max_retries", config.max_retries
                ))
            
            if config.retry_delay < 0:
                errors.append(ValidationError(
                    "retry_delay must be non-negative",
                    "retry_delay", config.retry_delay
                ))
            
            if config.backoff_factor < 1.0:
                errors.append(ValidationError(
                    "backoff_factor must be at least 1.0",
                    "backoff_factor", config.backoff_factor
                ))
            
            # Bandwidth validation
            if config.bandwidth_limit_mbps is not None and config.bandwidth_limit_mbps < 1:
                errors.append(ValidationError(
                    "bandwidth_limit_mbps must be at least 1",
                    "bandwidth_limit_mbps", config.bandwidth_limit_mbps
                ))
            
            # DNS validation
            for i, dns_server in enumerate(config.custom_dns_servers):
                if not self._is_valid_ip(dns_server):
                    errors.append(ValidationError(
                        f"Invalid DNS server IP at index {i}",
                        "custom_dns_servers", dns_server
                    ))
            
            if not self._is_in_range(config.dns_timeout, (1, 60)):
                errors.append(ValidationError(
                    "dns_timeout must be between 1 and 60 seconds",
                    "dns_timeout", config.dns_timeout
                ))
            
            # Source IP range validation
            if config.source_ip_range:
                if not self._is_valid_ip_range(config.source_ip_range):
                    errors.append(ValidationError(
                        "Invalid source IP range format",
                        "source_ip_range", config.source_ip_range
                    ))
            
        except Exception as e:
            errors.append(ValidationError(f"Network config validation error: {e}"))
        
        return errors
    
    def validate_logging_config(self, config) -> List[ValidationError]:
        """Validate logging configuration"""
        errors = []
        
        try:
            # Log level validation
            log_levels = [
                ('log_level', config.log_level),
                ('console_log_level', config.console_log_level),
                ('file_log_level', config.file_log_level)
            ]
            
            for name, level in log_levels:
                if level not in self.valid_log_levels:
                    errors.append(ValidationError(
                        f"{name} must be one of: {', '.join(self.valid_log_levels)}",
                        name, level
                    ))
            
            # File size validation
            if config.max_log_size_mb < 1:
                errors.append(ValidationError(
                    "max_log_size_mb must be at least 1",
                    "max_log_size_mb", config.max_log_size_mb
                ))
            
            if config.backup_count < 0:
                errors.append(ValidationError(
                    "backup_count must be non-negative",
                    "backup_count", config.backup_count
                ))
            
            # Metrics interval validation
            if config.metrics_interval < 1:
                errors.append(ValidationError(
                    "metrics_interval must be at least 1 second",
                    "metrics_interval", config.metrics_interval
                ))
            
            # Remote logging validation
            if config.enable_remote_logging:
                if not config.remote_log_server:
                    errors.append(ValidationError(
                        "remote_log_server must be specified when remote logging is enabled",
                        "remote_log_server"
                    ))
                elif not self._is_valid_ip(config.remote_log_server) and not self._is_valid_domain(config.remote_log_server):
                    errors.append(ValidationError(
                        "Invalid remote log server address",
                        "remote_log_server", config.remote_log_server
                    ))
                
                if not self._is_in_range(config.remote_log_port, self.port_range):
                    errors.append(ValidationError(
                        f"remote_log_port must be between {self.port_range[0]} and {self.port_range[1]}",
                        "remote_log_port", config.remote_log_port
                    ))
            
        except Exception as e:
            errors.append(ValidationError(f"Logging config validation error: {e}"))
        
        return errors
    
    def validate_full_config(self, config_manager) -> List[ValidationError]:
        """Validate complete configuration"""
        all_errors = []
        
        # Validate individual sections
        all_errors.extend(self.validate_global_config(config_manager.global_config))
        all_errors.extend(self.validate_attack_config(config_manager.attack_config))
        all_errors.extend(self.validate_security_config(config_manager.security_config))
        all_errors.extend(self.validate_network_config(config_manager.network_config))
        all_errors.extend(self.validate_logging_config(config_manager.logging_config))
        
        # Cross-section validation
        all_errors.extend(self._validate_cross_section(config_manager))
        
        return all_errors
    
    def _validate_cross_section(self, config_manager) -> List[ValidationError]:
        """Validate cross-section dependencies"""
        errors = []
        
        try:
            global_cfg = config_manager.global_config
            attack_cfg = config_manager.attack_config
            network_cfg = config_manager.network_config
            
            # Thread consistency
            if attack_cfg.threads > global_cfg.max_threads:
                errors.append(ValidationError(
                    f"Attack threads ({attack_cfg.threads}) exceeds global max_threads ({global_cfg.max_threads})",
                    "threads_consistency"
                ))
            
            # Connection consistency
            if network_cfg.connection_pool_size > network_cfg.max_connections:
                errors.append(ValidationError(
                    f"Connection pool size ({network_cfg.connection_pool_size}) exceeds max_connections ({network_cfg.max_connections})",
                    "connection_consistency"
                ))
            
            # Resource limits
            estimated_memory = attack_cfg.threads * 10  # Rough estimate: 10MB per thread
            if estimated_memory > global_cfg.memory_limit_mb:
                errors.append(ValidationError(
                    f"Estimated memory usage ({estimated_memory}MB) exceeds limit ({global_cfg.memory_limit_mb}MB)",
                    "memory_consistency"
                ))
            
            # Attack layer consistency
            if attack_cfg.attack_layer == "layer4" and attack_cfg.attack_type in ["http_flood", "slowloris"]:
                errors.append(ValidationError(
                    f"Attack type '{attack_cfg.attack_type}' is not compatible with layer4",
                    "layer_consistency"
                ))
            
            if attack_cfg.attack_layer == "layer7" and attack_cfg.attack_type in ["tcp_flood", "udp_flood"]:
                errors.append(ValidationError(
                    f"Attack type '{attack_cfg.attack_type}' is not compatible with layer7",
                    "layer_consistency"
                ))
            
        except Exception as e:
            errors.append(ValidationError(f"Cross-section validation error: {e}"))
        
        return errors
    
    def _is_in_range(self, value: Any, range_tuple: Tuple[Any, Any]) -> bool:
        """Check if value is in range"""
        try:
            return range_tuple[0] <= value <= range_tuple[1]
        except (TypeError, ValueError):
            return False
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Validate domain name"""
        if not domain or len(domain) > 253:
            return False
        return bool(self.domain_pattern.match(domain))
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _is_valid_proxy(self, proxy: str) -> bool:
        """Validate proxy format"""
        try:
            # Support formats: ip:port, user:pass@ip:port, protocol://ip:port
            if '://' in proxy:
                parsed = urlparse(proxy)
                return bool(parsed.hostname and parsed.port)
            elif '@' in proxy:
                auth, address = proxy.rsplit('@', 1)
                return ':' in address and self._is_valid_ip(address.split(':')[0])
            else:
                parts = proxy.split(':')
                return len(parts) == 2 and self._is_valid_ip(parts[0]) and parts[1].isdigit()
        except Exception:
            return False
    
    def _is_valid_ip_range(self, ip_range: str) -> bool:
        """Validate IP range (CIDR notation)"""
        try:
            ipaddress.ip_network(ip_range, strict=False)
            return True
        except ValueError:
            return False


def validate_config(config_manager) -> Tuple[bool, List[ValidationError]]:
    """Validate configuration and return results"""
    validator = ConfigValidator()
    errors = validator.validate_full_config(config_manager)
    return len(errors) == 0, errors


def validate_target(target: str) -> bool:
    """Quick target validation"""
    validator = ConfigValidator()
    
    # Check if it's a valid URL
    if validator._is_valid_url(target):
        return True
    
    # Check if it's a valid IP
    if validator._is_valid_ip(target):
        return True
    
    # Check if it's a valid domain
    if validator._is_valid_domain(target):
        return True
    
    return False


def get_validation_summary(errors: List[ValidationError]) -> Dict[str, Any]:
    """Get validation summary"""
    if not errors:
        return {
            'valid': True,
            'error_count': 0,
            'errors_by_category': {},
            'critical_errors': []
        }
    
    errors_by_category = {}
    critical_errors = []
    
    for error in errors:
        category = error.field.split('_')[0] if error.field else 'general'
        if category not in errors_by_category:
            errors_by_category[category] = []
        errors_by_category[category].append(error.message)
        
        # Mark critical errors
        if any(keyword in error.message.lower() for keyword in ['must', 'required', 'invalid']):
            critical_errors.append(error.message)
    
    return {
        'valid': False,
        'error_count': len(errors),
        'errors_by_category': errors_by_category,
        'critical_errors': critical_errors
    }