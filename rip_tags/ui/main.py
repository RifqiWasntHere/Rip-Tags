import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QStackedWidget, QStatusBar
from PySide6.QtCore import Qt

from rip_tags import __version__
from rip_tags.ui.styles import APP_STYLE
from rip_tags.ui.sidebar import SidebarWidget
from rip_tags.ui.batch_cleaner import BatchCleanerWidget
from rip_tags.ui.file_viewer import FileViewerWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle(f"Rip Tags {__version__}")
        self.resize(1400, 900)
        self.setMinimumSize(1400, 900)
        
        icon_path = Path(__file__).parent.parent.parent / "Rip-Tags.png"
        if icon_path.exists():
            from PySide6.QtGui import QIcon
            self.setWindowIcon(QIcon(str(icon_path)))
        
        self.status_bar = QStatusBar()
        self.status_bar.showMessage(f"Ready  ·  v{__version__}")
        self.setStatusBar(self.status_bar)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        self.setCentralWidget(splitter)
        
        self.sidebar = SidebarWidget(icon_path)
        self.sidebar.setFixedWidth(280)
        self.sidebar.setMinimumWidth(280)
        self.sidebar.setMaximumWidth(280)
        splitter.addWidget(self.sidebar)
        
        self.stack = QStackedWidget()
        splitter.addWidget(self.stack)
        
        self.batch_cleaner = BatchCleanerWidget(self.status_bar)
        self.stack.addWidget(self.batch_cleaner)
        
        self.file_viewer = FileViewerWidget()
        self.stack.addWidget(self.file_viewer)
        
        self.stack.setCurrentWidget(self.batch_cleaner)
        
        self.sidebar.folder_selected.connect(self.batch_cleaner.set_folder)
        self.sidebar.file_selected.connect(self.show_file_viewer)
        self.batch_cleaner.file_selected.connect(self.show_file_viewer)
        self.sidebar.preferences_requested.connect(self.batch_cleaner.show_preferences)
        self.file_viewer.back_requested.connect(self.show_batch_cleaner)
        
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        splitter.setSizes([280, 1120])
    
    def show_file_viewer(self, file_path: str):
        self.file_viewer.set_file(file_path)
        self.stack.setCurrentWidget(self.file_viewer)
    
    def show_batch_cleaner(self):
        self.stack.setCurrentWidget(self.batch_cleaner)


def run_app():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
