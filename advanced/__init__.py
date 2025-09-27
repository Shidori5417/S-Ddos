"""
Advanced Attack Techniques Module
Sophisticated attack methods and evasion techniques
"""

from .geo_spoofing import (
    GeoSpoofingConfig,
    IPGeolocationDatabase,
    DecoyTrafficGenerator,
    GeoIPSpoofing,
    CDNMimicry,
    TrafficPatternMimicry,
    GeoSpoofingManager
)

from .waf_bypass import (
    WAFBypassConfig,
    EncodingBypass,
    ObfuscationBypass,
    FragmentationBypass,
    ProtocolConfusion,
    PolyglotPayloads,
    MutationFuzzer,
    WAFSignatureEvasion,
    AdvancedWAFBypass
)

__all__ = [
    # Geo Spoofing
    'GeoSpoofingConfig',
    'IPGeolocationDatabase',
    'DecoyTrafficGenerator',
    'GeoIPSpoofing',
    'CDNMimicry',
    'TrafficPatternMimicry',
    'GeoSpoofingManager',
    
    # WAF Bypass
    'WAFBypassConfig',
    'EncodingBypass',
    'ObfuscationBypass',
    'FragmentationBypass',
    'ProtocolConfusion',
    'PolyglotPayloads',
    'MutationFuzzer',
    'WAFSignatureEvasion',
    'AdvancedWAFBypass'
]

# Advanced technique registry
ADVANCED_TECHNIQUES = {
    'geo_spoofing': GeoSpoofingManager,
    'waf_bypass': AdvancedWAFBypass,
    'ip_geolocation': IPGeolocationDatabase,
    'decoy_traffic': DecoyTrafficGenerator,
    'cdn_mimicry': CDNMimicry,
    'traffic_mimicry': TrafficPatternMimicry,
    'encoding_bypass': EncodingBypass,
    'obfuscation_bypass': ObfuscationBypass,
    'fragmentation_bypass': FragmentationBypass,
    'protocol_confusion': ProtocolConfusion,
    'polyglot_payloads': PolyglotPayloads,
    'mutation_fuzzer': MutationFuzzer,
    'signature_evasion': WAFSignatureEvasion
}

def get_geo_spoofing_manager(config=None):
    """Get configured geo spoofing manager"""
    return GeoSpoofingManager(config)

def get_waf_bypass_manager(config=None):
    """Get configured WAF bypass manager"""
    return AdvancedWAFBypass(config)

def list_advanced_techniques():
    """List available advanced techniques"""
    return list(ADVANCED_TECHNIQUES.keys())