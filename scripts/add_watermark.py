#!/usr/bin/env python3
"""
PDF watermark adder with customizable text/image watermarks
Supports both centered and tiled watermarks
Requires: PyPDF2, reportlab, Pillow
"""

import os
import sys
import argparse
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from PyPDF2 import PdfReader, PdfWriter

CJK_FONT_CANDIDATES = [
    os.environ.get("PPT2PDF_CJK_FONT"),
    "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/Library/Fonts/STHeiti Medium.ttc",
    "C:\\Windows\\Fonts\\msyh.ttc",
    "C:\\Windows\\Fonts\\simhei.ttf",
]


def _register_cjk_font():
    # Allow override via env var if different font path is preferred
    candidates = [path for path in CJK_FONT_CANDIDATES if path]
    for index, font_path in enumerate(candidates):
        if os.path.exists(font_path):
            try:
                font_name = f"CJKFont{index}"
                if font_name not in pdfmetrics.getRegisteredFontNames():
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                return font_name
            except Exception:
                continue

    # Fall back to built-in CID font (covers Chinese/Japanese/Korean)
    try:
        fallback_name = "STSong-Light"
        if fallback_name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(UnicodeCIDFont(fallback_name))
        return fallback_name
    except Exception:
        return None

def create_text_watermark(text, output_path, page_size=(612, 792), 
                         opacity=0.3, rotation=45, font_size=40, 
                         font_color=(0.5, 0.5, 0.5)):
    """Create a PDF with centered text watermark"""
    c = canvas.Canvas(str(output_path), pagesize=page_size)
    
    # Set transparency
    c.setFillColor(Color(font_color[0], font_color[1], font_color[2], alpha=opacity))
    
    # Set font (prefer CJK font if available)
    font_name = _register_cjk_font() or "Helvetica"
    c.setFont(font_name, font_size)
    
    # Rotate and position text at center
    c.saveState()
    c.translate(page_size[0]/2, page_size[1]/2)
    c.rotate(rotation)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    
    c.save()

def create_tiled_watermark(text, output_path, page_size=(612, 792), 
                          opacity=0.3, rotation=45, font_size=40,
                          spacing_x=None, spacing_y=None):
    """Create a PDF with tiled text watermark across entire page"""
    c = canvas.Canvas(str(output_path), pagesize=page_size)
    c.setFillColor(Color(0.5, 0.5, 0.5, alpha=opacity))
    font_name = _register_cjk_font() or "Helvetica"
    c.setFont(font_name, font_size)
    
    # Calculate default spacing based on font size if not provided
    if spacing_x is None:
        spacing_x = font_size * 8
    if spacing_y is None:
        spacing_y = font_size * 4
    
    # Tile the watermark across the entire page
    width, height = page_size
    for y in range(0, int(height), spacing_y):
        for x in range(0, int(width), spacing_x):
            c.saveState()
            c.translate(x, y)
            c.rotate(rotation)
            c.drawCentredString(0, 0, text)
            c.restoreState()
    
    c.save()

def create_image_watermark(image_path, output_path, page_size=(612, 792), 
                          opacity=0.3, scale=0.5):
    """Create a PDF with image watermark (placeholder implementation)"""
    c = canvas.Canvas(str(output_path), pagesize=page_size)
    c.setFillColor(Color(0.5, 0.5, 0.5, alpha=opacity))
    font_name = _register_cjk_font() or "Helvetica"
    c.setFont(font_name, 20)
    c.drawString(50, 50, f"Image watermark: {Path(image_path).name}")
    c.save()

def add_watermark_to_pdf(input_pdf, watermark_pdf, output_pdf):
    """Add watermark to all pages of PDF"""
    reader = PdfReader(input_pdf)
    watermark_reader = PdfReader(watermark_pdf)
    writer = PdfWriter()
    
    watermark_page = watermark_reader.pages[0]
    
    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)
    
    with open(output_pdf, 'wb') as output_file:
        writer.write(output_file)

def main():
    parser = argparse.ArgumentParser(description='Add watermark to PDF')
    parser.add_argument('input_pdf', help='Input PDF file')
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
        print("Error: Must specify either --text or --image", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Create temporary watermark file
        temp_watermark = Path(args.input_pdf).parent / "temp_watermark.pdf"
        
        if args.text:
            if args.tiled:
                create_tiled_watermark(
                    args.text, temp_watermark,
                    opacity=args.opacity,
                    rotation=args.rotation,
                    font_size=args.font_size,
                    spacing_x=args.spacing_x,
                    spacing_y=args.spacing_y
                )
            else:
                create_text_watermark(
                    args.text, temp_watermark,
                    opacity=args.opacity,
                    rotation=args.rotation,
                    font_size=args.font_size
                )
        else:
            create_image_watermark(args.image, temp_watermark, opacity=args.opacity)
        
        # Add watermark to PDF
        add_watermark_to_pdf(args.input_pdf, str(temp_watermark), args.output)
        
        # Clean up temp file
        temp_watermark.unlink()
        
        print(f"Successfully added watermark to: {args.output}")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
