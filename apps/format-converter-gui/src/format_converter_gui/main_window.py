"""Main window for the Format Converter GUI."""

from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QMenuBar, QMenu, QMessageBox
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

from .converter_tab import ConverterTab
from .converter_image import ImageConverter
from .converter_video import VideoConverter
from .converter_audio import AudioConverter
from .converter_document import DocumentConverter
from .settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Format Converter")
        self.setMinimumSize(800, 600)
        
        self._setup_ui()
        self._create_menu()
    
    def _setup_ui(self):
        """Setup the UI."""
        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create tabs for each converter type
        self._create_image_tab()
        self._create_video_tab()
        self._create_audio_tab()
        self._create_document_tab()
    
    def _create_image_tab(self):
        """Create the image converter tab."""
        converter = ImageConverter()
        tab = ConverterTab(
            "Image",
            converter,
            ImageConverter.SUPPORTED_FORMATS['input'],
            ImageConverter.SUPPORTED_FORMATS['output']
        )
        self.tabs.addTab(tab, "Image")
    
    def _create_video_tab(self):
        """Create the video converter tab."""
        converter = VideoConverter()
        tab = ConverterTab(
            "Video",
            converter,
            VideoConverter.SUPPORTED_FORMATS['input'],
            VideoConverter.SUPPORTED_FORMATS['output']
        )
        self.tabs.addTab(tab, "Video")
    
    def _create_audio_tab(self):
        """Create the audio converter tab."""
        converter = AudioConverter()
        tab = ConverterTab(
            "Audio",
            converter,
            AudioConverter.SUPPORTED_FORMATS['input'],
            AudioConverter.SUPPORTED_FORMATS['output']
        )
        self.tabs.addTab(tab, "Audio")
    
    def _create_document_tab(self):
        """Create the document converter tab."""
        converter = DocumentConverter()
        tab = ConverterTab(
            "Document",
            converter,
            DocumentConverter.SUPPORTED_FORMATS['input'],
            DocumentConverter.SUPPORTED_FORMATS['output']
        )
        self.tabs.addTab(tab, "Document")
    
    def _create_menu(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Format Converter",
            "<h2>Format Converter</h2>"
            "<p>Version 1.0.0</p>"
            "<p>A Windows GUI application for converting images, videos, "
            "audio, and documents.</p>"
            "<p><b>Powered by:</b></p>"
            "<ul>"
            "<li>FFmpeg - Video and audio conversion</li>"
            "<li>ImageMagick - Image conversion</li>"
            "<li>Pandoc - Document conversion</li>"
            "</ul>"
        )
