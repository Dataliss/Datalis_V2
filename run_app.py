"""
Dabby Demo - Financial Intelligence Application with Agent Selection Sidebar
"""
import os
import sys
from importlib import import_module
import pkg_resources

# List of required packages
REQUIRED_PACKAGES = [
    "gradio>=4.0.0",
    "python-dotenv>=1.0.0",
    "groq>=0.4.0", 
    "pandas>=2.0.0",
    "docx>=0.2.4",
    "PyPDF2>=3.0.0",
    "python-docx>=0.8.11",
]

def check_requirements():
    """Check if all required packages are installed"""
    missing = []
    for package in REQUIRED_PACKAGES:
        package_name = package.split('>=')[0]
        try:
            pkg_resources.get_distribution(package_name)
        except pkg_resources.DistributionNotFound:
            missing.append(package)
    
    if missing:
        print(f"Missing required packages: {', '.join(missing)}")
        print("Installing missing packages...")
        
        try:
            import subprocess
            for package in missing:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print("All required packages installed successfully!")
        except Exception as e:
            print(f"Error installing packages: {str(e)}")
            print("Please install the required packages manually:")
            for package in missing:
                print(f"  pip install {package}")
            sys.exit(1)

def run_app():
    """Run the Dabby Demo application"""
    from new_app import create_ui
    
    print("Starting Datalis - AI-Powered Financial Intelligence...")
    app = create_ui()
    app.queue()
    app.launch(share=False)

if __name__ == "__main__":
    # Check if all required packages are installed
    check_requirements()
    
    # Check if GROQ_API_KEY environment variable is set
    if not os.environ.get("GROQ_API_KEY"):
        from dotenv import load_dotenv
        load_dotenv()
        
        if not os.environ.get("GROQ_API_KEY"):
            print("Warning: GROQ_API_KEY environment variable not set.")
            print("Please set this variable in a .env file or in your environment.")
            api_key = input("Enter your GROQ API key to continue: ")
            os.environ["GROQ_API_KEY"] = api_key
    
    # Run the app
    run_app()
