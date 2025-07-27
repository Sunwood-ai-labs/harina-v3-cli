"""CLI interface for Harina v3 - Receipt OCR."""

import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from loguru import logger

from .ocr import ReceiptOCR


@click.command()
@click.argument('image_path', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path),
                help='Output XML file path (default: same directory as input with .xml extension)')
@click.option('--model', default='gemini/gemini-1.5-flash', envvar='HARINA_MODEL',
                help='Model to use (default: gemini/gemini-1.5-flash). Examples: gpt-4o, claude-3-sonnet-20240229')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(image_path, output, model, verbose):
    """Recognize receipt content from image and output as XML."""
    
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
        logger.info(f"🚀 Starting receipt processing for: {image_path.name}")
        logger.info(f"📱 Using model: {model}")
        
        # Initialize OCR (API key is read from environment variables automatically)
        logger.info("🔧 Initializing OCR processor...")
        ocr = ReceiptOCR(model)
        
        logger.info("📸 Processing receipt image...")
        xml_result = ocr.process_receipt(image_path)
        
        # If no output specified, create XML file in same directory as input
        if not output:
            output = image_path.parent / f"{image_path.stem}.xml"
        
        logger.info(f"💾 Saving XML output to: {output}")
        # Save to file
        output.write_text(xml_result, encoding='utf-8')
        
        logger.success(f"✅ Successfully processed receipt! Output saved to: {output}")
            
    except Exception as e:
        logger.error(f"❌ Error processing receipt: {e}")
        raise click.Abort()


if __name__ == '__main__':
    main()