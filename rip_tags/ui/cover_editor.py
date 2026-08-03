from pathlib import Path
from io import BytesIO
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage

from rip_tags.metadata import AudioInfo
from rip_tags.cover_art import (
    DEFAULT_COVER_SIZE,
    embed_cover,
    remove_cover,
    prepare_cover_image,
    resize_cover_image,
)
from rip_tags.ui.components import Card


class CoverEditorWidget(QWidget):
    cover_changed = Signal()

    def __init__(self, audio_info: AudioInfo, parent=None):
        super().__init__(parent)
        self.audio_info = audio_info
        self.current_cover_data: Optional[bytes] = audio_info.cover_data

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.cover_card = Card()
        self.cover_card.layout.setContentsMargins(16, 16, 16, 16)

        self.cover_label = QLabel()
        self.cover_label.setFixedSize(280, 280)
        self.cover_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.cover_label.setStyleSheet("background: #1e1e1e; border-radius: 12px;")
        self.update_cover_display()
        self.cover_card.layout.addWidget(
            self.cover_label, alignment=Qt.AlignLeft | Qt.AlignTop
        )

        layout.addWidget(self.cover_card)

        action_bar = QHBoxLayout()
        action_bar.setSpacing(8)

        upload_btn = QPushButton("Upload")
        upload_btn.setObjectName("primary")
        upload_btn.clicked.connect(self.upload_cover)
        action_bar.addWidget(upload_btn)

        if self.current_cover_data:
            resize_layout = QHBoxLayout()
            resize_layout.setSpacing(8)

            self.resize_combo = QComboBox()
            for size in range(500, 1001, 100):
                self.resize_combo.addItem(f"{size}×{size}", size)
            self.resize_combo.setCurrentText(f"{DEFAULT_COVER_SIZE}×{DEFAULT_COVER_SIZE}")
            self.resize_combo.setMinimumWidth(100)
            resize_layout.addWidget(self.resize_combo)

            resize_btn = QPushButton("Resize")
            resize_btn.setObjectName("secondary")
            resize_btn.clicked.connect(self.resize_cover)
            resize_layout.addWidget(resize_btn)

            action_bar.addLayout(resize_layout)

            remove_btn = QPushButton("Remove")
            remove_btn.setObjectName("secondary")
            remove_btn.clicked.connect(self.remove_cover)
            action_bar.addWidget(remove_btn)

        action_bar.addStretch()
        layout.addLayout(action_bar)

    def update_cover_display(self):
        if self.current_cover_data:
            image = QImage.fromData(self.current_cover_data)
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                scaled = pixmap.scaled(260, 260, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.cover_label.setPixmap(scaled)
            else:
                self.cover_label.setText("Failed to load cover")
        else:
            self.cover_label.setText("No cover art")

    def upload_cover(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Cover Image",
            "",
            "Images (*.jpg *.jpeg *.png *.webp)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "rb") as f:
                image_data = f.read()

            prepared = prepare_cover_image(BytesIO(image_data), DEFAULT_COVER_SIZE, DEFAULT_COVER_SIZE, resize=True)
            embed_cover(self.audio_info.path, prepared)

            self.current_cover_data = prepared
            self.update_cover_display()
            self.cover_changed.emit()

            QMessageBox.information(self, "Success", "Cover art embedded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to embed cover: {str(e)}")

    def resize_cover(self):
        if not self.current_cover_data:
            return

        size = self.resize_combo.currentData()

        try:
            resized = resize_cover_image(self.current_cover_data, size, size)
            embed_cover(self.audio_info.path, resized)

            self.current_cover_data = resized
            self.update_cover_display()
            self.cover_changed.emit()

            QMessageBox.information(self, "Success", f"Cover resized to {size}×{size}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to resize cover: {str(e)}")

    def remove_cover(self):
        if not self.current_cover_data:
            return

        reply = QMessageBox.question(
            self,
            "Confirm",
            "Remove cover art from this file?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            remove_cover(self.audio_info.path)
            self.current_cover_data = None
            self.update_cover_display()
            self.cover_changed.emit()

            QMessageBox.information(self, "Success", "Cover art removed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove cover: {str(e)}")
