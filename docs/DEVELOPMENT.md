# 🔧 Harina v3 CLI - 開発者向けガイド

このドキュメントは、Harina v3 CLIの開発に参加する開発者向けの情報を提供します。

## 🏗️ プロジェクト構造

```
harina-v3-cli/
├── harina/                 # メインパッケージ
│   ├── __init__.py        # パッケージ初期化
│   ├── cli.py             # CLIインターフェース
│   ├── ocr.py             # OCR処理のメインロジック
│   ├── receipt_template.xml # XMLテンプレート
│   └── product_categories.xml # 商品カテゴリ定義
├── example/               # サンプルファイル
│   ├── README.md          # サンプル使用方法
│   └── receipt-sample/    # サンプルレシート画像
├── docs/                  # ドキュメント
├── .env.example           # 環境変数テンプレート
├── pyproject.toml         # プロジェクト設定
└── README.md              # メインドキュメント
```

## 🛠️ 開発環境のセットアップ

### 1. 依存関係のインストール

```bash
# uvを使用した環境構築
uv sync

# 開発モードでインストール
uv pip install -e .
```

### 2. 環境変数の設定

#### .envファイルを使用（推奨）

```bash
# .env.exampleをコピー
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

# Azure OpenAIを使用する場合
AZURE_API_KEY=your_azure_api_key_here
AZURE_API_BASE=your_azure_endpoint
AZURE_API_VERSION=your_azure_api_version

# デフォルトモデルの設定（オプション）
HARINA_MODEL=gemini/gemini-1.5-flash
```

#### 環境変数を直接設定

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_actual_gemini_api_key_here"
$env:OPENAI_API_KEY="your_actual_openai_api_key_here"
$env:ANTHROPIC_API_KEY="your_actual_anthropic_api_key_here"
```

**Windows (CMD):**
```cmd
set GEMINI_API_KEY=your_actual_gemini_api_key_here
set OPENAI_API_KEY=your_actual_openai_api_key_here
set ANTHROPIC_API_KEY=your_actual_anthropic_api_key_here
```

**Linux/macOS:**
```bash
export GEMINI_API_KEY="your_actual_gemini_api_key_here"
export OPENAI_API_KEY="your_actual_openai_api_key_here"
export ANTHROPIC_API_KEY="your_actual_anthropic_api_key_here"
```

**重要**: 実際のAPIキーを設定してください。プレースホルダーは実際の値に置き換えてください。

## 🧪 テストとデバッグ

### 基本的なテスト

```bash
# サンプル画像でテスト
harina example/receipt-sample/IMG_8923.jpg -v

# 異なるモデルでテスト
harina example/receipt-sample/IMG_8924.jpg --model gemini/gemini-1.5-pro -v
```

### デバッグモード

```bash
# 詳細ログを有効にして実行
harina path/to/image.jpg -v
```

## 📝 コード品質

### Linting

```bash
# flake8でコード品質チェック
flake8 harina/

# blackでコードフォーマット
black harina/
```

### 推奨事項

- 行の長さは100文字以内
- docstringは必須
- 型ヒントの使用を推奨
- ログメッセージには絵文字を使用

## 🔄 新機能の追加

### 新しいAIプロバイダーの追加

1. `ocr.py`でLiteLLMの設定を確認
2. 環境変数を`.env.example`に追加
3. README.mdの使用例を更新

### XMLテンプレートの修正

1. `harina/receipt_template.xml`を編集
2. `harina/product_categories.xml`でカテゴリを更新
3. サンプル出力を更新

## 🚀 リリースプロセス

### バージョン管理

```bash
# バージョンを更新
# harina/__init__.py の __version__ を更新
# pyproject.toml の version を更新
```

### ビルドとテスト

```bash
# パッケージをビルド
uv build

# インストールテスト
uv pip install dist/harina_v3_cli-*.whl
```

## 🤝 コントリビューション

### Pull Requestの作成

1. フィーチャーブランチを作成
2. 変更を実装
3. テストを実行
4. ドキュメントを更新
5. Pull Requestを作成

### コミットメッセージ

```
feat: 新機能の追加
fix: バグ修正
docs: ドキュメント更新
style: コードスタイル修正
refactor: リファクタリング
test: テスト追加
```

## 📊 パフォーマンス最適化

### 画像処理の最適化

- 画像サイズの最適化（品質85%のJPEG）
- base64エンコーディングの効率化
- メモリ使用量の監視

### API呼び出しの最適化

- リトライ機能の実装
- レート制限の考慮
- エラーハンドリングの改善

## 🔍 トラブルシューティング

### よくある開発時の問題

1. **ImportError**: パッケージが正しくインストールされているか確認
2. **API Error**: 環境変数が正しく設定されているか確認
3. **XML Parse Error**: テンプレートの構文を確認

### ログの活用

```python
from loguru import logger

# デバッグ情報の出力
logger.debug("Processing image: {}", image_path)
logger.info("API response received")
logger.error("Failed to process: {}", error)
```

## 📚 参考資料

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Google Gemini API](https://ai.google.dev/)
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic Claude API](https://docs.anthropic.com/)