"""CLI interface for Harina v3 - Receipt OCR."""

import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from loguru import logger
from tqdm import tqdm

from .core import HarinaCore


def find_image_files(directory: Path):
    """Find all image files in a directory recursively."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    image_files = []
    for file_path in directory.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(file_path)
    return image_files


@click.command()
@click.argument('input_path', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path),
                help='Output file path (default: same directory as input with .xml or .csv extension)')
@click.option('--model', default='gemini/gemini-2.5-flash', envvar='HARINA_MODEL',
                help='Model to use (default: gemini/gemini-2.5-flash). Examples: gpt-4o, claude-3-sonnet-20240229')
@click.option('--format', '-f', type=click.Choice(['xml', 'csv']), default='xml',
                help='Output format (default: xml)')
@click.option('--template', '-t', type=click.Path(exists=True, path_type=Path),
                help='Path to custom XML template file')
@click.option('--categories', '-c', type=click.Path(exists=True, path_type=Path),
                help='Path to custom product categories file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(input_path, output, model, format, template, categories, verbose):
    """Recognize receipt content from image and output as XML or CSV."""
    
    # Configure logger
    logger.remove()  # Remove default handler
    if verbose:
        logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>", level="DEBUG")
    else:
        logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", level="INFO")
    
    # Load .env file from current working directory and project root
    load_dotenv()  # Load from current directory
    load_dotenv(Path.cwd() / '.env')  # Explicitly load from project root
    
    try:
        # Prepare template and categories paths
        template_path = str(template) if template else None
        categories_path = str(categories) if categories else None
        
        # Initialize OCR (API key is read from environment variables automatically)
        logger.info("🔧 Initializing OCR processor...")
        ocr = HarinaCore(model, template_path=template_path, categories_path=categories_path)
        
        # Determine if input_path is a file or directory
        if input_path.is_file():
            image_files = [input_path]
        elif input_path.is_dir():
            logger.info(f"📂 Searching for image files in directory: {input_path}")
            image_files = find_image_files(input_path)
            logger.info(f"📸 Found {len(image_files)} image files to process")
        else:
            logger.error(f"❌ Invalid input path: {input_path}")
            raise click.Abort()
        
        # Process each image file
        for i, image_file in enumerate(tqdm(image_files, desc="Processing receipts", unit="file"), 1):
            logger.info(f"🚀 Starting receipt processing ({i}/{len(image_files)}): {image_file.name}")
            logger.info(f"📱 Using model: {model}")
            
            try:
                logger.info("📸 Processing receipt image...")
                xml_result = ocr.process_receipt(image_file)
                
                # Determine output path
                if output and output.is_dir():
                    # If output is a directory, create file in that directory
                    output_file = output / f"{image_file.stem}.{format}"
                elif output and not output.suffix:
                    # If output is specified but has no extension, treat it as a directory
                    output_file = Path(output) / f"{image_file.stem}.{format}"
                elif output:
                    # If output is a file path
                    output_file = output
                else:
                    # If no output specified, create file in same directory as input
                    output_file = image_file.parent / f"{image_file.stem}.{format}"
                
                logger.info(f"💾 Saving {format.upper()} output to: {output_file}")
                # Save to file
                if format == 'xml':
                    output_file.write_text(xml_result, encoding='utf-8')
                elif format == 'csv':
                    csv_result = ocr.convert_xml_to_csv(xml_result)
                    output_file.write_text(csv_result, encoding='utf-8')
                
                logger.success(f"✅ Successfully processed receipt! Output saved to: {output_file}")
                    
            except Exception as e:
                logger.error(f"❌ Error processing receipt {image_file.name}: {e}")
                if len(image_files) == 1:
                    raise click.Abort()
                # Continue with next file if processing multiple files
                continue
            
    except Exception as e:
        logger.error(f"❌ Error processing receipts: {e}")
        raise click.Abort()


if __name__ == '__main__':
    main()