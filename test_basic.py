#!/usr/bin/env python3
"""
Test version with minimal dependencies
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget
from PyQt6.QtCore import Qt

class MinimalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test App")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        tabs = QTabWidget()
        
        # Test tab
        test_tab = QWidget()
        test_layout = QVBoxLayout(test_tab)
        test_layout.addWidget(QLabel("Basic PyQt6 test - this should work"))
        tabs.addTab(test_tab, "Test")
        
        layout.addWidget(tabs)

def main():
    app = QApplication(sys.argv)
    window = MinimalApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()