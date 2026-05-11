# 🌐 ApiForge

> 🚀 轻量级LLM API统一网关与负载均衡引擎 | Lightweight LLM API Gateway & Load Balancer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Stars](https://img.shields.io/github/stars/YOUR_USERNAME/ApiForge?style=flat-square)](https://github.com/YOUR_USERNAME/ApiForge/stargazers)

<!-- Language Switcher -->
<div align="center">

| [简体中文](README.md) | [繁體中文](README_zh_TW.md) | [English](README_en.md) | [日本語](README_ja.md) |
|:---:|:---:|:---:|:---:|

</div>

---

## 🎉 项目介绍

**ApiForge** 是一款专为LLM应用设计的轻量级API网关与负载均衡引擎。它能够统一管理多个LLM服务提供商（如OpenAI、Anthropic、Ollama等），提供智能路由、成本控制、熔断保护等企业级功能，让您的AI应用更加稳定、高效、经济！

### 🔥 解决的核心痛点

- 🔄 **多提供商切换**：无需修改代码，即可自由切换不同的LLM服务商
- 💰 **成本控制**：精确追踪每个请求的成本，设置预算上限避免超支
- ⚡ **负载均衡**：多种策略（轮询/加权/最少连接）智能分配请求
- 🛡️ **熔断保护**：自动熔断故障提供商，保障服务可用性
- 📊 **实时监控**：清晰的成本与流量仪表盘

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🌐 **多Provider支持** | OpenAI、Anthropic Claude、Ollama及所有兼容OpenAI格式的API |
| ⚖️ **5种负载均衡策略** | 轮询(Round Robin)、加权(Weighted)、最少连接(Least Connections)、随机(Random)、优先级(Priority) |
| 💰 **智能成本追踪** | 实时记录每个请求的token消耗与成本 |
| 🛡️ **熔断器模式** | 自动检测故障Provider并切换到健康节点 |
| 📈 **预算控制** | 日/月度预算上限，超额自动拦截 |
| 🔄 **统一API接口** | OpenAI兼容的 `/v1/chat/completions` 接口 |
| 🌊 **SSE流式响应** | 支持流式输出，实时返回生成内容 |
| 📊 **实时监控** | Provider状态、请求量、延迟、成本一目了然 |
| 🔧 **YAML配置** | 极简配置，即改即用，无需代码修改 |
| 🪶 **零外部依赖** | 核心功能仅需PyYAML和aiohttp |
| 🌍 **跨平台运行** | Linux / macOS / Windows 全平台支持 |

### 🚀 快速开始

#### 📦 安装

```bash
# 使用 pip 安装
pip install apiforge

# 或下载源码安装
git clone https://github.com/YOUR_USERNAME/ApiForge.git
cd ApiForge
pip install -e .
```

#### ⚙️ 配置

```bash
# 初始化配置文件
apiforge --init

# 编辑配置文件，填入您的API密钥
vim config.yaml
```

**配置文件示例 (config.yaml)**：

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

#### 🚀 启动服务

```bash
# 启动网关服务
apiforge

# 服务启动后显示：
# ╔══════════════════════════════════════════════════════════════╗
# ║                    🚀 ApiForge v1.0.0                       ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  Server:     http://0.0.0.0:8080                            ║
# ╚══════════════════════════════════════════════════════════════╝
```

#### 📡 API调用示例

**cURL调用**：

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

**Python SDK调用**：

```python
import openai

# 切换base URL即可使用ApiForge
client = openai.OpenAI(
    api_key="dummy",  # 实际密钥在config.yaml中管理
    base_url="http://localhost:8080/v1"
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

#### 📊 监控接口

```bash
# 获取网关指标
curl http://localhost:8080/metrics

# 健康检查
curl http://localhost:8080/health

# 预算状态
curl http://localhost:8080/budget
```

### 📖 详细使用指南

#### 🔄 负载均衡策略详解

| 策略 | 适用场景 | 说明 |
|------|----------|------|
| `round_robin` | 通用场景 | 轮流分配请求，简单高效 |
| `weighted` | 多Provider性能不同时 | 按权重比例分配 |
| `least_connections` | 请求耗时差异大时 | 分配给当前连接数最少的Provider |
| `random` | 无状态服务 | 完全随机选择 |
| `priority` | 主备切换 | 优先使用高优先级Provider |

#### 💰 成本计算

```yaml
# 成本自动计算（基于实际使用量）
safety:
  daily_budget_usd: 100.0    # 日预算上限
  monthly_budget_usd: 1000.0 # 月预算上限
```

#### 🛡️ 熔断机制

```yaml
load_balancer:
  failure_threshold: 3    # 连续失败3次后熔断
  recovery_timeout: 60    # 60秒后尝试恢复
```

### 💡 设计思路与迭代规划

#### 🎯 设计理念

- **极简主义**：零外部依赖，核心功能仅需PyYAML和aiohttp
- **YAML驱动**：所有配置通过YAML文件管理，无需代码修改
- **容错优先**：内置熔断器、重试机制、自动切换
- **成本透明**：精确追踪每一分钱的去向

#### 🗺️ 未来迭代计划

- [ ] **v1.1.0** - Redis缓存支持，重复请求秒级响应
- [ ] **v1.2.0** - Prometheus监控集成，Grafana可视化
- [ ] **v1.3.0** - Web Dashboard，图形化配置与监控
- [ ] **v2.0.0** - 插件系统，支持自定义Provider
- [ ] **v2.1.0** - Kubernetes部署支持，自动扩缩容

### 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. 🍴 Fork 本仓库
2. 🔨 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 💬 提交变更 (`git commit -m 'Add some AmazingFeature'`)
4. 📤 推送到分支 (`git push origin feature/AmazingFeature`)
5. 🎉 创建Pull Request

### 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请不要忘记 Star！**

Made with ❤️ by [Your Name]

</div>
