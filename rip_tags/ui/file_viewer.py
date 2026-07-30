from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal

from rip_tags.metadata import AudioInfo, read_audio_info
from rip_tags.ui.cover_editor import CoverEditorWidget


class FileViewerWidget(QWidget):
    back_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_info: Optional[AudioInfo] = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        top_bar = QHBoxLayout()
        
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(self.back_requested.emit)
        top_bar.addWidget(back_btn)
        
        top_bar.addStretch()
        layout.addLayout(top_bar)
        
        self.title_label = QLabel()
        self.title_label.setObjectName("title")
        layout.addWidget(self.title_label)
        
        content_layout = QHBoxLayout()
        
        self.cover_editor: Optional[CoverEditorWidget] = None
        content_layout.setStretch(0, 1)
        
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        self.audio_info_label = QLabel()
        self.audio_info_label.setWordWrap(True)
        info_layout.addWidget(self.audio_info_label)
        
        self.metadata_table = QTableWidget()
        self.metadata_table.setColumnCount(2)
        self.metadata_table.setHorizontalHeaderLabels(["Tag", "Value"])
        self.metadata_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.metadata_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        info_layout.addWidget(self.metadata_table, 1)
        
        content_layout.addWidget(info_widget, 2)
        layout.addLayout(content_layout, 1)
    
    def set_file(self, file_path: str):
        self.audio_info = read_audio_info(Path(file_path))
        
        self.title_label.setText(self.audio_info.path.name)
        
        info_lines = [
            f"Path: {self.audio_info.path}",
            f"Type: {self.audio_info.file_type}",
            f"Duration: {self._format_duration(self.audio_info.duration)}",
            f"Bitrate: {self._format_bitrate(self.audio_info.bitrate)}",
            f"Sample Rate: {self._format_sample_rate(self.audio_info.sample_rate)}",
            f"Bit Depth: {self._format_bit_depth(self.audio_info.bit_depth)}",
            f"Channels: {self.audio_info.channels if self.audio_info.channels else '-'}",
        ]
        self.audio_info_label.setText("\n".join(info_lines))
        
        self.metadata_table.setRowCount(len(self.audio_info.tags))
        for row, (key, value) in enumerate(self.audio_info.tags.items()):
            self.metadata_table.setItem(row, 0, QTableWidgetItem(key))
            self.metadata_table.setItem(row, 1, QTableWidgetItem(str(value)))
        
        if self.cover_editor:
            self.cover_editor.setParent(None)
            self.cover_editor.deleteLater()
        
        self.cover_editor = CoverEditorWidget(self.audio_info)
        self.layout().itemAt(2).layout().insertWidget(0, self.cover_editor)
    
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
