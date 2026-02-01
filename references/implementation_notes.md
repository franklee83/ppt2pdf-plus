# Implementation Notes

## Current Limitations

### Image Watermark Support
The current implementation has placeholder support for image watermarks but doesn't fully implement the image embedding functionality. This is because:

1. ReportLab's image handling requires additional complexity for proper positioning and scaling
2. Different image formats (PNG, JPG, SVG) need different handling approaches
3. Memory usage can be significant for large images

### Page Size Detection
The watermark creation assumes standard page sizes. For presentations with custom slide dimensions, the watermark may not be properly centered.

## Dependencies Required

### System Dependencies
- **LibreOffice**: For PPT/PPTX to PDF conversion
  - Available on most Linux distributions: `sudo apt-get install libreoffice`
  - On macOS: `brew install --cask libreoffice`
  - On Windows: Download from LibreOffice website

### Python Dependencies
- **PyPDF2**: For PDF manipulation
- **ReportLab**: For creating watermark PDFs
- **Pillow (PIL)**: For image handling (future image watermark support)

Install with: `pip install PyPDF2 reportlab Pillow`

## Error Handling

The scripts include basic error handling for:
- Missing input files
- LibreOffice conversion failures
- PDF processing errors

However, more robust error handling could be added for:
- Memory constraints during large file processing
- Network issues (if extending to cloud storage)
- Permission errors

## Performance Considerations

- **Large presentations**: Conversion time scales with slide count and complexity
- **Memory usage**: Temporary files are used to avoid loading entire documents into memory
- **Batch processing**: Consider processing files sequentially to avoid resource exhaustion

## Security Considerations

- Input files should be validated to prevent path traversal attacks
- Temporary files are automatically cleaned up
- External dependencies (LibreOffice) should be kept updated

## Future Enhancements

1. **Complete image watermark support** with proper positioning and scaling
2. **Multiple watermark types** (text + image simultaneously)
3. **Per-page watermark customization**
4. **Watermark templates** for common use cases (CONFIDENTIAL, DRAFT, etc.)
5. **GUI interface** for non-technical users
6. **Cloud integration** for processing files from cloud storage