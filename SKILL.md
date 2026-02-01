---
name: ppt2pdf-plus
description: Convert PPT/PPTX files to PDF with customizable watermark support. Use when you need to convert presentations to PDF format and add text watermarks with custom opacity, rotation, and font size.
---

# PPT to PDF Converter with Watermark

This skill provides tools to convert PowerPoint presentations (PPT/PPTX) to PDF format with customizable text watermarks.

## Features
- Convert PPT/PPTX to PDF using LibreOffice
- Add customizable text watermarks
- Control watermark opacity (0.0-1.0)
- Adjust watermark rotation angle
- Set custom font size
- Tiled watermark support (repeated across entire page)
- Batch processing support

## Scripts
- `scripts/ppt_to_pdf.py` - Basic PPT to PDF conversion
- `scripts/add_watermark.py` - Add watermark to existing PDF
- `scripts/convert_with_watermark.py` - Complete workflow in one step

## Dependencies
- LibreOffice (system package)
- PyPDF2, ReportLab, Pillow (Python packages)

## Usage Examples
See references/usage_examples.md for detailed examples.