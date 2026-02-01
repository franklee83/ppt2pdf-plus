# PPT to PDF Converter with Watermark Support

Convert PowerPoint presentations to PDF with customizable text watermarks.

## Features
- ✅ PPT/PPTX to PDF conversion
- ✅ Customizable text watermarks
- ✅ Adjustable opacity (0.0-1.0)
- ✅ Rotation angle control
- ✅ Font size customization
- ✅ Tiled watermark support (repeated across entire page)
- ✅ Batch processing support

## Installation
### System Dependencies
```bash
sudo apt-get install libreoffice
```

### Python Dependencies
```bash
pip install PyPDF2 reportlab Pillow
```

## Usage
### Basic conversion (no watermark):
```bash
python scripts/ppt_to_pdf.py presentation.pptx --output-dir ./output/
```

### Add watermark to existing PDF:
```bash
python scripts/add_watermark.py document.pdf --output watermarked.pdf --text "CONFIDENTIAL"
```

### Complete workflow (PPT to PDF + watermark):
```bash
python scripts/convert_with_watermark.py presentation.pptx --output final.pdf --text "DRAFT"
```

### Tiled watermark (repeated across entire page):
```bash
python scripts/convert_with_watermark.py pres.pptx --output final.pdf \
    --text "CONFIDENTIAL" \
    --tiled \
    --opacity 0.2
```

### Custom options:
```bash
python scripts/convert_with_watermark.py pres.pptx --output final.pdf \
    --text "INTERNAL USE ONLY" \
    --opacity 0.5 \
    --rotation 30 \
    --font-size 24
```

### Custom tiled spacing:
```bash
python scripts/convert_with_watermark.py pres.pptx --output final.pdf \
    --text "DRAFT" \
    --tiled \
    --spacing-x 200 \
    --spacing-y 150 \
    --opacity 0.2 \
    --rotation 30
```

## Dependencies
- **System**: LibreOffice
- **Python**: PyPDF2, ReportLab, Pillow

## Chinese Watermark Support
If Chinese watermarks do not render, install a CJK font and (optionally) set:
```bash
export PPT2PDF_CJK_FONT="/path/to/NotoSansCJKsc-Regular.otf"
```
macOS (recommended):
```bash
brew install --cask font-noto-sans-cjk-sc
```

## License
MIT