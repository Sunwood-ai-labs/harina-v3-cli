# Harina v3 CLI

レシート画像を認識してXML形式で出力するCLIツールです。LiteLLM経由でGoogle Gemini APIを使用してレシートの内容を解析します。

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
GEMINI_API_KEY=your_api_key_here
```

#### 方法2: 環境変数を直接設定

```bash
export GEMINI_API_KEY="your_api_key_here"
```

### 基本的な使用方法

```bash
# 標準出力にXMLを出力
harina path/to/receipt_image.jpg

# ファイルに出力
harina path/to/receipt_image.jpg -o output.xml

# API キーを直接指定
harina path/to/receipt_image.jpg --api-key YOUR_API_KEY

# 異なるモデルを使用
harina path/to/receipt_image.jpg --model gemini/gemini-1.5-pro
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

Google AI Studio (https://makersuite.google.com/app/apikey) でGemini API キーを取得してください。

## ライセンス

MIT License