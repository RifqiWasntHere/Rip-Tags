from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from mutagen.flac import FLAC
from mutagen.mp4 import MP4, MP4Tags

KEEP_MP4 = {
    "\xa9nam",
    "\xa9ART",
    "\xa9alb",
    "\xa9day",
    "trkn",
    "\xa9gen",
    "aART",
    "cprt",
    "\xa9wrt",
    "\xa9too",
    "covr",
}

KEEP_FLAC = {
    "title",
    "artist",
    "album",
    "date",
    "year",
    "tracknumber",
    "genre",
    "albumartist",
    "copyright",
    "composer",
    "encodedby",
}

SUPPORTED_SUFFIXES = {".m4a", ".mp4", ".flac"}


@dataclass
class CleanResult:
    path: Path
    status: str
    kept: list[str]
    removed: list[str]
    error: str = ""


def clean_file(path: Path, dry_run=False, log_func=print):
    try:
        path = Path(path)

        if path.suffix.lower() in {".m4a", ".mp4"}:
            result = _clean_mp4(path, dry_run)
        elif path.suffix.lower() == ".flac":
            result = _clean_flac(path, dry_run)
        else:
            result = CleanResult(path, "skipped", [], [])

        _log_result(result, dry_run, log_func)
        return result

    except Exception as e:
        result = CleanResult(Path(path), "failed", [], [], str(e))
        _log_result(result, dry_run, log_func)
        return result


def scan(folder, dry_run=False, log_func=print):
    results = []

    for file in Path(folder).rglob("*"):
        if not file.is_file():
            continue

        if file.name.startswith("._"):
            continue

        if file.suffix.lower() in SUPPORTED_SUFFIXES:
            results.append(clean_file(file, dry_run=dry_run, log_func=log_func))

    return [result for result in results if result is not None]


def _shorten_year(value):
    if isinstance(value, list) and value:
        return [str(value[0])[:4]]

    if isinstance(value, str):
        return value[:4]

    return value


def _log_result(result: CleanResult, dry_run: bool, log_func: Callable[[str], None]):
    if result.status == "skipped":
        return

    if result.status == "failed":
        log_func(f"Failed: {result.path} -> {result.error}")
        return

    if dry_run:
        log_func(f"\n{result.path.name}")
        log_func("Remove:")
        if result.removed:
            for key in result.removed:
                log_func(f"  {key}")
        else:
            log_func("  Nothing")
        return

    if result.status == "unchanged":
        log_func(f"Unchanged: {result.path.name}")
        return

    log_func(f"Cleaned: {result.path.name}")


def _clean_mp4(path: Path, dry_run: bool) -> CleanResult:
    audio = MP4(path)

    if audio.tags is None:
        return CleanResult(path, "skipped", [], [])

    original = dict(audio.tags)
    kept = {key: value for key, value in original.items() if key in KEEP_MP4}

    if "\xa9day" in kept:
        kept["\xa9day"] = _shorten_year(kept["\xa9day"])

    removed = sorted(set(original) - KEEP_MP4)

    if not dry_run and removed:
        audio.tags = MP4Tags()

        for key, value in kept.items():
            audio.tags[key] = value

        audio.save()

    status = "would_clean" if dry_run else "cleaned"
    if not removed:
        status = "unchanged"

    return CleanResult(path, status, sorted(kept), removed)


def _clean_flac(path: Path, dry_run: bool) -> CleanResult:
    audio = FLAC(path)

    if audio.tags is None:
        return CleanResult(path, "skipped", [], [])

    original = dict(audio.tags)
    kept = {
        key: value
        for key, value in original.items()
        if key.lower() in KEEP_FLAC
    }

    for key in ("date", "year"):
        if key in kept:
            kept[key] = _shorten_year(kept[key])

    removed = sorted(key for key in original if key.lower() not in KEEP_FLAC)

    if not dry_run and removed:
        audio.tags.clear()

        for key, value in kept.items():
            audio.tags[key] = value

        audio.save()

    status = "would_clean" if dry_run else "cleaned"
    if not removed:
        status = "unchanged"

    return CleanResult(path, status, sorted(kept), removed)
