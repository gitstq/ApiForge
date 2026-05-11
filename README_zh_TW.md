# 🌐 ApiForge

> 🚀 輕量級LLM API統一網關與負載均衡引擎 | Lightweight LLM API Gateway & Load Balancer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Stars](https://img.shields.io/github/stars/YOUR_USERNAME/ApiForge?style=flat-square)](https://github.com/YOUR_USERNAME/ApiForge/stargazers)

<!-- Language Switcher -->
<div align="center">

| [简体中文](README.md) | [繁體中文](README_zh_TW.md) | [English](README_en.md) | [日本語](README_ja.md) |
|:---:|:---:|:---:|:---:|

</div>

---

## 🎉 項目介紹

**ApiForge** 是一款專為LLM應用設計的輕量級API網關與負載均衡引擎。它能夠統一管理多個LLM服務提供商（如OpenAI、Anthropic、Ollama等），提供智能路由、成本控制、熔斷保護等企業級功能，讓您的AI應用更加穩定、高效、經濟！

### 🔥 解決的核心痛點

- 🔄 **多提供商切換**：無需修改代碼，即可自由切換不同的LLM服務商
- 💰 **成本控制**：精確追蹤每個請求的成本，設置預算上限避免超支
- ⚡ **負載均衡**：多種策略（輪詢/加權/最少連接）智能分配請求
- 🛡️ **熔斷保護**：自動熔斷故障提供商，保障服務可用性
- 📊 **實時監控**：清晰的成本與流量儀表盤

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🌐 **多Provider支援** | OpenAI、Anthropic Claude、Ollama及所有相容OpenAI格式的API |
| ⚖️ **5種負載均衡策略** | 輪詢(Round Robin)、加權(Weighted)、最少連接(Least Connections)、隨機(Random)、優先級(Priority) |
| 💰 **智能成本追蹤** | 即時記錄每個請求的token消耗與成本 |
| 🛡️ **熔斷器模式** | 自動檢測故障Provider並切換到健康節點 |
| 📈 **預算控制** | 日/月度預算上限，超額自動攔截 |
| 🔄 **統一API介面** | OpenAI相容的 `/v1/chat/completions` 介面 |
| 🌊 **SSE流式響應** | 支援流式輸出，即時返回生成內容 |
| 📊 **即時監控** | Provider狀態、請求量、延遲、成本一目了然 |
| 🔧 **YAML配置** | 極簡配置，即改即用，無需代碼修改 |
| 🪶 **零外部依賴** | 核心功能僅需PyYAML和aiohttp |
| 🌍 **跨平台運行** | Linux / macOS / Windows 全平台支援 |

### 🚀 快速開始

#### 📦 安裝

```bash
# 使用 pip 安裝
pip install apiforge

# 或下載原始碼安裝
git clone https://github.com/YOUR_USERNAME/ApiForge.git
cd ApiForge
pip install -e .
```

#### ⚙️ 配置

```bash
# 初始化配置文件
apiforge --init

# 編輯配置文件，填入您的API密鑰
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

#### 🚀 啟動服務

```bash
# 啟動網關服務
apiforge

# 服務啟動後顯示：
# ╔══════════════════════════════════════════════════════════════╗
# ║                    🚀 ApiForge v1.0.0                       ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  Server:     http://0.0.0.0:8080                            ║
# ╚══════════════════════════════════════════════════════════════╝
```

#### 📡 API調用示例

**cURL調用**：

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

**Python SDK調用**：

```python
import openai

# 切換base URL即可使用ApiForge
client = openai.OpenAI(
    api_key="dummy",  # 實際密鑰在config.yaml中管理
    base_url="http://localhost:8080/v1"
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

#### 📊 監控介面

```bash
# 獲取網關指標
curl http://localhost:8080/metrics

# 健康檢查
curl http://localhost:8080/health

# 預算狀態
curl http://localhost:8080/budget
```

### 📖 詳細使用指南

#### 🔄 負載均衡策略詳解

| 策略 | 適用場景 | 說明 |
|------|----------|------|
| `round_robin` | 通用場景 | 輪流分配請求，簡單高效 |
| `weighted` | 多Provider效能不同時 | 按權重比例分配 |
| `least_connections` | 請求耗時差異大時 | 分配給當前連接數最少的Provider |
| `random` | 無狀態服務 | 完全隨機選擇 |
| `priority` | 主備切換 | 優先使用高優先級Provider |

#### 💰 成本計算

```yaml
# 成本自動計算（基於實際使用量）
safety:
  daily_budget_usd: 100.0    # 日預算上限
  monthly_budget_usd: 1000.0 # 月預算上限
```

#### 🛡️ 熔斷機制

```yaml
load_balancer:
  failure_threshold: 3    # 連續失敗3次後熔斷
  recovery_timeout: 60    # 60秒後嘗試恢復
```

### 💡 設計思路與迭代規劃

#### 🎯 設計理念

- **極簡主義**：零外部依賴，核心功能僅需PyYAML和aiohttp
- **YAML驅動**：所有配置通過YAML檔案管理，無需代碼修改
- **容錯優先**：內建熔斷器、重試機制、自動切換
- **成本透明**：精確追蹤每一分錢的去向

#### 🗺️ 未來迭代計劃

- [ ] **v1.1.0** - Redis緩存支援，重複請求秒級回應
- [ ] **v1.2.0** - Prometheus監控集成，Grafana視覺化
- [ ] **v1.3.0** - Web Dashboard，圖形化配置與監控
- [ ] **v2.0.0** - 插件系統，支援自訂義Provider
- [ ] **v2.1.0** - Kubernetes部署支援，自動擴縮容

### 🤝 貢獻指南

歡迎提交Issue和Pull Request！

1. 🍴 Fork 本倉庫
2. 🔨 建立特性分支 (`git checkout -b feature/AmazingFeature`)
3. 💬 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 📤 推送至分支 (`git push origin feature/AmazingFeature`)
5. 🎉 建立Pull Request

### 📄 開源協議

本項目基於 [MIT License](LICENSE) 開源。

---

<div align="center">

**⭐ 如果這個專案對您有幫助，請不要忘記 Star！**

Made with ❤️ by [Your Name]

</div>
