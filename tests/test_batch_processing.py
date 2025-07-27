"""Test script for batch processing of multiple images."""

import sys
from pathlib import Path

# Add the project root directory to the path so we can import harina as a package
sys.path.insert(0, str(Path(__file__).parent.parent))

from harina.core import HarinaCore
from harina.utils import convert_xml_to_csv


def find_image_files(directory: Path):
    """Find all image files in a directory recursively."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    image_files = []
    for file_path in directory.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(file_path)
    return image_files


def test_batch_processing_xml():
    """Test batch processing of images and outputting as XML."""
    print("Testing batch image processing (XML format)...")
    
    # Initialize OCR processor
    ocr = HarinaCore()
    
    # Directory with sample images
    image_dir = Path("example/receipt-sample")
    
    if not image_dir.exists():
        print(f"Error: Image directory {image_dir} not found.")
        return
    
    # Find all image files
    image_files = find_image_files(image_dir)
    print(f"Found {len(image_files)} image files to process")
    
    if not image_files:
        print("No image files found to process.")
        return
    
    # Process each image file
    output_dir = Path("tests/batch_output_xml")
    output_dir.mkdir(exist_ok=True)
    
    for i, image_file in enumerate(image_files, 1):
        print(f"Processing image ({i}/{len(image_files)}): {image_file.name}")
        
        try:
            # Process the receipt image
            xml_result = ocr.process_receipt(image_file, output_format='xml')
            
            # Save to file
            output_file = output_dir / f"{image_file.stem}.xml"
            output_file.write_text(xml_result, encoding='utf-8')
            print(f"XML output saved to: {output_file}")
            
        except Exception as e:
            print(f"Error processing receipt {image_file.name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"Batch processing completed. XML outputs saved to: {output_dir}")


def test_batch_processing_csv():
    """Test batch processing of images and outputting as CSV."""
    print("\nTesting batch image processing (CSV format)...")
    
    # Initialize OCR processor
    ocr = HarinaCore()
    
    # Directory with sample images
    image_dir = Path("example/receipt-sample")
    
    if not image_dir.exists():
        print(f"Error: Image directory {image_dir} not found.")
        return
    
    # Find all image files
    image_files = find_image_files(image_dir)
    print(f"Found {len(image_files)} image files to process")
    
    if not image_files:
        print("No image files found to process.")
        return
    
    # Process each image file
    output_dir = Path("tests/batch_output_csv")
    output_dir.mkdir(exist_ok=True)
    
    for i, image_file in enumerate(image_files, 1):
        print(f"Processing image ({i}/{len(image_files)}): {image_file.name}")
        
        try:
            # Process the receipt image
            xml_result = ocr.process_receipt(image_file, output_format='xml')
            csv_result = convert_xml_to_csv(xml_result)
            
            # Save to file
            output_file = output_dir / f"{image_file.stem}.csv"
            output_file.write_text(csv_result, encoding='utf-8')
            print(f"CSV output saved to: {output_file}")
            
        except Exception as e:
            print(f"Error processing receipt {image_file.name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"Batch processing completed. CSV outputs saved to: {output_dir}")


if __name__ == "__main__":
    test_batch_processing_xml()
    test_batch_processing_csv()