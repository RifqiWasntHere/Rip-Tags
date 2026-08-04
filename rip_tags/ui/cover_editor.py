from pathlib import Path
from io import BytesIO
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QComboBox, QMessageBox, QButtonGroup, QRadioButton, QDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap

from rip_tags.metadata import AudioInfo
from rip_tags.cover_art import (
    DEFAULT_COVER_SIZE,
    embed_cover,
    remove_cover,
    prepare_cover_image,
    resize_cover_image,
    get_cover_dimensions,
)
from rip_tags.ui.components import Card


class CoverEditorWidget(QWidget):
    cover_changed = Signal()

    def __init__(self, audio_info: AudioInfo, parent=None):
        super().__init__(parent)
        self.audio_info = audio_info
        self.current_cover_data: Optional[bytes] = audio_info.cover_data
        self.cover_size = DEFAULT_COVER_SIZE

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.cover_card = Card()
        self.cover_card.layout.setContentsMargins(16, 16, 16, 16)
        self.cover_card.layout.setSpacing(12)

        self.cover_label = QLabel()
        self.cover_label.setFixedSize(500, 500)
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setStyleSheet("background: #1e1e1e; border-radius: 12px;")
        self.update_cover_display()
        self.cover_card.layout.addWidget(self.cover_label)

        self.setAcceptDrops(True)

        self.cover_info_label = QLabel()
        self.cover_info_label.setObjectName("subtitle")
        self.cover_card.layout.addWidget(self.cover_info_label)
        # self._update_cover_info()

        layout.addWidget(self.cover_card)

        action_bar = QHBoxLayout()
        action_bar.setSpacing(8)

        upload_btn = QPushButton("Upload")
        upload_btn.setObjectName("primary")
        upload_btn.clicked.connect(self.upload_cover)
        action_bar.addWidget(upload_btn)

        resize_layout = QHBoxLayout()
        resize_layout.setSpacing(8)

        self.resize_combo = QComboBox()
        for size in range(500, 1001, 100):
            self.resize_combo.addItem(f"{size}×{size}", size)
        self.resize_combo.setCurrentText(f"{DEFAULT_COVER_SIZE}×{DEFAULT_COVER_SIZE}")
        self.resize_combo.setMinimumWidth(100)
        self.resize_combo.setEnabled(self.current_cover_data is not None)
        resize_layout.addWidget(self.resize_combo)

        resize_btn = QPushButton("Resize")
        resize_btn.setObjectName("secondary")
        resize_btn.clicked.connect(self.resize_cover)
        resize_btn.setEnabled(self.current_cover_data is not None)
        resize_layout.addWidget(resize_btn)
        self.resize_btn = resize_btn

        action_bar.addLayout(resize_layout)

        remove_btn = QPushButton("Remove")
        remove_btn.setObjectName("secondary")
        remove_btn.clicked.connect(self.remove_cover)
        remove_btn.setEnabled(self.current_cover_data is not None)
        action_bar.addWidget(remove_btn)
        self.remove_btn = remove_btn

        action_bar.addStretch()
        layout.addLayout(action_bar)

    def update_cover_display(self):
        if self.current_cover_data:
            image = QImage.fromData(self.current_cover_data)
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                scaled = pixmap.scaled(480, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.cover_label.setPixmap(scaled)
            else:
                self.cover_label.setText("Failed to load cover")
        else:
            self.cover_label.setText("No cover art")

    def _update_cover_info(self):
        if self.current_cover_data:
            try:
                width, height = get_cover_dimensions(self.current_cover_data)
                size_kb = len(self.current_cover_data) / 1024
                self.cover_info_label.setText(f"{width}×{height}  •  {size_kb:.1f} KB")
            except Exception:
                self.cover_info_label.setText("Cover art present")
        else:
            # self.cover_info_label.setText("No cover art")
            return

    def _set_cover_controls_enabled(self, enabled: bool):
        self.resize_combo.setEnabled(enabled)
        self.resize_btn.setEnabled(enabled)
        self.remove_btn.setEnabled(enabled)

    def upload_cover(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Cover Image",
            "",
            "Images (*.jpg *.jpeg *.png *.webp)"
        )

        if not file_path:
            return

        action = "Replace" if self.current_cover_data else "Add"
        accepted, resize = self._confirm_cover_embed(
            f"{action} Cover Art",
            f"Resize uploaded cover for {self.audio_info.path.name}:",
            action
        )
        if not accepted:
            return

        self._embed_image(file_path, resize)

    def _confirm_cover_embed(self, title: str, message: str, action: str) -> tuple[bool, bool]:
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.setSpacing(12)

        dialog_layout.addWidget(QLabel(message))

        group = QButtonGroup(dialog)
        resize_radio = QRadioButton("500×500 (recommended)")
        original_radio = QRadioButton("Keep original size")
        resize_radio.setChecked(True)
        group.addButton(resize_radio)
        group.addButton(original_radio)
        dialog_layout.addWidget(resize_radio)
        dialog_layout.addWidget(original_radio)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        ok_btn = QPushButton(action)
        ok_btn.setObjectName("primary")
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        dialog_layout.addLayout(btn_layout)

        dialog.setMinimumWidth(300)
        accepted = dialog.exec() == 1
        return accepted, resize_radio.isChecked()

    def _embed_image(self, file_path: str, resize: bool):
        try:
            with open(file_path, "rb") as f:
                image_data = f.read()

            width = DEFAULT_COVER_SIZE if resize else None
            height = DEFAULT_COVER_SIZE if resize else None
            if width and height:
                prepared = prepare_cover_image(BytesIO(image_data), width, height, resize=True)
            else:
                prepared = prepare_cover_image(BytesIO(image_data), resize=False)

            embed_cover(self.audio_info.path, prepared)

            self.current_cover_data = prepared
            self.update_cover_display()
            # self._update_cover_info()
            self._set_cover_controls_enabled(True)
            self.cover_changed.emit()

            QMessageBox.information(self, "Success", "Cover art embedded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to embed cover: {str(e)}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile() and self._is_image_file(url.toLocalFile()):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile() and self._is_image_file(url.toLocalFile()):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        file_path = None
        for url in event.mimeData().urls():
            candidate = url.toLocalFile()
            if self._is_image_file(candidate):
                file_path = candidate
                break

        if not file_path:
            event.ignore()
            return

        event.acceptProposedAction()

        action = "Replace" if self.current_cover_data else "Add"
        accepted, resize = self._confirm_cover_embed(
            f"{action} Cover Art",
            f"Use the dropped image to {action.lower()} the cover art for {self.audio_info.path.name}?",
            action
        )
        if accepted:
            self._embed_image(file_path, resize)

    def _is_image_file(self, file_path: str) -> bool:
        return Path(file_path).suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}

    def resize_cover(self):
        if not self.current_cover_data:
            return

        size = self.resize_combo.currentData()

        try:
            resized = resize_cover_image(self.current_cover_data, size, size)
            embed_cover(self.audio_info.path, resized)

            self.current_cover_data = resized
            self.update_cover_display()
            # self._update_cover_info()
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
            # self._update_cover_info()
            self._set_cover_controls_enabled(False)
            self.cover_changed.emit()

            QMessageBox.information(self, "Success", "Cover art removed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove cover: {str(e)}")
