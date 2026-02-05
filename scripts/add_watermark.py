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
from PyPDF2 import PdfReader, PdfWriter

CJK_FONT_ENV = "PPT2PDF_CJK_FONT"
DEFAULT_CJK_FONT = "/Users/mac/Library/Fonts/NotoSansCJKsc-Regular.otf"

_CJK_FONT_NAME_HINTS = [
    "notosanscjk",
    "notoserifcjk",
    "sourcehansans",
    "sourcehanserif",
    "noto sans cjk",
    "noto serif cjk",
    "pingfang",
    "hiragino sans",
    "stheiti",
    "heiti",
    "simsun",
    "simhei",
    "msyh",
    "microsoft yahei",
    "malgungothic",
    "applegothic",
]

_CJK_FONT_EXTS = {".otf", ".ttf", ".ttc"}

_DEFAULT_TILE_SPACING_X_MULT = 6
_DEFAULT_TILE_SPACING_Y_MULT = 3
_DEFAULT_TILE_SPACING_X_MIN = 180
_DEFAULT_TILE_SPACING_Y_MIN = 120
_DEFAULT_TILE_SPACING_X_MAX = 600
_DEFAULT_TILE_SPACING_Y_MAX = 400


def _text_has_cjk(text):
    if not text:
        return False
    for ch in text:
        code = ord(ch)
        if (
            0x4E00 <= code <= 0x9FFF  # CJK Unified Ideographs
            or 0x3400 <= code <= 0x4DBF  # CJK Extension A
            or 0x20000 <= code <= 0x2A6DF  # Extension B
            or 0x2A700 <= code <= 0x2B73F  # Extension C
            or 0x2B740 <= code <= 0x2B81F  # Extension D
            or 0x2B820 <= code <= 0x2CEAF  # Extension E
            or 0xF900 <= code <= 0xFAFF  # CJK Compatibility Ideographs
            or 0x2F800 <= code <= 0x2FA1F  # Compatibility Supplement
            or 0x3040 <= code <= 0x309F  # Hiragana
            or 0x30A0 <= code <= 0x30FF  # Katakana
            or 0x31F0 <= code <= 0x31FF  # Katakana Phonetic Extensions
            or 0xAC00 <= code <= 0xD7AF  # Hangul Syllables
        ):
            return True
    return False


def _candidate_font_dirs():
    platform = sys.platform
    dirs = []
    if platform == "darwin":
        dirs = [
            Path("/System/Library/Fonts"),
            Path("/System/Library/Fonts/Supplemental"),
            Path("/Library/Fonts"),
            Path.home() / "Library/Fonts",
        ]
    elif platform.startswith("win"):
        windir = os.environ.get("WINDIR", "C:\\Windows")
        dirs = [Path(windir) / "Fonts"]
    else:
        dirs = [
            Path("/usr/share/fonts"),
            Path("/usr/local/share/fonts"),
            Path.home() / ".fonts",
            Path.home() / ".local/share/fonts",
        ]
    return dirs


def _candidate_font_paths():
    platform = sys.platform
    candidates = []
    if DEFAULT_CJK_FONT:
        candidates.append(Path(DEFAULT_CJK_FONT))

    if platform == "darwin":
        candidates.extend(
            [
                Path("/System/Library/Fonts/PingFang.ttc"),
                Path("/System/Library/Fonts/STHeiti Medium.ttc"),
                Path("/System/Library/Fonts/Supplemental/Heiti TC.ttc"),
                Path("/Library/Fonts/NotoSansCJKsc-Regular.otf"),
                Path("/Library/Fonts/NotoSansCJK-Regular.ttc"),
                Path.home() / "Library/Fonts/NotoSansCJKsc-Regular.otf",
            ]
        )
    elif platform.startswith("win"):
        candidates.extend(
            [
                Path("C:/Windows/Fonts/msyh.ttc"),
                Path("C:/Windows/Fonts/msyh.ttf"),
                Path("C:/Windows/Fonts/simsun.ttc"),
                Path("C:/Windows/Fonts/simhei.ttf"),
                Path("C:/Windows/Fonts/msjh.ttc"),
                Path("C:/Windows/Fonts/malgun.ttf"),
            ]
        )
    else:
        candidates.extend(
            [
                Path("/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf"),
                Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
                Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
                Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
                Path("/usr/share/fonts/opentype/source-han-sans/SourceHanSansSC-Regular.otf"),
                Path("/usr/share/fonts/truetype/arphic/uming.ttc"),
            ]
        )
    return candidates


def _register_font(font_path):
    font_path = Path(font_path)
    font_name = f"PPT2PDFCJK_{font_path.stem}".replace(" ", "_")
    if font_name in pdfmetrics.getRegisteredFontNames():
        return font_name
    try:
        pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
        return font_name
    except Exception:
        return None


def _scan_for_cjk_font(font_dirs):
    for font_dir in font_dirs:
        if not font_dir.exists():
            continue
        for root, dirnames, filenames in os.walk(font_dir):
            depth = len(Path(root).parts) - len(font_dir.parts)
            if depth > 2:
                dirnames[:] = []
                continue
            for filename in filenames:
                path = Path(root) / filename
                if path.suffix.lower() not in _CJK_FONT_EXTS:
                    continue
                lower_name = filename.lower()
                if any(hint in lower_name for hint in _CJK_FONT_NAME_HINTS):
                    return path
    return None


def _resolve_cjk_font(font_path_override=None, require_cjk=False):
    warnings = []
    if font_path_override:
        font_path = Path(font_path_override).expanduser()
        if not font_path.exists():
            raise RuntimeError(
                f"CJK font path not found: {font_path}. "
                "Provide a valid font file with --font-path or unset it."
            )
        font_name = _register_font(font_path)
        if not font_name:
            raise RuntimeError(
                f"Failed to load CJK font from {font_path}. "
                "Try a .ttf or .otf font, or provide a different --font-path."
            )
        return font_name

    env_path = os.environ.get(CJK_FONT_ENV)
    if env_path:
        env_font = Path(env_path).expanduser()
        if env_font.exists():
            font_name = _register_font(env_font)
            if font_name:
                return font_name
            warnings.append(
                f"Failed to load CJK font from {env_font} set in {CJK_FONT_ENV}."
            )
        else:
            warnings.append(
                f"CJK font path in {CJK_FONT_ENV} was not found: {env_font}."
            )

    for candidate in _candidate_font_paths():
        if candidate.exists():
            font_name = _register_font(candidate)
            if font_name:
                return font_name

    found = _scan_for_cjk_font(_candidate_font_dirs())
    if found:
        font_name = _register_font(found)
        if font_name:
            return font_name

    if require_cjk:
        warning_text = " ".join(warnings)
        guidance = (
            "Install a CJK font and provide it via --font-path or set "
            f"{CJK_FONT_ENV}. Example installs: "
            "macOS `brew install --cask font-noto-sans-cjk-sc`, "
            "Linux `sudo apt-get install fonts-noto-cjk`."
        )
        message = "No CJK font found to render the watermark text."
        if warning_text:
            message = f"{message} {warning_text}"
        raise RuntimeError(f"{message} {guidance}")

    for warning in warnings:
        print(f"Warning: {warning}", file=sys.stderr)

    return None


def _font_for_text(text, font_path_override=None):
    needs_cjk = _text_has_cjk(text)
    cjk_font = _resolve_cjk_font(
        font_path_override=font_path_override,
        require_cjk=needs_cjk,
    )
    return cjk_font or "Helvetica"


def _clamp(value, min_value, max_value):
    return max(min_value, min(max_value, int(value)))

def create_text_watermark(
    text,
    output_path,
    page_size=(612, 792),
    opacity=0.3,
    rotation=45,
    font_size=40,
    font_color=(0.5, 0.5, 0.5),
    font_path=None,
):
    """Create a PDF with centered text watermark"""
    c = canvas.Canvas(str(output_path), pagesize=page_size)
    
    # Set transparency
    c.setFillColor(Color(font_color[0], font_color[1], font_color[2], alpha=opacity))
    
    # Set font (prefer CJK font if needed/available)
    font_name = _font_for_text(text, font_path_override=font_path)
    c.setFont(font_name, font_size)
    
    # Rotate and position text at center
    c.saveState()
    c.translate(page_size[0]/2, page_size[1]/2)
    c.rotate(rotation)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    
    c.save()

def create_tiled_watermark(
    text,
    output_path,
    page_size=(612, 792),
    opacity=0.3,
    rotation=45,
    font_size=40,
    spacing_x=None,
    spacing_y=None,
    font_path=None,
):
    """Create a PDF with tiled text watermark across entire page.

    Default spacing scales with font size and is clamped to keep results readable.
    """
    c = canvas.Canvas(str(output_path), pagesize=page_size)
    c.setFillColor(Color(0.5, 0.5, 0.5, alpha=opacity))
    font_name = _font_for_text(text, font_path_override=font_path)
    c.setFont(font_name, font_size)
    
    # Calculate default spacing based on font size if not provided
    if spacing_x is None:
        spacing_x = _clamp(
            font_size * _DEFAULT_TILE_SPACING_X_MULT,
            _DEFAULT_TILE_SPACING_X_MIN,
            _DEFAULT_TILE_SPACING_X_MAX,
        )
    if spacing_y is None:
        spacing_y = _clamp(
            font_size * _DEFAULT_TILE_SPACING_Y_MULT,
            _DEFAULT_TILE_SPACING_Y_MIN,
            _DEFAULT_TILE_SPACING_Y_MAX,
        )
    
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
    font_name = _resolve_cjk_font() or "Helvetica"
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
    parser.add_argument('--font-path', help='Path to a CJK font file (overrides PPT2PDF_CJK_FONT)')
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
                    spacing_y=args.spacing_y,
                    font_path=args.font_path,
                )
            else:
                create_text_watermark(
                    args.text, temp_watermark,
                    opacity=args.opacity,
                    rotation=args.rotation,
                    font_size=args.font_size,
                    font_path=args.font_path,
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
