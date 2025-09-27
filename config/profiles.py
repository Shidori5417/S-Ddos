"""
Attack Profiles
Predefined configuration profiles for different attack scenarios
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from .settings import GlobalConfig, AttackConfig, SecurityConfig, NetworkConfig, LoggingConfig


@dataclass
class AttackProfile:
    """Attack profile containing all configuration settings"""
    
    name: str
    description: str
    category: str
    difficulty: str  # beginner, intermediate, advanced, expert
    
    global_config: GlobalConfig
    attack_config: AttackConfig
    security_config: SecurityConfig
    network_config: NetworkConfig
    logging_config: LoggingConfig
    
    # Profile metadata
    author: str = "FsocietyDDoS"
    version: str = "1.0"
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ProfileManager:
    """Manager for attack profiles"""
    
    def __init__(self):
        self._profiles = {}
        self._load_default_profiles()
    
    def _load_default_profiles(self):
        """Load default attack profiles"""
        # Basic HTTP Flood Profile
        self._profiles['basic_http'] = AttackProfile(
            name="Basic HTTP Flood",
            description="Simple HTTP GET flood attack for beginners",
            category="layer7",
            difficulty="beginner",
            global_config=GlobalConfig(
                debug_mode=False,
                max_threads=50,
                thread_pool_size=25
            ),
            attack_config=AttackConfig(
                attack_type="http_flood",
                attack_layer="layer7",
                threads=25,
                requests_per_second=50,
                duration_seconds=60,
                http_method="GET",
                use_proxies=False,
                randomize_headers=False
            ),
            security_config=SecurityConfig(
                enable_stealth_mode=False,
                avoid_honeypots=True,
                human_like_behavior=False
            ),
            network_config=NetworkConfig(
                max_connections=100,
                max_retries=1
            ),
            logging_config=LoggingConfig(
                log_level="INFO",
                enable_file_logging=True
            ),
            tags=["http", "basic", "beginner"]
        )
        
        # Advanced HTTP Flood Profile
        self._profiles['advanced_http'] = AttackProfile(
            name="Advanced HTTP Flood",
            description="Advanced HTTP flood with evasion techniques",
            category="layer7",
            difficulty="advanced",
            global_config=GlobalConfig(
                debug_mode=False,
                max_threads=200,
                thread_pool_size=100
            ),
            attack_config=AttackConfig(
                attack_type="http_flood",
                attack_layer="layer7",
                threads=100,
                requests_per_second=200,
                duration_seconds=300,
                http_method="GET",
                use_proxies=True,
                randomize_headers=True,
                bypass_cloudflare=True
            ),
            security_config=SecurityConfig(
                enable_stealth_mode=True,
                avoid_honeypots=True,
                evade_waf=True,
                human_like_behavior=True,
                randomize_timing=True
            ),
            network_config=NetworkConfig(
                max_connections=500,
                max_retries=3,
                bandwidth_limit_mbps=100
            ),
            logging_config=LoggingConfig(
                log_level="DEBUG",
                enable_file_logging=True,
                enable_monitoring=True
            ),
            tags=["http", "advanced", "evasion", "stealth"]
        )
        
        # Slowloris Profile
        self._profiles['slowloris'] = AttackProfile(
            name="Slowloris Attack",
            description="Low-bandwidth connection exhaustion attack",
            category="layer7",
            difficulty="intermediate",
            global_config=GlobalConfig(
                debug_mode=False,
                max_threads=500,
                thread_pool_size=250
            ),
            attack_config=AttackConfig(
                attack_type="slowloris",
                attack_layer="layer7",
                threads=200,
                requests_per_second=10,
                duration_seconds=600,
                http_method="GET",
                use_proxies=True,
                randomize_headers=True
            ),
            security_config=SecurityConfig(
                enable_stealth_mode=True,
                avoid_honeypots=True,
                human_like_behavior=True,
                random_delays=True,
                delay_range=(10, 30)
            ),
            network_config=NetworkConfig(
                max_connections=1000,
                keep_alive=True,
                max_retries=5
            ),
            logging_config=LoggingConfig(
                log_level="INFO",
                enable_file_logging=True
            ),
            tags=["slowloris", "low-bandwidth", "connection-exhaustion"]
        )
        
        # TCP Flood Profile
        self._profiles['tcp_flood'] = AttackProfile(
            name="TCP SYN Flood",
            description="High-volume TCP SYN flood attack",
            category="layer4",
            difficulty="intermediate",
            global_config=GlobalConfig(
                debug_mode=False,
                max_threads=100,
                thread_pool_size=50
            ),
            attack_config=AttackConfig(
                attack_type="tcp_flood",
                attack_layer="layer4",
                threads=50,
                requests_per_second=1000,
                duration_seconds=120,
                protocol="tcp",
                enable_spoofing=True,
                fragment_packets=False
            ),
            security_config=SecurityConfig(
                enable_stealth_mode=True,
                rotate_source_ip=True,
                spoof_mac_address=True,
                randomize_ttl=True
            ),
            network_config=NetworkConfig(
                max_connections=2000,
                max_retries=0
            ),
            logging_config=LoggingConfig(
                log_level="INFO",
                enable_file_logging=True
            ),
            tags=["tcp", "syn-flood", "layer4", "spoofing"]
        )
        
        # UDP Flood Profile
        self._profiles['udp_flood'] = AttackProfile(
            name="UDP Flood",
            description="High-volume UDP flood attack",
            category="layer4",
            difficulty="beginner",
            global_config=GlobalConfig(
                debug_mode=False,
                max_threads=75,
                thread_pool_size=40
            ),
            attack_config=AttackConfig(
                attack_type="udp_flood",
                attack_layer="layer4",
                threads=40,
                requests_per_second=800,
                duration_seconds=90,
                protocol="udp",
                enable_spoofing=True,
                packet_size=1024
            ),
            security_config=SecurityConfig(
                enable_stealth_mode=True,
                rotate_source_ip=True,
                randomize_timing=True
            ),
            network_config=NetworkConfig(
                max_connections=1500,
                max_retries=0
            ),
            logging_config=LoggingConfig(
                log_level="INFO",
                enable_file_logging=True
            ),
            tags=["udp", "flood", "layer4", "high-volume"]
        )
        
        # DNS Amplification Profile
        self._profiles['dns_amplification'] = AttackProfile(
            name="DNS Amplification",
            description="DNS amplification attack using public resolvers",
            category="layer4",
            difficulty="expert",
            global_config=GlobalConfig(
                debug_mode=False,
                max_threads=50,
                thread_pool_size=25
            ),
            attack_config=AttackConfig(
                attack_type="amplification",
                attack_layer="layer4",
                threads=25,
                requests_per_second=100,
                duration_seconds=180,
                protocol="udp",
                enable_spoofing=True
            ),
            security_config=SecurityConfig(
                enable_stealth_mode=True,
                rotate_source_ip=True,
                randomize_timing=True,
                avoid_honeypots=True
            ),
            network_config=NetworkConfig(
                max_connections=500,
                max_retries=2,
                custom_dns_servers=["8.8.8.8", "1.1.1.1", "208.67.222.222"]
            ),
            logging_config=LoggingConfig(
                log_level="DEBUG",
                enable_file_logging=True,
                enable_monitoring=True
            ),
            tags=["dns", "amplification", "reflection", "expert"]
        )
        
        # Stealth Profile
        self._profiles['stealth_mode'] = AttackProfile(
            name="Maximum Stealth",
            description="Highly evasive attack with maximum stealth features",
            category="stealth",
            difficulty="expert",
            global_config=GlobalConfig(
                debug_mode=False,
                max_threads=30,
                thread_pool_size=15,
                secure_mode=True
            ),
            attack_config=AttackConfig(
                attack_type="http_flood",
                attack_layer="layer7",
                threads=15,
                requests_per_second=20,
                duration_seconds=900,
                http_method="GET",
                use_proxies=True,
                randomize_headers=True,
                bypass_cloudflare=True
            ),
            security_config=SecurityConfig(
                enable_stealth_mode=True,
                hide_process=True,
                obfuscate_traffic=True,
                anti_forensics=True,
                avoid_honeypots=True,
                evade_ids=True,
                evade_waf=True,
                human_like_behavior=True,
                random_delays=True,
                delay_range=(5, 15),
                detect_sandbox=True,
                detect_vm=True,
                encrypt_payloads=True
            ),
            network_config=NetworkConfig(
                max_connections=100,
                max_retries=5,
                bandwidth_limit_mbps=10
            ),
            logging_config=LoggingConfig(
                log_level="WARNING",
                enable_file_logging=False,
                sanitize_logs=True
            ),
            tags=["stealth", "evasion", "anti-detection", "expert"]
        )
        
        # Stress Test Profile
        self._profiles['stress_test'] = AttackProfile(
            name="Stress Test",
            description="Maximum intensity stress testing profile",
            category="testing",
            difficulty="expert",
            global_config=GlobalConfig(
                debug_mode=False,
                max_threads=500,
                thread_pool_size=250,
                memory_limit_mb=1024
            ),
            attack_config=AttackConfig(
                attack_type="http_flood",
                attack_layer="layer7",
                threads=250,
                requests_per_second=1000,
                duration_seconds=60,
                http_method="POST",
                use_proxies=False,
                randomize_headers=True
            ),
            security_config=SecurityConfig(
                enable_stealth_mode=False,
                human_like_behavior=False,
                randomize_timing=False
            ),
            network_config=NetworkConfig(
                max_connections=5000,
                max_retries=0,
                tcp_nodelay=True
            ),
            logging_config=LoggingConfig(
                log_level="ERROR",
                enable_file_logging=True,
                performance_tracking=True
            ),
            tags=["stress-test", "high-intensity", "performance"]
        )
    
    def get_profile(self, name: str) -> AttackProfile:
        """Get profile by name"""
        if name not in self._profiles:
            raise ValueError(f"Profile not found: {name}")
        return self._profiles[name]
    
    def list_profiles(self) -> List[str]:
        """List all available profiles"""
        return list(self._profiles.keys())
    
    def get_profiles_by_category(self, category: str) -> List[AttackProfile]:
        """Get profiles by category"""
        return [profile for profile in self._profiles.values() 
                if profile.category == category]
    
    def get_profiles_by_difficulty(self, difficulty: str) -> List[AttackProfile]:
        """Get profiles by difficulty level"""
        return [profile for profile in self._profiles.values() 
                if profile.difficulty == difficulty]
    
    def search_profiles(self, query: str) -> List[AttackProfile]:
        """Search profiles by name, description, or tags"""
        query = query.lower()
        results = []
        
        for profile in self._profiles.values():
            if (query in profile.name.lower() or 
                query in profile.description.lower() or
                any(query in tag.lower() for tag in profile.tags)):
                results.append(profile)
        
        return results
    
    def add_profile(self, profile: AttackProfile):
        """Add custom profile"""
        self._profiles[profile.name.lower().replace(' ', '_')] = profile
    
    def remove_profile(self, name: str):
        """Remove profile"""
        if name in self._profiles:
            del self._profiles[name]
    
    def get_profile_info(self, name: str) -> Dict:
        """Get detailed profile information"""
        if name not in self._profiles:
            raise ValueError(f"Profile not found: {name}")
        
        profile = self._profiles[name]
        return {
            'name': profile.name,
            'description': profile.description,
            'category': profile.category,
            'difficulty': profile.difficulty,
            'author': profile.author,
            'version': profile.version,
            'tags': profile.tags,
            'attack_type': profile.attack_config.attack_type,
            'attack_layer': profile.attack_config.attack_layer,
            'threads': profile.attack_config.threads,
            'duration': profile.attack_config.duration_seconds,
            'stealth_enabled': profile.security_config.enable_stealth_mode
        }
    
    def export_profile(self, name: str) -> Dict:
        """Export profile to dictionary"""
        if name not in self._profiles:
            raise ValueError(f"Profile not found: {name}")
        
        profile = self._profiles[name]
        return {
            'name': profile.name,
            'description': profile.description,
            'category': profile.category,
            'difficulty': profile.difficulty,
            'author': profile.author,
            'version': profile.version,
            'tags': profile.tags,
            'global_config': profile.global_config.__dict__,
            'attack_config': profile.attack_config.__dict__,
            'security_config': profile.security_config.__dict__,
            'network_config': profile.network_config.__dict__,
            'logging_config': profile.logging_config.__dict__
        }


# Default profiles registry
DEFAULT_PROFILES = {
    'beginner': ['basic_http', 'udp_flood'],
    'intermediate': ['advanced_http', 'slowloris', 'tcp_flood'],
    'advanced': ['dns_amplification', 'stealth_mode'],
    'expert': ['stress_test'],
    'layer4': ['tcp_flood', 'udp_flood', 'dns_amplification'],
    'layer7': ['basic_http', 'advanced_http', 'slowloris'],
    'stealth': ['stealth_mode'],
    'testing': ['stress_test']
}