"""CLI interface for Harina v3 - Receipt OCR."""

import os
from pathlib import Path

import click
from dotenv import load_dotenv

from .ocr import ReceiptOCR


@click.command()
@click.argument('image_path', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path),
                help='Output XML file path (default: stdout)')
@click.option('--model', default='gemini/gemini-1.5-flash', envvar='HARINA_MODEL',
                help='Model to use (default: gemini/gemini-1.5-flash). Examples: gpt-4o, claude-3-sonnet-20240229')
def main(image_path, output, model):
    """Recognize receipt content from image and output as XML."""
    
    # Load .env file from current working directory and project root
    load_dotenv()  # Load from current directory
    load_dotenv(Path.cwd() / '.env')  # Explicitly load from project root
    
    try:
        # Initialize OCR (API key is read from environment variables automatically)
        ocr = ReceiptOCR(model)
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