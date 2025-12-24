"""Settings dialog showing tool status and versions."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QHeaderView
)
from PySide6.QtCore import Qt

from .utils import check_tools_status


class SettingsDialog(QDialog):
    """Dialog showing tool discovery status and versions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings - Tool Status")
        self.setModal(True)
        self.setMinimumSize(600, 400)
        
        self._setup_ui()
        self._load_tool_status()
    
    def _setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Tool Discovery Status")
        header.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(header)
        
        info = QLabel(
            "The following tools are required for format conversion.\n"
            "Run scripts/fetch_tools.ps1 to download them."
        )
        layout.addWidget(info)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Tool", "Status", "Version/Path"])
        
        # Make table read-only
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Stretch last column
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        layout.addWidget(self.table)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._load_tool_status)
        layout.addWidget(refresh_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def _load_tool_status(self):
        """Load and display tool status."""
        tools = check_tools_status()
        
        self.table.setRowCount(len(tools))
        
        for row, (tool_name, tool_info) in enumerate(tools.items()):
            # Tool name
            name_item = QTableWidgetItem(tool_name)
            self.table.setItem(row, 0, name_item)
            
            # Status
            path = tool_info.get("path")
            if path and path.exists():
                status_item = QTableWidgetItem("✓ Found")
                status_item.setForeground(Qt.darkGreen)
            else:
                status_item = QTableWidgetItem("✗ Not Found")
                status_item.setForeground(Qt.red)
            self.table.setItem(row, 1, status_item)
            
            # Version or path
            version = tool_info.get("version")
            if version:
                info_item = QTableWidgetItem(version)
            elif path:
                info_item = QTableWidgetItem(str(path))
            else:
                info_item = QTableWidgetItem("Tool not installed")
            self.table.setItem(row, 2, info_item)
