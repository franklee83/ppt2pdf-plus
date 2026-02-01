# Usage Examples

## Basic Conversion (No Watermark)
```bash
python scripts/ppt_to_pdf.py presentation.pptx --output-dir ./output/
```

## Add Watermark to Existing PDF
```bash
python scripts/add_watermark.py document.pdf --output watermarked.pdf --text "CONFIDENTIAL"
```

## Complete Workflow: PPT to PDF with Watermark
```bash
python scripts/convert_with_watermark.py presentation.pptx --output final.pdf --text "DRAFT"
```

## Tiled Watermark (Repeated Across Entire Page)
```bash
python scripts/convert_with_watermark.py pres.pptx --output final.pdf \
    --text "CONFIDENTIAL" \
    --tiled \
    --opacity 0.2
```

## Custom Tiled Watermark Spacing
```bash
python scripts/convert_with_watermark.py pres.pptx --output final.pdf \
    --text "DRAFT" \
    --tiled \
    --spacing-x 200 \
    --spacing-y 150 \
    --opacity 0.2 \
    --rotation 30
```

## Custom Watermark Options
```bash
python scripts/convert_with_watermark.py pres.pptx --output final.pdf \
    --text "INTERNAL USE ONLY" \
    --opacity 0.5 \
    --rotation 30 \
    --font-size 24
```

## Batch Processing
For multiple files, use a simple shell loop:
```bash
for ppt in *.pptx; do
    python scripts/convert_with_watermark.py "$ppt" --output "${ppt%.pptx}_watermarked.pdf" --text "CONFIDENTIAL"
done
```