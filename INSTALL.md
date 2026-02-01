# Installation Guide

## Step 1: Install System Dependencies
See [system-dependencies.md](system-dependencies.md) for detailed system requirements.

## Step 2: Install Python Dependencies  
```bash
pip install -r requirements.txt
```

## Step 3: Test Installation
```bash
python scripts/ppt_to_pdf.py --help
```

## Troubleshooting

### Missing LibreOffice
If you get "libreoffice: command not found", install LibreOffice first.

### Python Module Errors
If you get "ModuleNotFoundError", ensure all Python dependencies are installed:
```bash
pip install PyPDF2 reportlab Pillow
```

### Permission Issues
On some systems, you may need to use `sudo` for system package installation.