"""開発用起動スクリプト（リロード機能付き）"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"],
        reload_excludes=[".venv/*", "__pycache__/*", "*.pyc"]
    )