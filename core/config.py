"""
Configuration management for FsocietyDDoS
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for the framework"""
    
    DEFAULT_CONFIG = {
        'general': {
            'max_threads': 1000,
            'timeout': 10,
            'retry_attempts': 3,
            'log_level': 'INFO',
            'output_dir': 'output'
        },
        'layer4': {
            'default_port': 80,
            'packet_size': 1024,
            'flood_rate': 1000,
            'spoofing_enabled': True,
            'fragmentation_enabled': False
        },
        'layer7': {
            'user_agents': [
                # Chrome User Agents (Windows)
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
                
                # Chrome User Agents (macOS)
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                
                # Chrome User Agents (Linux)
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                
                # Firefox User Agents (Windows)
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0',
                
                # Firefox User Agents (macOS)
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:119.0) Gecko/20100101 Firefox/119.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:118.0) Gecko/20100101 Firefox/118.0',
                
                # Firefox User Agents (Linux)
                'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
                'Mozilla/5.0 (X11; Linux x86_64; rv:119.0) Gecko/20100101 Firefox/119.0',
                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:118.0) Gecko/20100101 Firefox/118.0',
                
                # Safari User Agents (macOS)
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
                
                # Safari User Agents (iOS)
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
                
                # Edge User Agents (Windows)
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.0.0',
                
                # Edge User Agents (macOS)
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
                
                # Opera User Agents
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0',
                
                # Brave User Agents
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Brave/120.0.0.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Brave/120.0.0.0',
                
                # Vivaldi User Agents
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Vivaldi/6.5.3206.39',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Vivaldi/6.5.3206.39',
                
                # Android Chrome User Agents
                'Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
                'Mozilla/5.0 (Linux; Android 13; SM-A515F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
                'Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36',
                'Mozilla/5.0 (Linux; Android 11; OnePlus 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36',
                
                # Android Firefox User Agents
                'Mozilla/5.0 (Mobile; rv:120.0) Gecko/120.0 Firefox/120.0',
                'Mozilla/5.0 (Mobile; rv:119.0) Gecko/119.0 Firefox/119.0',
                'Mozilla/5.0 (Android 14; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0',
                
                # Tablet User Agents
                'Mozilla/5.0 (Linux; Android 13; SM-T870) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Linux; Android 12; SM-T725) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                
                # Bot/Crawler User Agents (for evasion testing)
                'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
                'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
                'Mozilla/5.0 (compatible; facebookexternalhit/1.1; +http://www.facebook.com/externalhit_uatext.php)',
                'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
                'Twitterbot/1.0',
                'LinkedInBot/1.0 (compatible; Mozilla/5.0; Apache-HttpClient +http://www.linkedin.com/)',
                
                # Headless Browser User Agents
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/119.0.0.0 Safari/537.36',
                
                # Gaming Console User Agents
                'Mozilla/5.0 (PlayStation 5 5.00) AppleWebKit/605.1.15 (KHTML, like Gecko)',
                'Mozilla/5.0 (PlayStation 4 11.00) AppleWebKit/605.1.15 (KHTML, like Gecko)',
                'Mozilla/5.0 (Nintendo Switch; WebApplet) AppleWebKit/606.4 (KHTML, like Gecko) NF/6.0.2.20.3 NintendoBrowser/5.1.0.22023',
                'Mozilla/5.0 (Xbox One) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edge/44.18363.8131',
                
                # Smart TV User Agents
                'Mozilla/5.0 (SMART-TV; LINUX; Tizen 6.5) AppleWebKit/537.36 (KHTML, like Gecko) 85.0.4183.93/6.5 TV Safari/537.36',
                'Mozilla/5.0 (Web0S; Linux/SmartTV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 WebAppManager',
                'Mozilla/5.0 (Linux; Android 9; SHIELD Android TV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                
                # API Testing User Agents
                'PostmanRuntime/7.35.0',
                'Insomnia/2023.8.6',
                'HTTPie/3.2.2',
                'python-requests/2.31.0',
                'node-fetch/3.3.2',
                'axios/1.6.2',
                'RestSharp/110.2.0.0',
                
                # Load Testing User Agents
                'Apache-HttpClient/4.5.14 (Java/17.0.8)',
                'okhttp/4.12.0',
                'Go-http-client/1.1',
                'libwww-perl/6.67',
                'Ruby/3.2.0',
                'PHP/8.3.0',
                
                # Monitoring User Agents
                'UptimeRobot/2.0; http://www.uptimerobot.com/',
                'Pingdom.com_bot_version_1.4_(http://www.pingdom.com/)',
                'StatusCake_Pagespeed_Checker',
                'Site24x7',
                'GTmetrix',
                
                # Custom Testing User Agents
                'Mozilla/5.0 (compatible; CustomBot/1.0; +http://example.com/bot)',
                'TestAgent/1.0 (Testing Framework)',
                'LoadTester/2.0 (Performance Testing)',
                'StressTester/3.0 (Stress Testing)',
                'BenchmarkBot/1.0 (Benchmark Testing)',
                'QualityAssurance/2.0 (QA Testing)',
                'AutomationBot/1.0 (Test Automation)',
                'PerformanceBot/2.0 (Performance Analysis)',
                'SecurityAudit/1.0 (Security Audit)',
                'ComplianceChecker/1.0 (Compliance Testing)'
            ],
            'proxy_sources': [
                # Free Proxy APIs and Sources
                'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
                'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
                'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt',
                'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
                'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
                'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
                'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt',
                'https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt',
                'https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt',
                'https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/http.txt',
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt',
                'https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt',
                'https://raw.githubusercontent.com/saisuiu/Lionkings-Http-Proxys-Proxies/main/free.txt',
                'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt',
                
                # Regional Proxy Sources
                # US Proxies
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http_us.txt',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http_us.txt',
                
                # European Proxies
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http_eu.txt',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http_eu.txt',
                
                # Asian Proxies
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http_asia.txt',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http_asia.txt',
                
                # SOCKS Proxy Sources
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
                'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
                'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt',
                'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
                'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt',
                'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt',
                'https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt',
                'https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt',
                
                # Elite/Anonymous Proxy Sources
                'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-elite.txt',
                'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-anonymous.txt',
                'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt',
                'https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt',
                
                # High-Speed Proxy Sources
                'https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/socks4.txt',
                'https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/socks5.txt',
                'https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks4.txt',
                'https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/socks5.txt',
                
                # Country-Specific Proxy Sources
                # Germany
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http_de.txt',
                # United Kingdom
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http_uk.txt',
                # France
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http_fr.txt',
                # Canada
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http_ca.txt',
                # Australia
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http_au.txt',
                # Japan
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http_jp.txt',
                # South Korea
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http_kr.txt',
                # Singapore
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http_sg.txt',
                # India
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http_in.txt',
                # Brazil
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http_br.txt',
                # Russia
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http_ru.txt',
                # China
                'https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http_cn.txt',
                
                # Backup and Alternative Sources
                'https://www.proxy-list.download/api/v1/get?type=http',
                'https://www.proxy-list.download/api/v1/get?type=https',
                'https://www.proxy-list.download/api/v1/get?type=socks4',
                'https://www.proxy-list.download/api/v1/get?type=socks5',
                
                # ProxyScrape API endpoints
                'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=5000&country=US',
                'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=5000&country=DE',
                'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=5000&country=UK',
                'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=5000&country=FR',
                'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=5000&country=CA',
                'https://api.proxyscrape.com/v2/?request=get&protocol=socks4&timeout=5000&country=all',
                'https://api.proxyscrape.com/v2/?request=get&protocol=socks5&timeout=5000&country=all',
                
                # Additional GitHub Sources
                'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks4_proxies.txt',
                'https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks5_proxies.txt',
                'https://raw.githubusercontent.com/saisuiu/Lionkings-Http-Proxys-Proxies/main/cnfree.txt',
                'https://raw.githubusercontent.com/ObcbO/getproxy/master/http.txt',
                'https://raw.githubusercontent.com/ObcbO/getproxy/master/https.txt',
                'https://raw.githubusercontent.com/ObcbO/getproxy/master/socks4.txt',
                'https://raw.githubusercontent.com/ObcbO/getproxy/master/socks5.txt',
                
                # Rotating and Premium-like Sources
                'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt',
                'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks4.txt',
                'https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt',
                'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt',
                'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks4.txt',
                'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt',
                
                # Fallback Static Proxies (for testing)
                'http://proxy.example.com:8080',
                'http://backup-proxy.example.com:3128',
                'socks4://socks-proxy.example.com:1080',
                'socks5://socks5-proxy.example.com:1080'
            ],
            'proxy_timeout': 5,
            'max_proxy_workers': 100,
            'request_delay': 0.1,
            'follow_redirects': False
        },
        'security': {
            'stealth_mode': True,
            'randomize_headers': True,
            'use_encryption': False,
            'anti_forensics': True,
            'traffic_obfuscation': True
        },
        'evasion': {
            'captcha_bypass': {
                'enabled': False,
                'auto_detect': True,
                'bypass_methods': [
                    'selenium_automation',
                    'ocr_recognition', 
                    'audio_captcha',
                    'behavioral_simulation',
                    'third_party_services'
                ],
                'selenium_config': {
                    'headless': True,
                    'user_data_dir': None,
                    'disable_images': True,
                    'disable_javascript': False,
                    'window_size': '1920,1080',
                    'user_agent_override': True
                },
                'ocr_config': {
                    'engine': 'tesseract',  # tesseract, easyocr, paddleocr
                    'preprocessing': True,
                    'noise_reduction': True,
                    'contrast_enhancement': True,
                    'confidence_threshold': 0.7
                },
                'audio_config': {
                    'enabled': True,
                    'speech_recognition_engine': 'google',  # google, sphinx, wit
                    'audio_preprocessing': True,
                    'noise_filtering': True
                },
                'behavioral_config': {
                    'mouse_movements': True,
                    'typing_delays': True,
                    'scroll_simulation': True,
                    'click_patterns': 'human_like',
                    'session_persistence': True
                },
                'third_party_config': {
                    'services': [
                        '2captcha',
                        'anticaptcha', 
                        'deathbycaptcha',
                        'imagetyperz'
                    ],
                    'api_keys': {
                        '2captcha': None,
                        'anticaptcha': None,
                        'deathbycaptcha': None,
                        'imagetyperz': None
                    },
                    'timeout': 120,
                    'retry_attempts': 3
                },
                'detection_config': {
                    'captcha_selectors': [
                        'div[class*="captcha"]',
                        'div[id*="captcha"]', 
                        'iframe[src*="recaptcha"]',
                        'div[class*="recaptcha"]',
                        'div[class*="hcaptcha"]',
                        'div[id*="hcaptcha"]',
                        'img[src*="captcha"]',
                        'canvas[id*="captcha"]'
                    ],
                    'response_indicators': [
                        'captcha required',
                        'please complete the captcha',
                        'verify you are human',
                        'security check',
                        'robot verification'
                    ],
                    'auto_retry': True,
                    'max_retry_attempts': 5,
                    'retry_delay': 2
                }
            },
            'waf_bypass': True,
            'rate_limiting_bypass': True,
            'geo_blocking_bypass': True,
            'request_timing_variation': True,
            'payload_encoding': True,
            'fingerprint_randomization': True
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or 'config.json'
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        config_path = Path(self.config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    if config_path.suffix.lower() == '.yaml' or config_path.suffix.lower() == '.yml':
                        loaded_config = yaml.safe_load(f)
                    else:
                        loaded_config = json.load(f)
                
                # Merge with default config
                self._merge_config(self.config, loaded_config)
                
            except Exception as e:
                print(f"⚠️  Failed to load config from {config_path}: {e}")
                print("🔧 Using default configuration")
    
    def save_config(self):
        """Save current configuration to file"""
        config_path = Path(self.config_file)
        
        try:
            # Create directory if it doesn't exist
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.yaml' or config_path.suffix.lower() == '.yml':
                    yaml.dump(self.config, f, default_flow_style=False, indent=2)
                else:
                    json.dump(self.config, f, indent=2)
                    
        except Exception as e:
            print(f"❌ Failed to save config to {config_path}: {e}")
    
    def _merge_config(self, base: Dict[str, Any], update: Dict[str, Any]):
        """Recursively merge configuration dictionaries"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.config.get(section, {})
    
    def update_section(self, section: str, values: Dict[str, Any]):
        """Update entire configuration section"""
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section].update(values)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
    
    def validate_config(self) -> bool:
        """Validate current configuration"""
        required_sections = ['general', 'layer4', 'layer7', 'security']
        
        for section in required_sections:
            if section not in self.config:
                print(f"❌ Missing required configuration section: {section}")
                return False
        
        # Validate specific values
        if self.get('general.max_threads', 0) <= 0:
            print("❌ Invalid max_threads value")
            return False
        
        if self.get('general.timeout', 0) <= 0:
            print("❌ Invalid timeout value")
            return False
        
        return True
    
    def create_default_config_file(self):
        """Create a default configuration file"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
        print(f"✅ Created default configuration file: {self.config_file}")


# Global configuration instance
# Create global config instance
config = Config()
CONFIG = config.config  # For backward compatibility