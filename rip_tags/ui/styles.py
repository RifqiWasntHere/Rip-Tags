APP_STYLE = """
QMainWindow {
    background-color: #1e1e1e;
}

QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 13px;
}

QSplitter::handle {
    background-color: #2d2d2d;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QPushButton {
    background-color: #3d3d3d;
    border: 1px solid #4d4d4d;
    border-radius: 4px;
    padding: 6px 12px;
    color: #e0e0e0;
}

QPushButton:hover {
    background-color: #4d4d4d;
    border-color: #5d5d5d;
}

QPushButton:pressed {
    background-color: #2d2d2d;
}

QPushButton:disabled {
    background-color: #2d2d2d;
    color: #6d6d6d;
    border-color: #3d3d3d;
}

QPushButton#primary {
    background-color: #0078d4;
    border-color: #0078d4;
    color: white;
}

QPushButton#primary:hover {
    background-color: #1088de;
}

QPushButton#primary:pressed {
    background-color: #006cbd;
}

QPushButton#primary:disabled {
    background-color: #2d4a6d;
    border-color: #2d4a6d;
}

QLineEdit, QSpinBox, QComboBox {
    background-color: #2d2d2d;
    border: 1px solid #4d4d4d;
    border-radius: 4px;
    padding: 4px 8px;
    color: #e0e0e0;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border-color: #0078d4;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    border: 1px solid #4d4d4d;
    selection-background-color: #0078d4;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #4d4d4d;
    border-radius: 3px;
    background-color: #2d2d2d;
}

QCheckBox::indicator:checked {
    background-color: #0078d4;
    border-color: #0078d4;
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgNEw0LjUgNy41TDExIDEiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PC9zdmc+);
}

QTreeWidget, QListWidget, QTableWidget {
    background-color: #252525;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    alternate-background-color: #2a2a2a;
    outline: none;
}

QTreeWidget::item, QListWidget::item, QTableWidget::item {
    padding: 4px;
    border: none;
}

QTreeWidget::item:hover, QListWidget::item:hover, QTableWidget::item:hover {
    background-color: #2d2d2d;
}

QTreeWidget::item:selected, QListWidget::item:selected, QTableWidget::item:selected {
    background-color: #0078d4;
}

QHeaderView::section {
    background-color: #2d2d2d;
    border: none;
    border-right: 1px solid #3d3d3d;
    border-bottom: 1px solid #3d3d3d;
    padding: 6px 8px;
    color: #b0b0b0;
    font-weight: 500;
}

QHeaderView::section:first {
    border-top-left-radius: 4px;
}

QHeaderView::section:last {
    border-right: none;
    border-top-right-radius: 4px;
}

QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 12px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #4d4d4d;
    min-height: 20px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5d5d5d;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #1e1e1e;
    height: 12px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #4d4d4d;
    min-width: 20px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #5d5d5d;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QLabel#title {
    font-size: 18px;
    font-weight: 600;
    color: #ffffff;
}

QLabel#subtitle {
    font-size: 14px;
    color: #b0b0b0;
}

QLabel#metric-value {
    font-size: 24px;
    font-weight: 600;
    color: #ffffff;
}

QLabel#metric-label {
    font-size: 11px;
    color: #808080;
}

QGroupBox {
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 500;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}

QProgressBar {
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    text-align: center;
    background-color: #2d2d2d;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #0078d4;
    border-radius: 3px;
}

QTabWidget::pane {
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    background-color: #252525;
}

QTabBar::tab {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #3d3d3d;
    border-bottom-color: #3d3d3d;
}

QTabBar::tab:hover {
    background-color: #3d3d3d;
}

QDialog {
    background-color: #1e1e1e;
}

QDialogButtonBox QPushButton {
    min-width: 80px;
}

QToolTip {
    background-color: #2d2d2d;
    border: 1px solid #4d4d4d;
    color: #e0e0e0;
    padding: 4px 8px;
    border-radius: 4px;
}
"""
