"""
Layer 4 (Transport Layer) Attack Module
Professional DDoS testing tools for TCP/UDP protocols
"""

from .attacks import (
    UDPFloodAttack,
    TCPFloodAttack,
    ICMPFloodAttack,
    AmplificationAttack,
    Layer4Config
)

from .packet_builder import (
    PacketBuilder,
    TCPPacketBuilder,
    UDPPacketBuilder,
    ICMPPacketBuilder,
    PacketConfig
)

from .spoofing import (
    IPSpoofing,
    SourcePortSpoofing,
    SpoofingManager,
    SpoofingConfig
)

from .amplification import (
    DNSAmplification,
    NTPAmplification,
    SNMPAmplification,
    AmplificationManager
)

__all__ = [
    # Attack classes
    'UDPFloodAttack',
    'TCPFloodAttack',
    'ICMPFloodAttack',
    'AmplificationAttack',
    'Layer4Config',
    
    # Packet building
    'PacketBuilder',
    'TCPPacketBuilder',
    'UDPPacketBuilder',
    'ICMPPacketBuilder',
    'PacketConfig',
    
    # Spoofing
    'IPSpoofing',
    'SourcePortSpoofing',
    'SpoofingManager',
    'SpoofingConfig',
    
    # Amplification classes
    'DNSAmplification',
    'NTPAmplification',
    'SNMPAmplification',
    'AmplificationManager',
    
    # Utility functions
    'get_attack_class',
    'list_available_attacks',
    'get_recommended_attack'
]

# Layer 4 attack registry
LAYER4_ATTACKS = {
    'udp_flood': UDPFloodAttack,
    'tcp_flood': TCPFloodAttack,
    'icmp_flood': ICMPFloodAttack,
    'amplification': AmplificationAttack
}

# Attack categories for organization
ATTACK_CATEGORIES = {
    'flood': ['syn_flood', 'udp_flood', 'tcp_flood', 'icmp_flood'],
    'exhaustion': ['connection_exhaustion', 'slow_connection'],
    'fragmentation': ['fragmentation'],
    'reflection': ['reflection', 'amplification']
}

# Difficulty levels
ATTACK_DIFFICULTY = {
    'beginner': ['udp_flood', 'icmp_flood'],
    'intermediate': ['syn_flood', 'tcp_flood', 'fragmentation'],
    'advanced': ['connection_exhaustion', 'slow_connection'],
    'expert': ['reflection', 'amplification']
}


def get_attack_class(attack_name: str):
    """Get attack class by name"""
    return LAYER4_ATTACKS.get(attack_name.lower())


def list_available_attacks() -> dict:
    """List all available Layer 4 attacks"""
    return {
        name: {
            'class': attack_class,
            'description': attack_class.__doc__ or 'No description available',
            'category': _get_attack_category(name),
            'difficulty': _get_attack_difficulty(name)
        }
        for name, attack_class in LAYER4_ATTACKS.items()
    }


def get_attacks_by_category(category: str) -> list:
    """Get attacks by category"""
    return ATTACK_CATEGORIES.get(category.lower(), [])


def get_attacks_by_difficulty(difficulty: str) -> list:
    """Get attacks by difficulty level"""
    return ATTACK_DIFFICULTY.get(difficulty.lower(), [])


def get_recommended_attack(target_info: dict) -> str:
    """Get recommended attack based on target information"""
    # Simple recommendation logic
    if target_info.get('has_firewall', False):
        return 'fragmentation'
    elif target_info.get('protocol') == 'tcp':
        return 'syn_flood'
    elif target_info.get('protocol') == 'udp':
        return 'udp_flood'
    else:
        return 'syn_flood'  # Default


def _get_attack_category(attack_name: str) -> str:
    """Get category for an attack"""
    for category, attacks in ATTACK_CATEGORIES.items():
        if attack_name in attacks:
            return category
    return 'unknown'


def _get_attack_difficulty(attack_name: str) -> str:
    """Get difficulty level for an attack"""
    for difficulty, attacks in ATTACK_DIFFICULTY.items():
        if attack_name in attacks:
            return difficulty
    return 'unknown'