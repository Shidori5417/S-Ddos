"""
Utility functions for FsocietyDDoS
"""

import os
import sys
import time
import random
import socket
import struct
import hashlib
import platform
import subprocess
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import threading
import queue
import ipaddress
from urllib.parse import urlparse


class NetworkUtils:
    """Network utility functions"""
    
    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """Check if IP address is valid"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_port(port: Union[str, int]) -> bool:
        """Check if port is valid"""
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def resolve_hostname(hostname: str) -> Optional[str]:
        """Resolve hostname to IP address"""
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror:
            return None
    
    @staticmethod
    def get_local_ip() -> str:
        """Get local IP address"""
        try:
            # Connect to a remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
    
    @staticmethod
    def check_port_open(host: str, port: int, timeout: float = 3.0) -> bool:
        """Check if port is open on host"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                return result == 0
        except Exception:
            return False
    
    @staticmethod
    def get_random_port() -> int:
        """Get random available port"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    @staticmethod
    def parse_target(target: str) -> Tuple[str, int]:
        """Parse target string to host and port"""
        if '://' in target:
            parsed = urlparse(target)
            host = parsed.hostname or parsed.netloc
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        elif ':' in target:
            parts = target.rsplit(':', 1)
            host = parts[0]
            try:
                port = int(parts[1])
            except ValueError:
                port = 80
        else:
            host = target
            port = 80
        
        return host, port
    
    @staticmethod
    def generate_random_ip() -> str:
        """Generate random IP address"""
        return ".".join([str(random.randint(1, 254)) for _ in range(4)])
    
    @staticmethod
    def get_network_interfaces() -> List[Dict[str, str]]:
        """Get network interfaces information"""
        interfaces = []
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['ipconfig'], capture_output=True, text=True)
                # Parse Windows ipconfig output
                # This is a simplified version
                interfaces.append({
                    'name': 'default',
                    'ip': NetworkUtils.get_local_ip(),
                    'status': 'active'
                })
            else:
                result = subprocess.run(['ifconfig'], capture_output=True, text=True)
                # Parse Unix ifconfig output
                interfaces.append({
                    'name': 'default',
                    'ip': NetworkUtils.get_local_ip(),
                    'status': 'active'
                })
        except Exception:
            interfaces.append({
                'name': 'default',
                'ip': NetworkUtils.get_local_ip(),
                'status': 'unknown'
            })
        
        return interfaces


class SystemUtils:
    """System utility functions"""
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get system information"""
        return {
            'platform': platform.system(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'hostname': platform.node(),
            'user': os.getenv('USER') or os.getenv('USERNAME', 'unknown')
        }
    
    @staticmethod
    def is_admin() -> bool:
        """Check if running with admin privileges"""
        try:
            if platform.system() == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except Exception:
            return False
    
    @staticmethod
    def get_cpu_count() -> int:
        """Get CPU core count"""
        return os.cpu_count() or 1
    
    @staticmethod
    def get_memory_info() -> Dict[str, int]:
        """Get memory information"""
        try:
            if platform.system() == "Windows":
                import psutil
                memory = psutil.virtual_memory()
                return {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percentage': memory.percent
                }
        except ImportError:
            pass
        
        # Fallback for systems without psutil
        return {
            'total': 0,
            'available': 0,
            'used': 0,
            'percentage': 0
        }
    
    @staticmethod
    def clear_screen():
        """Clear terminal screen"""
        os.system('cls' if platform.system() == "Windows" else 'clear')
    
    @staticmethod
    def set_terminal_title(title: str):
        """Set terminal window title"""
        if platform.system() == "Windows":
            os.system(f'title {title}')
        else:
            sys.stdout.write(f'\033]0;{title}\007')
            sys.stdout.flush()


class CryptoUtils:
    """Cryptographic utility functions"""
    
    @staticmethod
    def generate_random_string(length: int = 16) -> str:
        """Generate random string"""
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_random_bytes(length: int = 16) -> bytes:
        """Generate random bytes"""
        return os.urandom(length)
    
    @staticmethod
    def hash_string(data: str, algorithm: str = 'sha256') -> str:
        """Hash string with specified algorithm"""
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(data.encode('utf-8'))
        return hash_obj.hexdigest()
    
    @staticmethod
    def xor_encrypt(data: bytes, key: bytes) -> bytes:
        """XOR encryption/decryption"""
        return bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1)))
    
    @staticmethod
    def simple_obfuscate(text: str) -> str:
        """Simple text obfuscation"""
        key = random.randint(1, 255)
        obfuscated = ''.join(chr(ord(c) ^ key) for c in text)
        return f"{key:02x}{obfuscated.encode('latin-1').hex()}"
    
    @staticmethod
    def simple_deobfuscate(obfuscated: str) -> str:
        """Simple text deobfuscation"""
        try:
            key = int(obfuscated[:2], 16)
            data = bytes.fromhex(obfuscated[2:]).decode('latin-1')
            return ''.join(chr(ord(c) ^ key) for c in data)
        except Exception:
            return ""


class FileUtils:
    """File utility functions"""
    
    @staticmethod
    def ensure_directory(path: Union[str, Path]):
        """Ensure directory exists"""
        Path(path).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def read_file_lines(filepath: Union[str, Path]) -> List[str]:
        """Read file lines"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception:
            return []
    
    @staticmethod
    def write_file_lines(filepath: Union[str, Path], lines: List[str]):
        """Write lines to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(f"{line}\n")
    
    @staticmethod
    def append_file_line(filepath: Union[str, Path], line: str):
        """Append line to file"""
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"{line}\n")
    
    @staticmethod
    def get_file_size(filepath: Union[str, Path]) -> int:
        """Get file size in bytes"""
        try:
            return Path(filepath).stat().st_size
        except Exception:
            return 0
    
    @staticmethod
    def secure_delete_file(filepath: Union[str, Path]):
        """Securely delete file"""
        try:
            path = Path(filepath)
            if path.exists():
                # Overwrite with random data
                file_size = path.stat().st_size
                with open(path, 'r+b') as f:
                    for _ in range(3):  # 3 passes
                        f.seek(0)
                        f.write(os.urandom(file_size))
                        f.flush()
                        os.fsync(f.fileno())
                
                path.unlink()
        except Exception:
            pass


class ThreadUtils:
    """Threading utility functions"""
    
    @staticmethod
    def run_with_timeout(func, args=(), kwargs=None, timeout=30):
        """Run function with timeout"""
        if kwargs is None:
            kwargs = {}
        
        result_queue = queue.Queue()
        exception_queue = queue.Queue()
        
        def target():
            try:
                result = func(*args, **kwargs)
                result_queue.put(result)
            except Exception as e:
                exception_queue.put(e)
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            # Thread is still running, timeout occurred
            return None, TimeoutError("Function execution timed out")
        
        if not exception_queue.empty():
            return None, exception_queue.get()
        
        if not result_queue.empty():
            return result_queue.get(), None
        
        return None, Exception("Unknown error occurred")
    
    @staticmethod
    def create_thread_pool(target_func, args_list: List[tuple], max_threads: int = 10):
        """Create and manage thread pool"""
        threads = []
        results = []
        
        def worker(args, index):
            try:
                result = target_func(*args)
                results.append((index, result))
            except Exception as e:
                results.append((index, e))
        
        # Create threads
        for i, args in enumerate(args_list[:max_threads]):
            thread = threading.Thread(target=worker, args=(args, i))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        return results


class ValidationUtils:
    """Validation utility functions"""
    
    @staticmethod
    def validate_target(target: str) -> bool:
        """Validate target format"""
        try:
            host, port = NetworkUtils.parse_target(target)
            return bool(host) and NetworkUtils.is_valid_port(port)
        except Exception:
            return False
    
    @staticmethod
    def validate_proxy(proxy: str) -> bool:
        """Validate proxy format"""
        try:
            if '://' in proxy:
                parsed = urlparse(proxy)
                return bool(parsed.hostname and parsed.port)
            elif ':' in proxy:
                host, port = proxy.rsplit(':', 1)
                return NetworkUtils.is_valid_ip(host) and NetworkUtils.is_valid_port(port)
            return False
        except Exception:
            return False
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file operations"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename[:255]  # Limit length
    
    @staticmethod
    def validate_config_value(value: Any, expected_type: type, min_val=None, max_val=None) -> bool:
        """Validate configuration value"""
        try:
            if not isinstance(value, expected_type):
                return False
            
            if min_val is not None and value < min_val:
                return False
            
            if max_val is not None and value > max_val:
                return False
            
            return True
        except Exception:
            return False


# Convenience functions
def get_timestamp() -> str:
    """Get current timestamp string"""
    return time.strftime("%Y-%m-%d %H:%M:%S")

def sleep_random(min_seconds: float = 0.1, max_seconds: float = 1.0):
    """Sleep for random duration"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def format_bytes(bytes_count: int) -> str:
    """Format bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.2f} PB"

def format_duration(seconds: float) -> str:
    """Format duration to human readable string"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"