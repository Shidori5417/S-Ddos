"""
Configuration Module
Centralized configuration management for FsocietyDDoS
"""

from .settings import (
    GlobalConfig,
    AttackConfig,
    SecurityConfig,
    NetworkConfig,
    LoggingConfig,
    ConfigManager
)

from .profiles import (
    AttackProfile,
    ProfileManager,
    DEFAULT_PROFILES
)

from .validation import (
    ConfigValidator,
    ValidationError,
    validate_config
)

__all__ = [
    # Configuration classes
    'GlobalConfig',
    'AttackConfig', 
    'SecurityConfig',
    'NetworkConfig',
    'LoggingConfig',
    'ConfigManager',
    
    # Profile management
    'AttackProfile',
    'ProfileManager',
    'DEFAULT_PROFILES',
    
    # Validation
    'ConfigValidator',
    'ValidationError',
    'validate_config'
]

# Configuration system registry
CONFIG_SYSTEMS = {
    'global': {
        'class': GlobalConfig,
        'description': 'Global application settings',
        'required': True
    },
    'attack': {
        'class': AttackConfig,
        'description': 'Attack-specific configurations',
        'required': True
    },
    'security': {
        'class': SecurityConfig,
        'description': 'Security and stealth settings',
        'required': True
    },
    'network': {
        'class': NetworkConfig,
        'description': 'Network and connection settings',
        'required': True
    },
    'logging': {
        'class': LoggingConfig,
        'description': 'Logging and monitoring settings',
        'required': False
    }
}


def create_default_config():
    """Create default configuration"""
    return ConfigManager()


def load_config_from_file(config_path: str):
    """Load configuration from file"""
    manager = ConfigManager()
    manager.load_from_file(config_path)
    return manager


def create_config_from_profile(profile_name: str):
    """Create configuration from predefined profile"""
    profile_manager = ProfileManager()
    profile = profile_manager.get_profile(profile_name)
    
    manager = ConfigManager()
    manager.apply_profile(profile)
    return manager


def list_config_systems():
    """List available configuration systems"""
    return list(CONFIG_SYSTEMS.keys())


def get_config_info(system_name: str):
    """Get information about a configuration system"""
    if system_name not in CONFIG_SYSTEMS:
        raise ValueError(f"Unknown configuration system: {system_name}")
    
    return CONFIG_SYSTEMS[system_name]


def validate_full_config(config_manager):
    """Validate complete configuration"""
    validator = ConfigValidator()
    return validator.validate_full_config(config_manager)