"""Converter tab widget for different media types."""

from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QProgressBar,
    QTextEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal

from .converter_base import BaseConverter


class ConversionWorker(QThread):
    """Worker thread for running conversions."""
    
    log_signal = Signal(str)
    progress_signal = Signal(float)
    finished_signal = Signal(bool)
    
    def __init__(self, converter: BaseConverter, input_path: Path, 
                 output_path: Path, output_format: str):
        super().__init__()
        self.converter = converter
        self.input_path = input_path
        self.output_path = output_path
        self.output_format = output_format
    
    def run(self):
        """Run the conversion."""
        success = self.converter.convert(
            self.input_path,
            self.output_path,
            self.output_format,
            log_callback=self._log,
            progress_callback=self._progress
        )
        self.finished_signal.emit(success)
    
    def _log(self, message: str):
        """Log callback."""
        self.log_signal.emit(message)
    
    def _progress(self, value: float):
        """Progress callback."""
        self.progress_signal.emit(value)


class ConverterTab(QWidget):
    """Tab widget for converting media files."""
    
    def __init__(self, title: str, converter: BaseConverter, 
                 input_formats: List[str], output_formats: List[str]):
        super().__init__()
        self.title = title
        self.converter = converter
        self.input_formats = input_formats
        self.output_formats = output_formats
        self.worker: Optional[ConversionWorker] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Input file selection
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Input File:"))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_layout.addWidget(self.input_edit, 1)
        self.input_btn = QPushButton("Browse...")
        self.input_btn.clicked.connect(self._select_input)
        input_layout.addWidget(self.input_btn)
        layout.addLayout(input_layout)
        
        # Output file selection
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output File:"))
        self.output_edit = QLineEdit()
        self.output_edit.setReadOnly(True)
        output_layout.addWidget(self.output_edit, 1)
        self.output_btn = QPushButton("Browse...")
        self.output_btn.clicked.connect(self._select_output)
        output_layout.addWidget(self.output_btn)
        layout.addLayout(output_layout)
        
        # Output format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Output Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(self.output_formats)
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        layout.addLayout(format_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.clicked.connect(self._start_conversion)
        self.convert_btn.setEnabled(False)
        button_layout.addWidget(self.convert_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._cancel_conversion)
        self.cancel_btn.setEnabled(False)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Log output
        layout.addWidget(QLabel("Log:"))
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setMaximumHeight(200)
        layout.addWidget(self.log_edit)
    
    def _select_input(self):
        """Select input file."""
        file_filter = f"{self.title} Files ({' '.join('*.' + fmt for fmt in self.input_formats)});;All Files (*.*)"
        filename, _ = QFileDialog.getOpenFileName(
            self,
            f"Select Input {self.title} File",
            "",
            file_filter
        )
        
        if filename:
            self.input_edit.setText(filename)
            self._update_output_path()
            self._update_buttons()
    
    def _select_output(self):
        """Select output file."""
        output_format = self.format_combo.currentText()
        file_filter = f"{self.title} Files (*.{output_format});;All Files (*.*)"
        filename, _ = QFileDialog.getSaveFileName(
            self,
            f"Select Output {self.title} File",
            self.output_edit.text(),
            file_filter
        )
        
        if filename:
            self.output_edit.setText(filename)
            self._update_buttons()
    
    def _on_format_changed(self):
        """Handle format change."""
        self._update_output_path()
    
    def _update_output_path(self):
        """Update output path based on input and format."""
        input_path = self.input_edit.text()
        if input_path:
            input_file = Path(input_path)
            output_format = self.format_combo.currentText()
            output_file = input_file.with_suffix(f'.{output_format}')
            self.output_edit.setText(str(output_file))
            self._update_buttons()
    
    def _update_buttons(self):
        """Update button states."""
        has_input = bool(self.input_edit.text())
        has_output = bool(self.output_edit.text())
        self.convert_btn.setEnabled(has_input and has_output and not self.worker)
    
    def _start_conversion(self):
        """Start the conversion process."""
        input_path = Path(self.input_edit.text())
        output_path = Path(self.output_edit.text())
        output_format = self.format_combo.currentText()
        
        # Clear log
        self.log_edit.clear()
        self.progress_bar.setValue(0)
        
        # Disable controls
        self.input_btn.setEnabled(False)
        self.output_btn.setEnabled(False)
        self.format_combo.setEnabled(False)
        self.convert_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        
        # Create and start worker
        self.worker = ConversionWorker(
            self.converter,
            input_path,
            output_path,
            output_format
        )
        self.worker.log_signal.connect(self._on_log)
        self.worker.progress_signal.connect(self._on_progress)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.start()
    
    def _cancel_conversion(self):
        """Cancel the current conversion."""
        if self.worker:
            self.converter.cancel()
            self._append_log("Cancelling conversion...")
    
    def _on_log(self, message: str):
        """Handle log message."""
        self._append_log(message)
    
    def _append_log(self, message: str):
        """Append message to log."""
        self.log_edit.append(message)
        # Auto-scroll to bottom
        self.log_edit.verticalScrollBar().setValue(
            self.log_edit.verticalScrollBar().maximum()
        )
    
    def _on_progress(self, value: float):
        """Handle progress update."""
        self.progress_bar.setValue(int(value * 100))
    
    def _on_finished(self, success: bool):
        """Handle conversion finished."""
        # Re-enable controls
        self.input_btn.setEnabled(True)
        self.output_btn.setEnabled(True)
        self.format_combo.setEnabled(True)
        self.convert_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        # Show result
        if success:
            QMessageBox.information(
                self,
                "Conversion Complete",
                f"File converted successfully to {self.output_edit.text()}"
            )
        else:
            QMessageBox.warning(
                self,
                "Conversion Failed",
                "The conversion failed. Check the log for details."
            )
        
        self.worker = None
