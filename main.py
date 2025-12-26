"""Main entry point for TARS AI Assistant."""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.main_window import TARSMainWindow
from PyQt5.QtWidgets import QApplication


def main():
    """Main entry point."""
    # Check for API key
    if not os.getenv('GEMINI_API_KEY'):
        print("ERROR: GEMINI_API_KEY not found in environment variables.")
        print("Please create a .env file with your Gemini API key:")
        print("GEMINI_API_KEY=your_key_here")
        sys.exit(1)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("TARS AI Assistant")
    
    # Create and show main window
    window = TARSMainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

