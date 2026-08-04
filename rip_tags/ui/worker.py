from pathlib import Path
from typing import Optional

from PySide6.QtCore import QThread, Signal

from rip_tags.cleaner import SUPPORTED_SUFFIXES, CleanResult, clean_file, scan


class ScanWorker(QThread):
    finished = Signal(list)
    progress = Signal(str)

    def __init__(self, folder: Path, keep_tags: Optional[set] = None, dry_run: bool = True):
        super().__init__()
        self.folder = folder
        self.keep_tags = keep_tags
        self.dry_run = dry_run

    def run(self):
        def log_func(msg):
            self.progress.emit(msg)

        results = scan(self.folder, dry_run=self.dry_run, log_func=log_func, keep_tags=self.keep_tags)
        self.finished.emit(results)


class CleanWorker(QThread):
    finished = Signal(list)
    progress = Signal(str)
    file_done = Signal(object)

    def __init__(self, files: list, keep_tags: Optional[set] = None, dry_run: bool = True):
        super().__init__()
        self.files = files
        self.keep_tags = keep_tags
        self.dry_run = dry_run

    def run(self):
        results = []
        for file in self.files:
            def log_func(msg):
                self.progress.emit(msg)

            result = clean_file(file, dry_run=self.dry_run, log_func=log_func, keep_tags=self.keep_tags)
            results.append(result)
            self.file_done.emit(result)

        self.finished.emit(results)
