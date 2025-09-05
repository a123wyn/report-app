# Report Generator Web App

A Flask web application for generating reports from data files with automatic email distribution.

## Features

- Upload HTML/PDF templates  
- Upload markdown prompt files
- Upload Excel/CSV data files
- Generate PDF reports using ReportLab
- Automatic email distribution via Outlook

## Quick Start

The binary compatibility issue has been fixed by removing pandas dependency.

### Method 1: Quick Start Script
```bash
cd report-app
./run.sh
```

### Method 2: Direct Python (if venv exists)
```bash
cd report-app
python3 start.py
```

### Method 3: Manual Setup
```bash
cd report-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Configuration

Before using email functionality, update the email settings in `app.py`:
- `sender_email = "your-email@outlook.com"`
- `sender_password = "your-password"`

## Usage

1. Access the app at `http://localhost:5000`
2. Fill in the email list (comma-separated)
3. Upload your files:
   - Template file (HTML - not used in current version, but required)
   - Markdown prompt file
   - Data file (Excel or CSV)
4. Click "Generate Report" to create and download the PDF

## Current Implementation

The app now uses:
- **ReportLab** for PDF generation (no binary compatibility issues)
- **openpyxl** for Excel file reading
- **csv** module for CSV file reading
- Simple table-based report layout

## File Structure
```
report-app/
├── app.py              # Main Flask application
├── templates/index.html # Web interface
├── requirements.txt    # Python dependencies (simplified)
├── run.sh             # Setup and start script
├── start.py           # Simple startup script
└── README.md          # This file
```

## Troubleshooting

If you encounter binary compatibility errors:
1. Delete the `venv` folder: `rm -rf venv`
2. Run `./run.sh` again

The app is now working and accessible at http://localhost:5000
