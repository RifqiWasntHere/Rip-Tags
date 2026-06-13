from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from mutagen.flac import FLAC
from mutagen.mp4 import MP4, MP4Tags

SUPPORTED_SUFFIXES = {".m4a", ".mp4", ".flac"}

DEFAULT_KEEP_TAGS = {
    "title", "artist", "album", "date", "tracknumber", "genre",
    "albumartist", "copyright", "composer", "encoder", "cover"
}


@dataclass
class CleanResult:
    path: Path
    status: str
    kept: list[str]
    removed: list[str]
    error: str = ""


def clean_file(path: Path, dry_run=False, log_func=print, keep_tags=None):
    if keep_tags is None:
        keep_tags = DEFAULT_KEEP_TAGS

    try:
        path = Path(path)

        if path.suffix.lower() in {".m4a", ".mp4"}:
            result = _clean_mp4(path, dry_run, keep_tags)
        elif path.suffix.lower() == ".flac":
            result = _clean_flac(path, dry_run, keep_tags)
        else:
            result = CleanResult(path, "skipped", [], [])

        _log_result(result, dry_run, log_func)
        return result

    except Exception as e:
        result = CleanResult(Path(path), "failed", [], [], str(e))
        _log_result(result, dry_run, log_func)
        return result


def scan(folder, dry_run=False, log_func=print, keep_tags=None):
    results = []

    for file in Path(folder).rglob("*"):
        if not file.is_file():
            continue

        if file.name.startswith("._"):
            continue

        if file.suffix.lower() in SUPPORTED_SUFFIXES:
            results.append(clean_file(file, dry_run=dry_run, log_func=log_func, keep_tags=keep_tags))

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


def _clean_mp4(path: Path, dry_run: bool, keep_tags: set[str]) -> CleanResult:
    audio = MP4(path)

    if audio.tags is None:
        return CleanResult(path, "skipped", [], [])

    original = dict(audio.tags)

    from rip_tags.metadata import to_human_tag
    kept = {}
    for key, value in original.items():
        human_name = to_human_tag(key)
        if human_name in keep_tags:
            kept[key] = value

    if "\xa9day" in kept:
        kept["\xa9day"] = _shorten_year(kept["\xa9day"])

    removed = sorted(set(original) - set(kept))

    if not dry_run and removed:
        audio.tags = MP4Tags()

        for key, value in kept.items():
            audio.tags[key] = value

        audio.save()

    status = "would_clean" if dry_run else "cleaned"
    if not removed:
        status = "unchanged"

    kept_human = sorted(to_human_tag(key) for key in kept)
    removed_human = sorted(to_human_tag(key) for key in removed)

    return CleanResult(path, status, kept_human, removed_human)


def _clean_flac(path: Path, dry_run: bool, keep_tags: set[str]) -> CleanResult:
    audio = FLAC(path)

    if audio.tags is None:
        return CleanResult(path, "skipped", [], [])

    original = dict(audio.tags)

    kept = {}
    for key, value in original.items():
        if key.lower() in keep_tags:
            kept[key] = value

    for key in ("date", "year"):
        if key in kept:
            kept[key] = _shorten_year(kept[key])

    removed = sorted(key for key in original if key not in kept)

    if not dry_run and removed:
        audio.tags.clear()

        for key, value in kept.items():
            audio.tags[key] = value

        audio.save()

    status = "would_clean" if dry_run else "cleaned"
    if not removed:
        status = "unchanged"

    kept_human = sorted(key.lower() for key in kept)
    removed_human = sorted(key.lower() for key in removed)

    return CleanResult(path, status, kept_human, removed_human)
