"""
FsocietyDDoS v2.0 - Advanced DDoS Attack Framework

A comprehensive, professional-grade DDoS testing framework designed for 
security researchers, penetration testers, and cybersecurity professionals.
"""

__version__ = "2.0.0"
__author__ = "FsocietyDDoS Team"
__license__ = "MIT"

# Import core modules with absolute imports
try:
    import core
    import security
    import web
    import monitoring
    import layer4
    import layer7
    import cli
    import config
    import utils
except ImportError as e:
    print(f"Warning: Could not import module: {e}")

# Define public API
__all__ = [
    # Core functionality
    'get_framework_info',
    'create_integrated_framework', 
    'list_all_capabilities',
    
    # Module access
    'core',
    'security', 
    'web',
    'monitoring',
    'layer4',
    'layer7',
    'cli',
    'config',
    'utils'
]

def get_framework_info():
    """Get comprehensive framework information"""
    return {
        'name': 'FsocietyDDoS',
        'version': __version__,
        'author': __author__,
        'license': __license__,
        'description': 'Advanced DDoS Attack Framework with Security & Privacy Features',
        'modules': {
            'core': 'Core attack engine and configuration management',
            'security': 'Privacy protection and anti-forensics capabilities', 
            'web': 'Web-based attack methods and techniques',
            'monitoring': 'Real-time system monitoring and analytics',
            'layer4': 'Layer 4 network attacks (TCP/UDP)',
            'layer7': 'Layer 7 application attacks (HTTP/HTTPS)',
            'cli': 'Command-line interface and user interaction',
            'config': 'Configuration management and validation',
            'utils': 'Utility functions and helpers'
        },
        'features': {
            'privacy': ['VPN Integration', 'Tor Support', 'IP Masking', 'DNS Security'],
            'anti_forensics': ['Secure Deletion', 'Memory Protection', 'Log Cleaning', 'Registry Cleaning'],
            'web_attacks': ['HTTP Flood', 'Slowloris', 'Slow POST', 'WAF Bypass'],
            'evasion': ['Geographical Spoofing', 'Decoy Traffic', 'Behavioral Evasion', 'CDN Mimicry'],
            'monitoring': ['System Resources', 'Performance Metrics', 'Real-time Analytics', 'Reporting']
        }
    }

def create_integrated_framework(config=None):
    """Create integrated framework instance with all modules"""
    try:
        framework = {
            'core': core if 'core' in globals() else None,
            'security': security if 'security' in globals() else None,
            'web': web if 'web' in globals() else None,
            'monitoring': monitoring if 'monitoring' in globals() else None,
            'config': config or {}
        }
        return framework
    except Exception as e:
        print(f"Error creating integrated framework: {e}")
        return None

def list_all_capabilities():
    """List all available capabilities across modules"""
    capabilities = {
        'attack_methods': [
            'UDP Flood', 'SYN Flood', 'ICMP Flood', 'DNS Amplification', 'NTP Amplification',
            'HTTP Flood', 'Slowloris', 'Slow POST', 'CC Attacks', 'XML/JSON Bombs'
        ],
        'security_features': [
            'VPN Integration', 'Tor Network', 'IP Spoofing', 'Traffic Obfuscation',
            'Secure File Deletion', 'Memory Protection', 'Log Manipulation', 'Registry Cleaning'
        ],
        'evasion_techniques': [
            'Geographical Spoofing', 'Decoy Traffic Generation', 'CDN Mimicry',
            'Behavioral Evasion', 'Signature Evasion', 'WAF Bypass'
        ],
        'monitoring_capabilities': [
            'Real-time System Monitoring', 'Performance Analytics', 'Network Analysis',
            'Comprehensive Reporting', 'Database Integration'
        ]
    }
    return capabilities