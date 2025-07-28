"""
Fast API server for Harina v3 CLI - Receipt OCR API
"""
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

from harina.core import HarinaCore

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Harina v3 Receipt OCR API",
    description="レシート画像を認識してXML/CSV形式で出力するAPI",
    version="3.0.1"
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

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Harina v3 Receipt OCR API",
        "version": "3.0.1",
        "endpoints": {
            "process": "/process - レシート画像を処理",
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
    """
    レシート画像を処理してXMLまたはCSV形式で返す
    
    Args:
        file: アップロードされた画像ファイル
        model: 使用するAIモデル (デフォルト: gemini/gemini-2.5-flash)
        format: 出力形式 (xml または csv)
    
    Returns:
        ReceiptResponse: 処理結果
    """
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
                result = ocr.convert_xml_to_csv(xml_result)
            
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

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)