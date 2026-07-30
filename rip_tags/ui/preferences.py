from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox,
    QGridLayout, QGroupBox, QLabel
)
from PySide6.QtCore import Qt

from rip_tags.tags import ALL_SUPPORTED_TAGS, RECOMMENDED_TAGS


class PreferencesDialog(QDialog):
    def __init__(self, current_prefs: dict[str, bool], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clean Preferences")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.prefs = current_prefs.copy()
        self.checkboxes: dict[str, QCheckBox] = {}
        
        layout = QVBoxLayout(self)
        
        header = QLabel("Choose which tags you want to keep during the cleaning process.")
        header.setWordWrap(True)
        layout.addWidget(header)
        
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all)
        button_layout.addWidget(deselect_all_btn)
        
        recommended_btn = QPushButton("Recommended")
        recommended_btn.setObjectName("primary")
        recommended_btn.clicked.connect(self.set_recommended)
        button_layout.addWidget(recommended_btn)
        
        layout.addLayout(button_layout)
        
        group = QGroupBox("Tags to Keep")
        grid = QGridLayout(group)
        
        half = (len(ALL_SUPPORTED_TAGS) + 1) // 2
        for idx, tag in enumerate(ALL_SUPPORTED_TAGS):
            row = idx % half
            col = idx // half
            
            display_name = tag.replace("_", " ").title()
            checkbox = QCheckBox(display_name)
            checkbox.setChecked(self.prefs.get(tag, True))
            checkbox.stateChanged.connect(lambda state, t=tag: self.on_checkbox_changed(t, state))
            self.checkboxes[tag] = checkbox
            
            grid.addWidget(checkbox, row, col)
        
        layout.addWidget(group)
        
        button_box = QHBoxLayout()
        button_box.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_box.addWidget(cancel_btn)
        
        apply_btn = QPushButton("Apply")
        apply_btn.setObjectName("primary")
        apply_btn.clicked.connect(self.accept)
        button_box.addWidget(apply_btn)
        
        layout.addLayout(button_box)
    
    def on_checkbox_changed(self, tag: str, state: int):
        self.prefs[tag] = (state == Qt.Checked)
    
    def select_all(self):
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)
    
    def deselect_all(self):
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
    
    def set_recommended(self):
        for tag, checkbox in self.checkboxes.items():
            checkbox.setChecked(tag in RECOMMENDED_TAGS)
    
    def get_preferences(self) -> dict[str, bool]:
        return self.prefs
