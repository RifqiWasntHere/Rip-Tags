from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QCheckBox, QTreeWidget, QTreeWidgetItem, QLineEdit,
    QHeaderView, QProgressBar, QTabWidget, QTableWidget, QTableWidgetItem,
    QStatusBar, QMessageBox
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

    def __init__(self, status_bar: Optional[QStatusBar] = None, parent=None):
        super().__init__(parent)
        self.current_folder: Optional[Path] = None
        self.keep_tags_pref: dict = {tag: (tag in RECOMMENDED_TAGS) for tag in ALL_SUPPORTED_TAGS}
        self.clean_worker: Optional[CleanWorker] = None
        self.status_bar = status_bar
        self.all_files: list[Path] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        header = QLabel("Batch Tag Cleaner")
        header.setObjectName("title")
        layout.addWidget(header)

        self.empty_state = EmptyState(
            "folder",
            "No Folder Selected",
            "Open a folder from the sidebar to start cleaning music tags."
        )
        layout.addWidget(self.empty_state, 1)

        self.main_content = QWidget()
        self.main_content.setVisible(False)
        main_layout = QVBoxLayout(self.main_content)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        header_card = Card()
        header_card.layout.setContentsMargins(16, 16, 16, 16)
        header_card.layout.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        self.folder_name_label = QLabel()
        self.folder_name_label.setObjectName("section-title")
        top_row.addWidget(self.folder_name_label)

        top_row.addStretch()

        self.file_count_label = MetricItem("0", "Files")
        self.flac_count_label = MetricItem("0", "FLAC")
        self.m4a_count_label = MetricItem("0", "M4A/MP4")
        top_row.addWidget(self.file_count_label)
        top_row.addWidget(self.flac_count_label)
        top_row.addWidget(self.m4a_count_label)

        header_card.layout.addLayout(top_row)

        controls_row = QHBoxLayout()
        controls_row.setSpacing(8)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search files...")
        self.search_edit.textChanged.connect(self.filter_files)
        controls_row.addWidget(self.search_edit, 1)

        select_all_btn = QPushButton("Select All")
        select_all_btn.setObjectName("secondary")
        select_all_btn.clicked.connect(self.select_all_files)
        controls_row.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.setObjectName("secondary")
        deselect_all_btn.clicked.connect(self.deselect_all_files)
        controls_row.addWidget(deselect_all_btn)

        invert_btn = QPushButton("Invert")
        invert_btn.setObjectName("secondary")
        invert_btn.clicked.connect(self.invert_selection)
        controls_row.addWidget(invert_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("secondary")
        refresh_btn.clicked.connect(self.refresh_folder)
        controls_row.addWidget(refresh_btn)

        header_card.layout.addLayout(controls_row)
        main_layout.addWidget(header_card)

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["File", "Format", "Folder"])
        self.file_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.file_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.file_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.file_tree.setItemDelegate(TextOnlySelectionDelegate(self.file_tree))
        self.file_tree.itemClicked.connect(self.on_tree_item_clicked)
        self.file_tree.itemChanged.connect(self.on_tree_item_changed)
        main_layout.addWidget(self.file_tree, 1)

        action_bar = QHBoxLayout()
        action_bar.setSpacing(8)

        prefs_btn = QPushButton("Preferences")
        prefs_btn.setObjectName("secondary")
        prefs_btn.clicked.connect(self.show_preferences)
        action_bar.addWidget(prefs_btn)

        self.preview_checkbox = QCheckBox("Preview only")
        self.preview_checkbox.setChecked(True)
        action_bar.addWidget(self.preview_checkbox)

        self.selected_count_label = QLabel("0 selected")
        self.selected_count_label.setObjectName("subtitle")
        action_bar.addWidget(self.selected_count_label)

        action_bar.addStretch()

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        action_bar.addWidget(self.progress_bar)

        self.clean_btn = QPushButton("Clean Selected Files")
        self.clean_btn.setObjectName("primary")
        self.clean_btn.clicked.connect(self.clean_files)
        self.clean_btn.setEnabled(False)
        action_bar.addWidget(self.clean_btn)

        main_layout.addLayout(action_bar)

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
        self.search_edit.clear()
        self.scan_folder()

    def refresh_folder(self):
        if self.current_folder:
            self.scan_folder()

    def scan_folder(self):
        if not self.current_folder or not self.current_folder.exists():
            return

        self.file_tree.clear()
        self.clean_btn.setEnabled(False)
        self.all_files = sorted([
            f for f in self.current_folder.rglob("*")
            if f.is_file() and f.suffix.lower() in SUPPORTED_SUFFIXES and not f.name.startswith("._")
        ])

        flac_count = sum(1 for f in self.all_files if f.suffix.lower() == ".flac")
        m4a_count = sum(1 for f in self.all_files if f.suffix.lower() in {".m4a", ".mp4"})

        self.file_count_label.set_value(str(len(self.all_files)))
        self.flac_count_label.set_value(str(flac_count))
        self.m4a_count_label.set_value(str(m4a_count))

        if not self.all_files:
            self.selected_count_label.setText("0 selected")
            return

        groups: dict[str, list[Path]] = {}
        for file in self.all_files:
            try:
                rel_path = file.relative_to(self.current_folder)
                if rel_path.parent == Path("."):
                    group_name = "Root"
                else:
                    group_name = str(rel_path.parent)
            except ValueError:
                group_name = "Root"

            groups.setdefault(group_name, []).append(file)

        for group_name in sorted(groups.keys()):
            group_files = groups[group_name]
            group_item = QTreeWidgetItem(self.file_tree)
            group_item.setText(0, group_name)
            group_item.setText(1, f"{len(group_files)} files")
            group_item.setText(2, "")
            group_item.setFlags(group_item.flags() | Qt.ItemIsUserCheckable)
            group_item.setCheckState(0, Qt.Checked)
            group_item.setData(0, Qt.UserRole, "group")
            group_item.setData(0, Qt.UserRole + 2, group_name)

            for file in group_files:
                file_item = QTreeWidgetItem(group_item)
                file_item.setText(0, file.name)
                file_item.setText(1, file.suffix.upper().lstrip("."))
                file_item.setText(2, group_name)
                file_item.setFlags(file_item.flags() | Qt.ItemIsUserCheckable)
                file_item.setCheckState(0, Qt.Checked)
                file_item.setData(0, Qt.UserRole, "file")
                file_item.setData(0, Qt.UserRole + 1, str(file))
                file_item.setData(0, Qt.UserRole + 2, group_name)

        self.file_tree.expandAll()
        self.clean_btn.setEnabled(True)
        self.update_selected_count()
        self._update_status(f"Loaded {len(self.all_files)} files from {self.current_folder.name}")

    def filter_files(self, text: str):
        text = text.lower()
        for i in range(self.file_tree.topLevelItemCount()):
            group_item = self.file_tree.topLevelItem(i)
            group_visible = False
            for j in range(group_item.childCount()):
                file_item = group_item.child(j)
                file_name = file_item.text(0).lower()
                folder_name = file_item.text(2).lower()
                visible = text in file_name or text in folder_name
                file_item.setHidden(not visible)
                if visible:
                    group_visible = True
            group_item.setHidden(not group_visible)

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
                if not child.isHidden():
                    child.setCheckState(0, state)
        elif item_type == "file":
            parent = item.parent()
            if parent:
                checked_count = 0
                visible_count = 0
                for i in range(parent.childCount()):
                    child = parent.child(i)
                    if child.isHidden():
                        continue
                    visible_count += 1
                    if child.checkState(0) == Qt.Checked:
                        checked_count += 1

                if visible_count == 0:
                    parent.setCheckState(0, Qt.Unchecked)
                elif checked_count == 0:
                    parent.setCheckState(0, Qt.Unchecked)
                elif checked_count == visible_count:
                    parent.setCheckState(0, Qt.Checked)
                else:
                    parent.setCheckState(0, Qt.PartiallyChecked)

        self.update_selected_count()

    def update_selected_count(self):
        count = 0
        for i in range(self.file_tree.topLevelItemCount()):
            group_item = self.file_tree.topLevelItem(i)
            if group_item.isHidden():
                continue
            for j in range(group_item.childCount()):
                file_item = group_item.child(j)
                if file_item.isHidden():
                    continue
                if file_item.checkState(0) == Qt.Checked:
                    count += 1
        self.selected_count_label.setText(f"{count} selected")
        self.clean_btn.setEnabled(count > 0)

    def select_all_files(self):
        for i in range(self.file_tree.topLevelItemCount()):
            group_item = self.file_tree.topLevelItem(i)
            if group_item.isHidden():
                continue
            group_item.setCheckState(0, Qt.Checked)

    def deselect_all_files(self):
        for i in range(self.file_tree.topLevelItemCount()):
            group_item = self.file_tree.topLevelItem(i)
            if group_item.isHidden():
                continue
            group_item.setCheckState(0, Qt.Unchecked)

    def invert_selection(self):
        for i in range(self.file_tree.topLevelItemCount()):
            group_item = self.file_tree.topLevelItem(i)
            if group_item.isHidden():
                continue
            for j in range(group_item.childCount()):
                file_item = group_item.child(j)
                if file_item.isHidden():
                    continue
                current = file_item.checkState(0)
                file_item.setCheckState(0, Qt.Unchecked if current == Qt.Checked else Qt.Checked)
            self._update_group_state(group_item)

    def _update_group_state(self, group_item: QTreeWidgetItem):
        visible_count = 0
        checked_count = 0
        for i in range(group_item.childCount()):
            child = group_item.child(i)
            if child.isHidden():
                continue
            visible_count += 1
            if child.checkState(0) == Qt.Checked:
                checked_count += 1
        if visible_count == 0:
            group_item.setCheckState(0, Qt.Unchecked)
        elif checked_count == 0:
            group_item.setCheckState(0, Qt.Unchecked)
        elif checked_count == visible_count:
            group_item.setCheckState(0, Qt.Checked)
        else:
            group_item.setCheckState(0, Qt.PartiallyChecked)

    def show_preferences(self):
        dialog = PreferencesDialog(self.keep_tags_pref, self)
        if dialog.exec():
            self.keep_tags_pref = dialog.get_preferences()
            keep_count = sum(1 for keep in self.keep_tags_pref.values() if keep)
            self._update_status(f"Preferences updated: {keep_count} tags will be kept")

    def clean_files(self):
        if not self.current_folder:
            return

        files_to_clean = []
        for i in range(self.file_tree.topLevelItemCount()):
            group_item = self.file_tree.topLevelItem(i)
            if group_item.isHidden() or group_item.checkState(0) == Qt.Unchecked:
                continue
            for j in range(group_item.childCount()):
                file_item = group_item.child(j)
                if file_item.isHidden():
                    continue
                if file_item.checkState(0) == Qt.Checked:
                    file_path = file_item.data(0, Qt.UserRole + 1)
                    if file_path:
                        files_to_clean.append(Path(file_path))

        if not files_to_clean:
            return

        dry_run = self.preview_checkbox.isChecked()
        if not dry_run:
            reply = QMessageBox.question(
                self,
                "Confirm Clean",
                f"This will modify {len(files_to_clean)} file(s). Continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        keep_tags = {tag for tag, keep in self.keep_tags_pref.items() if keep}

        self.clean_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(files_to_clean))
        self.progress_bar.setValue(0)
        self.results_card.setVisible(False)

        self._update_status(f"{'Previewing' if dry_run else 'Cleaning'} {len(files_to_clean)} files...")

        self.clean_worker = CleanWorker(files_to_clean, keep_tags, dry_run)
        self.clean_worker.file_done.connect(self.on_file_cleaned)
        self.clean_worker.finished.connect(self.on_clean_finished)
        self.clean_worker.progress.connect(self.on_clean_progress)
        self.clean_worker.start()

    def on_file_cleaned(self, result: CleanResult):
        if self.progress_bar:
            self.progress_bar.setValue(self.progress_bar.value() + 1)

    def on_clean_progress(self, message: str):
        self._update_status(message)

    def on_clean_finished(self, results: list[CleanResult]):
        self.clean_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.show_results(results)
        cleaned = sum(1 for r in results if r.status == "cleaned")
        unchanged = sum(1 for r in results if r.status == "unchanged")
        errors = sum(1 for r in results if r.status == "failed")
        mode = "preview" if self.preview_checkbox.isChecked() else "clean"
        self._update_status(f"{mode.capitalize()} complete: {cleaned} cleaned, {unchanged} unchanged, {errors} errors")

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

    def _update_status(self, message: str):
        if self.status_bar:
            self.status_bar.showMessage(message)
