#!/usr/bin/env python3
"""
ApiForge Test Suite
"""

import pytest
import asyncio
import yaml
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api_forge import (
    Config, LLMRequest, LLMResponse, ApiForgeConfig,
    ProviderConfig, LoadBalancerConfig, SafetyConfig,
    LoadBalancer, CostTracker, CircuitBreaker, ApiGateway,
    OpenAIProvider, AnthropicProvider, OllamaProvider
)


class TestConfig:
    """Test configuration loading"""
    
    def test_config_defaults(self):
        """Test default configuration"""
        config = Config()
        assert config.config.port == 8080
        assert config.config.host == '0.0.0.0'
        assert config.config.debug == False
        
    def test_config_load(self):
        """Test configuration from YAML"""
        config_data = {
            'version': '1.0.0',
            'server': {
                'port': 9000,
                'host': '127.0.0.1',
                'debug': True
            },
            'providers': [
                {
                    'name': 'test-provider',
                    'api_type': 'openai',
                    'api_key': 'test-key',
                    'base_url': 'https://api.test.com',
                    'model': 'test-model',
                    'max_rpm': 100,
                    'max_tpm': 100000,
                    'weight': 2,
                    'enabled': True,
                    'priority': 1
                }
            ],
            'load_balancer': {
                'strategy': 'weighted',
                'health_check_interval': 60
            },
            'safety': {
                'daily_budget_usd': 50.0,
                'monthly_budget_usd': 500.0
            }
        }
        
        with patch('builtins.open', create=True):
            with patch('yaml.safe_load', return_value=config_data):
                config = Config()
                cfg = config._parse_config(config_data)
                
                assert cfg.port == 9000
                assert cfg.host == '127.0.0.1'
                assert cfg.debug == True
                assert len(cfg.providers) == 1
                assert cfg.providers[0].name == 'test-provider'
                assert cfg.load_balancer.strategy == 'weighted'
                assert cfg.safety.daily_budget_usd == 50.0


class TestLLMRequest:
    """Test LLM request model"""
    
    def test_request_creation(self):
        """Test creating LLM request"""
        request = LLMRequest(
            model='gpt-4',
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant'},
                {'role': 'user', 'content': 'Hello!'}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        assert request.model == 'gpt-4'
        assert len(request.messages) == 2
        assert request.temperature == 0.7
        assert request.max_tokens == 100
        assert request.stream == False
        
    def test_request_to_dict(self):
        """Test request serialization"""
        request = LLMRequest(
            model='claude-3',
            messages=[{'role': 'user', 'content': 'Test'}]
        )
        
        data = request.to_dict()
        assert data['model'] == 'claude-3'
        assert 'messages' in data


class TestLLMResponse:
    """Test LLM response model"""
    
    def test_response_creation(self):
        """Test creating LLM response"""
        response = LLMResponse(
            id='test-123',
            model='gpt-4',
            content='Hello, how can I help?',
            usage={
                'prompt_tokens': 10,
                'completion_tokens': 20,
                'total_tokens': 30
            },
            finish_reason='stop',
            provider='openai',
            latency_ms=150.5,
            cost_usd=0.001
        )
        
        assert response.id == 'test-123'
        assert response.content == 'Hello, how can I help?'
        assert response.usage['total_tokens'] == 30
        assert response.cost_usd == 0.001
        
    def test_response_to_dict(self):
        """Test response serialization"""
        response = LLMResponse(
            id='resp-1',
            model='test-model',
            content='Test response',
            usage={'prompt_tokens': 5, 'completion_tokens': 10, 'total_tokens': 15},
            finish_reason='stop',
            provider='test',
            latency_ms=100.0,
            cost_usd=0.0005
        )
        
        data = response.to_dict()
        assert data['id'] == 'resp-1'
        assert data['content'] == 'Test response'
        assert 'error' not in data or data['error'] is None


class TestLoadBalancer:
    """Test load balancer"""
    
    @pytest.fixture
    def mock_providers(self):
        """Create mock providers"""
        providers = []
        for i in range(3):
            config = ProviderConfig(
                name=f'provider-{i}',
                api_type='openai',
                api_key=f'key-{i}',
                base_url='https://api.test.com',
                model='test-model',
                weight=1,
                enabled=True
            )
            provider = OpenAIProvider(config)
            providers.append(provider)
        return providers
    
    def test_round_robin(self, mock_providers):
        """Test round-robin strategy"""
        lb = LoadBalancer(mock_providers, 'round_robin')
        
        selected = []
        for _ in range(6):
            provider = asyncio.run(lb.select_provider())
            if provider:
                selected.append(provider.config.name)
                asyncio.run(lb.release_provider(provider))
        
        # Should cycle through all providers
        assert len(selected) == 6
        assert selected[0] == 'provider-0'
        assert selected[3] == 'provider-0'  # Second round
        
    def test_weighted_selection(self, mock_providers):
        """Test weighted selection"""
        mock_providers[0].config.weight = 3
        mock_providers[1].config.weight = 2
        mock_providers[2].config.weight = 1
        
        lb = LoadBalancer(mock_providers, 'weighted')
        
        # Provider 0 should be selected more often
        counts = {'provider-0': 0, 'provider-1': 0, 'provider-2': 0}
        for _ in range(100):
            provider = asyncio.run(lb.select_provider())
            if provider:
                counts[provider.config.name] += 1
                asyncio.run(lb.release_provider(provider))
        
        assert counts['provider-0'] > counts['provider-2']
        
    def test_least_connections(self, mock_providers):
        """Test least connections strategy"""
        lb = LoadBalancer(mock_providers, 'least_connections')
        
        # Select first provider
        p1 = asyncio.run(lb.select_provider())
        assert p1.config.name == 'provider-0'
        
        # Should select different provider with fewer connections
        p2 = asyncio.run(lb.select_provider())
        assert p2.config.name in ['provider-1', 'provider-2']
        
        if p1:
            asyncio.run(lb.release_provider(p1))
        if p2:
            asyncio.run(lb.release_provider(p2))


class TestCostTracker:
    """Test cost tracker"""
    
    def test_cost_tracking(self):
        """Test basic cost tracking"""
        tracker = CostTracker(daily_limit=10.0, monthly_limit=100.0)
        
        tracker.add_request(0.5, 1000, 'openai', 'gpt-4')
        tracker.add_request(0.3, 500, 'openai', 'gpt-4')
        
        stats = tracker.get_stats()
        assert stats['total_cost'] == 0.8
        assert stats['total_requests'] == 2
        
    def test_budget_check(self):
        """Test budget checking"""
        tracker = CostTracker(daily_limit=5.0, monthly_limit=50.0)
        
        tracker.add_request(3.0, 6000, 'openai', 'gpt-4')
        
        budget = tracker.check_budget()
        assert budget['daily']['remaining'] == 2.0
        assert budget['daily']['exceeded'] == False
        
        tracker.add_request(3.0, 6000, 'openai', 'gpt-4')
        
        budget = tracker.check_budget()
        assert budget['daily']['exceeded'] == True
        
    def test_budget_exceeded(self):
        """Test budget exceeded scenario"""
        tracker = CostTracker(daily_limit=1.0, monthly_limit=10.0)
        
        # Add requests that exceed daily limit
        for _ in range(10):
            tracker.add_request(0.2, 400, 'openai', 'gpt-4')
        
        budget = tracker.check_budget()
        assert budget['daily']['exceeded'] == True


class TestCircuitBreaker:
    """Test circuit breaker"""
    
    def test_circuit_closed_by_default(self):
        """Test circuit is closed initially"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        
        assert cb.is_open('test-provider') == False
        assert cb.get_state('test-provider') == 'closed'
        
    def test_circuit_opens_after_failures(self):
        """Test circuit opens after threshold failures"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        
        for _ in range(3):
            cb.record_failure('test-provider')
        
        assert cb.is_open('test-provider') == True
        assert cb.get_state('test-provider') == 'open'
        
    def test_circuit_resets_on_success(self):
        """Test circuit resets on success"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        
        cb.record_failure('test-provider')
        cb.record_failure('test-provider')
        cb.record_success('test-provider')
        
        # Failures should be reset, need 3 more to open
        cb.record_failure('test-provider')
        cb.record_failure('test-provider')
        cb.record_failure('test-provider')
        
        assert cb.is_open('test-provider') == True


class TestApiGateway:
    """Test API Gateway"""
    
    @pytest.fixture
    def gateway_config(self):
        """Create test gateway config"""
        return ApiForgeConfig(
            port=8080,
            host='0.0.0.0',
            providers=[
                ProviderConfig(
                    name='test-provider',
                    api_type='openai',
                    api_key='test-key',
                    base_url='https://api.test.com',
                    model='test-model',
                    enabled=True,
                    weight=1
                )
            ],
            load_balancer=LoadBalancerConfig(
                strategy='round_robin'
            ),
            safety=SafetyConfig(
                daily_budget_usd=100.0,
                monthly_budget_usd=1000.0
            )
        )
    
    def test_gateway_initialization(self, gateway_config):
        """Test gateway initialization"""
        gateway = ApiGateway(gateway_config)
        
        assert len(gateway.providers) == 1
        assert gateway.cost_tracker is not None
        assert gateway.circuit_breaker is not None
        assert gateway.load_balancer is not None
        
    def test_gateway_metrics(self, gateway_config):
        """Test gateway metrics"""
        gateway = ApiGateway(gateway_config)
        
        metrics = gateway.get_metrics()
        
        assert 'total_requests' in metrics
        assert 'successful_requests' in metrics
        assert 'failed_requests' in metrics
        assert 'total_cost' in metrics
        assert 'success_rate' in metrics
        
    def test_gateway_health_check(self, gateway_config):
        """Test gateway health check"""
        gateway = ApiGateway(gateway_config)
        
        health = asyncio.run(gateway.health_check())
        
        assert 'test-provider' in health
        assert 'healthy' in health['test-provider']


class TestProviderStats:
    """Test provider statistics"""
    
    def test_provider_stats_update(self):
        """Test provider stats update"""
        config = ProviderConfig(
            name='test',
            api_type='openai',
            api_key='key',
            base_url='https://api.test.com',
            model='model'
        )
        provider = OpenAIProvider(config)
        
        provider.update_stats(1000, 0.001, error=False)
        provider.update_stats(500, 0.0005, error=False)
        provider.update_stats(0, 0, error=True)
        
        stats = provider.get_stats()
        assert stats['requests'] == 3
        assert stats['tokens'] == 1500
        assert stats['errors'] == 1
        assert stats['consecutive_failures'] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
