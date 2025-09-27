"""
FsocietyDDoS - Professional Modular DDoS Testing Framework
Core Module - Base classes and utilities
"""

__version__ = "2.0.0"
__author__ = "FsocietyDDoS Team"
__description__ = "Professional Modular DDoS Testing Framework"

from .base import BaseAttack, AttackResult
from .config import Config
from .logger import SecurityLogger as Logger
from .utils import NetworkUtils, SystemUtils
from .network_attacks import NetworkAttacks
from .advanced_layer4 import AdvancedLayer4Attacks

__all__ = [
    'BaseAttack',
    'AttackResult', 
    'Config',
    'Logger',
    'NetworkUtils',
    'SystemUtils',
    'NetworkAttacks',
    'AdvancedLayer4Attacks'
]