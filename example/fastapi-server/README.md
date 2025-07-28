# Harina v3 Fast API Server

このディレクトリには、Harina v3 CLIツールをFast APIサーバーとして展開するためのファイルが含まれています。

## 📁 ファイル構成

```
fastapi-server/
├── main.py              # Fast APIサーバーのメインファイル
├── client_sample.py     # APIクライアントのサンプル
├── requirements.txt     # 依存関係
└── README.md           # このファイル
```

## 🚀 セットアップと起動

### 前提条件

このFast APIサーバーは、プロジェクトルートの`harina`パッケージを直接インポートします。
`example/fastapi-server/`ディレクトリから実行してください。

**依存関係について:**
- プロジェクトルートの`pyproject.toml`と同じ依存関係を使用
- `harina-v3-cli`パッケージをインストールする代わりに、プロジェクトルートから直接インポート
- Windows環境での互換性問題を回避

### 1. 依存関係のインストール

#### uv add を使用した依存関係追加（推奨）

```bash
# Fast API関連
uv add fastapi
uv add "uvicorn[standard]"
uv add python-multipart
uv add python-dotenv
uv add requests

# Harina v3 CLI関連
uv add pillow
uv add click
uv add loguru
uv add tqdm
uv add litellm

# 開発用依存関係
uv add --dev pytest
uv add --dev pytest-asyncio
uv add --dev httpx
uv add --dev black
uv add --dev flake8

# 最終的な同期
uv sync
```

#### 一括コマンド

```bash
# 全ての依存関係を一度に追加
uv add fastapi "uvicorn[standard]" python-multipart python-dotenv requests pillow click loguru tqdm litellm

# 開発用依存関係
uv add --dev pytest pytest-asyncio httpx black flake8
```

#### pip を使用

```bash
# 仮想環境を作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt
```

### 2. 環境変数の設定

プロジェクトルートの `.env` ファイルでAPIキーを設定してください：

```bash
# Google Geminiを使用する場合（デフォルト）
GEMINI_API_KEY=your_actual_gemini_api_key_here

# その他のプロバイダーを使用する場合
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. サーバーの起動

```bash
# 起動スクリプトを使用（推奨）
uv run python run_server.py

# または直接起動
uv run python main.py

# uvicorn で起動
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

サーバーが起動すると、以下のURLでアクセスできます：
- API: http://localhost:8000
- ドキュメント: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 API エンドポイント

### GET /
ルートエンドポイント - API情報を返します

### GET /health
ヘルスチェックエンドポイント

### POST /process
レシート画像を処理するメインエンドポイント

**パラメータ:**
- `file`: レシート画像ファイル（必須）
- `model`: 使用するAIモデル（オプション、デフォルト: `gemini/gemini-2.5-flash`）
- `format`: 出力形式（オプション、`xml` または `csv`、デフォルト: `xml`）

**レスポンス例:**
```json
{
  "success": true,
  "data": "<?xml version=\"1.0\" ?>...",
  "format": "xml",
  "model": "gemini/gemini-2.5-flash",
  "error": null
}
```

## 🧪 クライアントサンプルの使用

```bash
# サーバーが起動していることを確認してから実行
uv run python client_sample.py

# APIテストの実行
uv run python test_api.py
```

クライアントサンプルは以下の処理を行います：
1. ヘルスチェック
2. サンプル画像の処理（XML形式）
3. サンプル画像の処理（CSV形式）
4. 結果をファイルに保存

## 🔧 カスタマイズ

### 異なるモデルの使用

```python
# OpenAI GPT-4oを使用
process_receipt_image("image.jpg", model="gpt-4o")

# Anthropic Claudeを使用
process_receipt_image("image.jpg", model="claude-3-sonnet-20240229")
```

### カスタムテンプレートの使用

`main.py` を編集して、カスタムテンプレートパスを指定できます：

```python
ocr = HarinaCore(
    model_name=model,
    template_path="path/to/custom_template.xml",
    categories_path="path/to/custom_categories.xml"
)
```

## 🐳 Docker での実行

Dockerfileを作成して、コンテナ化することも可能です：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔒 セキュリティ考慮事項

- 本番環境では適切な認証・認可を実装してください
- APIキーは環境変数で管理し、コードに直接記述しないでください
- ファイルアップロードのサイズ制限を設定してください
- CORS設定を本番環境に合わせて調整してください

## 📊 パフォーマンス

- 大きな画像ファイルの処理には時間がかかる場合があります
- 必要に応じて非同期処理やキューシステムの導入を検討してください
- APIレート制限の実装を検討してください
## 📦 uv を
使用した開発

### プロジェクトのセットアップ

```bash
# プロジェクトディレクトリに移動
cd example/fastapi-server

# 依存関係をインストール
uv sync

# 開発用依存関係も含めてインストール
uv sync --dev
```

### 開発コマンド

```bash
# サーバー起動
uv run python run_server.py

# APIテスト実行
uv run python test_api.py

# クライアントサンプル実行
uv run python client_sample.py

# 依存関係の追加
uv add package_name

# 開発用依存関係の追加
uv add --dev package_name

# 依存関係の更新
uv sync --upgrade
```

### 仮想環境の管理

```bash
# 仮想環境をアクティベート
uv shell

# 仮想環境内でコマンド実行
uv run command

# 依存関係の確認
uv tree
```