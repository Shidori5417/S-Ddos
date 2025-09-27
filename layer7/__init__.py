"""
Layer 7 (Application Layer) Attack Module

This module provides HTTP/HTTPS based attack methods with advanced
evasion techniques and proxy support.
"""

from .attacks import (
    HTTPFloodAttack,
    SlowlorisAttack,
    RUDYAttack
)

from .advanced_http import AdvancedLayer7Attacks
from .proxy_manager import ProxyManager, ProxyScanner, ProxyTester
from .request_builder import RequestBuilder, HeaderGenerator, PayloadGenerator
from .evasion import HTTPEvasion, TimingEvasion, ProtocolEvasion, WAFEvasion, Layer7EvasionManager

__all__ = [
    # Attack classes
    'HTTPFloodAttack',
    'SlowlorisAttack', 
    'RUDYAttack',
    'AdvancedLayer7Attacks',
    
    # Proxy management
    'ProxyManager',
    'ProxyScanner',
    'ProxyTester',
    
    # Request building
    'RequestBuilder',
    'HeaderGenerator',
    'PayloadGenerator',
    
    # Evasion techniques
    'HTTPEvasion',
    'TimingEvasion',
    'ProtocolEvasion',
    'WAFEvasion',
    'Layer7EvasionManager'
]

# Available attack methods
LAYER7_METHODS = {
    'http-flood': HTTPFloodAttack,
    'slowloris': SlowlorisAttack,
    'rudy': RUDYAttack,
    'advanced-http': AdvancedLayer7Attacks
}

def get_attack_class(method: str):
    """Get attack class by method name"""
    return LAYER7_METHODS.get(method.lower())

def list_methods():
    """List available Layer 7 attack methods"""
    return list(LAYER7_METHODS.keys())