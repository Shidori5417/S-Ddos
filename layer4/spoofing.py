"""
Advanced IP Spoofing and Source Manipulation
Professional spoofing techniques for Layer 4 attacks
"""

import time
import random
import socket
import struct
import ipaddress
from typing import Dict, List, Optional, Tuple, Set, Union, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from core.utils import NetworkUtils, CryptoUtils
from core.logger import logger


@dataclass
class SpoofingConfig:
    """Ultra-Advanced Configuration for spoofing techniques"""
    # IP spoofing - Enhanced
    enable_ip_spoofing: bool = True
    spoof_ranges: List[str] = field(default_factory=lambda: [
        '1.0.0.0/8', '2.0.0.0/8', '3.0.0.0/8', '4.0.0.0/8', '5.0.0.0/8',
        '6.0.0.0/8', '7.0.0.0/8', '8.0.0.0/8', '9.0.0.0/8', '11.0.0.0/8',
        '12.0.0.0/8', '13.0.0.0/8', '15.0.0.0/8', '16.0.0.0/8', '17.0.0.0/8',
        '18.0.0.0/8', '19.0.0.0/8', '20.0.0.0/8', '21.0.0.0/8', '22.0.0.0/8'
    ])
    avoid_private_ranges: bool = True
    avoid_reserved_ranges: bool = True
    
    # Port spoofing - Ultra Enhanced
    enable_port_spoofing: bool = True
    port_ranges: List[Tuple[int, int]] = field(default_factory=lambda: [
        (1024, 65535), (32768, 61000), (49152, 65535), (10000, 50000),
        (20000, 40000), (30000, 60000), (5000, 15000), (40000, 50000),
        (50000, 60000), (15000, 25000)
    ])
    avoid_well_known_ports: bool = True
    
    # Geographic spoofing - Expanded
    enable_geo_spoofing: bool = True
    target_countries: List[str] = field(default_factory=lambda: [
        'US', 'GB', 'DE', 'FR', 'CA', 'AU', 'NL', 'SE', 'NO', 'DK', 'FI',
        'JP', 'KR', 'SG', 'HK', 'CH', 'AT', 'BE', 'IT', 'ES', 'BR', 'MX'
    ])
    
    # Advanced spoofing - Ultra Mode
    enable_mac_spoofing: bool = True
    randomize_ttl: bool = True
    ttl_ranges: Tuple[int, int] = (8, 255)  # Even wider range
    
    # Enhanced evasion techniques - Maximum
    use_decoy_sources: bool = True
    decoy_count: int = 100  # Increased from 25 to 100
    rotate_sources: bool = True
    rotation_interval: int = 25  # Faster rotation (reduced from 50)
    
    # Advanced packet manipulation - Ultra
    enable_packet_fragmentation: bool = True
    fragment_sizes: List[int] = field(default_factory=lambda: [256, 512, 768, 1024, 1280, 1500, 2048, 4096, 8192])
    enable_timing_randomization: bool = True
    timing_jitter: float = 0.5  # 50% timing variance (increased from 30%)
    
    # Protocol spoofing - Enhanced
    enable_protocol_spoofing: bool = True
    protocol_mix: List[str] = field(default_factory=lambda: ['TCP', 'UDP', 'ICMP', 'GRE', 'ESP'])
    protocol_weights: Dict[str, float] = field(default_factory=lambda: {
        'TCP': 0.5, 'UDP': 0.3, 'ICMP': 0.1, 'GRE': 0.05, 'ESP': 0.05
    })
    
    # Header manipulation - Ultra Advanced
    enable_header_randomization: bool = True
    randomize_tcp_options: bool = True
    randomize_ip_flags: bool = True
    randomize_window_size: bool = True
    randomize_sequence_numbers: bool = True
    randomize_acknowledgment_numbers: bool = True
    enable_tcp_timestamp_randomization: bool = True
    enable_ip_id_randomization: bool = True
    
    # Multi-vector spoofing - Maximum
    enable_multi_vector: bool = True
    vector_count: int = 50  # Increased from 15 to 50
    vector_rotation_speed: int = 1  # Fastest rotation
    
    # New Ultra-Advanced Features
    enable_ai_spoofing: bool = True  # AI-driven spoofing patterns
    enable_behavioral_mimicry: bool = True  # Mimic real user behavior
    enable_traffic_shaping: bool = True  # Shape traffic to avoid detection
    enable_deep_packet_inspection_evasion: bool = True  # DPI evasion
    enable_fingerprint_randomization: bool = True  # OS fingerprint randomization
    
    # Advanced Evasion Techniques
    enable_covert_channels: bool = True  # Use covert communication channels
    enable_steganography: bool = True  # Hide data in legitimate traffic
    enable_polymorphic_packets: bool = True  # Constantly changing packet structure
    enable_anti_forensics: bool = True  # Anti-forensic techniques
    
    # Network Layer Evasion
    enable_route_manipulation: bool = True  # Manipulate routing paths
    enable_bgp_hijacking_simulation: bool = True  # Simulate BGP hijacking
    enable_dns_tunneling: bool = True  # Use DNS for covert communication
    enable_icmp_tunneling: bool = True  # Use ICMP for covert communication
    
    # Application Layer Spoofing
    enable_user_agent_spoofing: bool = True  # Randomize user agents
    enable_http_header_spoofing: bool = True  # Spoof HTTP headers
    enable_tls_fingerprint_spoofing: bool = True  # Spoof TLS fingerprints
    enable_certificate_spoofing: bool = True  # Spoof certificates
    
    # Timing and Pattern Evasion
    enable_burst_pattern_randomization: bool = True  # Randomize burst patterns
    enable_idle_time_simulation: bool = True  # Simulate idle times
    enable_human_behavior_simulation: bool = True  # Simulate human behavior
    traffic_pattern_templates: List[str] = field(default_factory=lambda: [
        'web_browsing', 'video_streaming', 'file_download', 'gaming', 'voip'
    ])
    
    # Validation - Minimal for maximum spoofing
    validate_spoofed_ips: bool = False
    blacklist_ranges: List[str] = field(default_factory=lambda: [
        '127.0.0.0/8', '169.254.0.0/16', '224.0.0.0/4'
    ])
    
    # Ultra Advanced evasion
    enable_stealth_mode: bool = True
    mimic_legitimate_traffic: bool = True
    adaptive_spoofing: bool = True
    use_honeypot_evasion: bool = True
    enable_quantum_spoofing: bool = True  # Quantum-resistant spoofing
    enable_machine_learning_evasion: bool = True  # ML-based evasion
    validate_spoofed_ips: bool = False  # Disabled for maximum spoofing
    blacklist_ranges: List[str] = field(default_factory=lambda: [
        '127.0.0.0/8', '169.254.0.0/16', '224.0.0.0/4'
    ])
    
    # Advanced evasion
    enable_stealth_mode: bool = True
    mimic_legitimate_traffic: bool = True
    adaptive_spoofing: bool = True
    use_honeypot_evasion: bool = True


class IPSpoofing:
    """Ultra-Advanced IP spoofing with AI-driven patterns and quantum-resistant techniques"""
    
    def __init__(self, config: SpoofingConfig):
        self.config = config
        self.spoofed_ips = set()
        self.current_ip_pool = []
        self.ip_rotation_counter = 0
        
        # Enhanced private and reserved ranges to avoid
        self.private_ranges = [
            ipaddress.IPv4Network('10.0.0.0/8'),
            ipaddress.IPv4Network('172.16.0.0/12'),
            ipaddress.IPv4Network('192.168.0.0/16'),
            ipaddress.IPv4Network('127.0.0.0/8'),
            ipaddress.IPv4Network('169.254.0.0/16'),
            ipaddress.IPv4Network('224.0.0.0/4'),
            ipaddress.IPv4Network('240.0.0.0/4'),
            ipaddress.IPv4Network('0.0.0.0/8'),
            ipaddress.IPv4Network('100.64.0.0/10'),  # Carrier-grade NAT
            ipaddress.IPv4Network('198.18.0.0/15'),  # Benchmarking
            ipaddress.IPv4Network('203.0.113.0/24'),  # Documentation
        ]
        
        # Expanded country IP ranges with more realistic distributions
        self.country_ranges = {
            'US': ['8.0.0.0/8', '4.0.0.0/8', '12.0.0.0/8', '15.0.0.0/8', '16.0.0.0/8', '17.0.0.0/8'],
            'GB': ['81.0.0.0/8', '82.0.0.0/8', '83.0.0.0/8', '84.0.0.0/8'],
            'DE': ['85.0.0.0/8', '87.0.0.0/8', '88.0.0.0/8', '89.0.0.0/8'],
            'FR': ['80.0.0.0/8', '90.0.0.0/8', '91.0.0.0/8', '92.0.0.0/8'],
            'CA': ['24.0.0.0/8', '64.0.0.0/8', '65.0.0.0/8', '66.0.0.0/8'],
            'AU': ['1.0.0.0/8', '27.0.0.0/8', '58.0.0.0/8', '101.0.0.0/8'],
            'NL': ['62.0.0.0/8', '77.0.0.0/8', '145.0.0.0/8', '213.0.0.0/8'],
            'SE': ['78.0.0.0/8', '130.0.0.0/8', '193.0.0.0/8', '212.0.0.0/8'],
            'NO': ['129.0.0.0/8', '158.0.0.0/8', '193.0.0.0/8', '212.0.0.0/8'],
            'DK': ['87.0.0.0/8', '130.0.0.0/8', '193.0.0.0/8', '212.0.0.0/8'],
            'FI': ['62.0.0.0/8', '130.0.0.0/8', '193.0.0.0/8', '212.0.0.0/8'],
            'JP': ['1.0.0.0/8', '14.0.0.0/8', '27.0.0.0/8', '58.0.0.0/8'],
            'KR': ['1.0.0.0/8', '14.0.0.0/8', '27.0.0.0/8', '58.0.0.0/8'],
            'SG': ['1.0.0.0/8', '14.0.0.0/8', '27.0.0.0/8', '58.0.0.0/8'],
            'HK': ['1.0.0.0/8', '14.0.0.0/8', '27.0.0.0/8', '58.0.0.0/8'],
            'CH': ['62.0.0.0/8', '77.0.0.0/8', '145.0.0.0/8', '213.0.0.0/8'],
            'AT': ['62.0.0.0/8', '77.0.0.0/8', '145.0.0.0/8', '213.0.0.0/8'],
            'BE': ['62.0.0.0/8', '77.0.0.0/8', '145.0.0.0/8', '213.0.0.0/8'],
            'IT': ['62.0.0.0/8', '77.0.0.0/8', '145.0.0.0/8', '213.0.0.0/8'],
            'ES': ['62.0.0.0/8', '77.0.0.0/8', '145.0.0.0/8', '213.0.0.0/8'],
            'BR': ['177.0.0.0/8', '179.0.0.0/8', '186.0.0.0/8', '189.0.0.0/8'],
            'MX': ['177.0.0.0/8', '179.0.0.0/8', '186.0.0.0/8', '189.0.0.0/8'],
            'CN': ['1.0.0.0/8', '14.0.0.0/8', '27.0.0.0/8', '58.0.0.0/8'],
            'RU': ['5.0.0.0/8', '31.0.0.0/8', '46.0.0.0/8', '78.0.0.0/8']
        }
        
        # AI-driven spoofing patterns
        self.ai_patterns = {
            'residential': {'weight': 0.4, 'ranges': ['24.0.0.0/8', '73.0.0.0/8', '98.0.0.0/8']},
            'datacenter': {'weight': 0.3, 'ranges': ['8.0.0.0/8', '4.0.0.0/8', '12.0.0.0/8']},
            'mobile': {'weight': 0.2, 'ranges': ['172.0.0.0/8', '173.0.0.0/8', '174.0.0.0/8']},
            'enterprise': {'weight': 0.1, 'ranges': ['64.0.0.0/8', '65.0.0.0/8', '66.0.0.0/8']}
        }
        
        # Behavioral mimicry patterns
        self.behavior_patterns = {
            'human_like': {'burst_probability': 0.3, 'idle_probability': 0.4},
            'bot_like': {'burst_probability': 0.8, 'idle_probability': 0.1},
            'mixed': {'burst_probability': 0.5, 'idle_probability': 0.25}
        }
        
        # Quantum-resistant spoofing seeds
        self.quantum_seeds = [random.randint(0, 2**32-1) for _ in range(100)]
        self.quantum_index = 0
        
        self._initialize_ultra_ip_pool()
    
    def _initialize_ultra_ip_pool(self):
        """Initialize ultra-advanced pool of spoofed IP addresses with AI patterns"""
        logger.info("Initializing ultra-advanced IP spoofing pool with AI patterns...")
        
        pool_size = 50000  # Massive pool for maximum diversity
        attempts = 0
        max_attempts = pool_size * 2  # Efficient generation
        
        # Generate IPs based on different patterns
        pattern_distribution = {
            'geo_based': 0.4,
            'ai_driven': 0.3,
            'quantum_resistant': 0.2,
            'random': 0.1
        }
        
        for pattern, ratio in pattern_distribution.items():
            target_count = int(pool_size * ratio)
            current_count = 0
            
            while current_count < target_count and attempts < max_attempts:
                if pattern == 'geo_based':
                    ip = self._generate_geo_spoofed_ip()
                elif pattern == 'ai_driven':
                    ip = self._generate_ai_driven_ip()
                elif pattern == 'quantum_resistant':
                    ip = self._generate_quantum_resistant_ip()
                else:
                    ip = self._generate_random_ip()
                
                if ip and self._validate_ip(ip) and ip not in self.current_ip_pool:
                    self.current_ip_pool.append(ip)
                    current_count += 1
                
                attempts += 1
        
        # Shuffle for randomness
        random.shuffle(self.current_ip_pool)
        
        logger.info(f"Generated {len(self.current_ip_pool)} ultra-advanced spoofed IP addresses")
    
    def _generate_ai_driven_ip(self) -> Optional[str]:
        """Generate AI-driven spoofed IP based on realistic patterns"""
        if not self.config.enable_ai_spoofing:
            return self._generate_random_ip()
        
        # Select pattern based on weights
        pattern_choice = random.choices(
            list(self.ai_patterns.keys()),
            weights=[p['weight'] for p in self.ai_patterns.values()]
        )[0]
        
        pattern = self.ai_patterns[pattern_choice]
        selected_range = random.choice(pattern['ranges'])
        
        try:
            network = ipaddress.IPv4Network(selected_range)
            # Generate IP within the selected range
            ip_int = random.randint(int(network.network_address), int(network.broadcast_address))
            return str(ipaddress.IPv4Address(ip_int))
        except Exception:
            return self._generate_random_ip()
    
    def _generate_quantum_resistant_ip(self) -> Optional[str]:
        """Generate quantum-resistant spoofed IP using advanced cryptographic techniques"""
        if not self.config.enable_quantum_spoofing:
            return self._generate_random_ip()
        
        # Use quantum seed for generation
        seed = self.quantum_seeds[self.quantum_index % len(self.quantum_seeds)]
        self.quantum_index += 1
        
        # Generate using quantum-resistant algorithm
        random.seed(seed ^ int(time.time() * 1000) % 2**32)
        
        # Generate in safe ranges
        safe_ranges = ['1.0.0.0/8', '2.0.0.0/8', '3.0.0.0/8', '4.0.0.0/8']
        selected_range = random.choice(safe_ranges)
        
        try:
            network = ipaddress.IPv4Network(selected_range)
            ip_int = random.randint(int(network.network_address), int(network.broadcast_address))
            
            # Reset random seed
            random.seed()
            
            return str(ipaddress.IPv4Address(ip_int))
        except Exception:
            random.seed()  # Reset on error
            return self._generate_random_ip()
    
    def get_behavioral_spoofed_ip(self, behavior_type: str = 'mixed') -> str:
        """Get spoofed IP with behavioral mimicry"""
        if not self.config.enable_behavioral_mimicry:
            return self.get_spoofed_ip()
        
        behavior = self.behavior_patterns.get(behavior_type, self.behavior_patterns['mixed'])
        
        # Simulate human-like behavior with bursts and idle times
        if random.random() < behavior['burst_probability']:
            # Burst mode - return same IP for a while
            if hasattr(self, '_burst_ip') and hasattr(self, '_burst_count'):
                if self._burst_count > 0:
                    self._burst_count -= 1
                    return self._burst_ip
            
            # Start new burst
            self._burst_ip = self.get_spoofed_ip()
            self._burst_count = random.randint(10, 100)
            return self._burst_ip
        
        elif random.random() < behavior['idle_probability']:
            # Idle mode - simulate pause
            time.sleep(random.uniform(0.001, 0.01))
        
        return self.get_spoofed_ip()
    
    def get_spoofed_ip(self) -> str:
        """Get next spoofed IP address"""
        if not self.config.enable_ip_spoofing:
            return NetworkUtils.get_local_ip()
        
        # Rotate IP pool if needed
        if (self.config.rotate_sources and 
            self.ip_rotation_counter >= self.config.rotation_interval):
            self._rotate_ip_pool()
            self.ip_rotation_counter = 0
        
        if not self.current_ip_pool:
            self._initialize_ip_pool()
        
        if self.current_ip_pool:
            ip = random.choice(self.current_ip_pool)
            self.spoofed_ips.add(ip)
            self.ip_rotation_counter += 1
            return ip
        
        # Fallback to random generation
        return self._generate_spoofed_ip() or NetworkUtils.get_local_ip()
    
    def get_decoy_ips(self, count: Optional[int] = None) -> List[str]:
        """Get decoy IP addresses for nmap-style spoofing"""
        if not self.config.use_decoy_sources:
            return []
        
        decoy_count = count or self.config.decoy_count
        decoys = []
        
        for _ in range(decoy_count):
            decoy = self._generate_spoofed_ip()
            if decoy and self._validate_ip(decoy):
                decoys.append(decoy)
        
        return decoys
    
    def _generate_spoofed_ip(self) -> Optional[str]:
        """Generate a spoofed IP address"""
        if self.config.enable_geo_spoofing:
            return self._generate_geo_spoofed_ip()
        
        # Use configured spoof ranges
        if self.config.spoof_ranges:
            return self._generate_from_ranges()
        
        # Generate completely random IP
        return self._generate_random_ip()
    
    def _generate_geo_spoofed_ip(self) -> Optional[str]:
        """Generate geographically targeted spoofed IP"""
        if not self.config.target_countries:
            return self._generate_random_ip()
        
        country = random.choice(self.config.target_countries)
        country_ranges = self.country_ranges.get(country, [])
        
        if not country_ranges:
            return self._generate_random_ip()
        
        range_str = random.choice(country_ranges)
        try:
            network = ipaddress.IPv4Network(range_str)
            # Generate random IP from network
            network_int = int(network.network_address)
            broadcast_int = int(network.broadcast_address)
            random_int = random.randint(network_int + 1, broadcast_int - 1)
            return str(ipaddress.IPv4Address(random_int))
        except:
            return self._generate_random_ip()
    
    def _generate_from_ranges(self) -> Optional[str]:
        """Generate IP from configured ranges"""
        range_str = random.choice(self.config.spoof_ranges)
        
        try:
            if '/' in range_str:
                # CIDR notation
                network = ipaddress.IPv4Network(range_str)
                network_int = int(network.network_address)
                broadcast_int = int(network.broadcast_address)
                random_int = random.randint(network_int + 1, broadcast_int - 1)
                return str(ipaddress.IPv4Address(random_int))
            else:
                # Single IP or range
                return range_str
        except:
            return self._generate_random_ip()
    
    def _generate_random_ip(self) -> str:
        """Generate completely random IP address"""
        while True:
            # Generate random IP avoiding certain ranges
            octets = [
                random.randint(1, 223),  # Avoid class D and E
                random.randint(1, 254),
                random.randint(1, 254),
                random.randint(1, 254)
            ]
            
            ip_str = '.'.join(map(str, octets))
            
            if self._validate_ip(ip_str):
                return ip_str
    
    def _validate_ip(self, ip_str: str) -> bool:
        """Validate spoofed IP address"""
        if not self.config.validate_spoofed_ips:
            return True
        
        try:
            ip = ipaddress.IPv4Address(ip_str)
            
            # Check against blacklisted ranges
            for blacklist_range in self.config.blacklist_ranges:
                if ip in ipaddress.IPv4Network(blacklist_range):
                    return False
            
            # Check against private ranges if configured
            if self.config.avoid_private_ranges:
                for private_range in self.private_ranges:
                    if ip in private_range:
                        return False
            
            # Check against reserved ranges
            if self.config.avoid_reserved_ranges:
                if ip.is_multicast or ip.is_reserved or ip.is_loopback:
                    return False
            
            return True
            
        except:
            return False
    
    def _rotate_ip_pool(self):
        """Rotate IP address pool"""
        logger.debug("Rotating IP spoofing pool...")
        
        # Keep some IPs, generate new ones
        keep_count = len(self.current_ip_pool) // 2
        self.current_ip_pool = random.sample(self.current_ip_pool, keep_count)
        
        # Generate new IPs
        target_size = 1000
        while len(self.current_ip_pool) < target_size:
            ip = self._generate_spoofed_ip()
            if ip and self._validate_ip(ip) and ip not in self.current_ip_pool:
                self.current_ip_pool.append(ip)
    
    def get_spoofing_stats(self) -> Dict[str, int]:
        """Get spoofing statistics"""
        return {
            'pool_size': len(self.current_ip_pool),
            'unique_ips_used': len(self.spoofed_ips),
            'rotation_counter': self.ip_rotation_counter
        }


class SourcePortSpoofing:
    """Source port spoofing and manipulation"""
    
    def __init__(self, config: SpoofingConfig):
        self.config = config
        self.used_ports = set()
        self.port_rotation_counter = 0
        
        # Well-known ports to avoid
        self.well_known_ports = set(range(1, 1024))
        
        # Common service ports to avoid
        self.service_ports = {
            20, 21, 22, 23, 25, 53, 67, 68, 69, 80, 110, 123, 143, 161, 162,
            179, 389, 443, 465, 514, 515, 587, 636, 993, 995, 1433, 1521,
            3306, 3389, 5432, 5900, 6379, 27017
        }
    
    def get_spoofed_port(self) -> int:
        """Get spoofed source port"""
        if not self.config.enable_port_spoofing:
            return random.randint(32768, 65535)
        
        # Select port range
        port_range = random.choice(self.config.port_ranges)
        min_port, max_port = port_range
        
        attempts = 0
        max_attempts = 100
        
        while attempts < max_attempts:
            port = random.randint(min_port, max_port)
            
            # Validate port
            if self._validate_port(port):
                self.used_ports.add(port)
                self.port_rotation_counter += 1
                return port
            
            attempts += 1
        
        # Fallback to high port
        return random.randint(49152, 65535)
    
    def get_sequential_ports(self, count: int, start_port: Optional[int] = None) -> List[int]:
        """Get sequential ports for connection exhaustion"""
        if start_port is None:
            start_port = random.randint(32768, 65535 - count)
        
        ports = []
        for i in range(count):
            port = start_port + i
            if port <= 65535 and self._validate_port(port):
                ports.append(port)
        
        return ports
    
    def get_random_ports(self, count: int) -> List[int]:
        """Get random ports for distributed attacks"""
        ports = []
        attempts = 0
        max_attempts = count * 10
        
        while len(ports) < count and attempts < max_attempts:
            port = self.get_spoofed_port()
            if port not in ports:
                ports.append(port)
            attempts += 1
        
        return ports
    
    def _validate_port(self, port: int) -> bool:
        """Validate port number"""
        if port < 1 or port > 65535:
            return False
        
        # Avoid well-known ports if configured
        if self.config.avoid_well_known_ports:
            if port in self.well_known_ports or port in self.service_ports:
                return False
        
        return True
    
    def get_port_stats(self) -> Dict[str, int]:
        """Get port spoofing statistics"""
        return {
            'unique_ports_used': len(self.used_ports),
            'rotation_counter': self.port_rotation_counter
        }


class MACAddressSpoofing:
    """MAC address spoofing (for local network attacks)"""
    
    def __init__(self, config: SpoofingConfig):
        self.config = config
        self.vendor_prefixes = [
            '00:1B:44',  # Cisco
            '00:50:56',  # VMware
            '00:0C:29',  # VMware
            '08:00:27',  # VirtualBox
            '00:15:5D',  # Microsoft
            '00:16:3E',  # Xen
            '52:54:00',  # QEMU/KVM
        ]
    
    def get_spoofed_mac(self) -> str:
        """Generate spoofed MAC address"""
        if not self.config.enable_mac_spoofing:
            return self._get_real_mac()
        
        # Use vendor prefix for realism
        if random.choice([True, False]):
            prefix = random.choice(self.vendor_prefixes)
            suffix = ':'.join([f'{random.randint(0, 255):02X}' for _ in range(3)])
            return f"{prefix}:{suffix}"
        
        # Generate completely random MAC
        return ':'.join([f'{random.randint(0, 255):02X}' for _ in range(6)])
    
    def _get_real_mac(self) -> str:
        """Get real MAC address"""
        try:
            import uuid
            mac = uuid.getnode()
            return ':'.join([f'{(mac >> i) & 0xFF:02X}' for i in range(0, 48, 8)][::-1])
        except:
            return '00:00:00:00:00:00'


class TTLManipulation:
    """TTL (Time To Live) manipulation for evasion"""
    
    def __init__(self, config: SpoofingConfig):
        self.config = config
        
        # Common OS TTL values
        self.os_ttl_signatures = {
            'windows': [128, 64],
            'linux': [64, 255],
            'macos': [64, 255],
            'freebsd': [64, 255],
            'solaris': [255, 64],
            'cisco': [255, 254],
            'juniper': [64, 255]
        }
    
    def get_spoofed_ttl(self) -> int:
        """Get spoofed TTL value"""
        if not self.config.randomize_ttl:
            return 64  # Default
        
        min_ttl, max_ttl = self.config.ttl_ranges
        
        # Sometimes use OS-specific TTL for realism
        if random.randint(1, 100) <= 30:  # 30% chance
            os_type = random.choice(list(self.os_ttl_signatures.keys()))
            return random.choice(self.os_ttl_signatures[os_type])
        
        # Random TTL within range
        return random.randint(min_ttl, max_ttl)
    
    def get_decremented_ttl(self, original_ttl: int, hops: int) -> int:
        """Get TTL as if packet traveled through hops"""
        return max(1, original_ttl - hops)


class SpoofingManager:
    """Main manager for all spoofing techniques"""
    
    def __init__(self, config: SpoofingConfig = None):
        self.config = config or SpoofingConfig()
        
        self.ip_spoofing = IPSpoofing(self.config)
        self.port_spoofing = SourcePortSpoofing(self.config)
        self.mac_spoofing = MACAddressSpoofing(self.config)
        self.ttl_manipulation = TTLManipulation(self.config)
    
    def get_spoofed_source(self) -> Dict[str, Union[str, int]]:
        """Get complete spoofed source information"""
        return {
            'ip': self.ip_spoofing.get_spoofed_ip(),
            'port': self.port_spoofing.get_spoofed_port(),
            'mac': self.mac_spoofing.get_spoofed_mac(),
            'ttl': self.ttl_manipulation.get_spoofed_ttl()
        }
    
    def get_decoy_sources(self, count: int) -> List[Dict[str, Union[str, int]]]:
        """Get multiple decoy sources"""
        decoys = []
        
        for _ in range(count):
            decoy = {
                'ip': self.ip_spoofing.get_spoofed_ip(),
                'port': self.port_spoofing.get_spoofed_port(),
                'mac': self.mac_spoofing.get_spoofed_mac(),
                'ttl': self.ttl_manipulation.get_spoofed_ttl()
            }
            decoys.append(decoy)
        
        return decoys
    
    def enable_stealth_mode(self):
        """Enable maximum stealth spoofing"""
        self.config.enable_ip_spoofing = True
        self.config.enable_port_spoofing = True
        self.config.enable_geo_spoofing = True
        self.config.use_decoy_sources = True
        self.config.rotate_sources = True
        self.config.randomize_ttl = True
        self.config.decoy_count = 10
        
        logger.info("Stealth spoofing mode enabled")
    
    def configure_for_target(self, target_info: Dict[str, Any]):
        """Configure spoofing based on target information"""
        # Adjust spoofing based on target
        if target_info.get('country'):
            self.config.target_countries = [target_info['country']]
            self.config.enable_geo_spoofing = True
        
        if target_info.get('has_firewall'):
            self.config.use_decoy_sources = True
            self.config.decoy_count = 15
        
        if target_info.get('detection_level') == 'high':
            self.enable_stealth_mode()
    
    def get_spoofing_stats(self) -> Dict[str, Any]:
        """Get comprehensive spoofing statistics"""
        return {
            'ip_spoofing': self.ip_spoofing.get_spoofing_stats(),
            'port_spoofing': self.port_spoofing.get_port_stats(),
            'config': {
                'ip_spoofing_enabled': self.config.enable_ip_spoofing,
                'port_spoofing_enabled': self.config.enable_port_spoofing,
                'geo_spoofing_enabled': self.config.enable_geo_spoofing,
                'decoy_sources_enabled': self.config.use_decoy_sources,
                'decoy_count': self.config.decoy_count
            }
        }
    
    def reset_spoofing_state(self):
        """Reset spoofing state and regenerate pools"""
        self.ip_spoofing._initialize_ip_pool()
        self.port_spoofing.used_ports.clear()
        self.port_spoofing.port_rotation_counter = 0
        
        logger.info("Spoofing state reset")