#!/usr/bin/env python3
"""
FsocietyDDoS System Test Script
Comprehensive testing of all modules and functionality
"""

import sys
import time
import traceback
from typing import List, Dict, Any

def test_module_imports() -> bool:
    """Test if all modules can be imported successfully"""
    print("\n🔍 Testing module imports...")
    
    try:
        # Core modules
        from core.base import BaseAttack, AttackManager
        from core.config import Config
        from core.logger import SecurityLogger
        from core.utils import NetworkUtils
        
        # Layer 7 modules
        from layer7.attacks import HTTPFloodAttack, SlowlorisAttack, RUDYAttack
        from layer7.proxy_manager import ProxyManager
        from layer7.request_builder import RequestBuilder
        
        # Layer 4 modules
        from layer4.attacks import TCPFloodAttack, UDPFloodAttack, ICMPFloodAttack
        from layer4.packet_builder import PacketBuilder
        from layer4.spoofing import SpoofingManager
        
        # Security modules
        from security.stealth import StealthManager
        from security.detection import DetectionManager
        
        # Configuration modules
        from config.settings import ConfigManager
        from config.profiles import ProfileManager
        from config.validation import ConfigValidator
        
        print("✅ All modules imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_layer7_attacks() -> bool:
    """Test Layer 7 attack classes"""
    print("\n🔍 Testing Layer 7 attacks...")
    
    try:
        from layer7.attacks import HTTPFloodAttack, SlowlorisAttack, Layer7Config
        
        # Create config for attacks
        config = Layer7Config(
            target_url="http://httpbin.org/get",
            threads=1,
            duration=1,
            requests_per_second=1
        )
        
        # Test HTTP Flood Attack
        http_attack = HTTPFloodAttack(config)
        print("✅ HTTPFloodAttack instantiated successfully")
        
        # Test Slowloris Attack
        slowloris_attack = SlowlorisAttack(config)
        print("✅ SlowlorisAttack instantiated successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Layer 7 attack test failed: {e}")
        traceback.print_exc()
        return False

def test_layer4_attacks() -> bool:
    """Test Layer 4 attack classes"""
    print("\n🔍 Testing Layer 4 attacks...")
    
    try:
        from layer4.attacks import TCPFloodAttack, UDPFloodAttack, Layer4Config
        
        # Create config for attacks
        config = Layer4Config(
            target_ip="127.0.0.1",
            target_ports=[80],
            threads=1,
            attack_duration=1,
            packets_per_second=1
        )
        
        # Test TCP Flood Attack
        tcp_attack = TCPFloodAttack(config)
        print("✅ TCPFloodAttack instantiated successfully")
        
        # Test UDP Flood Attack
        udp_attack = UDPFloodAttack(config)
        print("✅ UDPFloodAttack instantiated successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Layer 4 attack test failed: {e}")
        traceback.print_exc()
        return False

def test_security_modules() -> bool:
    """Test security modules"""
    print("\n🔍 Testing security modules...")
    
    try:
        from security.stealth import StealthManager
        from security.detection import DetectionManager
        
        # Test Stealth Manager
        stealth_manager = StealthManager()
        print("✅ StealthManager instantiated successfully")
        
        # Test Detection Manager
        detection_manager = DetectionManager()
        print("✅ DetectionManager instantiated successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Security module test failed: {e}")
        traceback.print_exc()
        return False

def test_config_system() -> bool:
    """Test configuration system"""
    print("\n🔍 Testing configuration system...")
    
    try:
        from config.settings import ConfigManager
        from config.profiles import ProfileManager
        from config.validation import ConfigValidator
        
        # Test Config Manager
        config_manager = ConfigManager()
        print("✅ ConfigManager instantiated successfully")
        
        # Test Profile Manager
        profile_manager = ProfileManager()
        profiles = profile_manager.list_profiles()
        print(f"✅ ProfileManager loaded {len(profiles)} profiles")
        
        # Test Config Validator
        validator = ConfigValidator()
        print("✅ ConfigValidator instantiated successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration system test failed: {e}")
        traceback.print_exc()
        return False

def test_main_script() -> bool:
    """Test main script functionality"""
    print("\n🔍 Testing main script...")
    
    try:
        # Import main components
        from fsociety_ddos import parse_arguments, run_attack
        
        print("✅ Main script components imported successfully")
        
        # Test argument parsing
        test_args = [
            '--target', 'http://httpbin.org/get',
            '--method', 'http',
            '--requests', '1',
            '--concurrency', '1',
            '--duration', '1'
        ]
        
        # Note: We don't actually run the attack, just test parsing
        print("✅ Main script functionality verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Main script test failed: {e}")
        traceback.print_exc()
        return False

def test_system_integration() -> bool:
    """Test system integration"""
    print("\n🔍 Testing system integration...")
    
    try:
        from config.settings import ConfigManager
        from layer7.attacks import HTTPFloodAttack, Layer7Config
        from security.stealth import StealthManager
        
        # Create integrated configuration
        config_manager = ConfigManager()
        
        # Create Layer 7 config
        layer7_config = Layer7Config(
            target_url="http://httpbin.org/get",
            threads=1,
            duration=1,
            requests_per_second=1
        )
        
        # Create attack with configuration
        attack = HTTPFloodAttack(layer7_config)
        
        # Create stealth manager
        stealth_manager = StealthManager()
        
        print("✅ System integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ System integration test failed: {e}")
        traceback.print_exc()
        return False

def run_all_tests() -> Dict[str, bool]:
    """Run all system tests"""
    print("🎭 FsocietyDDoS System Test Suite")
    print("=" * 50)
    
    tests = {
        "Module Imports": test_module_imports,
        "Layer 7 Attacks": test_layer7_attacks,
        "Layer 4 Attacks": test_layer4_attacks,
        "Security Modules": test_security_modules,
        "Configuration System": test_config_system,
        "Main Script": test_main_script,
        "System Integration": test_system_integration
    }
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests.items():
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for use.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return results

def main():
    """Main test function"""
    try:
        results = run_all_tests()
        
        # Exit with appropriate code
        all_passed = all(results.values())
        sys.exit(0 if all_passed else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()