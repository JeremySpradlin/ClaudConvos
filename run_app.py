#!/usr/bin/env python3
"""
Launch script with better Qt compatibility
"""

import sys
import os

# Set Qt environment variables to help with compatibility
os.environ['QT_MAC_WANTS_LAYER'] = '1'
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

def main():
    """Launch the application with proper Qt setup."""
    try:
        # Try PySide6 first
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        
        # Set Qt attributes before creating QApplication
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        
        app = QApplication(sys.argv)
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        
        # Import and run the main app
        from main_fixed import AIConversationApp
        
        window = AIConversationApp()
        window.show()
        
        return app.exec()
        
    except ImportError:
        print("PySide6 not available, trying PyQt6...")
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import Qt
            
            app = QApplication(sys.argv)
            
            from main_fixed import AIConversationApp
            window = AIConversationApp()
            window.show()
            
            return app.exec()
            
        except ImportError:
            print("Neither PySide6 nor PyQt6 available!")
            return 1
    
    except Exception as e:
        print(f"Error starting application: {e}")
        print("\nFalling back to CLI analysis tool...")
        print("You can use: python analyze_cli.py --list")
        return 1

if __name__ == "__main__":
    sys.exit(main())