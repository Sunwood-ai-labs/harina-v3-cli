from harina.ocr import ReceiptOCR
from pathlib import Path

# OCRプロセッサの初期化
ocr = ReceiptOCR()

# 画像パスの指定
image_path = Path("example/receipt-sample/IMG_8923.jpg")

# XML形式で処理
print("Processing in XML format...")
xml_result = ocr.process_receipt(image_path, output_format='xml')
print(xml_result[:200] + "..." if len(xml_result) > 200 else xml_result)

# CSV形式で処理
print("\nProcessing in CSV format...")
csv_result = ocr.process_receipt(image_path, output_format='csv')
print(csv_result[:200] + "..." if len(csv_result) > 200 else csv_result)