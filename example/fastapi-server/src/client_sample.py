"""
Harina v3 Fast API クライアントサンプル
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import requests
import json
import base64

# APIサーバーのURL
API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """ヘルスチェックのテスト"""
    print("🔍 ヘルスチェックを実行中...")
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"ステータス: {response.status_code}")
    print(f"レスポンス: {response.json()}")
    print()

def process_receipt_image(image_path: str, model: str = "gemini/gemini-2.5-flash", format: str = "xml"):
    """
    レシート画像を処理する
    
    Args:
        image_path: 画像ファイルのパス
        model: 使用するAIモデル
        format: 出力形式 (xml/csv)
    """
    image_file = Path(image_path)
    
    if not image_file.exists():
        print(f"❌ 画像ファイルが見つかりません: {image_path}")
        return
    
    print(f"📸 レシート画像を処理中: {image_file.name}")
    print(f"🤖 使用モデル: {model}")
    print(f"📄 出力形式: {format}")
    
    try:
        with open(image_file, 'rb') as f:
            files = {'file': (image_file.name, f, 'image/jpeg')}
            data = {
                'model': model,
                'format': format
            }
            
            response = requests.post(
                f"{API_BASE_URL}/process",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ 処理成功!")
                print(f"📊 結果 ({result['format']} 形式):")
                print("-" * 50)
                print(result['data'])
                print("-" * 50)
                
                # ファイルに保存
                output_file = f"output_{image_file.stem}.{format}"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result['data'])
                print(f"💾 結果を保存しました: {output_file}")
            else:
                print(f"❌ 処理エラー: {result['error']}")
        else:
            print(f"❌ APIエラー: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ リクエストエラー: {e}")
    
    print()

def process_receipt_base64(image_path: str, model: str = "gemini/gemini-2.5-flash", format: str = "xml"):
    """
    BASE64エンコードでレシート画像を処理する（汎用的な方法）
    
    Args:
        image_path: 画像ファイルのパス
        model: 使用するAIモデル
        format: 出力形式 (xml/csv)
    """
    image_file = Path(image_path)
    
    if not image_file.exists():
        print(f"❌ 画像ファイルが見つかりません: {image_path}")
        return
    
    print(f"📸 レシート画像を処理中（BASE64）: {image_file.name}")
    print(f"🤖 使用モデル: {model}")
    print(f"📄 出力形式: {format}")
    
    try:
        # 画像をBASE64エンコード
        with open(image_file, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # APIリクエスト
        request_data = {
            "image_base64": image_base64,
            "model": model,
            "format": format
        }
        
        response = requests.post(
            f"{API_BASE_URL}/process_base64",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ 処理成功（BASE64）!")
                print(f"📊 結果 ({result['format']} 形式):")
                print("-" * 50)
                print(result['data'])
                print("-" * 50)
                
                # ファイルに保存
                output_file = f"output_base64_{image_file.stem}.{format}"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result['data'])
                print(f"💾 結果を保存しました: {output_file}")
            else:
                print(f"❌ 処理エラー: {result['error']}")
        else:
            print(f"❌ APIエラー: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ リクエストエラー: {e}")
    
    print()

def main():
    """メイン関数"""
    print("🚀 Harina v3 Fast API クライアントサンプル")
    print("=" * 50)
    
    # ヘルスチェック
    test_health_check()
    
    # サンプル画像のパス（ハードコード）
    image_path = Path(__file__).parent / "IMG_8923.jpg"
    
    if image_path.exists():
        print(f"📁 使用する画像: {image_path}")
        
        print("\n🔄 ファイルアップロード方式:")
        # XML形式で処理
        process_receipt_image(str(image_path), format="xml")
        
        # CSV形式で処理
        process_receipt_image(str(image_path), format="csv")
        
        print("\n🔄 BASE64方式（汎用的）:")
        # BASE64方式でXML形式で処理
        process_receipt_base64(str(image_path), format="xml")
        
        # BASE64方式でCSV形式で処理
        process_receipt_base64(str(image_path), format="csv")
        
        # 異なるモデルで処理（環境変数でAPIキーが設定されている場合）
        # process_receipt_base64(str(image_path), model="gpt-4o", format="xml")
        
    else:
        print(f"❌ サンプル画像が見つかりません: {image_path}")
        print("IMG_8923.jpg を src フォルダに配置してください")

if __name__ == "__main__":
    main()