"""Test script for single image processing."""

import sys
from pathlib import Path

# Add the project root directory to the path so we can import harina as a package
sys.path.insert(0, str(Path(__file__).parent.parent))

from harina.core import HarinaCore
from harina.utils import convert_xml_to_csv


def test_single_image_xml():
    """Test processing a single image and outputting as XML."""
    print("Testing single image processing (XML format)...")
    
    # Initialize OCR processor
    ocr = HarinaCore()
    
    # Path to sample image
    image_path = Path("example/receipt-sample/IMG_8923.jpg")
    
    if not image_path.exists():
        print(f"Error: Image file {image_path} not found.")
        return
    
    try:
        # Process the receipt image
        print(f"Processing image: {image_path}")
        xml_result = ocr.process_receipt(image_path, output_format='xml')
        
        # Save to file
        output_file = Path("tests/output_single_xml.xml")
        output_file.write_text(xml_result, encoding='utf-8')
        print(f"XML output saved to: {output_file}")
        
        # Print first 500 characters of the result
        print("First 500 characters of XML output:")
        print(xml_result[:500] + ("..." if len(xml_result) > 500 else ""))
        
    except Exception as e:
        print(f"Error processing receipt: {e}")
        import traceback
        traceback.print_exc()


def test_single_image_csv():
    """Test processing a single image and outputting as CSV."""
    print("\nTesting single image processing (CSV format)...")
    
    # Initialize OCR processor
    ocr = HarinaCore()
    
    # Path to sample image
    image_path = Path("example/receipt-sample/IMG_8923.jpg")
    
    if not image_path.exists():
        print(f"Error: Image file {image_path} not found.")
        return
    
    try:
        # Process the receipt image
        print(f"Processing image: {image_path}")
        xml_result = ocr.process_receipt(image_path, output_format='xml')
        csv_result = convert_xml_to_csv(xml_result)
        
        # Save to file
        output_file = Path("tests/output_single_csv.csv")
        output_file.write_text(csv_result, encoding='utf-8')
        print(f"CSV output saved to: {output_file}")
        
        # Print first 500 characters of the result
        print("First 500 characters of CSV output:")
        print(csv_result[:500] + ("..." if len(csv_result) > 500 else ""))
        
    except Exception as e:
        print(f"Error processing receipt: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_single_image_xml()
    test_single_image_csv()