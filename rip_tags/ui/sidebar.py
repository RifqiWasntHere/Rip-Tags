import json
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTreeWidget, QTreeWidgetItem, QHeaderView, QListWidget, QListWidgetItem,
    QStyle
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap

from rip_tags.cleaner import SUPPORTED_SUFFIXES
from rip_tags.ui.components import Card, EmptyState, svg_icon


RECENT_FOLDERS_FILE = Path.home() / ".rip_tags_recent.json"
MAX_RECENT_FOLDERS = 10


class SidebarWidget(QWidget):
    folder_selected = Signal(str)
    file_selected = Signal(str)
    preferences_requested = Signal()

    def __init__(self, icon_path: Path, parent=None):
        super().__init__(parent)
        self.icon_path = icon_path
        self.current_folder = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)
        header_layout.addStretch()

        if icon_path.exists():
            icon_label = QLabel()
            pixmap = QPixmap(str(icon_path))
            if not pixmap.isNull():
                scaled = pixmap.scaledToWidth(92, Qt.SmoothTransformation)
                icon_label.setPixmap(scaled)
        else:
            icon_label = QLabel("♪")
            icon_label.setStyleSheet("font-size: 64px; color: #4f9cf7;")

        icon_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.folder_card = Card()
        self.folder_card.layout.setContentsMargins(12, 12, 12, 12)
        self.folder_card.layout.setSpacing(8)

        self.folder_label = QLabel("No folder selected")
        self.folder_label.setObjectName("subtitle")
        self.folder_label.setWordWrap(True)
        self.folder_card.layout.addWidget(self.folder_label)

        self.folder_count_label = QLabel("0 files")
        self.folder_count_label.setObjectName("metric-label")
        self.folder_count_label.setStyleSheet("font-size: 11px; color: #808080;")
        self.folder_card.layout.addWidget(self.folder_count_label)

        browse_btn = QPushButton("Open Folder")
        browse_btn.setObjectName("primary")
        browse_btn.clicked.connect(self.browse_folder)
        self.folder_card.layout.addWidget(browse_btn)

        layout.addWidget(self.folder_card)

        recent_header = QLabel("Recent Folders")
        recent_header.setObjectName("section-title")
        layout.addWidget(recent_header)

        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(120)
        self.recent_list.itemClicked.connect(self.on_recent_clicked)
        self.load_recent_folders()
        layout.addWidget(self.recent_list)

        tree_header = QLabel("Folder Tree")
        tree_header.setObjectName("section-title")
        layout.addWidget(tree_header)

        self.tree = QTreeWidget()
        self.tree.setObjectName("sidebar_tree")
        self.tree.setHeaderHidden(True)
        self.tree.setIconSize(QSize(40, 40))
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        layout.addWidget(self.tree, 1)

        self.empty_state = EmptyState(
            "folder",
            "No Folder Selected",
            "Open a folder to start cleaning tags."
        )
        self.empty_state.setVisible(False)
        layout.addWidget(self.empty_state, 1)

        prefs_btn = QPushButton("Preferences")
        prefs_btn.setObjectName("secondary")
        prefs_btn.clicked.connect(self.preferences_requested.emit)
        layout.addWidget(prefs_btn)
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.set_folder(folder)

    def set_folder(self, folder: str):
        self.current_folder = folder
        self.folder_label.setText(folder)
        self.add_recent_folder(folder)
        self.folder_selected.emit(folder)
        self.populate_tree(Path(folder))

    def set_file_count(self, count: int):
        self.folder_count_label.setText(f"{count} files")

    def populate_tree(self, folder_path: Path):
        self.tree.clear()
        file_count = self._add_directory_items(self.tree.invisibleRootItem(), folder_path, depth=0, max_depth=3)
        self.folder_count_label.setText(f"{file_count} files")
        self.empty_state.setVisible(file_count == 0)
        self.tree.setVisible(file_count > 0)

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
                item.setIcon(0, self.style().standardIcon(QStyle.SP_DirIcon))
                item.setData(0, Qt.UserRole, str(entry))
                item.setData(0, Qt.UserRole + 1, "folder")
                file_count += self._add_directory_items(item, entry, depth + 1, max_depth)
            elif entry.suffix.lower() in SUPPORTED_SUFFIXES:
                item = QTreeWidgetItem(parent_item)
                item.setText(0, entry.name)
                item.setIcon(0, svg_icon("music", size=20))
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

    def on_recent_clicked(self, item: QListWidgetItem):
        folder = item.data(Qt.UserRole)
        if folder:
            self.set_folder(folder)

    def load_recent_folders(self):
        self.recent_list.clear()
        if not RECENT_FOLDERS_FILE.exists():
            return
        try:
            data = json.loads(RECENT_FOLDERS_FILE.read_text())
            folders = [f for f in data if isinstance(f, str) and Path(f).exists()]
            for folder in folders[:MAX_RECENT_FOLDERS]:
                item = QListWidgetItem(Path(folder).name)
                item.setData(Qt.UserRole, folder)
                item.setToolTip(folder)
                self.recent_list.addItem(item)
        except Exception:
            pass

    def add_recent_folder(self, folder: str):
        folders = []
        if RECENT_FOLDERS_FILE.exists():
            try:
                folders = json.loads(RECENT_FOLDERS_FILE.read_text())
            except Exception:
                pass
        folders = [f for f in folders if f != folder]
        folders.insert(0, folder)
        folders = folders[:MAX_RECENT_FOLDERS]
        try:
            RECENT_FOLDERS_FILE.write_text(json.dumps(folders))
        except Exception:
            pass
        self.load_recent_folders()
