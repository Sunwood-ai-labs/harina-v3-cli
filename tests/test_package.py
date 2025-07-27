import sys
from pathlib import Path

# Add the project root directory to the path so we can import harina as a package
sys.path.insert(0, str(Path(__file__).parent.parent))

from harina.core import HarinaCore
from harina.utils import convert_xml_to_csv
from pathlib import Path

# OCRプロセッサの初期化
ocr = HarinaCore()

# 画像パスの指定
image_path = Path("example/receipt-sample/IMG_8923.jpg")

# XML形式で処理
print("Processing in XML format...")
xml_result = ocr.process_receipt(image_path, output_format='xml')
print(xml_result[:200] + "..." if len(xml_result) > 200 else xml_result)

# CSV形式で処理
print("\nProcessing in CSV format...")
csv_result = convert_xml_to_csv(xml_result)
print(csv_result[:200] + "..." if len(csv_result) > 200 else csv_result)