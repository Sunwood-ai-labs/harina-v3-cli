# Harina v3 CLI

レシート画像を認識してXML形式で出力するCLIツールです。LiteLLM経由で複数のAIプロバイダー（Google Gemini、OpenAI、Anthropic Claude等）を使用してレシートの内容を解析します。

## 機能

- レシート画像からテキスト情報を抽出
- 店舗情報、商品情報、金額情報を構造化されたXML形式で出力
- Google Gemini APIを使用した高精度な画像認識
- コマンドライン インターフェース

## インストール

uvを使用して環境構築とインストールを行います：

```bash
# 依存関係をインストール
uv sync

# 開発モードでインストール
uv pip install -e .
```

## 使用方法

### 環境変数の設定

Gemini API キーを設定する方法は以下の通りです：

#### 方法1: .envファイルを使用（推奨）

プロジェクトルートに`.env`ファイルを作成してください：

```bash
# .envファイルの例をコピー
cp .env.example .env
```

`.env`ファイルを編集してAPIキーを設定：

```
# Google Geminiを使用する場合
GEMINI_API_KEY=your_actual_gemini_api_key_here

# OpenAI GPTを使用する場合
OPENAI_API_KEY=your_actual_openai_api_key_here

# Anthropic Claudeを使用する場合
ANTHROPIC_API_KEY=your_actual_anthropic_api_key_here
```

**重要**: 実際のAPIキーを設定してください。プレースホルダーは実際の値に置き換えてください。

#### 方法2: 環境変数を直接設定

Windows (PowerShell):
```powershell
# Google Geminiの場合
$env:GEMINI_API_KEY="your_actual_gemini_api_key_here"

# OpenAI GPTの場合
$env:OPENAI_API_KEY="your_actual_openai_api_key_here"

# Anthropic Claudeの場合
$env:ANTHROPIC_API_KEY="your_actual_anthropic_api_key_here"
```

Windows (CMD):
```cmd
rem Google Geminiの場合
set GEMINI_API_KEY=your_actual_gemini_api_key_here

rem OpenAI GPTの場合
set OPENAI_API_KEY=your_actual_openai_api_key_here

rem Anthropic Claudeの場合
set ANTHROPIC_API_KEY=your_actual_anthropic_api_key_here
```

Linux/macOS:
```bash
# Google Geminiの場合
export GEMINI_API_KEY="your_actual_gemini_api_key_here"

# OpenAI GPTの場合
export OPENAI_API_KEY="your_actual_openai_api_key_here"

# Anthropic Claudeの場合
export ANTHROPIC_API_KEY="your_actual_anthropic_api_key_here"
```

### 基本的な使用方法

```bash
# 標準出力にXMLを出力（デフォルト: Gemini 1.5 Flash）
harina path/to/receipt_image.jpg

# ファイルに出力
harina path/to/receipt_image.jpg -o output.xml

# 異なるGeminiモデルを使用
harina path/to/receipt_image.jpg --model gemini/gemini-1.5-pro

# OpenAIのGPT-4oを使用する場合（OPENAI_API_KEYが必要）
harina path/to/receipt_image.jpg --model gpt-4o

# Claude 3 Sonnetを使用する場合（ANTHROPIC_API_KEYが必要）
harina path/to/receipt_image.jpg --model claude-3-sonnet-20240229

# 環境変数でデフォルトモデルを設定
export HARINA_MODEL=gpt-4o
harina path/to/receipt_image.jpg
```

### 出力形式

XMLの出力形式は以下のようになります：

```xml
<?xml version="1.0" ?>
<receipt>
  <store_info>
    <name>店舗名</name>
    <address>住所</address>
    <phone>電話番号</phone>
  </store_info>
  <transaction_info>
    <date>2024-01-15</date>
    <time>14:30</time>
    <receipt_number>12345</receipt_number>
  </transaction_info>
  <items>
    <item>
      <name>商品名1</name>
      <quantity>1</quantity>
      <unit_price>100</unit_price>
      <total_price>100</total_price>
    </item>
    <item>
      <name>商品名2</name>
      <quantity>2</quantity>
      <unit_price>200</unit_price>
      <total_price>400</total_price>
    </item>
  </items>
  <totals>
    <subtotal>500</subtotal>
    <tax>50</tax>
    <total>550</total>
  </totals>
  <payment_info>
    <method>現金</method>
    <amount_paid>1000</amount_paid>
    <change>450</change>
  </payment_info>
</receipt>
```

## 対応画像形式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- その他PIL（Pillow）でサポートされている形式

## 必要な依存関係

- Python 3.8以上
- litellm
- click
- pillow
- requests

## API キーの取得

使用するモデルプロバイダーに応じて、以下からAPIキーを取得してください：

### Google Gemini
- [Google AI Studio](https://makersuite.google.com/app/apikey) でGemini API キーを取得
- 環境変数: `GEMINI_API_KEY`

### OpenAI GPT
- [OpenAI Platform](https://platform.openai.com/api-keys) でOpenAI API キーを取得
- 環境変数: `OPENAI_API_KEY`

### Anthropic Claude
- [Anthropic Console](https://console.anthropic.com/) でAnthropic API キーを取得
- 環境変数: `ANTHROPIC_API_KEY`

### セキュリティに関する重要な注意事項

- **APIキーを直接コードに書き込まないでください**
- **APIキーをGitリポジトリにコミットしないでください**
- `.env`ファイルは`.gitignore`に含まれているため、Gitで追跡されません
- 本番環境では環境変数を使用してAPIキーを設定してください
- APIキーが漏洩した場合は、すぐにGoogle AI Studioで無効化し、新しいキーを生成してください

## ライセンス

MIT License