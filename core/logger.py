"""
Advanced logging system for FsocietyDDoS
"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class SecurityLogger:
    """Security-focused logger with anti-forensics capabilities"""
    
    def __init__(self, name: str = "fsociety", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Anti-forensics settings (set before creating loggers)
        self.stealth_mode = False
        self.memory_only = False
        self.obfuscate_logs = False
        
        # Create separate loggers for different purposes
        self.loggers = {
            'main': self._create_logger('main'),
            'attack': self._create_logger('attack'),
            'security': self._create_logger('security'),
            'network': self._create_logger('network'),
            'error': self._create_logger('error')
        }
    
    def _create_logger(self, logger_type: str) -> logging.Logger:
        """Create a logger with appropriate handlers"""
        logger = logging.getLogger(f"{self.name}.{logger_type}")
        logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler (if not in memory-only mode)
        if not self.memory_only:
            log_file = self.log_dir / f"{logger_type}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def enable_stealth_mode(self):
        """Enable stealth logging mode"""
        self.stealth_mode = True
        self.memory_only = True
        
        # Reconfigure loggers for stealth
        for logger_name, logger in self.loggers.items():
            # Remove file handlers
            logger.handlers = [h for h in logger.handlers if not isinstance(h, logging.FileHandler)]
            
            # Reduce console logging
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.setLevel(logging.WARNING)
    
    def enable_obfuscation(self):
        """Enable log obfuscation"""
        self.obfuscate_logs = True
    
    def _obfuscate_message(self, message: str) -> str:
        """Obfuscate sensitive information in log messages"""
        if not self.obfuscate_logs:
            return message
        
        # Replace IP addresses
        import re
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        message = re.sub(ip_pattern, 'XXX.XXX.XXX.XXX', message)
        
        # Replace URLs
        url_pattern = r'https?://[^\s]+'
        message = re.sub(url_pattern, 'http://REDACTED', message)
        
        return message
    
    def log(self, level: LogLevel, message: str, logger_type: str = 'main', **kwargs):
        """Log a message with specified level"""
        if self.stealth_mode and level.value < logging.WARNING.value:
            return
        
        logger = self.loggers.get(logger_type, self.loggers['main'])
        message = self._obfuscate_message(message)
        
        # Add context information
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            message = f"{message} | {context}"
        
        logger.log(level.value, message)
    
    def debug(self, message: str, logger_type: str = 'main', **kwargs):
        """Log debug message"""
        self.log(LogLevel.DEBUG, message, logger_type, **kwargs)
    
    def info(self, message: str, logger_type: str = 'main', **kwargs):
        """Log info message"""
        self.log(LogLevel.INFO, message, logger_type, **kwargs)
    
    def warning(self, message: str, logger_type: str = 'main', **kwargs):
        """Log warning message"""
        self.log(LogLevel.WARNING, message, logger_type, **kwargs)
    
    def error(self, message: str, logger_type: str = 'error', **kwargs):
        """Log error message"""
        self.log(LogLevel.ERROR, message, logger_type, **kwargs)
    
    def critical(self, message: str, logger_type: str = 'error', **kwargs):
        """Log critical message"""
        self.log(LogLevel.CRITICAL, message, logger_type, **kwargs)
    
    def attack_log(self, message: str, **kwargs):
        """Log attack-related message"""
        self.info(message, 'attack', **kwargs)
    
    def security_log(self, message: str, **kwargs):
        """Log security-related message"""
        self.info(message, 'security', **kwargs)
    
    def network_log(self, message: str, **kwargs):
        """Log network-related message"""
        self.info(message, 'network', **kwargs)
    
    def clear_logs(self):
        """Clear all log files (anti-forensics)"""
        if self.stealth_mode:
            for log_file in self.log_dir.glob("*.log*"):
                try:
                    log_file.unlink()
                except Exception:
                    pass
    
    def secure_delete_logs(self):
        """Securely delete log files"""
        for log_file in self.log_dir.glob("*.log*"):
            try:
                # Overwrite file with random data multiple times
                if log_file.exists():
                    file_size = log_file.stat().st_size
                    with open(log_file, 'r+b') as f:
                        for _ in range(3):  # 3 passes
                            f.seek(0)
                            f.write(os.urandom(file_size))
                            f.flush()
                            os.fsync(f.fileno())
                    
                    log_file.unlink()
            except Exception:
                pass


class ColoredFormatter(logging.Formatter):
    """Colored console formatter"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to level name
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{level_color}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


# Global logger instance
logger = SecurityLogger()