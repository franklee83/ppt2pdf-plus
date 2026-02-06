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
    --font-size 24 \
    --font-path "/path/to/NotoSansCJKsc-Regular.otf"
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
Defaults for tiled spacing scale with font size and are clamped to stay reasonable:
`spacing_x = clamp(font_size * 6, 180, 600)`, `spacing_y = clamp(font_size * 3, 120, 400)`.

## Dependencies
- **System**: LibreOffice
- **Python**: PyPDF2, ReportLab, Pillow

## Chinese Watermark Support
If Chinese watermarks do not render, install a CJK font or provide an explicit font path.
The scripts auto-discover common CJK fonts across macOS, Windows, and Linux, and still
honor `PPT2PDF_CJK_FONT`. You can override with `--font-path`.

**Linux Note**: For best results on Linux, install WenQuanYi Micro Hei font:
```bash
sudo apt-get install fonts-wqy-microhei
```

```bash
export PPT2PDF_CJK_FONT="/path/to/NotoSansCJKsc-Regular.otf"
```
macOS (recommended):
```bash
brew install --cask font-noto-sans-cjk-sc
```

## License
MIT
