"""Security Module
Comprehensive security, stealth, evasion, privacy, and anti-forensics capabilities
"""

from .stealth import (
    StealthConfig,
    ProcessStealth,
    MemoryStealth,
    FileStealth,
    NetworkStealth,
    SystemStealth,
    StealthManager
)

from .detection import (
    DetectionConfig,
    SignatureEvasion,
    BehavioralEvasion,
    HoneypotDetection,
    IDSEvasion,
    SandboxEvasion,
    DetectionManager
)

from .privacy import (
    PrivacyConfig,
    VPNManager,
    TorManager,
    IPMaskingManager,
    TrafficObfuscator,
    PrivacyManager
)

from .forensics import (
    ForensicsConfig,
    SecureFileManager,
    MemoryManager,
    SystemLogManager,
    NetworkTraceManager,
    RegistryManager,
    TimestampManager,
    AntiForensicsManager
)

__all__ = [
    'StealthConfig',
    'ProcessStealth',
    'MemoryStealth',
    'FileStealth',
    'NetworkStealth',
    'SystemStealth',
    'StealthManager',
    'DetectionConfig',
    'SignatureEvasion',
    'BehavioralEvasion',
    'HoneypotDetection',
    'IDSEvasion',
    'SandboxEvasion',
    'DetectionManager',
    'PrivacyConfig',
    'VPNManager',
    'TorManager',
    'IPMaskingManager',
    'TrafficObfuscator',
    'PrivacyManager',
    'ForensicsConfig',
    'SecureFileManager',
    'MemoryManager',
    'SystemLogManager',
    'NetworkTraceManager',
    'RegistryManager',
    'TimestampManager',
    'AntiForensicsManager',
    'get_security_manager',
    'get_integrated_security_manager',
    'list_security_systems'
]

# Security systems registry
SECURITY_SYSTEMS = {
    'stealth': StealthManager,
    'detection_evasion': DetectionManager,
    'privacy': PrivacyManager,
    'anti_forensics': AntiForensicsManager,
}


def get_security_manager(system_type: str, config=None):
    """Get security manager instance"""
    if system_type not in SECURITY_SYSTEMS:
        raise ValueError(f"Unknown security system: {system_type}")
    
    manager_class = SECURITY_SYSTEMS[system_type]
    
    if config is None:
        # Create default config based on system type
        if system_type == 'stealth':
            config = StealthConfig()
        elif system_type == 'detection_evasion':
            config = DetectionConfig()
        elif system_type == 'privacy':
            config = PrivacyConfig()
        elif system_type == 'anti_forensics':
            config = ForensicsConfig()
    
    return manager_class(config)


def list_security_systems():
    """List available security systems"""
    return {
        'stealth': {
            'description': 'Advanced stealth and operational security',
            'features': [
                'Process hiding and manipulation',
                'Memory protection and encryption',
                'File stealth and secure deletion',
                'Network traffic obfuscation',
                'System-level stealth techniques'
            ]
        },
        'detection_evasion': {
            'description': 'Detection avoidance and evasion systems',
            'features': [
                'Signature-based detection evasion',
                'Behavioral analysis evasion',
                'Honeypot detection and avoidance',
                'IDS/IPS evasion techniques',
                'Sandbox detection and evasion'
            ]
        },
        'privacy': {
            'description': 'Privacy and anonymity protection',
            'features': [
                'VPN management and rotation',
                'Tor network integration',
                'IP masking and spoofing',
                'Traffic obfuscation',
                'DNS over HTTPS/TLS'
            ]
        },
        'anti_forensics': {
            'description': 'Anti-forensics and evidence elimination',
            'features': [
                'Secure file deletion',
                'Memory wiping',
                'Log manipulation',
                'Network trace removal',
                'Registry cleaning'
            ]
        }
    }


def create_integrated_security_config():
    """Create integrated security configuration"""
    return {
        'stealth': StealthConfig(
            enable_process_hiding=True,
            enable_memory_protection=True,
            enable_file_hiding=True,
            enable_traffic_obfuscation=True,
            enable_anti_forensics=True
        ),
        'detection_avoidance': DetectionConfig(
            enable_signature_evasion=True,
            enable_behavioral_evasion=True,
            enable_honeypot_detection=True,
            enable_ids_evasion=True,
            enable_sandbox_evasion=True,
            enable_anti_analysis=True
        ),
        'privacy': PrivacyConfig(
            enable_vpn=True,
            enable_tor=True,
            enable_ip_masking=True,
            enable_traffic_obfuscation=True,
            enable_dns_over_https=True
        ),
        'anti_forensics': ForensicsConfig(
            enable_secure_deletion=True,
            enable_memory_wiping=True,
            enable_log_manipulation=True,
            enable_network_trace_removal=True,
            enable_registry_cleaning=True
        )
    }


def get_integrated_security_manager(config=None):
    """Get integrated security manager with all systems"""
    return IntegratedSecurityManager(config)


class IntegratedSecurityManager:
    
    def __init__(self, config=None):
        if config is None:
            config = create_integrated_security_config()
        
        self.stealth_manager = StealthManager(config.get('stealth'))
        self.detection_manager = DetectionManager(config.get('detection_avoidance'))
        self.privacy_manager = PrivacyManager(config.get('privacy'))
        self.forensics_manager = AntiForensicsManager(config.get('anti_forensics'))
        
        self.is_active = False
    
    def enable_full_security(self):
        """Enable all security systems"""
        if self.is_active:
            return
        
        # Initialize detection avoidance first
        if not self.detection_manager.initialize_detection_avoidance():
            raise RuntimeError("Failed to initialize detection avoidance")
        
        # Enable privacy protection
        self.privacy_manager.enable_full_privacy()
        
        # Enable stealth systems
        self.stealth_manager.enable_full_stealth()
        
        # Enable anti-forensics
        self.forensics_manager.enable_anti_forensics()
        
        self.is_active = True
    
    def disable_security(self):
        """Disable all security systems"""
        if not self.is_active:
            return
        
        self.stealth_manager.disable_stealth()
        self.privacy_manager.disable_privacy()
        self.forensics_manager.disable_anti_forensics()
        self.is_active = False
    
    def validate_target(self, target: str, port: int = 80) -> bool:
        """Validate target through all security checks"""
        return self.detection_manager.validate_target(target, port)
    
    def prepare_secure_payload(self, payload: str) -> str:
        """Prepare payload with all security enhancements"""
        # Apply detection evasion
        evasive_payload = self.detection_manager.generate_evasive_payload(payload)
        
        # Obfuscate traffic
        obfuscated_payload = self.privacy_manager.obfuscate_traffic(evasive_payload)
        
        # Store securely in memory
        storage_key = self.stealth_manager.store_sensitive_data('payload', obfuscated_payload)
        
        return storage_key
    
    def get_secure_behavioral_patterns(self):
        """Get behavioral patterns with security enhancements"""
        patterns = self.detection_manager.get_behavioral_patterns()
        
        # Add network jitter
        if 'request_interval' in patterns:
            patterns['request_interval'] = self.stealth_manager.add_network_jitter(
                patterns['request_interval']
            )
        
        return patterns
    
    def get_anonymous_connection(self):
        """Get anonymous connection through privacy systems"""
        return self.privacy_manager.get_anonymous_connection()
    
    def clean_traces(self):
        """Clean all traces using anti-forensics"""
        self.forensics_manager.clean_all_traces()
    
    def create_secure_file(self, content: bytes, extension: str = ".tmp") -> str:
        """Create secure file with stealth techniques"""
        return self.stealth_manager.create_stealth_file(content, extension)
    
    def get_security_status(self):
        """Get comprehensive security status"""
        return {
            'integrated_security_active': self.is_active,
            'stealth_status': self.stealth_manager.get_stealth_status(),
            'detection_status': self.detection_manager.get_detection_status()
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.enable_full_security()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disable_security()