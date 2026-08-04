from pathlib import Path
from typing import Optional
import platform
import subprocess

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout, QMessageBox
)
from PySide6.QtCore import Qt, Signal

from rip_tags.metadata import AudioInfo, read_audio_info, to_canonical_tag, to_display_name
from rip_tags.ui.cover_editor import CoverEditorWidget
from rip_tags.ui.components import Card, MetricItem
from rip_tags.ui.preferences import TAG_GROUPS


class FileViewerWidget(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_info: Optional[AudioInfo] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("secondary")
        back_btn.clicked.connect(self.back_requested.emit)
        top_bar.addWidget(back_btn)

        top_bar.addStretch()

        self.show_btn = QPushButton("Show in Finder")
        self.show_btn.setObjectName("secondary")
        self.show_btn.clicked.connect(self.show_in_finder)
        top_bar.addWidget(self.show_btn)

        layout.addLayout(top_bar)

        self.title_label = QLabel()
        self.title_label.setObjectName("title")
        layout.addWidget(self.title_label)

        self.format_badge = QLabel()
        self.format_badge.setObjectName("badge")
        layout.addWidget(self.format_badge)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(16)

        self.cover_editor: Optional[CoverEditorWidget] = None
        left_layout.addWidget(self.cover_editor if self.cover_editor else QWidget())
        left_layout.addStretch()

        content_layout.addWidget(left_widget, 0)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(16)

        self.metrics_card = Card()
        self.metrics_card.layout.setContentsMargins(16, 16, 16, 16)

        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(16)

        self.duration_metric = MetricItem("-", "Duration")
        self.bitrate_metric = MetricItem("-", "Bitrate")
        self.sample_rate_metric = MetricItem("-", "Sample Rate")
        self.bit_depth_metric = MetricItem("-", "Bit Depth")
        self.channels_metric = MetricItem("-", "Channels")
        self.file_type_metric = MetricItem("-", "Format")

        metrics_grid.addWidget(self.duration_metric, 0, 0)
        metrics_grid.addWidget(self.bitrate_metric, 0, 1)
        metrics_grid.addWidget(self.sample_rate_metric, 0, 2)
        metrics_grid.addWidget(self.bit_depth_metric, 1, 0)
        metrics_grid.addWidget(self.channels_metric, 1, 1)
        metrics_grid.addWidget(self.file_type_metric, 1, 2)

        self.metrics_card.layout.addLayout(metrics_grid)
        right_layout.addWidget(self.metrics_card)

        self.metadata_card = Card()
        self.metadata_card.layout.setContentsMargins(16, 16, 16, 16)

        metadata_header = QLabel("Metadata Tags")
        metadata_header.setObjectName("section-title")
        self.metadata_card.layout.addWidget(metadata_header)

        self.metadata_table = QTableWidget()
        self.metadata_table.setColumnCount(3)
        self.metadata_table.setHorizontalHeaderLabels(["Tag", "Value", "Category"])
        self.metadata_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.metadata_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.metadata_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.metadata_table.setMinimumHeight(200)
        self.metadata_card.layout.addWidget(self.metadata_table, 1)

        right_layout.addWidget(self.metadata_card, 1)

        content_layout.addWidget(right_widget, 1)
        layout.addLayout(content_layout, 1)

    def set_file(self, file_path: str):
        self.audio_info = read_audio_info(Path(file_path))

        self.title_label.setText(self.audio_info.path.name)
        self.format_badge.setText(self.audio_info.file_type)
        self.show_btn.setText("Show in Finder" if platform.system() == "Darwin" else "Show in Explorer")

        self.duration_metric.set_value(self._format_duration(self.audio_info.duration))
        self.bitrate_metric.set_value(self._format_bitrate(self.audio_info.bitrate))
        self.sample_rate_metric.set_value(self._format_sample_rate(self.audio_info.sample_rate))
        self.bit_depth_metric.set_value(self._format_bit_depth(self.audio_info.bit_depth))
        self.channels_metric.set_value(str(self.audio_info.channels) if self.audio_info.channels else "-")
        self.file_type_metric.set_value(self.audio_info.file_type)

        self._populate_metadata_table()

        if self.cover_editor:
            self.cover_editor.setParent(None)
            self.cover_editor.deleteLater()

        self.cover_editor = CoverEditorWidget(self.audio_info)
        left_widget = self.layout().itemAt(3).layout().itemAt(0).widget()
        left_layout = left_widget.layout()
        for i in reversed(range(left_layout.count())):
            item = left_layout.itemAt(i)
            if item is None:
                continue
            widget = item.widget()
            if widget and widget is not self.cover_editor:
                widget.setParent(None)
        left_layout.insertWidget(0, self.cover_editor)

    def _populate_metadata_table(self):
        self.metadata_table.setRowCount(0)
        file_type = self.audio_info.file_type

        grouped: dict[str, list[tuple[str, str]]] = {}
        tag_to_group: dict[str, str] = {}
        for group_name, tags in TAG_GROUPS.items():
            for tag in tags:
                tag_to_group[tag] = group_name

        for key, value in self.audio_info.tags.items():
            canonical = to_canonical_tag(key, file_type)
            group = tag_to_group.get(canonical, "Other")
            grouped.setdefault(group, []).append((to_display_name(canonical), str(value)))

        group_order = list(TAG_GROUPS.keys()) + ["Other"]
        row = 0
        for group in group_order:
            if group not in grouped:
                continue
            items = sorted(grouped[group])
            for display, value in items:
                self.metadata_table.insertRow(row)
                self.metadata_table.setItem(row, 0, QTableWidgetItem(display))
                self.metadata_table.setItem(row, 1, QTableWidgetItem(value))
                self.metadata_table.setItem(row, 2, QTableWidgetItem(group))
                row += 1

    def show_in_finder(self):
        if not self.audio_info:
            return
        path = self.audio_info.path
        if not path.exists():
            QMessageBox.warning(self, "Not Found", "File no longer exists.")
            return
        system = platform.system()
        try:
            if system == "Darwin":
                subprocess.run(["open", "-R", str(path)], check=True)
            elif system == "Windows":
                subprocess.run(["explorer", "/select,", str(path)], check=True)
            else:
                subprocess.run(["xdg-open", str(path.parent)], check=True)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open file location: {e}")

    def _format_duration(self, seconds: Optional[float]) -> str:
        if seconds is None:
            return "-"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

    def _format_bitrate(self, bitrate: Optional[int]) -> str:
        if bitrate is None:
            return "-"
        return f"{bitrate // 1000} kbps"

    def _format_sample_rate(self, sample_rate: Optional[int]) -> str:
        if sample_rate is None:
            return "-"
        return f"{sample_rate / 1000:.1f} kHz"

    def _format_bit_depth(self, bit_depth: Optional[int]) -> str:
        if bit_depth is None:
            return "-"
        return f"{bit_depth}-bit"
