#!/usr/bin/env python3
"""
PPT to PDF converter with watermark support
Requires: libreoffice, PyPDF2, reportlab, Pillow
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def convert_ppt_to_pdf(input_file, output_dir=None):
    """Convert PPT/PPTX to PDF using LibreOffice"""
    input_path = Path(input_file).resolve()
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = input_path.parent
    
    # Use LibreOffice to convert
    cmd = [
        'libreoffice',
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', str(output_path),
        str(input_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")
        
        # Construct expected output filename
        pdf_name = input_path.stem + '.pdf'
        pdf_path = output_path / pdf_name
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"Expected PDF not created: {pdf_path}")
            
        return str(pdf_path)
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("LibreOffice conversion timed out")
    except Exception as e:
        raise RuntimeError(f"Conversion error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Convert PPT/PPTX to PDF')
    parser.add_argument('input_file', help='Input PPT/PPTX file')
    parser.add_argument('--output-dir', '-o', help='Output directory for PDF')
    
    args = parser.parse_args()
    
    try:
        pdf_path = convert_ppt_to_pdf(args.input_file, args.output_dir)
        print(f"Successfully converted to: {pdf_path}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()