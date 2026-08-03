from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QCheckBox, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QProgressBar, QTabWidget
)
from PySide6.QtCore import Qt, Signal

from rip_tags.cleaner import SUPPORTED_SUFFIXES, CleanResult
from rip_tags.metadata import to_display_name
from rip_tags.tags import ALL_SUPPORTED_TAGS, RECOMMENDED_TAGS
from rip_tags.ui.preferences import PreferencesDialog
from rip_tags.ui.worker import CleanWorker
from rip_tags.ui.components import Card, EmptyState, MetricItem, TextOnlySelectionDelegate


class BatchCleanerWidget(QWidget):
    file_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_folder: Optional[Path] = None
        self.keep_tags_pref: dict = {tag: (tag in RECOMMENDED_TAGS) for tag in ALL_SUPPORTED_TAGS}
        self.clean_worker: Optional[CleanWorker] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        header = QLabel("Batch Tag Cleaner")
        header.setObjectName("title")
        layout.addWidget(header)

        self.empty_state = EmptyState(
            "folder",
            "No Folder Selected",
            "Select a folder in the sidebar to scan for music files."
        )
        layout.addWidget(self.empty_state, 1)

        self.main_content = QWidget()
        self.main_content.setVisible(False)
        main_layout = QVBoxLayout(self.main_content)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        self.info_card = Card()
        self.info_card.layout.setContentsMargins(16, 16, 16, 16)

        info_layout = QHBoxLayout()
        self.folder_name_label = QLabel()
        self.folder_name_label.setObjectName("section-title")
        info_layout.addWidget(self.folder_name_label)

        info_layout.addStretch()

        self.file_count_label = QLabel()
        self.file_count_label.setObjectName("subtitle")
        info_layout.addWidget(self.file_count_label)

        self.info_card.layout.addLayout(info_layout)
        main_layout.addWidget(self.info_card)

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["File", "Format"])
        self.file_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.file_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.file_tree.setItemDelegate(TextOnlySelectionDelegate(self.file_tree))
        self.file_tree.itemClicked.connect(self.on_tree_item_clicked)
        self.file_tree.itemChanged.connect(self.on_tree_item_changed)
        main_layout.addWidget(self.file_tree, 1)

        action_bar = QHBoxLayout()

        select_all_btn = QPushButton("Select All")
        select_all_btn.setObjectName("secondary")
        select_all_btn.clicked.connect(self.select_all_files)
        action_bar.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.setObjectName("secondary")
        deselect_all_btn.clicked.connect(self.deselect_all_files)
        action_bar.addWidget(deselect_all_btn)

        action_bar.addStretch()

        prefs_btn = QPushButton("Preferences")
        prefs_btn.setObjectName("secondary")
        prefs_btn.clicked.connect(self.show_preferences)
        action_bar.addWidget(prefs_btn)

        self.preview_checkbox = QCheckBox("Preview only")
        self.preview_checkbox.setChecked(True)
        action_bar.addWidget(self.preview_checkbox)

        action_bar.addStretch()

        self.clean_btn = QPushButton("Clean Files")
        self.clean_btn.setObjectName("primary")
        self.clean_btn.clicked.connect(self.clean_files)
        self.clean_btn.setEnabled(False)
        action_bar.addWidget(self.clean_btn)

        main_layout.addLayout(action_bar)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.results_card = Card()
        self.results_card.setVisible(False)
        self.results_card.layout.setContentsMargins(16, 16, 16, 16)

        self.results_tabs = QTabWidget()
        self.results_card.layout.addWidget(self.results_tabs)

        main_layout.addWidget(self.results_card)

        layout.addWidget(self.main_content, 1)

    def set_folder(self, folder: str):
        self.current_folder = Path(folder)
        self.empty_state.setVisible(False)
        self.main_content.setVisible(True)
        self.folder_name_label.setText(self.current_folder.name)
        self.results_card.setVisible(False)
        self.scan_folder()

    def scan_folder(self):
        if not self.current_folder or not self.current_folder.exists():
            return

        self.file_tree.clear()
        self.clean_btn.setEnabled(False)

        files = sorted([
            f for f in self.current_folder.rglob("*")
            if f.is_file() and f.suffix.lower() in SUPPORTED_SUFFIXES and not f.name.startswith("._")
        ])

        if not files:
            self.file_count_label.setText("0 files")
            return

        self.file_count_label.setText(f"{len(files)} files")

        groups: dict[str, list[Path]] = {}
        for file in files:
            try:
                rel_path = file.relative_to(self.current_folder)
                if rel_path.parent == Path("."):
                    group_name = "Root"
                else:
                    group_name = rel_path.parent.name
            except ValueError:
                group_name = "Root"

            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(file)

        for group_name in sorted(groups.keys()):
            group_files = groups[group_name]
            group_item = QTreeWidgetItem(self.file_tree)
            group_item.setText(0, group_name)
            group_item.setText(1, f"{len(group_files)} files")
            group_item.setFlags(group_item.flags() | Qt.ItemIsUserCheckable)
            group_item.setCheckState(0, Qt.Checked)
            group_item.setData(0, Qt.UserRole, "group")

            for file in group_files:
                file_item = QTreeWidgetItem(group_item)
                file_item.setText(0, file.name)
                file_item.setText(1, file.suffix.upper().lstrip("."))
                file_item.setFlags(file_item.flags() | Qt.ItemIsUserCheckable)
                file_item.setCheckState(0, Qt.Checked)
                file_item.setData(0, Qt.UserRole, "file")
                file_item.setData(0, Qt.UserRole + 1, str(file))

        self.file_tree.expandAll()
        self.clean_btn.setEnabled(True)

    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        if column == 0:
            item_type = item.data(0, Qt.UserRole)
            if item_type == "file":
                file_path = item.data(0, Qt.UserRole + 1)
                if file_path:
                    self.file_selected.emit(file_path)

    def on_tree_item_changed(self, item: QTreeWidgetItem, column: int):
        if column != 0:
            return

        item_type = item.data(0, Qt.UserRole)

        if item_type == "group":
            state = item.checkState(0)
            for i in range(item.childCount()):
                child = item.child(i)
                child.setCheckState(0, state)
        elif item_type == "file":
            parent = item.parent()
            if parent:
                checked_count = 0
                for i in range(parent.childCount()):
                    if parent.child(i).checkState(0) == Qt.Checked:
                        checked_count += 1

                if checked_count == 0:
                    parent.setCheckState(0, Qt.Unchecked)
                elif checked_count == parent.childCount():
                    parent.setCheckState(0, Qt.Checked)
                else:
                    parent.setCheckState(0, Qt.PartiallyChecked)

    def select_all_files(self):
        for i in range(self.file_tree.topLevelItemCount()):
            group_item = self.file_tree.topLevelItem(i)
            group_item.setCheckState(0, Qt.Checked)

    def deselect_all_files(self):
        for i in range(self.file_tree.topLevelItemCount()):
            group_item = self.file_tree.topLevelItem(i)
            group_item.setCheckState(0, Qt.Unchecked)

    def show_preferences(self):
        dialog = PreferencesDialog(self.keep_tags_pref, self)
        if dialog.exec():
            self.keep_tags_pref = dialog.get_preferences()

    def clean_files(self):
        if not self.current_folder:
            return

        files_to_clean = []
        for i in range(self.file_tree.topLevelItemCount()):
            group_item = self.file_tree.topLevelItem(i)
            if group_item.checkState(0) == Qt.Unchecked:
                continue
            for j in range(group_item.childCount()):
                file_item = group_item.child(j)
                if file_item.checkState(0) == Qt.Checked:
                    file_path = file_item.data(0, Qt.UserRole + 1)
                    if file_path:
                        files_to_clean.append(Path(file_path))

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
        pass

    def on_clean_finished(self, results: list[CleanResult]):
        self.clean_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.show_results(results)

    def show_results(self, results: list[CleanResult]):
        self.results_card.setVisible(True)

        while self.results_tabs.count() > 0:
            self.results_tabs.removeTab(0)

        summary_widget = QWidget()
        summary_layout = QHBoxLayout(summary_widget)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(24)

        cleaned_count = sum(1 for r in results if r.status == "cleaned")
        unchanged_count = sum(1 for r in results if r.status == "unchanged")
        error_count = sum(1 for r in results if r.status == "failed")

        summary_layout.addWidget(MetricItem(str(cleaned_count), "Cleaned"))
        summary_layout.addWidget(MetricItem(str(unchanged_count), "Unchanged"))
        summary_layout.addWidget(MetricItem(str(error_count), "Errors"))
        summary_layout.addStretch()

        self.results_tabs.addTab(summary_widget, "Summary")

        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.setContentsMargins(0, 0, 0, 0)

        from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
        details_table = QTableWidget()
        details_table.setColumnCount(4)
        details_table.setHorizontalHeaderLabels(["File", "Status", "Removed", "Kept"])
        details_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        details_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        details_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        details_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        details_table.setRowCount(len(results))

        for row, result in enumerate(results):
            rel_path = str(result.path.relative_to(self.current_folder)) if self.current_folder else str(result.path)
            removed = dict.fromkeys(result.removed)
            kept = dict.fromkeys(result.kept)
            details_table.setItem(row, 0, QTableWidgetItem(rel_path))
            details_table.setItem(row, 1, QTableWidgetItem(result.status))
            details_table.setItem(row, 2, QTableWidgetItem(", ".join(to_display_name(tag) for tag in removed)))
            details_table.setItem(row, 3, QTableWidgetItem(", ".join(to_display_name(tag) for tag in kept)))

        details_layout.addWidget(details_table)
        self.results_tabs.addTab(details_widget, "Details")
