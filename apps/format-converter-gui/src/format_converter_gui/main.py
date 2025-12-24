"""Main entry point for the Format Converter GUI."""

import sys
from PySide6.QtWidgets import QApplication

from .main_window import MainWindow


def main():
    """Main function."""
    app = QApplication(sys.argv)
    app.setApplicationName("Format Converter")
    app.setOrganizationName("Format Converter")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
