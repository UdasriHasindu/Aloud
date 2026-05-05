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
        import os
        
        app = MainWindow()
        
        # Load PDF if passed via command line (Open With...)
        if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
            app.load_document(sys.argv[1])
            
        app.run()
    except ImportError as e:
        print(f"❌ Failed to start the application. Are dependencies installed?\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
