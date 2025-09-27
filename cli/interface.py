"""
Professional CLI interface for FsocietyDDoS
"""

import os
import sys
import time
import threading
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from core.logger import logger
from core.config import Config
from core.utils import SystemUtils, get_timestamp
from security.evasion import EvasionManager
from cli.colors import ModernCLI, StyleManager, Colors, console
from rich.panel import Panel
from rich.table import Table


class MenuSystem:
    """Advanced menu system with navigation"""
    
    def __init__(self):
        self.menus = {}
        self.current_menu = None
        self.menu_history = []
        self.running = False
        self.modern_cli = ModernCLI()
        self.style_manager = StyleManager()
        
    def add_menu(self, name: str, title: str, options: List[Dict[str, Any]]):
        """Add menu to system"""
        self.menus[name] = {
            'title': title,
            'options': options
        }
    
    def show_menu(self, menu_name: str) -> Optional[str]:
        """Display menu and get user selection"""
        if menu_name not in self.menus:
            return None
        
        menu = self.menus[menu_name]
        self.current_menu = menu_name
        
        # Clear screen and show header
        SystemUtils.clear_screen()
        self._show_header()
        
        # Show menu title
        print(f"\n{'='*60}")
        print(f"  {menu['title']}")
        print(f"{'='*60}")
        
        # Show options
        for i, option in enumerate(menu['options'], 1):
            status = ""
            if option.get('enabled', True):
                status = "✓" if option.get('active', False) else " "
            else:
                status = "✗"
            
            print(f"  [{i}] {status} {option['text']}")
            if option.get('description'):
                print(f"      {option['description']}")
        
        # Show navigation options
        print(f"\n{'='*60}")
        if self.menu_history:
            print("  [b] Back to previous menu")
        print("  [q] Quit")
        print(f"{'='*60}")
        
        # Get user input
        try:
            choice = input("\n  Select option: ").strip().lower()
            
            if choice == 'q':
                return 'quit'
            elif choice == 'b' and self.menu_history:
                return 'back'
            elif choice.isdigit():
                option_index = int(choice) - 1
                if 0 <= option_index < len(menu['options']):
                    option = menu['options'][option_index]
                    if option.get('enabled', True):
                        return option.get('action', choice)
            
            return None
            
        except KeyboardInterrupt:
            return 'quit'
        except Exception:
            return None
    
    def navigate_to(self, menu_name: str):
        """Navigate to specific menu"""
        if self.current_menu:
            self.menu_history.append(self.current_menu)
        self.current_menu = menu_name
    
    def go_back(self):
        """Go back to previous menu"""
        if self.menu_history:
            self.current_menu = self.menu_history.pop()
            return True
        return False
    
    def _show_header(self):
        """Show modern application header"""
        # ASCII Art Header
        header_text = """[bold cyan]
    ███████╗███████╗ ██████╗  ██████╗██╗███████╗████████╗██╗   ██╗
    ██╔════╝██╔════╝██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
    █████╗  ███████╗██║   ██║██║     ██║█████╗     ██║    ╚████╔╝ 
    ██╔══╝  ╚════██║██║   ██║██║     ██║██╔══╝     ██║     ╚██╔╝  
    ██║     ███████║╚██████╔╝╚██████╗██║███████╗   ██║      ██║   
    ╚═╝     ╚══════╝ ╚═════╝  ╚═════╝╚═╝╚══════╝   ╚═╝      ╚═╝   
[/]
[bold magenta]                    DDoS Testing Framework v2.0[/]
[dim]                    Professional Security Testing Tool[/]"""
        
        console.print(Panel(header_text, style=f"bold {Colors.PRIMARY}", width=80))
        
        # Show system info
        system_info = SystemUtils.get_system_info()
        info_table = Table(show_header=False, box=None)
        info_table.add_column("Label", style=f"bold {Colors.ACCENT}")
        info_table.add_column("Value", style=f"bold {Colors.SUCCESS}")
        
        info_table.add_row("System:", f"{system_info['platform']}")
        info_table.add_row("User:", f"{system_info['user']}")
        info_table.add_row("Time:", f"{get_timestamp()}")
        
        console.print(info_table)
        
        # Show warnings
        if not SystemUtils.is_admin():
            console.print(f"[bold {Colors.WARNING}]⚠️  WARNING: Not running with administrator privileges[/]")
        
        console.print(f"[bold {Colors.ERROR}]⚠️  FOR AUTHORIZED TESTING ONLY - USE RESPONSIBLY[/]")


class CLIInterface:
    """Main CLI interface controller"""
    
    def __init__(self, config: Config):
        self.config = config
        self.menu_system = MenuSystem()
        self.evasion_manager = EvasionManager()
        self.modern_cli = ModernCLI()
        self.style_manager = StyleManager()
        self.running = False
        self.current_layer = None
        self.attack_modules = {}
        
        self._setup_menus()
        self._setup_signal_handlers()
    
    def _setup_menus(self):
        """Setup all menu structures"""
        
        # Main menu
        self.menu_system.add_menu('main', 'MAIN MENU', [
            {
                'text': 'Layer 4 Attacks (Network Layer)',
                'description': 'TCP/UDP/ICMP flood attacks, SYN flood, etc.',
                'action': 'layer4_menu',
                'enabled': True
            },
            {
                'text': 'Layer 7 Attacks (Application Layer)', 
                'description': 'HTTP/HTTPS attacks with proxy support',
                'action': 'layer7_menu',
                'enabled': True
            },
            {
                'text': 'Security & Evasion Settings',
                'description': 'Configure stealth mode and evasion techniques',
                'action': 'security_menu',
                'enabled': True
            },
            {
                'text': 'System Configuration',
                'description': 'Configure attack parameters and settings',
                'action': 'config_menu',
                'enabled': True
            },
            {
                'text': 'View Logs & Reports',
                'description': 'View attack logs and generate reports',
                'action': 'logs_menu',
                'enabled': True
            }
        ])
        
        # Layer 4 menu
        self.menu_system.add_menu('layer4_menu', 'LAYER 4 ATTACKS', [
            {
                'text': 'TCP SYN Flood',
                'description': 'High-volume TCP SYN packet flood',
                'action': 'tcp_syn_flood',
                'enabled': True
            },
            {
                'text': 'UDP Flood',
                'description': 'UDP packet flood attack',
                'action': 'udp_flood', 
                'enabled': True
            },
            {
                'text': 'ICMP Flood',
                'description': 'ICMP ping flood attack',
                'action': 'icmp_flood',
                'enabled': True
            },
            {
                'text': 'TCP ACK Flood',
                'description': 'TCP ACK packet flood',
                'action': 'tcp_ack_flood',
                'enabled': True
            },
            {
                'text': 'Mixed Protocol Attack',
                'description': 'Combined TCP/UDP/ICMP attack',
                'action': 'mixed_protocol',
                'enabled': True
            },
            {
                'text': 'Advanced Layer 4 Options',
                'description': 'Configure advanced Layer 4 parameters',
                'action': 'layer4_config',
                'enabled': True
            }
        ])
        
        # Layer 7 menu
        self.menu_system.add_menu('layer7_menu', 'LAYER 7 ATTACKS', [
            {
                'text': 'HTTP GET Flood',
                'description': 'High-volume HTTP GET requests',
                'action': 'http_get_flood',
                'enabled': True
            },
            {
                'text': 'HTTP POST Flood',
                'description': 'HTTP POST request flood',
                'action': 'http_post_flood',
                'enabled': True
            },
            {
                'text': 'Slowloris Attack',
                'description': 'Slow HTTP connection attack',
                'action': 'slowloris',
                'enabled': True
            },
            {
                'text': 'HTTP/2 Flood',
                'description': 'HTTP/2 protocol flood attack',
                'action': 'http2_flood',
                'enabled': True
            },
            {
                'text': 'WebSocket Flood',
                'description': 'WebSocket connection flood',
                'action': 'websocket_flood',
                'enabled': True
            },
            {
                'text': 'Proxy Management',
                'description': 'Scan, test, and manage proxy lists',
                'action': 'proxy_menu',
                'enabled': True
            },
            {
                'text': 'Advanced Layer 7 Options',
                'description': 'Configure advanced Layer 7 parameters',
                'action': 'layer7_config',
                'enabled': True
            }
        ])
        
        # Security menu
        self.menu_system.add_menu('security_menu', 'SECURITY & EVASION', [
            {
                'text': 'Enable Stealth Mode',
                'description': 'Activate comprehensive stealth techniques',
                'action': 'enable_stealth',
                'enabled': True
            },
            {
                'text': 'Configure Anti-Detection',
                'description': 'Setup anti-detection techniques',
                'action': 'anti_detection_config',
                'enabled': True
            },
            {
                'text': 'Traffic Obfuscation',
                'description': 'Configure traffic obfuscation methods',
                'action': 'traffic_obfuscation',
                'enabled': True
            },
            {
                'text': 'IP Spoofing Settings',
                'description': 'Configure IP address spoofing',
                'action': 'ip_spoofing_config',
                'enabled': True
            },
            {
                'text': 'Timing Randomization',
                'description': 'Configure timing-based evasion',
                'action': 'timing_config',
                'enabled': True
            }
        ])
        
        # Proxy menu
        self.menu_system.add_menu('proxy_menu', 'PROXY MANAGEMENT', [
            {
                'text': 'Scan for Proxies',
                'description': 'Automatically scan for working proxies',
                'action': 'proxy_scan',
                'enabled': True
            },
            {
                'text': 'Test Proxy List',
                'description': 'Test existing proxy list for validity',
                'action': 'proxy_test',
                'enabled': True
            },
            {
                'text': 'Load Proxy File',
                'description': 'Load proxies from file',
                'action': 'proxy_load',
                'enabled': True
            },
            {
                'text': 'View Proxy Statistics',
                'description': 'Show proxy performance statistics',
                'action': 'proxy_stats',
                'enabled': True
            },
            {
                'text': 'Clear Proxy List',
                'description': 'Clear all loaded proxies',
                'action': 'proxy_clear',
                'enabled': True
            }
        ])
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        import signal
        
        def signal_handler(signum, frame):
            logger.info("Received shutdown signal, cleaning up...")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
    
    def run(self):
        """Run the CLI interface"""
        self.running = True
        logger.info("Starting FsocietyDDoS CLI interface")
        
        # Set terminal title
        SystemUtils.set_terminal_title("FsocietyDDoS - Professional DDoS Testing Framework")
        
        current_menu = 'main'
        
        while self.running:
            try:
                action = self.menu_system.show_menu(current_menu)
                
                if action == 'quit':
                    self.shutdown()
                    break
                elif action == 'back':
                    if self.menu_system.go_back():
                        current_menu = self.menu_system.current_menu
                    continue
                elif action is None:
                    self._show_error("Invalid selection. Please try again.")
                    time.sleep(1)
                    continue
                
                # Handle menu navigation
                if action.endswith('_menu'):
                    self.menu_system.navigate_to(action)
                    current_menu = action
                    continue
                
                # Handle actions
                result = self._handle_action(action)
                if result == 'menu_change':
                    current_menu = self.menu_system.current_menu
                elif result == 'quit':
                    break
                
                # Pause before returning to menu
                if result != 'no_pause':
                    input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                self.shutdown()
                break
            except Exception as e:
                logger.error(f"CLI error: {e}")
                self._show_error(f"An error occurred: {e}")
                time.sleep(2)
    
    def _handle_action(self, action: str) -> str:
        """Handle menu actions"""
        try:
            if action == 'enable_stealth':
                return self._enable_stealth_mode()
            elif action == 'proxy_scan':
                return self._proxy_scan()
            elif action.startswith('tcp_') or action.startswith('udp_') or action.startswith('icmp_'):
                return self._launch_layer4_attack(action)
            elif action.startswith('http_') or action == 'slowloris' or action == 'websocket_flood':
                return self._launch_layer7_attack(action)
            else:
                self._show_info(f"Action '{action}' is not yet implemented.")
                return 'continue'
                
        except Exception as e:
            logger.error(f"Action handler error: {e}")
            self._show_error(f"Failed to execute action: {e}")
            return 'continue'
    
    def _enable_stealth_mode(self) -> str:
        """Enable stealth mode"""
        try:
            print("\n" + "="*60)
            print("  ENABLING STEALTH MODE")
            print("="*60)
            
            print("  [1/5] Activating anti-detection techniques...")
            self.evasion_manager.anti_detection.enable_all_techniques()
            time.sleep(0.5)
            
            print("  [2/5] Enabling traffic obfuscation...")
            self.evasion_manager.enable_evasion('traffic_shaping')
            time.sleep(0.5)
            
            print("  [3/5] Configuring timing randomization...")
            self.evasion_manager.enable_evasion('timing_attacks')
            time.sleep(0.5)
            
            print("  [4/5] Starting decoy traffic...")
            self.evasion_manager.enable_evasion('decoy_traffic', decoy_count=2)
            time.sleep(0.5)
            
            print("  [5/5] Activating stealth logging...")
            logger.enable_stealth_mode()
            time.sleep(0.5)
            
            print("\n  ✓ Stealth mode activated successfully!")
            print("    - Anti-detection techniques enabled")
            print("    - Traffic obfuscation active")
            print("    - Timing randomization enabled")
            print("    - Decoy traffic running")
            print("    - Stealth logging active")
            
            return 'continue'
            
        except Exception as e:
            logger.error(f"Stealth mode activation failed: {e}")
            self._show_error(f"Failed to enable stealth mode: {e}")
            return 'continue'
    
    def _proxy_scan(self) -> str:
        """Scan for proxies"""
        print("\n" + "="*60)
        print("  PROXY SCANNING")
        print("="*60)
        print("  This feature will be implemented in the Layer 7 module.")
        print("  It will automatically scan for working proxies from multiple sources.")
        return 'continue'
    
    def _launch_layer4_attack(self, attack_type: str) -> str:
        """Launch Layer 4 attack"""
        print(f"\n" + "="*60)
        print(f"  LAYER 4 ATTACK: {attack_type.upper().replace('_', ' ')}")
        print("="*60)
        print("  This feature will be implemented in the Layer 4 module.")
        print(f"  Attack type: {attack_type}")
        return 'continue'
    
    def _launch_layer7_attack(self, attack_type: str) -> str:
        """Launch Layer 7 attack"""
        print(f"\n" + "="*60)
        print(f"  LAYER 7 ATTACK: {attack_type.upper().replace('_', ' ')}")
        print("="*60)
        print("  This feature will be implemented in the Layer 7 module.")
        print(f"  Attack type: {attack_type}")
        return 'continue'
    
    def _show_error(self, message: str):
        """Show error message"""
        print(f"\n  ❌ ERROR: {message}")
    
    def _show_info(self, message: str):
        """Show info message"""
        print(f"\n  ℹ️  INFO: {message}")
    
    def _show_success(self, message: str):
        """Show success message"""
        print(f"\n  ✅ SUCCESS: {message}")
    
    def shutdown(self):
        """Shutdown CLI interface"""
        if not self.running:
            return
        
        self.running = False
        logger.info("Shutting down CLI interface")
        
        try:
            # Cleanup evasion manager
            self.evasion_manager.cleanup()
            
            # Clear screen
            SystemUtils.clear_screen()
            
            print("\n" + "="*60)
            print("  FSOCIETY DDOS - SHUTDOWN")
            print("="*60)
            print("  Thank you for using FsocietyDDoS")
            print("  All operations have been terminated safely.")
            print("  Remember: Use this tool responsibly and legally.")
            print("="*60)
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
        
        logger.info("CLI interface shutdown complete")