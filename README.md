# Datalis - AI-Powered Financial Intelligence

This application provides AI-powered financial intelligence through three specialized agents:

1. **Dabby Consultant** - General financial consulting and document analysis
2. **Auditor Agent** - Specialized in audit frameworks and financial document auditing
3. **Tax Agent** - Tax analysis, planning, and compliance expert

## Features

- Home page with agent selection
- Sidebar for agent selection and file upload
- Document analysis for financial files
- Chat interface for interacting with specialized agents

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your GROQ API key:
```
GROQ_API_KEY=your_api_key_here
```

## Usage

Run the application with either of these methods:

### Method 1: Using the batch file (Windows)
Simply double-click on:
```
run_datalis.bat
```

### Method 2: Using Python directly
```bash
python launch_datalis.py
```

The application will start and open in your default web browser. You can:

1. Select an agent from the home page or the sidebar
2. Upload financial documents for analysis
3. Chat with the selected agent about financial matters
4. Switch between agents at any time using the dropdown in the sidebar

## File Types Supported

- PDF (.pdf)
- Word Documents (.docx)
- Text files (.txt)
- Excel files (.xlsx, .xls)
- CSV files (.csv)
