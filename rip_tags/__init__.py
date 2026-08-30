from rip_tags.cleaner import CleanResult, SUPPORTED_SUFFIXES, clean_file, scan
from rip_tags.tags import ALL_SUPPORTED_TAGS, RECOMMENDED_TAGS

__version__ = "1.0.1-beta.2"

__all__ = [
    "CleanResult",
    "SUPPORTED_SUFFIXES",
    "clean_file",
    "scan",
    "ALL_SUPPORTED_TAGS",
    "RECOMMENDED_TAGS",
    "__version__",
]
