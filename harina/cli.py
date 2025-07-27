"""CLI interface for Harina v3 - Receipt OCR."""

import click
import os
from pathlib import Path
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