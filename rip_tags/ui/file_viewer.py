from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout
)
from PySide6.QtCore import Qt, Signal

from rip_tags.metadata import AudioInfo, read_audio_info, to_canonical_tag, to_display_name
from rip_tags.ui.cover_editor import CoverEditorWidget
from rip_tags.ui.components import Card, MetricItem


class FileViewerWidget(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_info: Optional[AudioInfo] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        top_bar = QHBoxLayout()

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("secondary")
        back_btn.clicked.connect(self.back_requested.emit)
        top_bar.addWidget(back_btn)

        top_bar.addStretch()
        layout.addLayout(top_bar)

        self.title_label = QLabel()
        self.title_label.setObjectName("title")
        layout.addWidget(self.title_label)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(16)

        self.cover_editor: Optional[CoverEditorWidget] = None
        left_layout.addWidget(self.cover_editor if self.cover_editor else QWidget())

        content_layout.addWidget(left_widget, 1)

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
        metrics_grid.addWidget(self.sample_rate_metric, 1, 0)
        metrics_grid.addWidget(self.bit_depth_metric, 1, 1)
        metrics_grid.addWidget(self.channels_metric, 2, 0)
        metrics_grid.addWidget(self.file_type_metric, 2, 1)

        self.metrics_card.layout.addLayout(metrics_grid)
        right_layout.addWidget(self.metrics_card)

        self.metadata_card = Card()
        self.metadata_card.layout.setContentsMargins(16, 16, 16, 16)

        metadata_header = QLabel("Metadata Tags")
        metadata_header.setObjectName("section-title")
        self.metadata_card.layout.addWidget(metadata_header)

        self.metadata_table = QTableWidget()
        self.metadata_table.setColumnCount(2)
        self.metadata_table.setHorizontalHeaderLabels(["Tag", "Value"])
        self.metadata_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.metadata_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.metadata_table.setMinimumHeight(200)
        self.metadata_card.layout.addWidget(self.metadata_table, 1)

        right_layout.addWidget(self.metadata_card, 1)

        content_layout.addWidget(right_widget, 2)
        layout.addLayout(content_layout, 1)

    def set_file(self, file_path: str):
        self.audio_info = read_audio_info(Path(file_path))

        self.title_label.setText(self.audio_info.path.name)

        self.duration_metric.set_value(self._format_duration(self.audio_info.duration))
        self.bitrate_metric.set_value(self._format_bitrate(self.audio_info.bitrate))
        self.sample_rate_metric.set_value(self._format_sample_rate(self.audio_info.sample_rate))
        self.bit_depth_metric.set_value(self._format_bit_depth(self.audio_info.bit_depth))
        self.channels_metric.set_value(str(self.audio_info.channels) if self.audio_info.channels else "-")
        self.file_type_metric.set_value(self.audio_info.file_type)

        self.metadata_table.setRowCount(len(self.audio_info.tags))
        file_type = self.audio_info.file_type
        for row, (key, value) in enumerate(self.audio_info.tags.items()):
            canonical = to_canonical_tag(key, file_type)
            self.metadata_table.setItem(row, 0, QTableWidgetItem(to_display_name(canonical)))
            self.metadata_table.setItem(row, 1, QTableWidgetItem(str(value)))

        if self.cover_editor:
            self.cover_editor.setParent(None)
            self.cover_editor.deleteLater()

        self.cover_editor = CoverEditorWidget(self.audio_info)
        left_widget = self.layout().itemAt(2).layout().itemAt(0).widget()
        left_layout = left_widget.layout()
        for i in range(left_layout.count()):
            item = left_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
        left_layout.addWidget(self.cover_editor)

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
