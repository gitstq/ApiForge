# 🌐 ApiForge

> 🚀 Lightweight LLM API Unified Gateway & Load Balancer Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Stars](https://img.shields.io/github/stars/YOUR_USERNAME/ApiForge?style=flat-square)](https://github.com/YOUR_USERNAME/ApiForge/stargazers)

<!-- Language Switcher -->
<div align="center">

| [简体中文](README.md) | [繁體中文](README_zh_TW.md) | [English](README_en.md) | [日本語](README_ja.md) |
|:---:|:---:|:---:|:---:|

</div>

---

## 🎉 Introduction

**ApiForge** is a lightweight API gateway and load balancer engine designed specifically for LLM applications. It unified manages multiple LLM service providers (such as OpenAI, Anthropic, Ollama, etc.), providing enterprise-level features like intelligent routing, cost control, and circuit breaker protection to make your AI applications more stable, efficient, and cost-effective!

### 🔥 Core Pain Points Solved

- 🔄 **Multi-Provider Switching**: Switch between different LLM providers without code changes
- 💰 **Cost Control**: Precisely track each request's cost with budget limits
- ⚡ **Load Balancing**: Intelligently distribute requests with multiple strategies (Round Robin/Weighted/Least Connections)
- 🛡️ **Circuit Breaker Protection**: Auto-circuit faulty providers to ensure service availability
- 📊 **Real-time Monitoring**: Clear cost and traffic dashboards at a glance

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🌐 **Multi-Provider Support** | OpenAI, Anthropic Claude, Ollama, and all OpenAI-compatible APIs |
| ⚖️ **5 Load Balancing Strategies** | Round Robin, Weighted, Least Connections, Random, Priority |
| 💰 **Smart Cost Tracking** | Real-time token consumption and cost recording |
| 🛡️ **Circuit Breaker Mode** | Auto-detect faulty Providers and switch to healthy nodes |
| 📈 **Budget Control** | Daily/Monthly budget limits with auto-blocking |
| 🔄 **Unified API Interface** | OpenAI-compatible `/v1/chat/completions` endpoint |
| 🌊 **SSE Streaming Response** | Support streaming output for real-time content generation |
| 📊 **Real-time Monitoring** | Provider status, request volume, latency, and cost metrics |
| 🔧 **YAML Configuration** | Simple config, apply instantly, no code changes needed |
| 🪶 **Zero Dependencies** | Core functionality requires only PyYAML and aiohttp |
| 🌍 **Cross-Platform** | Linux / macOS / Windows fully supported |

### 🚀 Quick Start

#### 📦 Installation

```bash
# Install via pip
pip install apiforge

# Or install from source
git clone https://github.com/YOUR_USERNAME/ApiForge.git
cd ApiForge
pip install -e .
```

#### ⚙️ Configuration

```bash
# Initialize config file
apiforge --init

# Edit config, add your API keys
vim config.yaml
```

**Configuration Example (config.yaml)**:

```yaml
version: '1.0.0'

server:
  port: 8080
  host: 0.0.0.0

providers:
  - name: openai-default
    api_type: openai
    api_key: sk-your-openai-key
    base_url: https://api.openai.com/v1
    model: gpt-4o-mini
    weight: 1
    enabled: true

  - name: anthropic-claude
    api_type: anthropic
    api_key: sk-ant-your-key
    base_url: https://api.anthropic.com
    model: claude-3-5-haiku-20241022
    weight: 1
    enabled: true

load_balancer:
  strategy: round_robin  # round_robin | weighted | least_connections | random | priority

safety:
  daily_budget_usd: 100.0
  monthly_budget_usd: 1000.0
```

#### 🚀 Start Service

```bash
# Start gateway service
apiforge

# Output:
# ╔══════════════════════════════════════════════════════════════╗
# ║                    🚀 ApiForge v1.0.0                       ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  Server:     http://0.0.0.0:8080                            ║
# ╚══════════════════════════════════════════════════════════════╝
```

#### 📡 API Usage Examples

**cURL Call**:

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "Hello! Tell me a joke."}
    ],
    "temperature": 0.7
  }'
```

**Python SDK Call**:

```python
import openai

# Switch base URL to use ApiForge
client = openai.OpenAI(
    api_key="dummy",  # Actual keys managed in config.yaml
    base_url="http://localhost:8080/v1"
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

#### 📊 Monitoring Endpoints

```bash
# Get gateway metrics
curl http://localhost:8080/metrics

# Health check
curl http://localhost:8080/health

# Budget status
curl http://localhost:8080/budget
```

### 📖 Detailed Usage Guide

#### 🔄 Load Balancing Strategies

| Strategy | Best For | Description |
|----------|----------|-------------|
| `round_robin` | General use | Cycles through providers evenly |
| `weighted` | Different provider capabilities | Distributes by weight ratio |
| `least_connections` | Varying request durations | Routes to least busy provider |
| `random` | Stateless services | Random selection |
| `priority` | Primary/backup setup | Prefers high-priority providers |

#### 💰 Cost Calculation

```yaml
# Automatic cost calculation (based on actual usage)
safety:
  daily_budget_usd: 100.0
  monthly_budget_usd: 1000.0
```

#### 🛡️ Circuit Breaker Mechanism

```yaml
load_balancer:
  failure_threshold: 3    # Trip after 3 consecutive failures
  recovery_timeout: 60    # Retry after 60 seconds
```

### 💡 Design Philosophy & Roadmap

#### 🎯 Design Principles

- **Minimalism**: Zero external dependencies, core needs only PyYAML and aiohttp
- **YAML-Driven**: All config via YAML files, no code changes needed
- **Fault-Tolerance First**: Built-in circuit breaker, retry mechanism, auto-failover
- **Cost Transparency**: Precisely track every cent spent

#### 🗺️ Future Roadmap

- [ ] **v1.1.0** - Redis caching support, instant duplicate request responses
- [ ] **v1.2.0** - Prometheus metrics integration, Grafana visualization
- [ ] **v1.3.0** - Web Dashboard, graphical config & monitoring
- [ ] **v2.0.0** - Plugin system, custom Provider support
- [ ] **v2.1.0** - Kubernetes deployment, auto-scaling

### 🤝 Contributing

Issues and Pull Requests are welcome!

1. 🍴 Fork the repository
2. 🔨 Create feature branch (`git checkout -b feature/AmazingFeature`)
3. 💬 Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push to branch (`git push origin feature/AmazingFeature`)
5. 🎉 Open Pull Request

### 📄 License

This project is open source under [MIT License](LICENSE).

---

<div align="center">

**⭐ If this project helps you, don't forget to Star!**

Made with ❤️ by [Your Name]

</div>
