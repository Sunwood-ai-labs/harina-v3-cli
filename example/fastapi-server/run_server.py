"""
Harina v3 Fast API サーバー起動スクリプト
"""
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from dotenv import load_dotenv

def setup_environment():
    """環境設定"""
    # プロジェクトルートの.envファイルを読み込み
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / '.env'
    
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ 環境変数を読み込みました: {env_file}")
    else:
        print(f"⚠️  .envファイルが見つかりません: {env_file}")
        print("   APIキーが設定されていることを確認してください。")
    
    # ローカルの.envファイルも読み込み（優先）
    local_env = Path(__file__).parent / '.env'
    if local_env.exists():
        load_dotenv(local_env)
        print(f"✅ ローカル環境変数を読み込みました: {local_env}")

def check_api_keys():
    """APIキーの確認"""
    api_keys = {
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY')
    }
    
    available_keys = []
    for key_name, key_value in api_keys.items():
        if key_value and key_value != 'your_api_key_here':
            available_keys.append(key_name)
    
    if available_keys:
        print(f"🔑 利用可能なAPIキー: {', '.join(available_keys)}")
    else:
        print("⚠️  APIキーが設定されていません。")
        print("   .envファイルでAPIキーを設定してください。")

def main():
    """メイン関数"""
    print("🚀 Harina v3 Fast API サーバーを起動中...")
    print("=" * 50)
    
    # 環境設定
    setup_environment()
    
    # APIキー確認
    check_api_keys()
    
    # サーバー設定
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    
    print(f"🌐 サーバー設定:")
    print(f"   ホスト: {host}")
    print(f"   ポート: {port}")
    print(f"   URL: http://localhost:{port}")
    print(f"   ドキュメント: http://localhost:{port}/docs")
    print(f"   ReDoc: http://localhost:{port}/redoc")
    print("=" * 50)
    print("💡 使用方法:")
    print("   - APIテスト: uv run python test_api.py")
    print("   - クライアントサンプル: uv run python client_sample.py")
    print("=" * 50)
    
    try:
        # サーバー起動
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 サーバーを停止しました。")
    except Exception as e:
        print(f"❌ サーバー起動エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()