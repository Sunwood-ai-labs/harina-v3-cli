"""CLI interface for Harina v3 - Receipt OCR."""

import os
from pathlib import Path

import click
from dotenv import load_dotenv

from .ocr import ReceiptOCR


@click.command()
@click.argument('image_path', type=click.Path(exists=True, path_type=Path))
@click.option('--api-key', envvar='GEMINI_API_KEY', 
                help='Gemini API key (can also be set via GEMINI_API_KEY env var)')
@click.option('--output', '-o', type=click.Path(path_type=Path),
                help='Output XML file path (default: stdout)')
@click.option('--model', default='gemini/gemini-1.5-flash',
                help='Gemini model to use (default: gemini/gemini-1.5-flash)')
def main(image_path, api_key, output, model):
    """Recognize receipt content from image and output as XML."""
    
    # Load .env file from current working directory and project root
    load_dotenv()  # Load from current directory
    load_dotenv(Path.cwd() / '.env')  # Explicitly load from project root
    
    # If api_key is still not provided, try to get it from environment
    if not api_key:
        api_key = os.getenv('GEMINI_API_KEY')
    

    
    if not api_key:
        click.echo("Error: API key is required. Set GEMINI_API_KEY environment variable or use --api-key option.", err=True)
        raise click.Abort()
    
    try:
        ocr = ReceiptOCR(api_key, model)
        xml_result = ocr.process_receipt(image_path)
        
        if output:
            output.write_text(xml_result, encoding='utf-8')
            click.echo(f"XML output saved to: {output}")
        else:
            click.echo(xml_result)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    main()