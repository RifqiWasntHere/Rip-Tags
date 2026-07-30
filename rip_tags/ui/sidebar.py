from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTreeWidget, QTreeWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

from rip_tags.cleaner import SUPPORTED_SUFFIXES


class SidebarWidget(QWidget):
    folder_selected = Signal(str)
    file_selected = Signal(str)
    
    def __init__(self, icon_path: Path, parent=None):
        super().__init__(parent)
        self.icon_path = icon_path
        self.current_folder = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        if icon_path.exists():
            icon_label = QLabel()
            pixmap = QPixmap(str(icon_path))
            if not pixmap.isNull():
                scaled = pixmap.scaledToWidth(120, Qt.SmoothTransformation)
                icon_label.setPixmap(scaled)
                icon_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(icon_label)
        
        header = QLabel("Select Folder")
        header.setObjectName("title")
        layout.addWidget(header)
        
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setWordWrap(True)
        self.folder_label.setStyleSheet("color: #b0b0b0; padding: 8px; background: #252525; border-radius: 4px;")
        layout.addWidget(self.folder_label)
        
        browse_btn = QPushButton("Browse Folder")
        browse_btn.setObjectName("primary")
        browse_btn.clicked.connect(self.browse_folder)
        layout.addWidget(browse_btn)
        
        supported_text = "Supported: " + ", ".join(sorted(SUPPORTED_SUFFIXES))
        supported_label = QLabel(supported_text)
        supported_label.setStyleSheet("color: #808080; font-size: 11px;")
        layout.addWidget(supported_label)
        
        tree_header = QLabel("Folder Tree")
        tree_header.setObjectName("title")
        layout.addWidget(tree_header)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        layout.addWidget(self.tree, 1)
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.set_folder(folder)
    
    def set_folder(self, folder: str):
        self.current_folder = folder
        self.folder_label.setText(folder)
        self.folder_selected.emit(folder)
        self.populate_tree(Path(folder))
    
    def populate_tree(self, folder_path: Path):
        self.tree.clear()
        self._add_directory_items(self.tree.invisibleRootItem(), folder_path, depth=0, max_depth=3)
    
    def _add_directory_items(self, parent_item: QTreeWidgetItem, folder_path: Path, depth: int, max_depth: int):
        if depth >= max_depth:
            return
        
        try:
            entries = sorted(
                [e for e in folder_path.iterdir() if not e.name.startswith(".")],
                key=lambda e: (not e.is_dir(), e.name.lower())
            )
        except PermissionError:
            return
        
        for entry in entries[:100]:
            if entry.is_dir():
                item = QTreeWidgetItem(parent_item)
                item.setText(0, f"📁 {entry.name}")
                item.setData(0, Qt.UserRole, str(entry))
                self._add_directory_items(item, entry, depth + 1, max_depth)
            elif entry.suffix.lower() in SUPPORTED_SUFFIXES:
                item = QTreeWidgetItem(parent_item)
                item.setText(0, f"🎵 {entry.name}")
                item.setData(0, Qt.UserRole, str(entry))
    
    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        path_str = item.data(0, Qt.UserRole)
        if path_str:
            path = Path(path_str)
            if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
                self.file_selected.emit(path_str)
