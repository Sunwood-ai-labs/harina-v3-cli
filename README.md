<div align="center">
  <img src="https://raw.githubusercontent.com/Sunwood-ai-labs/harina-v3-cli/refs/heads/main/header.png" alt="Harina v3 CLI" />
  <h1>Harina v3 CLI</h1>
  
  <p>
    <img src="https://img.shields.io/pypi/v/harina-v3-cli.svg" alt="PyPI version">
    <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
    <img src="https://img.shields.io/badge/AI-Gemini%20%7C%20GPT%20%7C%20Claude-green.svg" alt="AI Models">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License">
    <img src="https://img.shields.io/badge/CLI-Receipt%20OCR-orange.svg" alt="CLI Tool">
  </p>
</div>

レシート画像を認識してXML形式で出力するCLIツールです。LiteLLM経由で複数のAIプロバイダー（Google Gemini、OpenAI、Anthropic Claude等）を使用してレシートの内容を解析します。

## ✨ 機能

- レシート画像からテキスト情報を抽出
- 店舗情報、商品情報、金額情報を構造化されたXMLまたはCSV形式で出力
- Google Gemini APIを使用した高精度な画像認識
- コマンドライン インターフェース
- **🆕 FastAPIサーバーモード** - RESTful APIとしても利用可能
- 複数のAIプロバイダー対応（Gemini、OpenAI、Anthropic Claude）
- ファイルアップロードとBASE64エンコード両方に対応

## 🚀 クイックスタート

```bash
# PyPIからインストール
pip install harina-v3-cli

# CLIモード - レシート画像を処理
harina path/to/receipt.jpg

# サーバーモード - FastAPI RESTful APIを起動
harina --server
```

## 📦 インストール

### PyPIからインストール（推奨）

```bash
pip install harina-v3-cli
```

### 開発者向けインストール

```bash
# リポジトリをクローン
git clone https://github.com/Sunwood-ai-labs/harina-v3-cli.git
cd harina-v3-cli

# 依存関係をインストール
uv sync

# 開発モードでインストール
uv pip install -e .
```

## 💡 使用方法

### 🚀 FastAPIサーバーモード

CLIからFastAPIサーバーを起動して、RESTful APIとして利用できます：

```bash
# デフォルト設定でサーバー起動（ホスト: 0.0.0.0, ポート: 8000）
harina --server

# カスタムホスト・ポートでサーバー起動
harina --server --host 127.0.0.1 --port 8080

# 開発モード（自動リロード）でサーバー起動
harina --server --reload --verbose
```

#### 📡 利用可能なエンドポイント

サーバーが起動すると、以下のエンドポイントが利用できます：

| エンドポイント | メソッド | 説明 |
|---------------|----------|------|
| `/` | GET | API情報とエンドポイント一覧 |
| `/health` | GET | ヘルスチェック |
| `/process` | POST | ファイルアップロード方式でレシート処理 |
| `/process_base64` | POST | BASE64エンコード方式でレシート処理 |

#### 🌐 アクセス可能なURL

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### 📝 API使用例

**ファイルアップロード方式:**
```bash
curl -X POST "http://localhost:8000/process" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@receipt.jpg" \
  -F "model=gemini/gemini-2.5-flash" \
  -F "format=xml"
```

**BASE64エンコード方式:**
```bash
curl -X POST "http://localhost:8000/process_base64" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "base64_encoded_image_data",
    "model": "gemini/gemini-2.5-flash",
    "format": "xml"
  }'
```

#### 🔧 サーバー設定オプション

| オプション | デフォルト | 説明 |
|-----------|-----------|------|
| `--host` | `0.0.0.0` | サーバーのホストアドレス |
| `--port` | `8000` | サーバーのポート番号 |
| `--reload` | `False` | 開発用自動リロード機能 |
| `--verbose` | `False` | 詳細ログ出力 |

### 🔑 環境変数の設定

APIキーを設定するには、`.env`ファイルを使用します：

```bash
# .envファイルの例をコピー
cp .env.example .env
```

`.env`ファイルを編集してAPIキーを設定：

```
# Google Geminiを使用する場合（デフォルト）
GEMINI_API_KEY=your_actual_gemini_api_key_here

# その他のプロバイダーについては.env.exampleを参照
```

**詳細な環境変数設定については、[開発者向けガイド](docs/DEVELOPMENT.md)をご覧ください。**

### 🛠️ 基本的な使用方法

```bash
# 標準出力にXMLを出力（デフォルト: Gemini 1.5 Flash）
harina path/to/receipt_image.jpg

# ファイルに出力（XML形式）
harina path/to/receipt_image.jpg -o output.xml

# CSV形式で出力
harina path/to/receipt_image.jpg --format csv -o output.csv

# 異なるGeminiモデルを使用
harina path/to/receipt_image.jpg --model gemini/gemini-1.5-pro

# OpenAIのGPT-4oを使用する場合（OPENAI_API_KEYが必要）
harina path/to/receipt_image.jpg --model gpt-4o

# Claude 3 Sonnetを使用する場合（ANTHROPIC_API_KEYが必要）
harina path/to/receipt_image.jpg --model claude-3-sonnet-20240229

# 環境変数でデフォルトモデルを設定
export HARINA_MODEL=gpt-4o
harina path/to/receipt_image.jpg

# FastAPIサーバーモードで起動
harina --server

# カスタムホスト・ポートでサーバー起動
harina --server --host 127.0.0.1 --port 8080

# 開発モード（自動リロード）でサーバー起動
harina --server --reload
```

### 📄 出力形式

### XML形式

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

### CSV形式

CSVの出力形式は以下のようになります：

```csv
store_name,store_address,store_phone,transaction_date,transaction_time,receipt_number,item_name,item_category,item_subcategory,item_quantity,item_unit_price,item_total_price,subtotal,tax,total,payment_method,amount_paid,change
店舗名,住所,電話番号,2024-01-15,14:30,12345,商品名1,カテゴリ1,サブカテゴリ1,1,100,100,500,50,550,現金,1000,450
店舗名,住所,電話番号,2024-01-15,14:30,12345,商品名2,カテゴリ2,サブカテゴリ2,2,200,400,500,50,550,現金,1000,450
```

各商品は1行として出力され、店舗情報や取引情報は各商品行に繰り返し含まれます。

## 🖼️ 対応画像形式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- その他PIL（Pillow）でサポートされている形式

## 📋 必要な依存関係

### 基本依存関係
- Python 3.8以上
- litellm
- click
- pillow
- requests
- python-dotenv
- loguru
- tqdm

### FastAPIサーバー用追加依存関係
- fastapi
- uvicorn[standard]
- python-multipart

これらの依存関係は`pip install harina-v3-cli`で自動的にインストールされます。

## 🔐 API キーの取得

使用するモデルプロバイダーに応じて、以下からAPIキーを取得してください：

| プロバイダー         | 取得先                                                       | 環境変数            |
| -------------------- | ------------------------------------------------------------ | ------------------- |
| **Google Gemini**    | [Google AI Studio](https://makersuite.google.com/app/apikey) | `GEMINI_API_KEY`    |
| **OpenAI GPT**       | [OpenAI Platform](https://platform.openai.com/api-keys)      | `OPENAI_API_KEY`    |
| **Anthropic Claude** | [Anthropic Console](https://console.anthropic.com/)          | `ANTHROPIC_API_KEY` |

### 🔒 セキュリティに関する重要な注意事項

- **APIキーを直接コードに書き込まないでください**
- **APIキーをGitリポジトリにコミットしないでください**
- `.env`ファイルは`.gitignore`に含まれているため、Gitで追跡されません
- 本番環境では環境変数を使用してAPIキーを設定してください
- APIキーが漏洩した場合は、すぐにGoogle AI Studioで無効化し、新しいキーを生成してください

## 🔄 使用モード比較

| 機能 | CLIモード | サーバーモード |
|------|-----------|---------------|
| **用途** | 単発のレシート処理 | 継続的なAPI提供 |
| **起動方法** | `harina image.jpg` | `harina --server` |
| **出力** | ファイル/標準出力 | JSON レスポンス |
| **統合** | シェルスクリプト | Web アプリケーション |
| **スケーラビリティ** | 単一処理 | 複数同時リクエスト対応 |

## 🛠️ 開発・カスタマイズ

### カスタムテンプレート
```bash
# カスタムXMLテンプレートを使用
harina image.jpg --template custom_template.xml

# カスタム商品カテゴリを使用
harina image.jpg --categories custom_categories.xml
```

### 環境変数での設定
```bash
# デフォルトモデルを設定
export HARINA_MODEL=gpt-4o

# サーバー設定
export HOST=127.0.0.1
export PORT=8080
```

## 📚 詳細ドキュメント

- [💡 使用例とサンプル](example/README.md)
- [🔧 開発者向けガイド](docs/DEVELOPMENT.md)
- [🌐 FastAPIサーバー詳細](example/fastapi-server/README.md)

## 🤝 コントリビューション

プルリクエストやイシューの報告を歓迎します！

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

MIT License