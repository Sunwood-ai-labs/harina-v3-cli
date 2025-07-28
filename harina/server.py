"""FastAPI server for Harina v3 CLI - Receipt OCR API"""

import os
import sys
import tempfile
import base64
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
from loguru import logger

from .core import HarinaCore
from .utils import convert_xml_to_csv


def setup_environment():
    """環境設定"""
    # プロジェクトルートの.envファイルを読み込み
    load_dotenv()
    load_dotenv(Path.cwd() / '.env')
    
    # 環境変数の確認
    api_keys = {
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY')
    }
    
    available_keys = [key for key, value in api_keys.items() 
                     if value and value != 'your_api_key_here']
    
    if available_keys:
        logger.info(f"🔑 利用可能なAPIキー: {', '.join(available_keys)}")
    else:
        logger.warning("⚠️  APIキーが設定されていません")


def create_app() -> FastAPI:
    """FastAPIアプリケーションを作成"""
    app = FastAPI(
        title="Harina v3 Receipt OCR API",
        description="レシート画像を認識してXML/CSV形式で出力するAPI",
        version="3.1.0"
    )

    # CORS設定
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class ReceiptResponse(BaseModel):
        """レシート処理結果のレスポンスモデル"""
        success: bool
        data: Optional[str] = None
        format: str
        model: str
        error: Optional[str] = None

    class Base64Request(BaseModel):
        """BASE64画像リクエストモデル"""
        image_base64: str
        model: str = "gemini/gemini-2.5-flash"
        format: str = "xml"

    @app.get("/")
    async def root():
        """ルートエンドポイント"""
        return {
            "message": "Harina v3 Receipt OCR API",
            "version": "3.1.0",
            "endpoints": {
                "process": "/process - レシート画像を処理（ファイルアップロード）",
                "process_base64": "/process_base64 - レシート画像を処理（BASE64）",
                "health": "/health - ヘルスチェック"
            }
        }

    @app.get("/health")
    async def health_check():
        """ヘルスチェックエンドポイント"""
        return {"status": "healthy", "service": "harina-v3-api"}

    @app.post("/process", response_model=ReceiptResponse)
    async def process_receipt(
        file: UploadFile = File(..., description="レシート画像ファイル"),
        model: str = Form(default="gemini/gemini-2.5-flash", description="使用するAIモデル"),
        format: str = Form(default="xml", description="出力形式 (xml/csv)")
    ):
        """レシート画像を処理してXMLまたはCSV形式で返す"""
        # ファイル形式チェック
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail="画像ファイルをアップロードしてください"
            )
        
        # 出力形式チェック
        if format not in ['xml', 'csv']:
            raise HTTPException(
                status_code=400,
                detail="formatは 'xml' または 'csv' を指定してください"
            )
        
        try:
            # 一時ファイルに保存
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = Path(temp_file.name)
            
            try:
                # OCR処理
                ocr = HarinaCore(model_name=model)
                
                if format == 'xml':
                    result = ocr.process_receipt(temp_file_path, output_format='xml')
                else:
                    xml_result = ocr.process_receipt(temp_file_path, output_format='xml')
                    result = convert_xml_to_csv(xml_result)
                
                return ReceiptResponse(
                    success=True,
                    data=result,
                    format=format,
                    model=model
                )
                
            finally:
                # 一時ファイルを削除
                if temp_file_path.exists():
                    temp_file_path.unlink()
                    
        except Exception as e:
            return ReceiptResponse(
                success=False,
                format=format,
                model=model,
                error=str(e)
            )

    @app.post("/process_base64", response_model=ReceiptResponse)
    async def process_receipt_base64(request: Base64Request):
        """BASE64エンコードされたレシート画像を処理してXMLまたはCSV形式で返す"""
        # 出力形式チェック
        if request.format not in ['xml', 'csv']:
            raise HTTPException(
                status_code=400,
                detail="formatは 'xml' または 'csv' を指定してください"
            )
        
        try:
            # BASE64デコード
            try:
                image_data = base64.b64decode(request.image_base64)
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail="無効なBASE64データです"
                )
            
            # 一時ファイルに保存
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(image_data)
                temp_file_path = Path(temp_file.name)
            
            try:
                # OCR処理
                ocr = HarinaCore(model_name=request.model)
                
                if request.format == 'xml':
                    result = ocr.process_receipt(temp_file_path, output_format='xml')
                else:
                    xml_result = ocr.process_receipt(temp_file_path, output_format='xml')
                    result = convert_xml_to_csv(xml_result)
                
                return ReceiptResponse(
                    success=True,
                    data=result,
                    format=request.format,
                    model=request.model
                )
                
            finally:
                # 一時ファイルを削除
                if temp_file_path.exists():
                    temp_file_path.unlink()
                    
        except HTTPException:
            raise
        except Exception as e:
            return ReceiptResponse(
                success=False,
                format=request.format,
                model=request.model,
                error=str(e)
            )

    return app


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """FastAPIサーバーを起動"""
    logger.info("🚀 Harina v3 Fast API サーバーを起動中...")
    logger.info("=" * 50)
    
    # 環境設定
    setup_environment()
    
    # アプリケーション作成
    app = create_app()
    
    logger.info(f"🌐 サーバー設定:")
    logger.info(f"   ホスト: {host}")
    logger.info(f"   ポート: {port}")
    logger.info(f"   URL: http://localhost:{port}")
    logger.info(f"   ドキュメント: http://localhost:{port}/docs")
    logger.info(f"   ReDoc: http://localhost:{port}/redoc")
    logger.info("=" * 50)
    
    try:
        uvicorn.run(
            app, 
            host=host, 
            port=port,
            reload=reload,
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("\n👋 サーバーを停止しました")
    except Exception as e:
        logger.error(f"❌ サーバー起動エラー: {e}")
        sys.exit(1)