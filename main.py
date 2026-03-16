"""
main.py
--------
Entry point for Aloud PDF Reader (GUI).
"""

import sys

def main():
    # Only try to load the GUI if we are definitely running the app normally.
    try:
        from gui.main_window import MainWindow
        app = MainWindow()
        app.run()
    except ImportError as e:
        print(f"❌ Failed to start the application. Are dependencies installed?\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
