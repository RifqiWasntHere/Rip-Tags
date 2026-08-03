APP_STYLE = """
QMainWindow {
    background-color: #121212;
}

QWidget {
    background-color: #121212;
    color: #e8e8e8;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 13px;
}

QSplitter::handle {
    background-color: #1e1e1e;
}

QSplitter::handle:horizontal {
    width: 1px;
}

QPushButton {
    background-color: #2a2a2a;
    border: 1px solid #3a3a3a;
    border-radius: 8px;
    padding: 8px 16px;
    color: #e8e8e8;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #333333;
    border-color: #4a4a4a;
}

QPushButton:pressed {
    background-color: #222222;
}

QPushButton:disabled {
    background-color: #1e1e1e;
    color: #666666;
    border-color: #2a2a2a;
}

QPushButton#primary {
    background-color: #4f9cf7;
    border-color: #4f9cf7;
    color: #ffffff;
}

QPushButton#primary:hover {
    background-color: #6bb3ff;
    border-color: #6bb3ff;
}

QPushButton#primary:pressed {
    background-color: #3d8ae6;
}

QPushButton#primary:disabled {
    background-color: #2a4a6d;
    border-color: #2a4a6d;
}

QPushButton#secondary {
    background-color: transparent;
    border-color: #3a3a3a;
}

QPushButton#secondary:hover {
    background-color: #2a2a2a;
}

QPushButton#icon-only {
    padding: 6px 10px;
    min-width: 32px;
    min-height: 32px;
}

QPushButton#flat {
    background-color: transparent;
    border: none;
    padding: 4px 8px;
}

QPushButton#flat:hover {
    background-color: #2a2a2a;
}

QLineEdit, QSpinBox, QComboBox {
    background-color: #1e1e1e;
    border: 1px solid #3a3a3a;
    border-radius: 8px;
    padding: 8px 12px;
    color: #e8e8e8;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border-color: #4f9cf7;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #1e1e1e;
    border: 1px solid #3a3a3a;
    border-radius: 8px;
    selection-background-color: #4f9cf7;
    padding: 4px;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #4a4a4a;
    border-radius: 4px;
    background-color: #1e1e1e;
}

QCheckBox::indicator:checked {
    background-color: #4f9cf7;
    border-color: #4f9cf7;
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgNEw0LjUgNy41TDExIDEiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PC9zdmc+);
}

QCheckBox::indicator:hover {
    border-color: #4f9cf7;
}

QTreeWidget, QListWidget, QTableWidget {
    background-color: #1a1a1a;
    border: 1px solid #2e2e2e;
    border-radius: 12px;
    alternate-background-color: #1e1e1e;
    outline: none;
    padding: 4px;
}

QTreeWidget::item, QListWidget::item, QTableWidget::item {
    padding: 8px 4px;
    border: none;
    border-radius: 6px;
}

QTreeWidget::item:hover, QListWidget::item:hover, QTableWidget::item:hover {
    background-color: #252525;
}

QTreeWidget::item:selected, QListWidget::item:selected, QTableWidget::item:selected {
    background-color: transparent;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #1a1a1a;
    border: none;
    border-right: 1px solid #2e2e2e;
    border-bottom: 1px solid #2e2e2e;
    padding: 10px 12px;
    color: #a0a0a0;
    font-weight: 500;
    font-size: 12px;
}

QHeaderView::section:first {
    border-top-left-radius: 12px;
}

QHeaderView::section:last {
    border-right: none;
    border-top-right-radius: 12px;
}

QScrollBar:vertical {
    background-color: #121212;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #3a3a3a;
    min-height: 20px;
    border-radius: 5px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4a4a4a;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #121212;
    height: 10px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #3a3a3a;
    min-width: 20px;
    border-radius: 5px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #4a4a4a;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QLabel#title {
    font-size: 20px;
    font-weight: 600;
    color: #ffffff;
}

QLabel#subtitle {
    font-size: 13px;
    color: #a0a0a0;
}

QLabel#section-title {
    font-size: 15px;
    font-weight: 600;
    color: #ffffff;
}

QLabel#metric-value {
    font-size: 28px;
    font-weight: 600;
    color: #ffffff;
}

QLabel#metric-label {
    font-size: 11px;
    color: #808080;
    font-weight: 500;
}

QLabel#empty-title {
    font-size: 16px;
    font-weight: 600;
    color: #e8e8e8;
}

QLabel#empty-subtitle {
    font-size: 13px;
    color: #a0a0a0;
}

QLabel#badge {
    background-color: #2a2a2a;
    border: 1px solid #3a3a3a;
    border-radius: 6px;
    padding: 4px 10px;
    color: #a0a0a0;
    font-size: 12px;
    font-weight: 500;
}

QGroupBox {
    border: 1px solid #2e2e2e;
    border-radius: 12px;
    margin-top: 16px;
    padding-top: 20px;
    font-weight: 500;
    background-color: #1a1a1a;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    color: #e8e8e8;
}

QProgressBar {
    border: 1px solid #2e2e2e;
    border-radius: 6px;
    text-align: center;
    background-color: #1e1e1e;
    height: 24px;
    color: #e8e8e8;
}

QProgressBar::chunk {
    background-color: #4f9cf7;
    border-radius: 5px;
}

QTabWidget::pane {
    border: 1px solid #2e2e2e;
    border-radius: 12px;
    background-color: #1a1a1a;
}

QTabBar::tab {
    background-color: #1e1e1e;
    border: 1px solid #2e2e2e;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    color: #a0a0a0;
}

QTabBar::tab:selected {
    background-color: #1a1a1a;
    border-bottom-color: #1a1a1a;
    color: #ffffff;
}

QTabBar::tab:hover {
    background-color: #252525;
}

QDialog {
    background-color: #121212;
}

QDialogButtonBox QPushButton {
    min-width: 100px;
}

QStatusBar {
    background-color: #1a1a1a;
    border-top: 1px solid #2e2e2e;
    color: #a0a0a0;
    padding: 4px 16px;
    font-size: 12px;
}

QStatusBar::item {
    border: none;
}

QRadioButton {
    spacing: 8px;
    color: #e8e8e8;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #4a4a4a;
    border-radius: 9px;
    background-color: #1e1e1e;
}

QRadioButton::indicator:checked {
    background-color: #4f9cf7;
    border-color: #4f9cf7;
}

QRadioButton::indicator:hover {
    border-color: #4f9cf7;
}

QToolTip {
    background-color: #2a2a2a;
    border: 1px solid #3a3a3a;
    color: #e8e8e8;
    padding: 6px 10px;
    border-radius: 6px;
}

QTextEdit {
    background-color: #1a1a1a;
    border: 1px solid #2e2e2e;
    border-radius: 12px;
    padding: 8px;
    color: #e8e8e8;
}

QFrame#card {
    background-color: #1a1a1a;
    border: 1px solid #2e2e2e;
    border-radius: 12px;
}

QFrame#card-header {
    background-color: #1e1e1e;
    border: 1px solid #2e2e2e;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    border-bottom: none;
}
"""
