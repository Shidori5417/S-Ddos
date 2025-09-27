"""
Command handlers for CLI interface
"""

import sys
import time
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from core.config import Config
from core.logger import logger
from core.utils import ValidationUtils, NetworkUtils
from cli.display import DisplayManager, AttackDisplay, ProgressBar
from cli.colors import ModernCLI, StyleManager, Colors, console
from security.evasion import EvasionManager


@dataclass
class CommandResult:
    """Result of command execution"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class CommandHandler:
    """Handle CLI commands"""
    
    def __init__(self, config: Config):
        self.config = config
        self.evasion_manager = EvasionManager()
        self.modern_cli = ModernCLI()
        self.style_manager = StyleManager()
        self.current_attack = None
        
        # Command registry
        self.commands = {
            'help': self.cmd_help,
            'config': self.cmd_config,
            'proxy': self.cmd_proxy,
            'scan': self.cmd_scan,
            'attack': self.cmd_attack,
            'stop': self.cmd_stop,
            'status': self.cmd_status,
            'stealth': self.cmd_stealth,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit
        }
    
    def execute_command(self, command: str, args: List[str]) -> CommandResult:
        """Execute a command with arguments"""
        try:
            if command not in self.commands:
                return CommandResult(
                    success=False,
                    message=f"Unknown command: {command}. Type 'help' for available commands."
                )
            
            return self.commands[command](args)
            
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return CommandResult(
                success=False,
                message=f"Command failed: {str(e)}"
            )
    
    def cmd_help(self, args: List[str]) -> CommandResult:
        """Show modern colorized help information"""
        console.clear()
        
        if args and args[0] in self.commands:
            # Show specific command help
            command = args[0]
            self._show_command_help(command)
        else:
            # Show general help
            self._show_general_help()
        
        return CommandResult(success=True, message="Help displayed")
    
    def cmd_config(self, args: List[str]) -> CommandResult:
        """Manage configuration"""
        if not args:
            return self._show_config()
        
        action = args[0].lower()
        
        if action == 'show':
            return self._show_config()
        elif action == 'set' and len(args) >= 3:
            return self._set_config(args[1], args[2])
        elif action == 'get' and len(args) >= 2:
            return self._get_config(args[1])
        elif action == 'reset':
            return self._reset_config()
        elif action == 'save':
            return self._save_config()
        elif action == 'load':
            return self._load_config()
        elif action == 'captcha':
            return self._handle_captcha_config(args[1:])
        elif action == 'evasion':
            return self._handle_evasion_config(args[1:])
        elif action == 'proxy':
            return self._handle_proxy_config(args[1:])
        else:
            return CommandResult(
                success=False,
                message="Usage: config [show|set|get|reset|save|load|captcha|evasion|proxy] [key] [value]"
            )
    
    def cmd_proxy(self, args: List[str]) -> CommandResult:
        """Manage proxy operations"""
        if not args:
            return CommandResult(
                success=False,
                message="Usage: proxy [scan|test|list|clear] [options]"
            )
        
        action = args[0].lower()
        
        if action == 'scan':
            return self._scan_proxies(args[1:])
        elif action == 'test':
            return self._test_proxies(args[1:])
        elif action == 'list':
            return self._list_proxies()
        elif action == 'clear':
            return self._clear_proxies()
        else:
            return CommandResult(
                success=False,
                message="Usage: proxy [scan|test|list|clear]"
            )
    
    def cmd_scan(self, args: List[str]) -> CommandResult:
        """Scan target for information"""
        if not args:
            return CommandResult(
                success=False,
                message="Usage: scan <target> [options]"
            )
        
        target = args[0]
        
        # Validate target
        if not ValidationUtils.is_valid_target(target):
            return CommandResult(
                success=False,
                message="Invalid target format"
            )
        
        return self._scan_target(target, args[1:])
    
    def cmd_attack(self, args: List[str]) -> CommandResult:
        """Start attack"""
        if len(args) < 2:
            return CommandResult(
                success=False,
                message="Usage: attack <layer4|layer7> <target> [method] [options]"
            )
        
        layer = args[0].lower()
        target = args[1]
        method = args[2] if len(args) > 2 else None
        
        # Validate inputs
        if layer not in ['layer4', 'layer7']:
            return CommandResult(
                success=False,
                message="Layer must be 'layer4' or 'layer7'"
            )
        
        if not ValidationUtils.is_valid_target(target):
            return CommandResult(
                success=False,
                message="Invalid target format"
            )
        
        return self._start_attack(layer, target, method, args[3:])
    
    def cmd_stop(self, args: List[str]) -> CommandResult:
        """Stop current attack"""
        if not self.current_attack:
            return CommandResult(
                success=False,
                message="No attack is currently running"
            )
        
        return self._stop_attack()
    
    def cmd_status(self, args: List[str]) -> CommandResult:
        """Show system status"""
        return self._show_status()
    
    def cmd_stealth(self, args: List[str]) -> CommandResult:
        """Manage stealth features"""
        if not args:
            return self._show_stealth_status()
        
        action = args[0].lower()
        
        if action == 'enable':
            return self._enable_stealth()
        elif action == 'disable':
            return self._disable_stealth()
        elif action == 'status':
            return self._show_stealth_status()
        else:
            return CommandResult(
                success=False,
                message="Usage: stealth [enable|disable|status]"
            )
    
    def cmd_exit(self, args: List[str]) -> CommandResult:
        """Exit the application"""
        if self.current_attack:
            if DisplayManager.confirm_action("Attack is running. Stop and exit?"):
                self._stop_attack()
            else:
                return CommandResult(
                    success=False,
                    message="Exit cancelled"
                )
        
        DisplayManager.show_status("info", "Cleaning up and exiting...")
        
        # Cleanup
        self.evasion_manager.cleanup()
        
        sys.exit(0)
    
    def _show_config(self) -> CommandResult:
        """Show current configuration"""
        config_data = {
            'General': {
                'Debug Mode': self.config.debug,
                'Threads': self.config.threads,
                'Timeout': self.config.timeout,
                'User Agent': self.config.user_agent
            },
            'Layer 4': {
                'Packet Size': self.config.layer4.packet_size,
                'Send Rate': self.config.layer4.send_rate,
                'Spoofing': self.config.layer4.spoofing
            },
            'Layer 7': {
                'Request Rate': self.config.layer7.request_rate,
                'Keep Alive': self.config.layer7.keep_alive,
                'Follow Redirects': self.config.layer7.follow_redirects
            },
            'Security': {
                'Stealth Mode': self.config.security.stealth_mode,
                'Anti Forensics': self.config.security.anti_forensics,
                'Process Hiding': self.config.security.process_hiding
            }
        }
        
        for section, settings in config_data.items():
            DisplayManager.show_section(section)
            for key, value in settings.items():
                print(f"  {key}: {value}")
        
        return CommandResult(success=True, message="Configuration displayed")
    
    def _set_config(self, key: str, value: str) -> CommandResult:
        """Set configuration value"""
        try:
            # Convert value to appropriate type
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif '.' in value and value.replace('.', '').isdigit():
                value = float(value)
            
            # Set configuration
            self.config.set(key, value)
            
            return CommandResult(
                success=True,
                message=f"Configuration updated: {key} = {value}"
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to set configuration: {e}"
            )
    
    def _get_config(self, key: str) -> CommandResult:
        """Get configuration value"""
        try:
            value = self.config.get(key)
            print(f"  {key}: {value}")
            
            return CommandResult(
                success=True,
                message="Configuration value retrieved",
                data={'key': key, 'value': value}
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to get configuration: {e}"
            )
    
    def _scan_proxies(self, args: List[str]) -> CommandResult:
        """Scan for proxies"""
        DisplayManager.show_status("info", "Starting proxy scan...")
        
        # Create progress bar
        progress = ProgressBar(total=100, title="Proxy Scan")
        progress.start()
        
        try:
            # Simulate proxy scanning
            sources = ['free-proxy-list', 'proxy-nova', 'spys-one']
            found_proxies = []
            
            for i, source in enumerate(sources):
                progress.update((i + 1) * 33, {'source': source})
                
                # Simulate scanning delay
                time.sleep(2)
                
                # Add some dummy proxies
                for j in range(10):
                    proxy = f"192.168.{i}.{j}:808{j}"
                    found_proxies.append(proxy)
            
            progress.finish()
            
            DisplayManager.show_list(found_proxies[:10], "Found Proxies (showing first 10)")
            
            return CommandResult(
                success=True,
                message=f"Found {len(found_proxies)} proxies",
                data={'proxies': found_proxies}
            )
            
        except Exception as e:
            progress.finish()
            return CommandResult(
                success=False,
                message=f"Proxy scan failed: {e}"
            )
    
    def _test_proxies(self, args: List[str]) -> CommandResult:
        """Test proxy connectivity"""
        DisplayManager.show_status("info", "Testing proxy connectivity...")
        
        # Simulate proxy testing
        test_results = [
            ['192.168.1.1:8080', 'HTTP', '150ms', 'Working'],
            ['192.168.1.2:8080', 'HTTPS', '200ms', 'Working'],
            ['192.168.1.3:8080', 'SOCKS5', 'Timeout', 'Failed'],
        ]
        
        DisplayManager.show_table(
            headers=['Proxy', 'Type', 'Response Time', 'Status'],
            rows=test_results,
            title="Proxy Test Results"
        )
        
        return CommandResult(success=True, message="Proxy testing completed")
    
    def _list_proxies(self) -> CommandResult:
        """List available proxies"""
        # Simulate proxy list
        proxies = [
            "192.168.1.1:8080 (HTTP)",
            "192.168.1.2:8080 (HTTPS)",
            "192.168.1.3:1080 (SOCKS5)"
        ]
        
        DisplayManager.show_list(proxies, "Available Proxies")
        
        return CommandResult(
            success=True,
            message=f"{len(proxies)} proxies available"
        )
    
    def _clear_proxies(self) -> CommandResult:
        """Clear proxy list"""
        if DisplayManager.confirm_action("Clear all proxies?"):
            DisplayManager.show_status("success", "Proxy list cleared")
            return CommandResult(success=True, message="Proxy list cleared")
        else:
            return CommandResult(success=False, message="Operation cancelled")
    
    def _scan_target(self, target: str, options: List[str]) -> CommandResult:
        """Scan target for information"""
        DisplayManager.show_status("info", f"Scanning target: {target}")
        
        # Simulate target scanning
        DisplayManager.show_loading("Performing reconnaissance", 3.0)
        
        scan_results = {
            'Target': target,
            'IP Address': NetworkUtils.resolve_hostname(target) or "Unknown",
            'Open Ports': "80, 443, 8080",
            'Server': "nginx/1.18.0",
            'Technologies': "PHP, MySQL",
            'Security Headers': "Partial",
            'WAF Detected': "No"
        }
        
        DisplayManager.show_stats(scan_results, "Target Information")
        
        return CommandResult(
            success=True,
            message="Target scan completed",
            data=scan_results
        )
    
    def _start_attack(self, layer: str, target: str, method: Optional[str], options: List[str]) -> CommandResult:
        """Start attack"""
        if self.current_attack:
            return CommandResult(
                success=False,
                message="Another attack is already running. Stop it first."
            )
        
        # Show attack configuration
        attack_config = {
            'layer': layer,
            'target': target,
            'method': method or 'default',
            'threads': self.config.threads,
            'duration': '60s'
        }
        
        DisplayManager.show_attack_info(layer, target, attack_config)
        
        if not DisplayManager.confirm_action("Start attack with these settings?"):
            return CommandResult(success=False, message="Attack cancelled")
        
        # Start attack display
        self.current_attack = AttackDisplay(layer, target)
        self.current_attack.start_display()
        
        # Simulate attack
        self._simulate_attack()
        
        return CommandResult(
            success=True,
            message="Attack started",
            data=attack_config
        )
    
    def _simulate_attack(self):
        """Simulate attack execution"""
        import threading
        
        def attack_worker():
            for i in range(60):  # 60 seconds
                if not self.current_attack or not self.current_attack.running:
                    break
                
                # Simulate attack statistics
                self.current_attack.update_stats(
                    requests_sent=100,
                    responses_received=95,
                    errors=5,
                    bytes_sent=1024 * 100,
                    bytes_received=1024 * 50
                )
                
                time.sleep(1)
            
            # Stop attack
            if self.current_attack:
                self.current_attack.stop_display()
                self.current_attack = None
        
        thread = threading.Thread(target=attack_worker, daemon=True)
        thread.start()
    
    def _stop_attack(self) -> CommandResult:
        """Stop current attack"""
        if self.current_attack:
            self.current_attack.stop_display()
            self.current_attack = None
            
            DisplayManager.show_status("success", "Attack stopped")
            return CommandResult(success=True, message="Attack stopped")
        
        return CommandResult(success=False, message="No attack is running")
    
    def _show_status(self) -> CommandResult:
        """Show system status"""
        status_info = {
            'System Status': 'Online',
            'Attack Status': 'Running' if self.current_attack else 'Idle',
            'Stealth Mode': 'Enabled' if self.config.security.stealth_mode else 'Disabled',
            'Available Proxies': '15',
            'Memory Usage': '45.2 MB',
            'CPU Usage': '12.5%',
            'Network Status': 'Connected'
        }
        
        DisplayManager.show_stats(status_info, "System Status")
        
        return CommandResult(success=True, message="Status displayed")
    
    def _show_stealth_status(self) -> CommandResult:
        """Show stealth mode status"""
        stealth_info = {
            'Stealth Mode': 'Enabled' if self.config.security.stealth_mode else 'Disabled',
            'Process Hiding': 'Active' if self.config.security.process_hiding else 'Inactive',
            'Anti Forensics': 'Enabled' if self.config.security.anti_forensics else 'Disabled',
            'Memory Encryption': 'Active',
            'Network Obfuscation': 'Enabled'
        }
        
        DisplayManager.show_stats(stealth_info, "Stealth Status")
        
        return CommandResult(success=True, message="Stealth status displayed")
    
    def _enable_stealth(self) -> CommandResult:
        """Enable stealth mode"""
        try:
            self.config.security.stealth_mode = True
            self.evasion_manager.enable_stealth_mode()
            
            DisplayManager.show_status("success", "Stealth mode enabled")
            return CommandResult(success=True, message="Stealth mode enabled")
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to enable stealth mode: {e}"
            )
    
    def _disable_stealth(self) -> CommandResult:
        """Disable stealth mode"""
        try:
            self.config.security.stealth_mode = False
            self.evasion_manager.disable_stealth_mode()
            
            DisplayManager.show_status("success", "Stealth mode disabled")
            return CommandResult(success=True, message="Stealth mode disabled")
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to disable stealth mode: {e}"
            )
    
    def _reset_config(self) -> CommandResult:
        """Reset configuration to defaults"""
        if DisplayManager.confirm_action("Reset all configuration to defaults?"):
            self.config = Config()
            DisplayManager.show_status("success", "Configuration reset to defaults")
            return CommandResult(success=True, message="Configuration reset")
        else:
            return CommandResult(success=False, message="Reset cancelled")
    
    def _save_config(self) -> CommandResult:
        """Save configuration to file"""
        try:
            self.config.save_config()
            DisplayManager.show_status("success", "Configuration saved")
            return CommandResult(success=True, message="Configuration saved")
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to save configuration: {e}"
            )
    
    def _load_config(self) -> CommandResult:
        """Load configuration from file"""
        try:
            self.config.load_config()
            DisplayManager.show_status("success", "Configuration loaded")
            return CommandResult(success=True, message="Configuration loaded")
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to load configuration: {e}"
            )
    
    def _handle_captcha_config(self, args: List[str]) -> CommandResult:
        """Handle captcha configuration commands"""
        if not args:
            # Show current captcha config
            captcha_config = self.config.get('evasion', {}).get('captcha_bypass', {})
            return CommandResult(
                success=True,
                message="Current captcha configuration:",
                data={
                    'enabled': captcha_config.get('enabled', False),
                    'auto_detect': captcha_config.get('auto_detect', True),
                    'bypass_methods': captcha_config.get('bypass_methods', []),
                    'selenium_headless': captcha_config.get('selenium_config', {}).get('headless', True),
                    'ocr_engine': captcha_config.get('ocr_config', {}).get('engine', 'tesseract'),
                    'third_party_services': captcha_config.get('third_party_config', {}).get('services', [])
                }
            )
        
        action = args[0].lower()
        
        if action == 'enable':
            self.config.set('evasion.captcha_bypass.enabled', True)
            return CommandResult(success=True, message="Captcha bypass enabled")
        
        elif action == 'disable':
            self.config.set('evasion.captcha_bypass.enabled', False)
            return CommandResult(success=True, message="Captcha bypass disabled")
        
        elif action == 'auto-detect' and len(args) >= 2:
            value = args[1].lower() in ['true', '1', 'yes', 'on']
            self.config.set('evasion.captcha_bypass.auto_detect', value)
            return CommandResult(success=True, message=f"Auto-detect {'enabled' if value else 'disabled'}")
        
        elif action == 'method' and len(args) >= 2:
            method = args[1]
            valid_methods = ['selenium_automation', 'ocr_recognition', 'audio_captcha', 'behavioral_simulation', 'third_party_services']
            if method in valid_methods:
                current_methods = self.config.get('evasion.captcha_bypass.bypass_methods', [])
                if method not in current_methods:
                    current_methods.append(method)
                    self.config.set('evasion.captcha_bypass.bypass_methods', current_methods)
                return CommandResult(success=True, message=f"Added bypass method: {method}")
            else:
                return CommandResult(success=False, message=f"Invalid method. Valid methods: {', '.join(valid_methods)}")
        
        elif action == 'selenium-headless' and len(args) >= 2:
            value = args[1].lower() in ['true', '1', 'yes', 'on']
            self.config.set('evasion.captcha_bypass.selenium_config.headless', value)
            return CommandResult(success=True, message=f"Selenium headless mode {'enabled' if value else 'disabled'}")
        
        elif action == 'ocr-engine' and len(args) >= 2:
            engine = args[1].lower()
            valid_engines = ['tesseract', 'easyocr', 'paddleocr']
            if engine in valid_engines:
                self.config.set('evasion.captcha_bypass.ocr_config.engine', engine)
                return CommandResult(success=True, message=f"OCR engine set to: {engine}")
            else:
                return CommandResult(success=False, message=f"Invalid engine. Valid engines: {', '.join(valid_engines)}")
        
        elif action == 'api-key' and len(args) >= 3:
            service = args[1].lower()
            api_key = args[2]
            valid_services = ['2captcha', 'anticaptcha', 'deathbycaptcha', 'imagetyperz']
            if service in valid_services:
                self.config.set(f'evasion.captcha_bypass.third_party_config.api_keys.{service}', api_key)
                return CommandResult(success=True, message=f"API key set for {service}")
            else:
                return CommandResult(success=False, message=f"Invalid service. Valid services: {', '.join(valid_services)}")
        
        else:
            return CommandResult(
                success=False,
                message="Usage: config captcha [enable|disable|auto-detect|method|selenium-headless|ocr-engine|api-key] [value]"
            )
    
    def _handle_evasion_config(self, args: List[str]) -> CommandResult:
        """Handle evasion configuration commands"""
        if not args:
            # Show current evasion config
            evasion_config = self.config.get('evasion', {})
            return CommandResult(
                success=True,
                message="Current evasion configuration:",
                data={
                    'waf_bypass': evasion_config.get('waf_bypass', True),
                    'rate_limiting_bypass': evasion_config.get('rate_limiting_bypass', True),
                    'geo_blocking_bypass': evasion_config.get('geo_blocking_bypass', True),
                    'ip_rotation': evasion_config.get('ip_rotation', True),
                    'header_randomization': evasion_config.get('header_randomization', True),
                    'request_timing_variation': evasion_config.get('request_timing_variation', True),
                    'payload_encoding': evasion_config.get('payload_encoding', True),
                    'fingerprint_randomization': evasion_config.get('fingerprint_randomization', True)
                }
            )
        
        action = args[0].lower()
        
        evasion_options = {
            'waf-bypass': 'waf_bypass',
            'rate-limit-bypass': 'rate_limiting_bypass', 
            'geo-bypass': 'geo_blocking_bypass',
            'ip-rotation': 'ip_rotation',
            'header-randomization': 'header_randomization',
            'timing-variation': 'request_timing_variation',
            'payload-encoding': 'payload_encoding',
            'fingerprint-randomization': 'fingerprint_randomization'
        }
        
        if action in evasion_options and len(args) >= 2:
            value = args[1].lower() in ['true', '1', 'yes', 'on', 'enable']
            config_key = f'evasion.{evasion_options[action]}'
            self.config.set(config_key, value)
            return CommandResult(
                success=True, 
                message=f"{action.replace('-', ' ').title()} {'enabled' if value else 'disabled'}"
            )
        
        else:
            options_list = ', '.join(evasion_options.keys())
            return CommandResult(
                success=False,
                message=f"Usage: config evasion [{options_list}] [enable|disable]"
            )
    
    def _handle_proxy_config(self, args: List[str]) -> CommandResult:
        """Handle proxy configuration commands"""
        if not args:
            # Show current proxy config
            proxy_config = self.config.get('layer7', {})
            return CommandResult(
                success=True,
                message="Current proxy configuration:",
                data={
                    'proxy_sources_count': len(proxy_config.get('proxy_sources', [])),
                    'proxy_rotation': proxy_config.get('proxy_rotation', True),
                    'proxy_timeout': proxy_config.get('proxy_timeout', 10),
                    'proxy_retry_attempts': proxy_config.get('proxy_retry_attempts', 3)
                }
            )
        
        action = args[0].lower()
        
        if action == 'rotation' and len(args) >= 2:
            value = args[1].lower() in ['true', '1', 'yes', 'on', 'enable']
            self.config.set('layer7.proxy_rotation', value)
            return CommandResult(success=True, message=f"Proxy rotation {'enabled' if value else 'disabled'}")
        
        elif action == 'timeout' and len(args) >= 2:
            try:
                timeout = int(args[1])
                if timeout > 0:
                    self.config.set('layer7.proxy_timeout', timeout)
                    return CommandResult(success=True, message=f"Proxy timeout set to {timeout} seconds")
                else:
                    return CommandResult(success=False, message="Timeout must be greater than 0")
            except ValueError:
                return CommandResult(success=False, message="Invalid timeout value")
        
        elif action == 'retry-attempts' and len(args) >= 2:
            try:
                attempts = int(args[1])
                if attempts >= 0:
                    self.config.set('layer7.proxy_retry_attempts', attempts)
                    return CommandResult(success=True, message=f"Proxy retry attempts set to {attempts}")
                else:
                    return CommandResult(success=False, message="Retry attempts must be 0 or greater")
            except ValueError:
                return CommandResult(success=False, message="Invalid retry attempts value")
        
        elif action == 'add-source' and len(args) >= 2:
            source_url = args[1]
            current_sources = self.config.get('layer7.proxy_sources', [])
            if source_url not in current_sources:
                current_sources.append(source_url)
                self.config.set('layer7.proxy_sources', current_sources)
                return CommandResult(success=True, message=f"Added proxy source: {source_url}")
            else:
                return CommandResult(success=False, message="Proxy source already exists")
        
        elif action == 'remove-source' and len(args) >= 2:
            source_url = args[1]
            current_sources = self.config.get('layer7.proxy_sources', [])
            if source_url in current_sources:
                current_sources.remove(source_url)
                self.config.set('layer7.proxy_sources', current_sources)
                return CommandResult(success=True, message=f"Removed proxy source: {source_url}")
            else:
                return CommandResult(success=False, message="Proxy source not found")
        
        else:
            return CommandResult(
                success=False,
                message="Usage: config proxy [rotation|timeout|retry-attempts|add-source|remove-source] [value]"
            )
    
    def _show_general_help(self):
        """Show modern colorized general help"""
        # Main banner
        banner = self.style_manager.create_banner(
            "FSOCIETY DDOS HELP SYSTEM",
            "Advanced Command Reference & Usage Guide"
        )
        console.print(banner)
        
        # Commands table
        commands_data = {
            "help [command]": "Show help information for specific command",
            "config <action>": "Manage configuration (show, set, get, reset, save, load)",
            "proxy <action>": "Manage proxies (scan, test, list, clear)",
            "scan <target>": "Scan target for vulnerabilities and information",
            "attack <layer> <target>": "Launch Layer 4/7 attacks with various methods",
            "stop": "Stop current running attack operations",
            "status": "Display system status and attack statistics",
            "stealth <action>": "Manage stealth features (enable, disable, status)",
            "exit/quit": "Exit the application safely"
        }
        
        commands_table = self.style_manager.create_command_table(commands_data)
        console.print(commands_table)
        
        # Examples section
        examples = [
            {
                'title': 'Basic Configuration',
                'command': 'config show',
                'description': 'Display current system configuration'
            },
            {
                'title': 'Proxy Management',
                'command': 'proxy scan --threads 50',
                'description': 'Scan for working proxies with 50 threads'
            },
            {
                'title': 'Target Reconnaissance',
                'command': 'scan example.com --deep',
                'description': 'Perform deep scan on target domain'
            },
            {
                'title': 'Layer 7 HTTP Attack',
                'command': 'attack layer7 example.com http-flood --rate 1000',
                'description': 'Launch HTTP flood attack with 1000 req/s'
            },
            {
                'title': 'Layer 4 SYN Flood',
                'command': 'attack layer4 192.168.1.1 syn-flood --threads 200',
                'description': 'Launch SYN flood attack with 200 threads'
            },
            {
                'title': 'Stealth Operations',
                'command': 'stealth enable --tor --obfuscation',
                'description': 'Enable stealth mode with Tor and traffic obfuscation'
            }
        ]
        
        examples_panel = self.style_manager.create_example_section(examples)
        console.print(examples_panel)
        
        # Quick tips
        tips_text = f"""
[bold {Colors.CYBER}]💡 Quick Tips:[/]

• Use [bold {Colors.SUCCESS}]help <command>[/] for detailed command information
• All attacks support [bold {Colors.WARNING}]--dry-run[/] for testing without execution
• Enable [bold {Colors.ACCENT}]stealth mode[/] for enhanced anonymity
• Use [bold {Colors.INFO}]status[/] command to monitor system resources
• Configure [bold {Colors.SECONDARY}]proxies[/] for better anonymity and performance
        """
        
        tips_panel = self.style_manager.create_help_section("Quick Tips", tips_text.strip(), "💡")
        console.print(tips_panel)
        
        # Footer
        from rich.rule import Rule
        console.print(Rule(f"[bold {Colors.ACCENT}]Type 'help <command>' for detailed information[/]"))
    
    def _show_command_help(self, command: str):
        """Show modern colorized help for specific command"""
        # Command-specific help data
        command_help_data = {
            'config': {
                'title': 'Configuration Management',
                'description': 'Manage system configuration settings and profiles',
                'usage': [
                    'config show - Display current configuration',
                    'config set <key> <value> - Set configuration value',
                    'config get <key> - Get configuration value',
                    'config reset - Reset to default configuration',
                    'config save [file] - Save configuration to file',
                    'config load [file] - Load configuration from file',
                    'config captcha [options] - Manage captcha bypass settings',
                    'config evasion [options] - Manage evasion technique settings',
                    'config proxy [options] - Manage proxy configuration settings'
                ],
                'examples': [
                    {
                        'title': 'View Configuration',
                        'command': 'config show',
                        'description': 'Display all current settings'
                    },
                    {
                        'title': 'Set Thread Count',
                        'command': 'config set threads 200',
                        'description': 'Set maximum thread count to 200'
                    },
                    {
                        'title': 'Configure Attack Rate',
                        'command': 'config set layer7.request_rate 5000',
                        'description': 'Set Layer 7 request rate to 5000/s'
                    },
                    {
                        'title': 'Enable Captcha Bypass',
                        'command': 'config captcha enable',
                        'description': 'Enable automatic captcha bypass'
                    },
                    {
                        'title': 'Configure WAF Bypass',
                        'command': 'config evasion waf-bypass enable',
                        'description': 'Enable WAF bypass techniques'
                    },
                    {
                        'title': 'Set Proxy Timeout',
                        'command': 'config proxy timeout 15',
                        'description': 'Set proxy timeout to 15 seconds'
                    }
                ]
            },
            'proxy': {
                'title': 'Proxy Management System',
                'description': 'Advanced proxy scanning, testing, and management',
                'usage': [
                    'proxy scan [options] - Scan for available proxies',
                    'proxy test [options] - Test proxy connectivity and speed',
                    'proxy list - List all available proxies',
                    'proxy clear - Clear proxy list'
                ],
                'examples': [
                    {
                        'title': 'Proxy Scanning',
                        'command': 'proxy scan --threads 100 --timeout 5',
                        'description': 'Scan proxies with 100 threads and 5s timeout'
                    },
                    {
                        'title': 'Proxy Testing',
                        'command': 'proxy test --target google.com',
                        'description': 'Test proxies against Google'
                    }
                ]
            },
            'attack': {
                'title': 'Attack Operations Center',
                'description': 'Launch sophisticated Layer 4/7 attacks with advanced features',
                'usage': [
                    'attack layer4 <target> <method> [options] - Layer 4 attacks',
                    'attack layer7 <target> <method> [options] - Layer 7 attacks'
                ],
                'examples': [
                    {
                        'title': 'HTTP Flood Attack',
                        'command': 'attack layer7 example.com http-flood --rate 2000 --duration 60',
                        'description': 'HTTP flood with 2000 req/s for 60 seconds'
                    },
                    {
                        'title': 'SYN Flood Attack',
                        'command': 'attack layer4 192.168.1.1 syn-flood --threads 500',
                        'description': 'SYN flood with 500 threads'
                    },
                    {
                        'title': 'Slowloris Attack',
                        'command': 'attack layer7 example.com slowloris --connections 1000',
                        'description': 'Slowloris attack with 1000 connections'
                    }
                ]
            },
            'stealth': {
                'title': 'Stealth & Evasion System',
                'description': 'Advanced stealth features for enhanced anonymity',
                'usage': [
                    'stealth enable [options] - Enable stealth mode',
                    'stealth disable - Disable stealth mode',
                    'stealth status - Show stealth status'
                ],
                'examples': [
                    {
                        'title': 'Full Stealth Mode',
                        'command': 'stealth enable --tor --obfuscation --anti-forensics',
                        'description': 'Enable all stealth features'
                    },
                    {
                        'title': 'Tor Only',
                        'command': 'stealth enable --tor',
                        'description': 'Enable only Tor proxy routing'
                    }
                ]
            }
        }
        
        if command not in command_help_data:
            console.print(f"[bold {Colors.ERROR}]No detailed help available for '{command}'[/]")
            return
        
        help_data = command_help_data[command]
        
        # Command banner
        banner = self.style_manager.create_banner(
            f"{help_data['title'].upper()}",
            help_data['description']
        )
        console.print(banner)
        
        # Usage section
        usage_text = "\n".join([f"• {usage}" for usage in help_data['usage']])
        usage_panel = self.style_manager.create_help_section("Usage", usage_text, "📖")
        console.print(usage_panel)
        
        # Examples section
        if 'examples' in help_data:
            examples_panel = self.style_manager.create_example_section(help_data['examples'])
            console.print(examples_panel)
        
        # Back to main help
        from rich.rule import Rule
        console.print(Rule(f"[bold {Colors.ACCENT}]Type 'help' to return to main help menu[/]"))


class ArgumentParser:
    """Parse command line arguments"""
    
    @staticmethod
    def parse_command(input_line: str) -> tuple[str, List[str]]:
        """Parse command line input"""
        parts = input_line.strip().split()
        
        if not parts:
            return "", []
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        return command, args
    
    @staticmethod
    def parse_options(args: List[str]) -> Dict[str, Any]:
        """Parse command options"""
        options = {}
        i = 0
        
        while i < len(args):
            arg = args[i]
            
            if arg.startswith('--'):
                # Long option
                key = arg[2:]
                if i + 1 < len(args) and not args[i + 1].startswith('-'):
                    options[key] = args[i + 1]
                    i += 2
                else:
                    options[key] = True
                    i += 1
            elif arg.startswith('-'):
                # Short option
                key = arg[1:]
                if i + 1 < len(args) and not args[i + 1].startswith('-'):
                    options[key] = args[i + 1]
                    i += 2
                else:
                    options[key] = True
                    i += 1
            else:
                i += 1
        
        return options