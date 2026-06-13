from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from mutagen import File
from mutagen.flac import FLAC
from mutagen.mp4 import MP4


@dataclass
class AudioInfo:
    path: Path
    file_type: str
    duration: Optional[float]
    bitrate: Optional[int]
    sample_rate: Optional[int]
    bit_depth: Optional[int]
    channels: Optional[int]
    tags: dict[str, Any]
    cover_data: Optional[bytes] = None
    cover_mime: Optional[str] = None
    error: str = ""


def read_audio_info(path: Path) -> AudioInfo:
    path = Path(path)

    try:
        audio = File(path)

        if audio is None:
            return AudioInfo(path, "unknown", None, None, None, None, None, {}, error="Unsupported file")

        info = getattr(audio, "info", None)

        return AudioInfo(
            path=path,
            file_type=type(audio).__name__,
            duration=getattr(info, "length", None),
            bitrate=getattr(info, "bitrate", None),
            sample_rate=getattr(info, "sample_rate", None),
            bit_depth=getattr(info, "bits_per_sample", None),
            channels=getattr(info, "channels", None),
            tags=_read_tags(audio),
            cover_data=_read_cover_data(audio),
            cover_mime=_read_cover_mime(audio),
        )

    except Exception as e:
        return AudioInfo(path, "unknown", None, None, None, None, None, {}, error=str(e))


MP4_TAG_MAPPING = {
    "\xa9nam": "title",
    "\xa9ART": "artist",
    "\xa9alb": "album",
    "\xa9day": "date",
    "trkn": "tracknumber",
    "\xa9gen": "genre",
    "aART": "albumartist",
    "cprt": "copyright",
    "\xa9wrt": "composer",
    "\xa9too": "encoder",
    "covr": "cover",
    "\xa9lyr": "lyrics",
    "\xa9cmt": "comment",
    "\xa9grp": "grouping",
}


def to_human_tag(tag: str) -> str:
    # Exact match check
    if tag in MP4_TAG_MAPPING:
        return MP4_TAG_MAPPING[tag]
    # Case insensitive check
    if tag.lower() in MP4_TAG_MAPPING:
        return MP4_TAG_MAPPING[tag.lower()]
    # Normalize unmapped tags starting with copyright symbol
    if tag.startswith("\xa9"):
        return "©" + tag[1:]
    return tag


def _read_tags(audio) -> dict[str, Any]:
    if audio.tags is None:
        return {}

    return {
        to_human_tag(str(key)): _format_tag_value(value)
        for key, value in sorted(audio.tags.items(), key=lambda item: to_human_tag(str(item[0])).lower())
    }


def _format_tag_value(value):
    if isinstance(value, list):
        return ", ".join(_format_tag_value(item) for item in value)

    if isinstance(value, tuple):
        return ", ".join(_format_tag_value(item) for item in value)

    if isinstance(value, bytes):
        return f"<{len(value)} bytes>"

    return str(value)


def _read_cover_data(audio) -> Optional[bytes]:
    if isinstance(audio, FLAC) and audio.pictures:
        return audio.pictures[0].data

    if isinstance(audio, MP4) and audio.tags and "covr" in audio.tags:
        covers = audio.tags["covr"]
        if covers:
            return bytes(covers[0])

    return None


def _read_cover_mime(audio) -> Optional[str]:
    if isinstance(audio, FLAC) and audio.pictures:
        return audio.pictures[0].mime

    if isinstance(audio, MP4) and audio.tags and "covr" in audio.tags:
        covers = audio.tags["covr"]
        if not covers:
            return None

        imageformat = getattr(covers[0], "imageformat", None)
        if imageformat == 13:
            return "image/jpeg"
        if imageformat == 14:
            return "image/png"

    return None
