"""
Launcher for Datalis app - Fixed version
"""

from new_app import create_ui

if __name__ == "__main__":
    print("Starting Datalis Financial Intelligence Platform...")
    app = create_ui()
    app.launch(share=False)
