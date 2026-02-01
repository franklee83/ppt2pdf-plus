#!/usr/bin/env python3
"""
Complete PPT to PDF conversion with watermark in one step
"""

import os
import sys
import argparse
import tempfile
from pathlib import Path

# Import our other scripts
sys.path.insert(0, str(Path(__file__).parent))
from ppt_to_pdf import convert_ppt_to_pdf
from add_watermark import create_text_watermark, create_tiled_watermark, create_image_watermark, add_watermark_to_pdf

def main():
    parser = argparse.ArgumentParser(description='Convert PPT to PDF with watermark')
    parser.add_argument('input_file', help='Input PPT/PPTX file')
    parser.add_argument('--output', '-o', required=True, help='Output PDF file')
    parser.add_argument('--text', help='Text watermark')
    parser.add_argument('--image', help='Image watermark file')
    parser.add_argument('--opacity', type=float, default=0.3, help='Watermark opacity (0.0-1.0)')
    parser.add_argument('--rotation', type=int, default=45, help='Text rotation angle')
    parser.add_argument('--font-size', type=int, default=40, help='Text font size')
    parser.add_argument('--tiled', action='store_true', help='Create tiled watermark across entire page')
    parser.add_argument('--spacing-x', type=int, default=None, help='Horizontal spacing for tiled watermark')
    parser.add_argument('--spacing-y', type=int, default=None, help='Vertical spacing for tiled watermark')
    
    args = parser.parse_args()
    
    if not args.text and not args.image:
        print("Error: Must specify either --text or --image for watermark", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Create temporary directory for intermediate files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Step 1: Convert PPT to PDF
            pdf_path = convert_ppt_to_pdf(args.input_file, temp_dir)
            
            # Step 2: Create watermark
            watermark_path = temp_path / "watermark.pdf"
            if args.text:
                from reportlab.lib.pagesizes import letter
                # Get page size from original PDF
                from PyPDF2 import PdfReader
                reader = PdfReader(pdf_path)
                if reader.pages:
                    page = reader.pages[0]
                    width = float(page.mediabox.width)
                    height = float(page.mediabox.height)
                    page_size = (width, height)
                else:
                    page_size = letter
                
                if args.tiled:
                    create_tiled_watermark(
                        args.text, watermark_path,
                        page_size=page_size,
                        opacity=args.opacity,
                        rotation=args.rotation,
                        font_size=args.font_size,
                        spacing_x=args.spacing_x,
                        spacing_y=args.spacing_y
                    )
                else:
                    create_text_watermark(
                        args.text, watermark_path,
                        page_size=page_size,
                        opacity=args.opacity,
                        rotation=args.rotation,
                        font_size=args.font_size
                    )
            else:
                # For image watermark, we'd need to handle page size similarly
                create_image_watermark(args.image, watermark_path, opacity=args.opacity)
            
            # Step 3: Add watermark to PDF
            add_watermark_to_pdf(pdf_path, str(watermark_path), args.output)
        
        print(f"Successfully converted and watermarked: {args.output}")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()