from pathlib import Path
from io import BytesIO
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QComboBox, QCheckBox, QMessageBox
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
    get_cover_dimensions,
)


class CoverEditorWidget(QWidget):
    cover_changed = Signal()
    
    def __init__(self, audio_info: AudioInfo, parent=None):
        super().__init__(parent)
        self.audio_info = audio_info
        self.current_cover_data: Optional[bytes] = audio_info.cover_data
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.cover_label = QLabel()
        self.cover_label.setMinimumSize(200, 200)
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setStyleSheet("background: #252525; border: 1px solid #3d3d3d; border-radius: 4px;")
        self.update_cover_display()
        layout.addWidget(self.cover_label)
        
        upload_btn = QPushButton("Upload Cover")
        upload_btn.clicked.connect(self.upload_cover)
        layout.addWidget(upload_btn)
        
        if self.current_cover_data:
            resize_layout = QHBoxLayout()
            
            self.resize_combo = QComboBox()
            for size in range(500, 1001, 100):
                self.resize_combo.addItem(f"{size}x{size}", size)
            self.resize_combo.setCurrentText(f"{DEFAULT_COVER_SIZE}x{DEFAULT_COVER_SIZE}")
            resize_layout.addWidget(QLabel("Resize:"))
            resize_layout.addWidget(self.resize_combo)
            
            resize_btn = QPushButton("Resize")
            resize_btn.clicked.connect(self.resize_cover)
            resize_layout.addWidget(resize_btn)
            
            layout.addLayout(resize_layout)
            
            remove_btn = QPushButton("Remove Cover")
            remove_btn.clicked.connect(self.remove_cover)
            layout.addWidget(remove_btn)
    
    def update_cover_display(self):
        if self.current_cover_data:
            image = QImage.fromData(self.current_cover_data)
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                scaled = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
            
            QMessageBox.information(self, "Success", f"Cover resized to {size}x{size}.")
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
