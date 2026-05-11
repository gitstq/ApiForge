# 🌐 ApiForge

> 🚀 軽量LLM API統一ゲートウェイ＆ロードバランサーエンジン

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Stars](https://img.shields.io/github/stars/YOUR_USERNAME/ApiForge?style=flat-square)](https://github.com/YOUR_USERNAME/ApiForge/stargazers)

<!-- Language Switcher -->
<div align="center">

| [简体中文](README.md) | [繁體中文](README_zh_TW.md) | [English](README_en.md) | [日本語](README_ja.md) |
|:---:|:---:|:---:|:---:|

</div>

---

## 🎉 プロジェクト紹介

**ApiForge** は、LLMアプリケーション用に設計された軽量なAPIゲートウェイ＆ロードバランサーエンジンです。OpenAI、Anthropic、Ollamaなど、複数のLLMサービスプロバイダを統一管理し、スマートルーティング、コスト管理、サーキットブレーカー保護などのエンタープライズ機能を提供し、AIアプリケーションをより安定高效的、経済的にします！

### 🔥 解決するコア課題

- 🔄 **マルチプロバイダー切替**：コード変更なしで異なるLLM服务商を自由に切替
- 💰 **コスト管理**：各リクエストのコストを正確に追跡、予算上限を設定して超過を防ぐ
- ⚡ **ロードバランシング**：複数の戦略（ラウンドロビン/加重/最小接続）でインテリジェントにリクエスト分配
- 🛡️ **サーキットブレーカー保護**：故障プロバイダーを自動遮断、サービスの可用性を確保
- 📊 **リアルタイム監視**：コストとトラフィックの清晰なダッシュボード

### ✨ コア機能

| 機能 | 説明 |
|------|------|
| 🌐 **マルチProvider支援** | OpenAI、Anthropic Claude、Ollama、すべてのOpenAI互換API |
| ⚖️ **5種類のロードバランシング戦略** | ラウンドロビン、加重、最小接続、ランダム、優先順位 |
| 💰 **スマートコスト追跡** | 各リクエストのトークン消費とコストをリアルタイム記録 |
| 🛡️ **サーキットブレーカーモード** | 故障Providerを自動検出、健康なノードに切り替え |
| 📈 **予算管理** | 日/月間予算上限、超過時は自動ブロック |
| 🔄 **統一APIインターフェース** | OpenAI互換の `/v1/chat/completions` エンドポイント |
| 🌊 **SSEストリーミング応答** | ストリーミング出力をサポート、リアルタイムコンテンツ生成 |
| 📊 **リアルタイム監視** | Providerステータス、リクエスト量、レイテンシー、コストを一目で確認 |
| 🔧 **YAML設定** | シンプルな設定、変更は即時適用、コード変更不要 |
| 🪶 **ゼロ依存** | コア機能はPyYAMLとaiohttpのみが必要 |
| 🌍 **クロスプラットフォーム** | Linux / macOS / Windows 完全対応 |

### 🚀 クイックスタート

#### 📦 インストール

```bash
# pipでインストール
pip install apiforge

# ソースからインストール
git clone https://github.com/YOUR_USERNAME/ApiForge.git
cd ApiForge
pip install -e .
```

#### ⚙️ 設定

```bash
# 設定ファイルを初期化
apiforge --init

# 設定ファイルを編集、APIキーを入力
vim config.yaml
```

**設定ファイル例 (config.yaml)**：

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

#### 🚀 サービス起動

```bash
# ゲートウェイサービスを開始
apiforge

# 起動後：
# ╔══════════════════════════════════════════════════════════════╗
# ║                    🚀 ApiForge v1.0.0                       ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  Server:     http://0.0.0.0:8080                            ║
# ╚══════════════════════════════════════════════════════════════╝
```

#### 📡 API呼び出し例

**cURL呼び出し**：

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

**Python SDK呼び出し**：

```python
import openai

# base URLを切り替えればApiForgeを使用可能
client = openai.OpenAI(
    api_key="dummy",  # 実際のキーはconfig.yamlで管理
    base_url="http://localhost:8080/v1"
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

#### 📊 監視エンドポイント

```bash
# ゲートウェイメトリクスを取得
curl http://localhost:8080/metrics

# ヘルスチェック
curl http://localhost:8080/health

# 予算ステータス
curl http://localhost:8080/budget
```

### 📖 詳細な使用方法

#### 🔄 ロードバランシング戦略の詳細

| 戦略 | 最適な用途 | 説明 |
|------|----------|------|
| `round_robin` | 汎用 | 均等分配、シンプルで効率的 |
| `weighted` | プロバイダー性能が異なる場合 | 重量比で分配 |
| `least_connections` | リクエスト時間が異なる場合 | 現在の接続数が最少のProviderに分配 |
| `random` | ステートレスサービス | 完全ランダム選択 |
| `priority` | プライマリ/バックアップ | 高優先度Providerを優先使用 |

#### 💰 コスト計算

```yaml
# コスト自動計算（実際の使用量に基づく）
safety:
  daily_budget_usd: 100.0
  monthly_budget_usd: 1000.0
```

#### 🛡️ サーキットブレーカーメカニズム

```yaml
load_balancer:
  failure_threshold: 3    # 3回連続失敗で遮断
  recovery_timeout: 60    # 60秒後に回復試行
```

### 💡 設計思想とロードマップ

#### 🎯 設計思想

- **ミニマリズム**：外部依存ゼロ、コア機能はPyYAMLとaiohttpのみ
- **YAML駆動**：すべての設定をYAMLファイルで管理、コード変更不要
- **フォールトトレランス優先**：サーキットブレーカー、リトライ機構、自动フェイルオーバーを内置
- **コスト透明性**：每一分の行き先を正確に追跡

#### 🗺️ 今後のロードマップ

- [ ] **v1.1.0** - Redisキャッシュサポート、重複リクエスト秒単位応答
- [ ] **v1.2.0** - Prometheusメトリクス統合、Grafana可視化
- [ ] **v1.3.0** - Web Dashboard、グラフィカル設定と監視
- [ ] **v2.0.0** - プラグインシステム、カスタムProviderサポート
- [ ] **v2.1.0** - Kubernetes展開サポート、自動スケーリング

### 🤝 コントリビューション

IssueとPull Requestを歓迎します！

1. 🍴 リポジトリをFork
2. 🔨 機能ブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 💬 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. 📤 ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. 🎉 Pull Requestを作成

### 📄 ライセンス

このプロジェクトは [MIT License](LICENSE) に基づいて开源です。

---

<div align="center">

**⭐ このプロジェクトが役に立ったら、Starを忘れずによろしく！**

Made with ❤️ by [Your Name]

</div>
