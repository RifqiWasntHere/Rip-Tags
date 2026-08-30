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
    "cpil": "compilation",
    "purd": "purchase date",
    "apID": "apple id",
    "cnID": "catalog id",
    "sfID": "storefront",
    "stik": "media type",
    "rtng": "explicit rating",
    "pgap": "gapless playback",
    "sonm": "title",
    "soar": "artist",
    "soal": "album",
    "soaa": "albumartist",
    "soco": "composer",
    "disk": "disk",
    "disc": "disk",
}


FLAC_TAG_MAPPING = {
    "title": "title",
    "artist": "artist",
    "album": "album",
    "albumartist": "albumartist",
    "album artist": "albumartist",
    "date": "date",
    "year": "date",
    "genre": "genre",
    "tracknumber": "tracknumber",
    "track": "tracknumber",
    "tracktotal": "tracktotal",
    "track total": "tracktotal",
    "disk": "disk",
    "disc": "disk",
    "discnumber": "disk",
    "disctotal": "disctotal",
    "disc total": "disctotal",
    "cover": "cover",
    "composer": "composer",
    "copyright": "copyright",
    "compilation": "compilation",
    "encoder": "encoder",
    "lyrics": "lyrics",
    "comment": "comment",
    "grouping": "grouping",
    "purchase date": "purchase date",
    "purchasedate": "purchase date",
    "itunespurchasedate": "purchase date",
    "apple id": "apple id",
    "appleid": "apple id",
    "itunesaccount": "apple id",
    "catalog id": "catalog id",
    "catalogid": "catalog id",
    "storefront": "storefront",
    "media type": "media type",
    "mediatype": "media type",
    "explicit rating": "explicit rating",
    "explicitrating": "explicit rating",
    "gapless playback": "gapless playback",
    "gaplessplayback": "gapless playback",
    "sort title": "title",
    "sorttitle": "title",
    "sort artist": "artist",
    "sortartist": "artist",
    "sort album": "album",
    "sortalbum": "album",
    "sort albumartist": "albumartist",
    "sort album artist": "albumartist",
    "sortalbumartist": "albumartist",
    "sort composer": "composer",
    "sortcomposer": "composer",
}


TAG_DISPLAY_NAMES = {
    "title": "Title",
    "artist": "Artist",
    "album": "Album",
    "albumartist": "Album Artist",
    "date": "Date",
    "genre": "Genre",
    "tracknumber": "Track Number",
    "tracktotal": "Track Total",
    "disk": "Disc Number",
    "disctotal": "Disc Total",
    "cover": "Cover",
    "composer": "Composer",
    "copyright": "Copyright",
    "compilation": "Compilation",
    "encoder": "Encoder",
    "lyrics": "Lyrics",
    "comment": "Comment",
    "grouping": "Grouping",
    "purchase date": "Purchase Date",
    "apple id": "Apple ID",
    "catalog id": "Catalog ID",
    "storefront": "Storefront",
    "media type": "Media Type",
    "explicit rating": "Explicit Rating",
    "gapless playback": "Gapless Playback",
}


def _normalize_tag_name(tag: str) -> str:
    return tag.lower().replace(" ", "").replace("_", "").replace("-", "")


MP4_SORT_KEYS = {"sonm", "soar", "soal", "soaa", "soco"}

MP4_SORT_TO_BASE = {
    "sonm": "\xa9nam",
    "soar": "\xa9ART",
    "soal": "\xa9alb",
    "soaa": "aART",
    "soco": "\xa9wrt",
}


def is_sort_tag_key(tag: str, file_type: str) -> bool:
    if file_type == "MP4":
        return tag in MP4_SORT_KEYS
    return _normalize_tag_name(tag).startswith("sort")


def to_canonical_tag(tag: str, file_type: str) -> str:
    tag = str(tag)

    if file_type == "MP4":
        if tag in MP4_TAG_MAPPING:
            return MP4_TAG_MAPPING[tag]
        if tag.lower() in MP4_TAG_MAPPING:
            return MP4_TAG_MAPPING[tag.lower()]
        if tag.startswith("----:com.apple.iTunes:"):
            suffix = tag.split(":", 2)[2]
            normalized = _normalize_tag_name(suffix)
            return FLAC_TAG_MAPPING.get(normalized, normalized)
        if tag.startswith("\xa9"):
            return "©" + tag[1:]
        return tag.lower()

    if file_type == "FLAC":
        normalized = _normalize_tag_name(tag)
        return FLAC_TAG_MAPPING.get(normalized, normalized)

    return tag.lower()


def to_sort_display(tag: str, file_type: str) -> Optional[str]:
    tag = str(tag)

    if file_type == "MP4":
        if tag in MP4_SORT_TO_BASE:
            base_canonical = to_canonical_tag(MP4_SORT_TO_BASE[tag], "MP4")
            return "sort " + base_canonical
        return None

    if is_sort_tag_key(tag, file_type):
        return tag.lower()

    return None


def to_display_name(canonical_tag: str) -> str:
    return TAG_DISPLAY_NAMES.get(canonical_tag, canonical_tag.replace("_", " ").title())


def to_human_tag(tag: str) -> str:
    return to_canonical_tag(tag, "MP4")


def _read_tags(audio) -> dict[str, Any]:
    if audio.tags is None:
        return {}

    file_type = type(audio).__name__

    return {
        str(key): _format_tag_value(value)
        for key, value in sorted(
            audio.tags.items(),
            key=lambda item: to_display_name(to_canonical_tag(str(item[0]), file_type)).lower(),
        )
    }


def _format_tag_value(value):
    if isinstance(value, list):
        return ", ".join(_format_tag_value(item) for item in value)

    if isinstance(value, tuple):
        return ", ".join(_format_tag_value(item) for item in value)

    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
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
