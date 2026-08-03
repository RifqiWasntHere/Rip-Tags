from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox,
    QGridLayout, QLabel, QScrollArea, QWidget
)
from PySide6.QtCore import Qt

from rip_tags.metadata import to_display_name
from rip_tags.tags import ALL_SUPPORTED_TAGS, RECOMMENDED_TAGS
from rip_tags.ui.components import Card


TAG_GROUPS = {
    "Core Tags": [
        "title", "artist", "album", "albumartist", "date",
        "genre", "tracknumber", "disk", "cover",
    ],
    "Secondary Tags": [
        "composer", "copyright", "compilation",
    ],
    "Technical / Metadata": [
        "encoder", "lyrics", "comment", "grouping",
    ],
    "iTunes / Store": [
        "purchase date", "apple id", "catalog id",
        "storefront", "media type", "explicit rating", "gapless playback",
    ],
    "Sorting Tags": [
        "sort title", "sort artist", "sort album",
        "sort albumartist", "sort composer",
    ],
}


class PreferencesDialog(QDialog):
    def __init__(self, current_prefs: dict[str, bool], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clean Preferences")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self.prefs = current_prefs.copy()
        self.checkboxes: dict[str, QCheckBox] = {}

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        header = QLabel("Choose which tags you want to keep during the cleaning process.")
        header.setWordWrap(True)
        header.setObjectName("subtitle")
        layout.addWidget(header)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        select_all_btn = QPushButton("Select All")
        select_all_btn.setObjectName("secondary")
        select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.setObjectName("secondary")
        deselect_all_btn.clicked.connect(self.deselect_all)
        button_layout.addWidget(deselect_all_btn)

        button_layout.addStretch()

        recommended_btn = QPushButton("Recommended")
        recommended_btn.setObjectName("primary")
        recommended_btn.clicked.connect(self.set_recommended)
        button_layout.addWidget(recommended_btn)

        layout.addLayout(button_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background: transparent;")

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(12)

        for group_name, tags in TAG_GROUPS.items():
            group_card = Card()
            group_card.layout.setContentsMargins(16, 16, 16, 16)

            group_header = QLabel(group_name)
            group_header.setObjectName("section-title")
            group_card.layout.addWidget(group_header)

            grid = QGridLayout()
            grid.setSpacing(8)

            cols = 2
            for idx, tag in enumerate(tags):
                row = idx // cols
                col = idx % cols

                display_name = to_display_name(tag)
                checkbox = QCheckBox(display_name)
                checkbox.setChecked(self.prefs.get(tag, True))
                checkbox.stateChanged.connect(lambda state, t=tag: self.on_checkbox_changed(t, state))
                self.checkboxes[tag] = checkbox

                grid.addWidget(checkbox, row, col)

            group_card.layout.addLayout(grid)
            scroll_layout.addWidget(group_card)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area, 1)

        button_box = QHBoxLayout()
        button_box.setSpacing(8)
        button_box.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
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
