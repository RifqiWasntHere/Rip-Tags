from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTreeWidget, QTreeWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

from rip_tags.cleaner import SUPPORTED_SUFFIXES
from rip_tags.ui.components import Card, EmptyState, TextOnlySelectionDelegate


class SidebarWidget(QWidget):
    folder_selected = Signal(str)
    file_selected = Signal(str)

    def __init__(self, icon_path: Path, parent=None):
        super().__init__(parent)
        self.icon_path = icon_path
        self.current_folder = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        if icon_path.exists():
            icon_label = QLabel()
            pixmap = QPixmap(str(icon_path))
            if not pixmap.isNull():
                scaled = pixmap.scaledToWidth(32, Qt.SmoothTransformation)
                icon_label.setPixmap(scaled)
        else:
            icon_label = QLabel("♪")
            icon_label.setStyleSheet("font-size: 24px; color: #4f9cf7;")

        header_layout.addWidget(icon_label)

        title_label = QLabel("Rip Tags")
        title_label.setObjectName("title")
        title_label.setStyleSheet("font-size: 18px;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.folder_card = Card()
        self.folder_card.layout.setContentsMargins(12, 12, 12, 12)

        self.folder_label = QLabel("No folder selected")
        self.folder_label.setObjectName("subtitle")
        self.folder_label.setWordWrap(True)
        self.folder_card.layout.addWidget(self.folder_label)

        browse_btn = QPushButton("Browse Folder")
        browse_btn.setObjectName("primary")
        browse_btn.clicked.connect(self.browse_folder)
        self.folder_card.layout.addWidget(browse_btn)

        layout.addWidget(self.folder_card)

        self.file_count_label = QLabel()
        self.file_count_label.setObjectName("subtitle")
        self.file_count_label.setStyleSheet("font-size: 11px; color: #808080;")
        layout.addWidget(self.file_count_label)

        tree_header = QLabel("Folder Tree")
        tree_header.setObjectName("section-title")
        layout.addWidget(tree_header)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setItemDelegate(TextOnlySelectionDelegate(self.tree))
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
        file_count = self._add_directory_items(self.tree.invisibleRootItem(), folder_path, depth=0, max_depth=3)
        self.file_count_label.setText(f"{file_count} files found")

    def _add_directory_items(self, parent_item: QTreeWidgetItem, folder_path: Path, depth: int, max_depth: int) -> int:
        if depth >= max_depth:
            return 0

        file_count = 0
        try:
            entries = sorted(
                [e for e in folder_path.iterdir() if not e.name.startswith(".")],
                key=lambda e: (not e.is_dir(), e.name.lower())
            )
        except PermissionError:
            return 0

        for entry in entries[:100]:
            if entry.is_dir():
                item = QTreeWidgetItem(parent_item)
                item.setText(0, entry.name)
                item.setData(0, Qt.UserRole, str(entry))
                item.setData(0, Qt.UserRole + 1, "folder")
                file_count += self._add_directory_items(item, entry, depth + 1, max_depth)
            elif entry.suffix.lower() in SUPPORTED_SUFFIXES:
                item = QTreeWidgetItem(parent_item)
                item.setText(0, entry.name)
                item.setData(0, Qt.UserRole, str(entry))
                item.setData(0, Qt.UserRole + 1, "file")
                file_count += 1

        return file_count

    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        path_str = item.data(0, Qt.UserRole)
        if path_str:
            path = Path(path_str)
            if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
                self.file_selected.emit(path_str)
