"""
Privacy and Anonymity Module
Advanced privacy protection and anonymity techniques for DDoS operations
"""

import os
import sys
import time
import random
import socket
import struct
import threading
import subprocess
import requests
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import tempfile
import json
import base64

from core.utils import NetworkUtils, CryptoUtils
from core.logger import logger


@dataclass
class PrivacyConfig:
    """Configuration for privacy and anonymity features"""
    # VPN Configuration
    enable_vpn: bool = True
    vpn_provider: str = "openvpn"  # openvpn, wireguard, custom
    vpn_config_path: str = ""
    auto_vpn_rotation: bool = True
    vpn_rotation_interval: int = 300  # seconds
    
    # Tor Configuration
    enable_tor: bool = True
    tor_proxy_host: str = "127.0.0.1"
    tor_proxy_port: int = 9050
    tor_control_port: int = 9051
    tor_password: str = ""
    new_identity_interval: int = 600  # seconds
    
    # IP Masking
    enable_ip_spoofing: bool = True
    spoof_source_ip: bool = True
    use_random_source_ports: bool = True
    geographic_spoofing: bool = True
    target_countries: List[str] = field(default_factory=lambda: ["US", "GB", "DE", "FR", "CA"])
    
    # DNS Privacy
    use_secure_dns: bool = True
    dns_over_https: bool = True
    dns_over_tls: bool = True
    custom_dns_servers: List[str] = field(default_factory=lambda: [
        "1.1.1.1",  # Cloudflare
        "8.8.8.8",  # Google
        "9.9.9.9"   # Quad9
    ])
    
    # Traffic Obfuscation
    enable_traffic_encryption: bool = True
    use_domain_fronting: bool = True
    enable_traffic_padding: bool = True
    randomize_packet_sizes: bool = True
    
    # Behavioral Privacy
    randomize_user_agents: bool = True
    randomize_request_timing: bool = True
    simulate_human_behavior: bool = True
    use_browser_fingerprinting_evasion: bool = True
    
    # Anti-Tracking
    disable_cookies: bool = True
    disable_javascript: bool = False
    block_tracking_pixels: bool = True
    use_fake_headers: bool = True


class VPNManager:
    """VPN connection and rotation management"""
    
    def __init__(self, config: PrivacyConfig):
        self.config = config
        self.current_vpn = None
        self.vpn_configs = []
        self.rotation_thread = None
        self.is_rotating = False
        
    def initialize_vpn(self):
        """Initialize VPN system"""
        if not self.config.enable_vpn:
            return False
            
        logger.info("Initializing VPN system...")
        
        # Load VPN configurations
        self._load_vpn_configs()
        
        # Connect to initial VPN
        if self.vpn_configs:
            return self._connect_vpn(self.vpn_configs[0])
        
        return False
    
    def _load_vpn_configs(self):
        """Load available VPN configurations"""
        config_dir = Path(self.config.vpn_config_path) if self.config.vpn_config_path else Path("configs/vpn")
        
        if not config_dir.exists():
            logger.warning(f"VPN config directory not found: {config_dir}")
            return
        
        # Load OpenVPN configs
        for config_file in config_dir.glob("*.ovpn"):
            self.vpn_configs.append({
                'type': 'openvpn',
                'path': str(config_file),
                'name': config_file.stem
            })
        
        # Load WireGuard configs
        for config_file in config_dir.glob("*.conf"):
            self.vpn_configs.append({
                'type': 'wireguard',
                'path': str(config_file),
                'name': config_file.stem
            })
        
        logger.info(f"Loaded {len(self.vpn_configs)} VPN configurations")
    
    def _connect_vpn(self, vpn_config: Dict) -> bool:
        """Connect to a specific VPN"""
        try:
            if vpn_config['type'] == 'openvpn':
                return self._connect_openvpn(vpn_config)
            elif vpn_config['type'] == 'wireguard':
                return self._connect_wireguard(vpn_config)
            
        except Exception as e:
            logger.error(f"Failed to connect to VPN {vpn_config['name']}: {e}")
            return False
    
    def _connect_openvpn(self, config: Dict) -> bool:
        """Connect to OpenVPN - Linux compatible"""
        try:
            import platform
            
            if platform.system() == "Linux":
                # Linux OpenVPN connection
                cmd = [
                    "openvpn",
                    "--config", config['path'],
                    "--daemon",
                    "--log", "/tmp/openvpn.log",
                    "--writepid", "/tmp/openvpn.pid"
                ]
                
                # Check if OpenVPN is installed
                try:
                    subprocess.run(["which", "openvpn"], check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    logger.error("OpenVPN not installed. Install with: sudo apt-get install openvpn")
                    return False
                
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(5)  # Wait for connection
                
                # Check if connected
                if self._verify_vpn_connection():
                    self.current_vpn = config
                    logger.info(f"Connected to OpenVPN: {config['name']}")
                    return True
                    
            else:
                # Windows fallback
                cmd = [
                    "openvpn",
                    "--config", config['path'],
                    "--daemon"
                ]
                
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(5)
                
                if self._verify_vpn_connection():
                    self.current_vpn = config
                    logger.info(f"Connected to OpenVPN: {config['name']}")
                    return True
                
        except Exception as e:
            logger.error(f"OpenVPN connection failed: {e}")
            
        return False
    
    def _connect_wireguard(self, config: Dict) -> bool:
        """Connect to WireGuard - Linux compatible"""
        try:
            import platform
            
            if platform.system() == "Linux":
                # Check if WireGuard is installed
                try:
                    subprocess.run(["which", "wg"], check=True, capture_output=True)
                    subprocess.run(["which", "wg-quick"], check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    logger.error("WireGuard not installed. Install with: sudo apt-get install wireguard")
                    return False
                
                # Start WireGuard interface
                subprocess.run(["wg-quick", "up", config['path']], check=True, timeout=30)
                
                # Verify connection
                if self._verify_vpn_connection():
                    self.current_vpn = config
                    logger.info(f"Connected to WireGuard: {config['name']}")
                    return True
                    
            else:
                # Windows fallback
                subprocess.run(["wg-quick", "up", config['path']], check=True)
                
                if self._verify_vpn_connection():
                    self.current_vpn = config
                    logger.info(f"Connected to WireGuard: {config['name']}")
                    return True
                
        except subprocess.TimeoutExpired:
            logger.error("WireGuard connection timeout")
        except Exception as e:
            logger.error(f"WireGuard connection failed: {e}")
            
        return False
    
    def _verify_vpn_connection(self) -> bool:
        """Verify VPN connection is active"""
        try:
            # Check external IP
            response = requests.get("https://httpbin.org/ip", timeout=10)
            if response.status_code == 200:
                ip_info = response.json()
                logger.debug(f"Current external IP: {ip_info.get('origin')}")
                return True
        except:
            pass
            
        return False
    
    def start_rotation(self):
        """Start automatic VPN rotation"""
        if not self.config.auto_vpn_rotation or len(self.vpn_configs) < 2:
            return
            
        self.is_rotating = True
        self.rotation_thread = threading.Thread(target=self._rotation_worker)
        self.rotation_thread.daemon = True
        self.rotation_thread.start()
        
        logger.info(f"Started VPN rotation (interval: {self.config.vpn_rotation_interval}s)")
    
    def _rotation_worker(self):
        """VPN rotation worker thread"""
        while self.is_rotating:
            time.sleep(self.config.vpn_rotation_interval)
            
            if not self.is_rotating:
                break
                
            # Select next VPN
            available_vpns = [v for v in self.vpn_configs if v != self.current_vpn]
            if available_vpns:
                next_vpn = random.choice(available_vpns)
                
                # Disconnect current and connect to next
                self.disconnect_vpn()
                if self._connect_vpn(next_vpn):
                    logger.info(f"Rotated to VPN: {next_vpn['name']}")
    
    def disconnect_vpn(self):
        """Disconnect current VPN"""
        if not self.current_vpn:
            return
            
        try:
            if self.current_vpn['type'] == 'openvpn':
                subprocess.run(["pkill", "-f", "openvpn"], check=False)
            elif self.current_vpn['type'] == 'wireguard':
                subprocess.run(["wg-quick", "down", self.current_vpn['path']], check=False)
                
            self.current_vpn = None
            logger.info("Disconnected from VPN")
            
        except Exception as e:
            logger.error(f"Failed to disconnect VPN: {e}")
    
    def stop_rotation(self):
        """Stop VPN rotation"""
        self.is_rotating = False
        if self.rotation_thread:
            self.rotation_thread.join(timeout=5)


class TorManager:
    """Cross-platform Tor proxy management and identity rotation"""
    
    def __init__(self, config: PrivacyConfig):
        self.config = config
        self.tor_process = None
        self.control_socket = None
        self.identity_rotation_thread = None
        self.is_rotating = False
        
    def initialize_tor(self) -> bool:
        """Initialize Tor proxy with cross-platform support"""
        if not self.config.enable_tor:
            return False
            
        logger.info("Initializing Tor proxy...")
        
        # Check Tor dependency
        if not self._check_tor_dependency():
            logger.error("Tor is not installed or not in PATH")
            return False
        
        # Check if Tor is already running
        if self._check_tor_running():
            logger.info("Tor is already running")
            return True
        
        # Start Tor process
        return self._start_tor_process()
    
    def _check_tor_dependency(self) -> bool:
        """Check if Tor is installed and available"""
        try:
            result = subprocess.run(["tor", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def _check_tor_running(self) -> bool:
        """Check if Tor is already running"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.config.tor_proxy_host, self.config.tor_proxy_port))
            sock.close()
            return result == 0
        except:
            return False
    
    def _start_tor_process(self) -> bool:
        """Start Tor process with cross-platform support"""
        try:
            # Create platform-specific data directory
            if os.name == 'nt':  # Windows
                data_dir = os.path.join(tempfile.gettempdir(), "tor_data")
                log_file = os.path.join(tempfile.gettempdir(), "tor.log")
            else:  # Linux/Unix
                data_dir = "/tmp/tor_data"
                log_file = "/tmp/tor.log"
            
            # Ensure data directory exists
            os.makedirs(data_dir, exist_ok=True)
            
            tor_config = [
                "tor",
                "--SocksPort", f"{self.config.tor_proxy_port}",
                "--ControlPort", f"{self.config.tor_control_port}",
                "--DataDirectory", data_dir,
                "--Log", f"notice file {log_file}"
            ]
            
            # Add Linux-specific configurations
            if os.name != 'nt':
                tor_config.extend([
                    "--RunAsDaemon", "0",  # Don't run as daemon for better control
                    "--DisableNetwork", "0"
                ])
            
            if self.config.tor_password:
                # Generate hashed password
                hash_cmd = ["tor", "--hash-password", self.config.tor_password]
                try:
                    result = subprocess.run(hash_cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        hashed_password = result.stdout.strip()
                        tor_config.extend(["--HashedControlPassword", hashed_password])
                except subprocess.TimeoutExpired:
                    logger.warning("Timeout generating Tor password hash")
            
            # Start Tor process
            if os.name == 'nt':  # Windows
                self.tor_process = subprocess.Popen(tor_config, 
                                                  creationflags=subprocess.CREATE_NO_WINDOW)
            else:  # Linux/Unix
                self.tor_process = subprocess.Popen(tor_config, 
                                                  stdout=subprocess.DEVNULL, 
                                                  stderr=subprocess.DEVNULL)
            
            # Wait for Tor to start
            for _ in range(10):  # Wait up to 10 seconds
                time.sleep(1)
                if self._check_tor_running():
                    logger.info("Tor proxy started successfully")
                    return True
            
            logger.error("Tor failed to start within timeout")
            return False
                
        except Exception as e:
            logger.error(f"Failed to start Tor: {e}")
            return False
    
    def get_tor_session(self) -> requests.Session:
        """Get requests session configured for Tor"""
        session = requests.Session()
        session.proxies = {
            'http': f'socks5h://{self.config.tor_proxy_host}:{self.config.tor_proxy_port}',
            'https': f'socks5h://{self.config.tor_proxy_host}:{self.config.tor_proxy_port}'
        }
        return session
    
    def new_identity(self) -> bool:
        """Request new Tor identity"""
        try:
            import stem.control
            
            with stem.control.Controller.from_port(port=self.config.tor_control_port) as controller:
                if self.config.tor_password:
                    controller.authenticate(password=self.config.tor_password)
                else:
                    controller.authenticate()
                
                controller.signal(stem.Signal.NEWNYM)
                logger.info("Requested new Tor identity")
                return True
                
        except Exception as e:
            logger.error(f"Failed to get new Tor identity: {e}")
            return False
    
    def start_identity_rotation(self):
        """Start automatic identity rotation"""
        self.is_rotating = True
        self.identity_rotation_thread = threading.Thread(target=self._identity_rotation_worker)
        self.identity_rotation_thread.daemon = True
        self.identity_rotation_thread.start()
        
        logger.info(f"Started Tor identity rotation (interval: {self.config.new_identity_interval}s)")
    
    def _identity_rotation_worker(self):
        """Identity rotation worker thread"""
        while self.is_rotating:
            time.sleep(self.config.new_identity_interval)
            
            if not self.is_rotating:
                break
                
            self.new_identity()
    
    def stop_identity_rotation(self):
        """Stop identity rotation"""
        self.is_rotating = False
        if self.identity_rotation_thread:
            self.identity_rotation_thread.join(timeout=5)
    
    def stop_tor(self):
        """Stop Tor process"""
        if self.tor_process:
            self.tor_process.terminate()
            self.tor_process.wait()
            self.tor_process = None
            logger.info("Tor process stopped")


class IPMaskingManager:
    """IP address masking and spoofing management"""
    
    def __init__(self, config: PrivacyConfig):
        self.config = config
        self.spoofed_ips = []
        self.geographic_ip_pools = {}
        
    def initialize_ip_masking(self):
        """Initialize IP masking system"""
        if not self.config.enable_ip_spoofing:
            return
            
        logger.info("Initializing IP masking system...")
        
        # Load geographic IP pools
        self._load_geographic_ips()
        
        # Generate spoofed IP pool
        self._generate_spoofed_ips()
    
    def _load_geographic_ips(self):
        """Load IP ranges for different countries"""
        # This would typically load from GeoIP databases
        # For demonstration, using sample ranges
        
        country_ranges = {
            "US": ["8.8.8.0/24", "1.1.1.0/24"],
            "GB": ["81.2.69.0/24", "86.1.1.0/24"],
            "DE": ["85.25.0.0/16", "91.64.0.0/16"],
            "FR": ["80.10.0.0/16", "82.64.0.0/16"],
            "CA": ["24.222.0.0/16", "70.26.0.0/16"]
        }
        
        for country in self.config.target_countries:
            if country in country_ranges:
                self.geographic_ip_pools[country] = []
                for ip_range in country_ranges[country]:
                    self.geographic_ip_pools[country].extend(
                        self._generate_ips_from_range(ip_range)
                    )
    
    def _generate_ips_from_range(self, ip_range: str) -> List[str]:
        """Generate IP addresses from CIDR range"""
        import ipaddress
        
        try:
            network = ipaddress.IPv4Network(ip_range, strict=False)
            # Generate sample IPs (not all to avoid memory issues)
            ips = []
            for i, ip in enumerate(network.hosts()):
                if i >= 100:  # Limit to 100 IPs per range
                    break
                ips.append(str(ip))
            return ips
        except:
            return []
    
    def _generate_spoofed_ips(self):
        """Generate pool of spoofed IP addresses"""
        # Generate random private and public IP ranges
        for _ in range(1000):
            if self.config.geographic_spoofing and self.geographic_ip_pools:
                # Use geographic IPs
                country = random.choice(self.config.target_countries)
                if country in self.geographic_ip_pools and self.geographic_ip_pools[country]:
                    ip = random.choice(self.geographic_ip_pools[country])
                    self.spoofed_ips.append(ip)
            else:
                # Generate random public IP
                ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
                # Avoid private ranges
                if not self._is_private_ip(ip):
                    self.spoofed_ips.append(ip)
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is in private range"""
        import ipaddress
        try:
            return ipaddress.IPv4Address(ip).is_private
        except:
            return True
    
    def get_random_spoofed_ip(self) -> str:
        """Get random spoofed IP address"""
        if self.spoofed_ips:
            return random.choice(self.spoofed_ips)
        return "127.0.0.1"
    
    def get_random_source_port(self) -> int:
        """Get random source port"""
        if self.config.use_random_source_ports:
            return random.randint(1024, 65535)
        return 0


class TrafficObfuscator:
    """Traffic obfuscation and encryption"""
    
    def __init__(self, config: PrivacyConfig):
        self.config = config
        self.crypto_utils = CryptoUtils()
        
    def obfuscate_payload(self, payload: bytes) -> bytes:
        """Obfuscate network payload"""
        if not self.config.enable_traffic_encryption:
            return payload
            
        # Encrypt payload
        encrypted = self.crypto_utils.encrypt_data(payload)
        
        # Add padding if enabled
        if self.config.enable_traffic_padding:
            encrypted = self._add_traffic_padding(encrypted)
            
        return encrypted
    
    def _add_traffic_padding(self, data: bytes) -> bytes:
        """Add random padding to traffic"""
        if self.config.randomize_packet_sizes:
            padding_size = random.randint(10, 100)
            padding = os.urandom(padding_size)
            return data + padding
        return data
    
    def generate_decoy_headers(self) -> Dict[str, str]:
        """Generate fake HTTP headers"""
        headers = {}
        
        if self.config.randomize_user_agents:
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            ]
            headers['User-Agent'] = random.choice(user_agents)
        
        if self.config.use_fake_headers:
            fake_headers = {
                'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.8', 'de-DE,de;q=0.9']),
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Upgrade-Insecure-Requests': '1'
            }
            headers.update(fake_headers)
            
        return headers


class PrivacyManager:
    """Main privacy and anonymity manager"""
    
    def __init__(self, config: PrivacyConfig = None):
        self.config = config or PrivacyConfig()
        self.vpn_manager = VPNManager(self.config)
        self.tor_manager = TorManager(self.config)
        self.ip_masking = IPMaskingManager(self.config)
        self.traffic_obfuscator = TrafficObfuscator(self.config)
        
    def enable_full_privacy(self) -> bool:
        """Enable all privacy features"""
        logger.info("Enabling full privacy protection...")
        
        success = True
        
        # Initialize VPN
        if self.config.enable_vpn:
            if not self.vpn_manager.initialize_vpn():
                logger.warning("VPN initialization failed")
                success = False
            else:
                self.vpn_manager.start_rotation()
        
        # Initialize Tor
        if self.config.enable_tor:
            if not self.tor_manager.initialize_tor():
                logger.warning("Tor initialization failed")
                success = False
            else:
                self.tor_manager.start_identity_rotation()
        
        # Initialize IP masking
        self.ip_masking.initialize_ip_masking()
        
        logger.info(f"Privacy protection {'enabled' if success else 'partially enabled'}")
        return success
    
    def disable_privacy(self):
        """Disable all privacy features"""
        logger.info("Disabling privacy protection...")
        
        # Stop VPN
        self.vpn_manager.stop_rotation()
        self.vpn_manager.disconnect_vpn()
        
        # Stop Tor
        self.tor_manager.stop_identity_rotation()
        self.tor_manager.stop_tor()
        
        logger.info("Privacy protection disabled")
    
    def get_anonymous_session(self) -> requests.Session:
        """Get anonymized requests session"""
        if self.config.enable_tor:
            session = self.tor_manager.get_tor_session()
        else:
            session = requests.Session()
        
        # Add privacy headers
        session.headers.update(self.traffic_obfuscator.generate_decoy_headers())
        
        return session
    
    def get_spoofed_ip(self) -> str:
        """Get spoofed IP address"""
        return self.ip_masking.get_random_spoofed_ip()
    
    def get_random_port(self) -> int:
        """Get random source port"""
        return self.ip_masking.get_random_source_port()
    
    def obfuscate_data(self, data: bytes) -> bytes:
        """Obfuscate network data"""
        return self.traffic_obfuscator.obfuscate_payload(data)
    
    def get_privacy_status(self) -> Dict[str, Any]:
        """Get current privacy status"""
        return {
            'vpn_connected': self.vpn_manager.current_vpn is not None,
            'tor_active': self.tor_manager._check_tor_running(),
            'ip_spoofing_enabled': self.config.enable_ip_spoofing,
            'traffic_encryption_enabled': self.config.enable_traffic_encryption,
            'current_vpn': self.vpn_manager.current_vpn['name'] if self.vpn_manager.current_vpn else None,
            'spoofed_ip_pool_size': len(self.ip_masking.spoofed_ips)
        }
    
    def __enter__(self):
        self.enable_full_privacy()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disable_privacy()