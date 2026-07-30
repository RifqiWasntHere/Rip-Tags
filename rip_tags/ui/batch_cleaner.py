from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QCheckBox, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QTextEdit, QHeaderView, QProgressBar
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

from rip_tags.cleaner import SUPPORTED_SUFFIXES, CleanResult
from rip_tags.tags import ALL_SUPPORTED_TAGS, RECOMMENDED_TAGS
from rip_tags.ui.preferences import PreferencesDialog
from rip_tags.ui.worker import ScanWorker, CleanWorker


class BatchCleanerWidget(QWidget):
    file_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_folder: Optional[Path] = None
        self.keep_tags_pref: dict = {tag: (tag in RECOMMENDED_TAGS) for tag in ALL_SUPPORTED_TAGS}
        self.scan_worker: Optional[ScanWorker] = None
        self.clean_worker: Optional[CleanWorker] = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        header = QLabel("Batch Tag Cleaner")
        header.setObjectName("title")
        layout.addWidget(header)
        
        self.info_label = QLabel("Select a folder in the sidebar to scan for music files.")
        layout.addWidget(self.info_label)
        
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.NoSelection)
        layout.addWidget(self.file_list, 1)
        
        list_buttons = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all_files)
        list_buttons.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all_files)
        list_buttons.addWidget(deselect_all_btn)
        
        list_buttons.addStretch()
        layout.addLayout(list_buttons)
        
        controls = QHBoxLayout()
        
        prefs_btn = QPushButton("⚙ Preferences")
        prefs_btn.clicked.connect(self.show_preferences)
        controls.addWidget(prefs_btn)
        
        self.preview_checkbox = QCheckBox("Preview only")
        self.preview_checkbox.setChecked(True)
        controls.addWidget(self.preview_checkbox)
        
        controls.addStretch()
        
        self.clean_btn = QPushButton("Clean Files")
        self.clean_btn.setObjectName("primary")
        self.clean_btn.clicked.connect(self.clean_files)
        self.clean_btn.setEnabled(False)
        controls.addWidget(self.clean_btn)
        
        layout.addLayout(controls)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["File", "Status", "Removed", "Kept", "Error"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.results_table.setVisible(False)
        layout.addWidget(self.results_table)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setVisible(False)
        layout.addWidget(self.log_text)
    
    def set_folder(self, folder: str):
        self.current_folder = Path(folder)
        self.info_label.setText(f"Scanning: {folder}")
        self.scan_folder()
    
    def scan_folder(self):
        if not self.current_folder or not self.current_folder.exists():
            return
        
        self.file_list.clear()
        self.results_table.setVisible(False)
        self.log_text.setVisible(False)
        
        files = sorted([
            f for f in self.current_folder.rglob("*")
            if f.is_file() and f.suffix.lower() in SUPPORTED_SUFFIXES and not f.name.startswith("._")
        ])
        
        if not files:
            self.info_label.setText("No supported music files found in this folder.")
            self.clean_btn.setEnabled(False)
            return
        
        self.info_label.setText(f"Found {len(files)} supported files.")
        
        for file in files:
            rel_path = file.relative_to(self.current_folder)
            item = QListWidgetItem(str(rel_path))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            item.setData(Qt.UserRole, str(file))
            self.file_list.addItem(item)
        
        self.clean_btn.setEnabled(True)
    
    def select_all_files(self):
        for i in range(self.file_list.count()):
            self.file_list.item(i).setCheckState(Qt.Checked)
    
    def deselect_all_files(self):
        for i in range(self.file_list.count()):
            self.file_list.item(i).setCheckState(Qt.Unchecked)
    
    def show_preferences(self):
        dialog = PreferencesDialog(self.keep_tags_pref, self)
        if dialog.exec():
            self.keep_tags_pref = dialog.get_preferences()
    
    def clean_files(self):
        if not self.current_folder:
            return
        
        files_to_clean = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item.checkState() == Qt.Checked:
                files_to_clean.append(Path(item.data(Qt.UserRole)))
        
        if not files_to_clean:
            return
        
        keep_tags = {tag for tag, keep in self.keep_tags_pref.items() if keep}
        dry_run = self.preview_checkbox.isChecked()
        
        self.clean_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(files_to_clean))
        self.progress_bar.setValue(0)
        
        self.clean_worker = CleanWorker(files_to_clean, keep_tags, dry_run)
        self.clean_worker.file_done.connect(self.on_file_cleaned)
        self.clean_worker.finished.connect(self.on_clean_finished)
        self.clean_worker.progress.connect(self.on_clean_progress)
        self.clean_worker.start()
    
    def on_file_cleaned(self, result: CleanResult):
        if self.progress_bar:
            self.progress_bar.setValue(self.progress_bar.value() + 1)
    
    def on_clean_progress(self, message: str):
        self.log_text.append(message)
    
    def on_clean_finished(self, results: list[CleanResult]):
        self.clean_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        self.show_results(results)
    
    def show_results(self, results: list[CleanResult]):
        self.results_table.setVisible(True)
        self.log_text.setVisible(True)
        
        self.results_table.setRowCount(len(results))
        
        for row, result in enumerate(results):
            self.results_table.setItem(row, 0, QTableWidgetItem(str(result.path.relative_to(self.current_folder))))
            self.results_table.setItem(row, 1, QTableWidgetItem(result.status))
            self.results_table.setItem(row, 2, QTableWidgetItem(", ".join(result.removed)))
            self.results_table.setItem(row, 3, QTableWidgetItem(", ".join(result.kept)))
            self.results_table.setItem(row, 4, QTableWidgetItem(result.error))
