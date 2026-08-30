from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox,
    QGridLayout, QLabel, QScrollArea, QWidget, QLineEdit
)
from PySide6.QtCore import Qt

from rip_tags.metadata import to_display_name
from rip_tags.tags import ALL_SUPPORTED_TAGS, RECOMMENDED_TAGS
from rip_tags.ui.components import Card


TAG_GROUPS = {
    "Core Tags": [
        "title", "artist", "album", "albumartist", "date",
        "genre", "tracknumber", "tracktotal", "disk", "disctotal", "cover",
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
}


class PreferencesDialog(QDialog):
    def __init__(self, current_prefs: dict[str, bool], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clean Preferences")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self.prefs = current_prefs.copy()
        self.checkboxes: dict[str, QCheckBox] = {}
        self.group_cards: dict[str, Card] = {}

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        header = QLabel("Choose which tags you want to keep during the cleaning process.")
        header.setWordWrap(True)
        header.setObjectName("subtitle")
        layout.addWidget(header)

        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search tags...")
        self.search_edit.textChanged.connect(self.filter_tags)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)

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

        reset_btn = QPushButton("Reset")
        reset_btn.setObjectName("secondary")
        reset_btn.clicked.connect(self.reset)
        button_layout.addWidget(reset_btn)

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
            group_card.layout.setSpacing(12)
            self.group_cards[group_name] = group_card

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

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)

        self.count_label = QLabel()
        self.count_label.setObjectName("subtitle")
        bottom_layout.addWidget(self.count_label)
        self._update_count()

        bottom_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(cancel_btn)

        apply_btn = QPushButton("Apply")
        apply_btn.setObjectName("primary")
        apply_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(apply_btn)

        layout.addLayout(bottom_layout)

    def on_checkbox_changed(self, tag: str, state: int):
        self.prefs[tag] = (state == Qt.Checked)
        self._update_count()

    def select_all(self):
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)
        self._update_count()

    def deselect_all(self):
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
        self._update_count()

    def reset(self):
        for tag, checkbox in self.checkboxes.items():
            checkbox.setChecked(self.prefs.get(tag, True))
        self._update_count()

    def set_recommended(self):
        for tag, checkbox in self.checkboxes.items():
            checkbox.setChecked(tag in RECOMMENDED_TAGS)
        self._update_count()

    def filter_tags(self, text: str):
        text = text.lower()
        for group_name, tags in TAG_GROUPS.items():
            group_visible = False
            for tag in tags:
                checkbox = self.checkboxes.get(tag)
                if checkbox:
                    display = to_display_name(tag).lower()
                    visible = text in display or text in tag.lower()
                    checkbox.setVisible(visible)
                    if visible:
                        group_visible = True
            group_card = self.group_cards.get(group_name)
            if group_card:
                group_card.setVisible(group_visible)

    def _update_count(self):
        keep_count = sum(1 for keep in self.prefs.values() if keep)
        total = len(self.prefs)
        self.count_label.setText(f"{keep_count} of {total} tags will be kept")

    def get_preferences(self) -> dict[str, bool]:
        return self.prefs
