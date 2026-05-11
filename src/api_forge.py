#!/usr/bin/env python3
"""
ApiForge - Lightweight LLM API Gateway & Load Balancer
轻量级LLM API统一网关与负载均衡引擎

Author: AI Project Generator
Version: 1.0.0
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import hmac
import re

# ============== 版本信息 ==============
__version__ = "1.0.0"
__author__ = "AI Project Generator"
__license__ = "MIT"

# ============== 日志配置 ==============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ApiForge")

# ============== 配置模型 ==============
@dataclass
class ProviderConfig:
    """Provider configuration model"""
    name: str
    api_type: str  # openai, anthropic, ollama, custom
    api_key: str
    base_url: str
    model: str
    max_rpm: int = 60  # requests per minute
    max_tpm: int = 90000  # tokens per minute
    weight: int = 1  # load balancer weight
    enabled: bool = True
    priority: int = 1  # 1-10, higher = more preferred

@dataclass
class LoadBalancerConfig:
    """Load balancer configuration"""
    strategy: str = "round_robin"  # round_robin, weighted, least_connections, random
    health_check_interval: int = 30  # seconds
    failure_threshold: int = 3  # consecutive failures before marking unhealthy
    recovery_timeout: int = 60  # seconds before retrying unhealthy provider

@dataclass
class SafetyConfig:
    """Safety and rate limiting configuration"""
    enable_rate_limiting: bool = True
    enable_budget_control: bool = True
    daily_budget_usd: float = 100.0
    monthly_budget_usd: float = 1000.0
    max_tokens_per_request: int = 4096
    enable_content_filter: bool = True
    allowed_content_patterns: List[str] = field(default_factory=list)
    blocked_content_patterns: List[str] = field(default_factory=lambda: ["[REDACTED]", "sensitive"])

@dataclass
class ApiForgeConfig:
    """Main configuration"""
    version: str = "1.0.0"
    port: int = 8080
    host: str = "0.0.0.0"
    debug: bool = False
    
    # Provider configs
    providers: List[ProviderConfig] = field(default_factory=list)
    
    # Load balancer
    load_balancer: LoadBalancerConfig = field(default_factory=LoadBalancerConfig)
    
    # Safety
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    
    # Advanced
    enable_cors: bool = True
    enable_metrics: bool = True
    log_requests: bool = True
    cache_enabled: bool = False
    cache_ttl: int = 3600

class Config:
    """Configuration manager"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config: ApiForgeConfig = ApiForgeConfig()
        self._provider_stats: Dict[str, Dict] = {}
        self._request_counts: Dict[str, int] = {}
        self._token_counts: Dict[str, int] = {}
        
    def load(self, config_path: Optional[str] = None) -> ApiForgeConfig:
        """Load configuration from YAML file"""
        path = config_path or self.config_path or "config.yaml"
        
        if not os.path.exists(path):
            logger.warning(f"Config file not found: {path}, using defaults")
            return self.config
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            self.config = self._parse_config(data)
            logger.info(f"✅ Configuration loaded from {path}")
            return self.config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self.config
    
    def _parse_config(self, data: Dict) -> ApiForgeConfig:
        """Parse configuration data"""
        config = ApiForgeConfig()
        
        if 'server' in data:
            config.port = data['server'].get('port', 8080)
            config.host = data['server'].get('host', '0.0.0.0')
            config.debug = data['server'].get('debug', False)
            
        if 'providers' in data:
            config.providers = [
                ProviderConfig(
                    name=p.get('name', ''),
                    api_type=p.get('api_type', 'openai'),
                    api_key=p.get('api_key', ''),
                    base_url=p.get('base_url', ''),
                    model=p.get('model', ''),
                    max_rpm=p.get('max_rpm', 60),
                    max_tpm=p.get('max_tpm', 90000),
                    weight=p.get('weight', 1),
                    enabled=p.get('enabled', True),
                    priority=p.get('priority', 1)
                )
                for p in data['providers']
            ]
            
        if 'load_balancer' in data:
            lb = data['load_balancer']
            config.load_balancer = LoadBalancerConfig(
                strategy=lb.get('strategy', 'round_robin'),
                health_check_interval=lb.get('health_check_interval', 30),
                failure_threshold=lb.get('failure_threshold', 3),
                recovery_timeout=lb.get('recovery_timeout', 60)
            )
            
        if 'safety' in data:
            s = data['safety']
            config.safety = SafetyConfig(
                enable_rate_limiting=s.get('enable_rate_limiting', True),
                enable_budget_control=s.get('enable_budget_control', True),
                daily_budget_usd=s.get('daily_budget_usd', 100.0),
                monthly_budget_usd=s.get('monthly_budget_usd', 1000.0),
                max_tokens_per_request=s.get('max_tokens_per_request', 4096),
                enable_content_filter=s.get('enable_content_filter', True)
            )
            
        config.enable_cors = data.get('enable_cors', True)
        config.enable_metrics = data.get('enable_metrics', True)
        config.log_requests = data.get('log_requests', True)
        
        return config
    
    def save(self, path: Optional[str] = None) -> bool:
        """Save current configuration to YAML file"""
        save_path = path or self.config_path or "config.yaml"
        
        try:
            data = {
                'version': self.config.version,
                'server': {
                    'port': self.config.port,
                    'host': self.config.host,
                    'debug': self.config.debug
                },
                'providers': [
                    {
                        'name': p.name,
                        'api_type': p.api_type,
                        'api_key': p.api_key,
                        'base_url': p.base_url,
                        'model': p.model,
                        'max_rpm': p.max_rpm,
                        'max_tpm': p.max_tpm,
                        'weight': p.weight,
                        'enabled': p.enabled,
                        'priority': p.priority
                    }
                    for p in self.config.providers
                ],
                'load_balancer': {
                    'strategy': self.config.load_balancer.strategy,
                    'health_check_interval': self.config.load_balancer.health_check_interval,
                    'failure_threshold': self.config.load_balancer.failure_threshold,
                    'recovery_timeout': self.config.load_balancer.recovery_timeout
                },
                'safety': {
                    'enable_rate_limiting': self.config.safety.enable_rate_limiting,
                    'enable_budget_control': self.config.safety.enable_budget_control,
                    'daily_budget_usd': self.config.safety.daily_budget_usd,
                    'monthly_budget_usd': self.config.safety.monthly_budget_usd,
                    'max_tokens_per_request': self.config.safety.max_tokens_per_request,
                    'enable_content_filter': self.config.safety.enable_content_filter
                },
                'enable_cors': self.config.enable_cors,
                'enable_metrics': self.config.enable_metrics,
                'log_requests': self.config.log_requests
            }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
                
            logger.info(f"✅ Configuration saved to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

# ============== 请求/响应模型 ==============
@dataclass
class LLMRequest:
    """LLM request model"""
    model: str
    messages: List[Dict[str, str]]
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    user: Optional[str] = None
    
    # Metadata
    request_id: str = ""
    timestamp: float = field(default_factory=time.time)
    client_ip: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'model': self.model,
            'messages': self.messages,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'stream': self.stream,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'user': self.user
        }

@dataclass
class LLMResponse:
    """LLM response model"""
    id: str
    model: str
    content: str
    usage: Dict[str, int]  # prompt_tokens, completion_tokens, total_tokens
    finish_reason: str
    provider: str
    latency_ms: float
    cost_usd: float
    timestamp: float = field(default_factory=time.time)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'model': self.model,
            'content': self.content,
            'usage': self.usage,
            'finish_reason': self.finish_reason,
            'provider': self.provider,
            'latency_ms': self.latency_ms,
            'cost_usd': self.cost_usd,
            'timestamp': self.timestamp,
            'error': self.error
        }

# ============== API Provider 客户端 ==============
class BaseProvider:
    """Base API provider class"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self._stats = {
            'requests': 0,
            'tokens': 0,
            'errors': 0,
            'total_cost': 0.0,
            'last_request_time': 0,
            'consecutive_failures': 0,
            'healthy': True
        }
        
    async def chat(self, request: LLMRequest) -> LLMResponse:
        """Send chat request to provider"""
        raise NotImplementedError
        
    def update_stats(self, tokens: int, cost: float, error: bool = False):
        """Update provider statistics"""
        self._stats['requests'] += 1
        self._stats['tokens'] += tokens
        self._stats['total_cost'] += cost
        self._stats['last_request_time'] = time.time()
        
        if error:
            self._stats['errors'] += 1
            self._stats['consecutive_failures'] += 1
        else:
            self._stats['consecutive_failures'] = 0
            
    def get_stats(self) -> Dict:
        """Get provider statistics"""
        return {
            **self._stats,
            'name': self.config.name,
            'healthy': self.is_healthy()
        }
    
    def is_healthy(self) -> bool:
        """Check if provider is healthy"""
        return self._stats['consecutive_failures'] < 3

class OpenAIProvider(BaseProvider):
    """OpenAI compatible API provider"""
    
    COST_PER_1K_PROMPT = 0.00015  # $0.15 per 1M tokens
    COST_PER_1K_COMPLETION = 0.0006  # $0.60 per 1M tokens
    
    async def chat(self, request: LLMRequest) -> LLMResponse:
        """Send chat request to OpenAI compatible API"""
        import aiohttp
        
        start_time = time.time()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.config.api_key}'
        }
        
        payload = {
            'model': request.model or self.config.model,
            'messages': request.messages,
            'temperature': request.temperature,
            'max_tokens': request.max_tokens,
            'stream': request.stream
        }
        
        if request.top_p:
            payload['top_p'] = request.top_p
        if request.frequency_penalty:
            payload['frequency_penalty'] = request.frequency_penalty
        if request.presence_penalty:
            payload['presence_penalty'] = request.presence_penalty
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"API Error {resp.status}: {error_text}")
                        
                    data = await resp.json()
                    
                    latency = (time.time() - start_time) * 1000
                    
                    # Calculate cost
                    usage = data.get('usage', {})
                    prompt_tokens = usage.get('prompt_tokens', 0)
                    completion_tokens = usage.get('completion_tokens', 0)
                    total_tokens = usage.get('total_tokens', prompt_tokens + completion_tokens)
                    
                    cost = (prompt_tokens / 1000 * self.COST_PER_1K_PROMPT + 
                           completion_tokens / 1000 * self.COST_PER_1K_COMPLETION)
                    
                    content = data['choices'][0]['message']['content']
                    finish_reason = data['choices'][0].get('finish_reason', 'stop')
                    
                    self.update_stats(total_tokens, cost)
                    
                    return LLMResponse(
                        id=data.get('id', ''),
                        model=data.get('model', request.model),
                        content=content,
                        usage={
                            'prompt_tokens': prompt_tokens,
                            'completion_tokens': completion_tokens,
                            'total_tokens': total_tokens
                        },
                        finish_reason=finish_reason,
                        provider=self.config.name,
                        latency_ms=latency,
                        cost_usd=cost
                    )
                    
        except Exception as e:
            self.update_stats(0, 0, error=True)
            raise Exception(f"OpenAI API request failed: {str(e)}")

class AnthropicProvider(BaseProvider):
    """Anthropic Claude API provider"""
    
    COST_PER_1K_PROMPT = 0.0008  # $0.80 per 1M tokens
    COST_PER_1K_COMPLETION = 0.004  # $4.00 per 1M tokens
    
    async def chat(self, request: LLMRequest) -> LLMResponse:
        """Send chat request to Anthropic API"""
        import aiohttp
        
        start_time = time.time()
        
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.config.api_key,
            'anthropic-version': '2023-06-01'
        }
        
        # Convert messages to Anthropic format
        system = ""
        anthropic_messages = []
        
        for msg in request.messages:
            if msg['role'] == 'system':
                system = msg['content']
            else:
                anthropic_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        payload = {
            'model': request.model or self.config.model,
            'messages': anthropic_messages,
            'temperature': request.temperature,
            'max_tokens': request.max_tokens
        }
        
        if system:
            payload['system'] = system
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config.base_url}/messages",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"API Error {resp.status}: {error_text}")
                        
                    data = await resp.json()
                    
                    latency = (time.time() - start_time) * 1000
                    
                    usage = data.get('usage', {})
                    prompt_tokens = usage.get('input_tokens', 0)
                    completion_tokens = usage.get('output_tokens', 0)
                    total_tokens = prompt_tokens + completion_tokens
                    
                    cost = (prompt_tokens / 1000 * self.COST_PER_1K_PROMPT + 
                           completion_tokens / 1000 * self.COST_PER_1K_COMPLETION)
                    
                    content = data['content'][0]['text']
                    stop_reason = data.get('stop_reason', 'end_turn')
                    
                    self.update_stats(total_tokens, cost)
                    
                    return LLMResponse(
                        id=f"anthropic-{data.get('id', '')}",
                        model=data.get('model', request.model),
                        content=content,
                        usage={
                            'prompt_tokens': prompt_tokens,
                            'completion_tokens': completion_tokens,
                            'total_tokens': total_tokens
                        },
                        finish_reason=stop_reason,
                        provider=self.config.name,
                        latency_ms=latency,
                        cost_usd=cost
                    )
                    
        except Exception as e:
            self.update_stats(0, 0, error=True)
            raise Exception(f"Anthropic API request failed: {str(e)}")

class OllamaProvider(BaseProvider):
    """Ollama local API provider"""
    
    COST_PER_1K_TOKENS = 0.0  # Free for local
    
    async def chat(self, request: LLMRequest) -> LLMResponse:
        """Send chat request to Ollama API"""
        import aiohttp
        
        start_time = time.time()
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': request.model or self.config.model,
            'messages': request.messages,
            'stream': False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config.base_url}/api/chat",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise Exception(f"API Error {resp.status}: {error_text}")
                        
                    data = await resp.json()
                    
                    latency = (time.time() - start_time) * 1000
                    
                    content = data['message']['content']
                    total_tokens = len(content.split()) * 2  # Rough estimate
                    
                    self.update_stats(total_tokens, 0.0)
                    
                    return LLMResponse(
                        id=f"ollama-{int(time.time() * 1000)}",
                        model=data.get('model', request.model),
                        content=content,
                        usage={
                            'prompt_tokens': 0,
                            'completion_tokens': total_tokens,
                            'total_tokens': total_tokens
                        },
                        finish_reason='stop',
                        provider=self.config.name,
                        latency_ms=latency,
                        cost_usd=0.0
                    )
                    
        except Exception as e:
            self.update_stats(0, 0, error=True)
            raise Exception(f"Ollama API request failed: {str(e)}")

# ============== 负载均衡器 ==============
class LoadBalancer:
    """Load balancer for multiple API providers"""
    
    STRATEGIES = ['round_robin', 'weighted', 'least_connections', 'random', 'priority']
    
    def __init__(self, providers: List[BaseProvider], strategy: str = 'round_robin'):
        self.providers = {p.config.name: p for p in providers}
        self.strategy = strategy
        self._current_index = 0
        self._connections: Dict[str, int] = {p.config.name: 0 for p in providers}
        self._lock = asyncio.Lock()
        
    async def select_provider(self) -> Optional[BaseProvider]:
        """Select a provider based on load balancing strategy"""
        async with self._lock:
            # Filter healthy providers
            healthy = [p for p in self.providers.values() 
                      if p.config.enabled and p.is_healthy()]
            
            if not healthy:
                logger.warning("⚠️ No healthy providers available!")
                return None
                
            if self.strategy == 'round_robin':
                provider = healthy[self._current_index % len(healthy)]
                self._current_index += 1
                
            elif self.strategy == 'weighted':
                # Weighted random selection
                weights = [(p.config.weight, p) for p in healthy]
                total = sum(w for w, _ in weights)
                import random
                r = random.uniform(0, total)
                cumsum = 0
                provider = healthy[0]
                for w, p in weights:
                    cumsum += w
                    if r <= cumsum:
                        provider = p
                        break
                        
            elif self.strategy == 'least_connections':
                provider = min(healthy, key=lambda p: self._connections[p.config.name])
                
            elif self.strategy == 'random':
                import random
                provider = random.choice(healthy)
                
            elif self.strategy == 'priority':
                # Select highest priority, then by weight
                provider = max(healthy, key=lambda p: (p.config.priority, p.config.weight))
                
            else:
                provider = healthy[0]
                
            self._connections[provider.config.name] += 1
            return provider
    
    async def release_provider(self, provider: BaseProvider):
        """Release provider after request completes"""
        async with self._lock:
            if provider.config.name in self._connections:
                self._connections[provider.config.name] = max(0, 
                    self._connections[provider.config.name] - 1)
    
    def get_stats(self) -> Dict:
        """Get load balancer statistics"""
        return {
            'strategy': self.strategy,
            'providers': {
                name: {
                    'healthy': p.is_healthy(),
                    'connections': self._connections.get(name, 0),
                    'stats': p.get_stats()
                }
                for name, p in self.providers.items()
            }
        }

# ============== 成本追踪器 ==============
class CostTracker:
    """Track API usage costs"""
    
    def __init__(self, daily_limit: float = 100.0, monthly_limit: float = 1000.0):
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit
        self._daily_cost = 0.0
        self._monthly_cost = 0.0
        self._daily_requests = 0
        self._monthly_requests = 0
        self._history: List[Dict] = []
        self._last_reset = datetime.now()
        
    def add_request(self, cost: float, tokens: int, provider: str, model: str):
        """Record a request"""
        now = datetime.now()
        
        # Reset daily/monthly if needed
        if now.date() > self._last_reset.date():
            self._daily_cost = 0.0
            self._daily_requests = 0
            
        if now.month != self._last_reset.month or now.year != self._last_reset.year:
            self._monthly_cost = 0.0
            self._monthly_requests = 0
            
        self._daily_cost += cost
        self._monthly_cost += cost
        self._daily_requests += 1
        self._monthly_requests += 1
        
        self._history.append({
            'timestamp': now.isoformat(),
            'cost': cost,
            'tokens': tokens,
            'provider': provider,
            'model': model
        })
        
        self._last_reset = now
        
    def check_budget(self) -> Dict[str, Any]:
        """Check if budget limits are exceeded"""
        return {
            'daily': {
                'cost': self._daily_cost,
                'limit': self.daily_limit,
                'remaining': max(0, self.daily_limit - self._daily_cost),
                'exceeded': self._daily_cost >= self.daily_limit,
                'requests': self._daily_requests
            },
            'monthly': {
                'cost': self._monthly_cost,
                'limit': self.monthly_limit,
                'remaining': max(0, self.monthly_limit - self._monthly_cost),
                'exceeded': self._monthly_cost >= self.monthly_limit,
                'requests': self._monthly_requests
            }
        }
    
    def get_stats(self) -> Dict:
        """Get cost statistics"""
        budget = self.check_budget()
        return {
            'total_cost': self._monthly_cost,
            'total_requests': self._monthly_requests,
            'budget': budget
        }

# ============== 熔断器 ==============
class CircuitBreaker:
    """Circuit breaker for fault tolerance"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._states: Dict[str, str] = {}  # provider -> state (closed, open, half_open)
        self._failures: Dict[str, int] = {}
        self._last_failure_time: Dict[str, float] = {}
        
    def is_open(self, provider: str) -> bool:
        """Check if circuit is open for provider"""
        state = self._states.get(provider, 'closed')
        
        if state == 'closed':
            return False
        elif state == 'open':
            # Check if recovery timeout has passed
            if time.time() - self._last_failure_time.get(provider, 0) > self.recovery_timeout:
                self._states[provider] = 'half_open'
                return False
            return True
        else:  # half_open
            return False
            
    def record_success(self, provider: str):
        """Record successful request"""
        self._states[provider] = 'closed'
        self._failures[provider] = 0
        
    def record_failure(self, provider: str):
        """Record failed request"""
        self._failures[provider] = self._failures.get(provider, 0) + 1
        self._last_failure_time[provider] = time.time()
        
        if self._failures[provider] >= self.failure_threshold:
            self._states[provider] = 'open'
            logger.warning(f"⚠️ Circuit breaker OPEN for {provider}")
            
    def get_state(self, provider: str) -> str:
        """Get circuit state for provider"""
        return self._states.get(provider, 'closed')

# ============== 主网关类 ==============
class ApiGateway:
    """Main API Gateway class"""
    
    def __init__(self, config: ApiForgeConfig):
        self.config = config
        self.cost_tracker = CostTracker(
            daily_limit=config.safety.daily_budget_usd,
            monthly_limit=config.safety.monthly_budget_usd
        )
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.load_balancer.failure_threshold,
            recovery_timeout=config.load_balancer.recovery_timeout
        )
        
        # Initialize providers
        self.providers: Dict[str, BaseProvider] = {}
        self._init_providers()
        
        # Initialize load balancer
        self.load_balancer = LoadBalancer(
            list(self.providers.values()),
            strategy=config.load_balancer.strategy
        )
        
        self._metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_cost': 0.0,
            'total_tokens': 0
        }
        
    def _init_providers(self):
        """Initialize API providers"""
        for provider_config in self.config.providers:
            if provider_config.api_type == 'openai':
                self.providers[provider_config.name] = OpenAIProvider(provider_config)
            elif provider_config.api_type == 'anthropic':
                self.providers[provider_config.name] = AnthropicProvider(provider_config)
            elif provider_config.api_type == 'ollama':
                self.providers[provider_config.name] = OllamaProvider(provider_config)
            else:
                self.providers[provider_config.name] = OpenAIProvider(provider_config)
                
        logger.info(f"✅ Initialized {len(self.providers)} providers")
        
    async def chat(self, request: LLMRequest) -> LLMResponse:
        """Process chat request through gateway"""
        self._metrics['total_requests'] += 1
        
        # Check budget
        budget = self.cost_tracker.check_budget()
        if budget['daily']['exceeded'] or budget['monthly']['exceeded']:
            raise Exception("Budget limit exceeded")
            
        # Select provider
        provider = await self.load_balancer.select_provider()
        if not provider:
            raise Exception("No available providers")
            
        try:
            # Check circuit breaker
            if self.circuit_breaker.is_open(provider.config.name):
                raise Exception(f"Provider {provider.config.name} is temporarily unavailable")
                
            # Send request
            response = await provider.chat(request)
            
            # Record success
            self.circuit_breaker.record_success(provider.config.name)
            await self.load_balancer.release_provider(provider)
            
            # Update metrics
            self._metrics['successful_requests'] += 1
            self._metrics['total_cost'] += response.cost_usd
            self._metrics['total_tokens'] += response.usage['total_tokens']
            
            # Update cost tracker
            self.cost_tracker.add_request(
                response.cost_usd,
                response.usage['total_tokens'],
                response.provider,
                response.model
            )
            
            return response
            
        except Exception as e:
            # Record failure
            self.circuit_breaker.record_failure(provider.config.name)
            await self.load_balancer.release_provider(provider)
            
            self._metrics['failed_requests'] += 1
            
            raise Exception(f"Request failed: {str(e)}")
    
    async def health_check(self):
        """Perform health check on all providers"""
        results = {}
        for name, provider in self.providers.items():
            results[name] = {
                'healthy': provider.is_healthy(),
                'stats': provider.get_stats(),
                'circuit_state': self.circuit_breaker.get_state(name)
            }
        return results
        
    def get_metrics(self) -> Dict:
        """Get gateway metrics"""
        return {
            **self._metrics,
            'cost_tracker': self.cost_tracker.get_stats(),
            'load_balancer': self.load_balancer.get_stats(),
            'success_rate': (
                self._metrics['successful_requests'] / max(1, self._metrics['total_requests']) * 100
            )
        }

# ============== HTTP 服务器 ==============
async def handle_chat(request, gateway: ApiGateway):
    """Handle chat completion request"""
    try:
        import aiohttp.web
        
        # Parse request body
        body = await request.json()
        
        # Create LLM request
        llm_request = LLMRequest(
            model=body.get('model', ''),
            messages=body.get('messages', []),
            temperature=body.get('temperature', 0.7),
            max_tokens=body.get('max_tokens', 2048),
            stream=body.get('stream', False),
            top_p=body.get('top_p'),
            frequency_penalty=body.get('frequency_penalty'),
            presence_penalty=body.get('presence_penalty'),
            user=body.get('user')
        )
        
        # Process through gateway
        response = await gateway.chat(llm_request)
        
        return response.to_dict()
        
    except Exception as e:
        raise aiohttp.web.HTTPBadRequest(text=str(e))

async def handle_metrics(request, gateway: ApiGateway):
    """Handle metrics request"""
    return gateway.get_metrics()

async def handle_health(request, gateway: ApiGateway):
    """Handle health check request"""
    health = await gateway.health_check()
    return {'status': 'healthy', 'providers': health}

async def handle_budget(request, gateway: ApiGateway):
    """Handle budget check request"""
    return gateway.cost_tracker.check_budget()

async def create_app(gateway: ApiGateway):
    """Create aiohttp application"""
    import aiohttp.web
    
    app = aiohttp.web.Application()
    
    # Add CORS middleware
    if gateway.config.enable_cors:
        from aiohttp.web import middleware
        @middleware
        async def cors_middleware(request, handler):
            resp = await handler(request)
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return resp
        app.middlewares.append(cors_middleware)
    
    # Routes
    async def chat_handler(request):
        result = await handle_chat(request, gateway)
        return aiohttp.web.json_response(result)
    
    async def metrics_handler(request):
        return aiohttp.web.json_response(await handle_metrics(request, gateway))
    
    async def health_handler(request):
        return aiohttp.web.json_response(await handle_health(request, gateway))
    
    async def budget_handler(request):
        return aiohttp.web.json_response(await handle_budget(request, gateway))
    
    app.router.add_post('/v1/chat/completions', chat_handler)
    app.router.add_get('/metrics', metrics_handler)
    app.router.add_get('/health', health_handler)
    app.router.add_get('/budget', budget_handler)
    
    return app

# ============== CLI 入口 ==============
def create_default_config():
    """Create default configuration file"""
    config_data = {
        'version': '1.0.0',
        'server': {
            'port': 8080,
            'host': '0.0.0.0',
            'debug': False
        },
        'providers': [
            {
                'name': 'openai-default',
                'api_type': 'openai',
                'api_key': 'your-api-key-here',
                'base_url': 'https://api.openai.com/v1',
                'model': 'gpt-4o-mini',
                'max_rpm': 60,
                'max_tpm': 90000,
                'weight': 1,
                'enabled': True,
                'priority': 1
            },
            {
                'name': 'anthropic-default',
                'api_type': 'anthropic',
                'api_key': 'your-api-key-here',
                'base_url': 'https://api.anthropic.com',
                'model': 'claude-3-5-haiku-20241022',
                'max_rpm': 50,
                'max_tpm': 40000,
                'weight': 1,
                'enabled': False,
                'priority': 2
            },
            {
                'name': 'ollama-local',
                'api_type': 'ollama',
                'api_key': '',  # No key for local
                'base_url': 'http://localhost:11434',
                'model': 'llama3.2',
                'max_rpm': 100,
                'max_tpm': 100000,
                'weight': 2,
                'enabled': False,
                'priority': 1
            }
        ],
        'load_balancer': {
            'strategy': 'round_robin',
            'health_check_interval': 30,
            'failure_threshold': 3,
            'recovery_timeout': 60
        },
        'safety': {
            'enable_rate_limiting': True,
            'enable_budget_control': True,
            'daily_budget_usd': 100.0,
            'monthly_budget_usd': 1000.0,
            'max_tokens_per_request': 4096,
            'enable_content_filter': True
        },
        'enable_cors': True,
        'enable_metrics': True,
        'log_requests': True
    }
    
    with open('config.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='🚀 ApiForge - Lightweight LLM API Gateway & Load Balancer'
    )
    parser.add_argument('--config', '-c', help='Configuration file path', default='config.yaml')
    parser.add_argument('--init', '-i', action='store_true', help='Initialize default configuration')
    parser.add_argument('--version', '-v', action='version', version=f'ApiForge {__version__}')
    
    args = parser.parse_args()
    
    if args.init:
        create_default_config()
        print("✅ Default configuration created: config.yaml")
        print("📝 Please edit config.yaml with your API keys")
        return
        
    # Load configuration
    config = Config(args.config)
    cfg = config.load()
    
    # Create gateway
    gateway = ApiGateway(cfg)
    
    # Create and run app
    app = asyncio.run(create_app(gateway))
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    🚀 ApiForge v{__version__}                       ║
║         Lightweight LLM API Gateway & Load Balancer           ║
╠══════════════════════════════════════════════════════════════╣
║  Server:     http://{cfg.host}:{cfg.port}                           ║
║  Providers:  {len(cfg.providers)} configured                                    ║
║  Strategy:   {cfg.load_balancer.strategy}                              ║
║  Daily Budget: ${cfg.safety.daily_budget_usd}                                 ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("📡 API Endpoints:")
    print("   POST /v1/chat/completions - Chat completion")
    print("   GET  /metrics             - Gateway metrics")
    print("   GET  /health              - Provider health")
    print("   GET  /budget              - Budget status")
    print()
    
    import aiohttp.web
    aiohttp.web.run_app(app, host=cfg.host, port=cfg.port)

if __name__ == '__main__':
    main()
