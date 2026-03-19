"""
main.py
--------
Entry point for Aloud PDF Reader (GUI).
"""

import sys

def main():
    try:
        from gui.downloader import ensure_model_exists
        
        if not ensure_model_exists():
            print("Model download failed or was cancelled. Exiting.")
            sys.exit(1)
            
        from gui.main_window import MainWindow
        app = MainWindow()
        app.run()
    except ImportError as e:
        print(f"❌ Failed to start the application. Are dependencies installed?\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
