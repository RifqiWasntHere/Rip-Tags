from io import BytesIO
from pathlib import Path

from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover, MP4Tags
from PIL import Image, ImageOps


DEFAULT_COVER_SIZE = 500
COVER_MIME = "image/jpeg"


def prepare_cover_image(image_file, width=DEFAULT_COVER_SIZE, height=DEFAULT_COVER_SIZE, resize=True):
    image = Image.open(image_file)
    image = ImageOps.exif_transpose(image)
    return _encode_cover_image(image, width=width, height=height, resize=resize)


def resize_cover_image(image_data: bytes, width=DEFAULT_COVER_SIZE, height=DEFAULT_COVER_SIZE):
    image = Image.open(BytesIO(image_data))
    image = ImageOps.exif_transpose(image)
    return _encode_cover_image(image, width=width, height=height, resize=True)


def get_cover_dimensions(image_data: bytes):
    image = Image.open(BytesIO(image_data))
    image = ImageOps.exif_transpose(image)
    return image.size


def _encode_cover_image(image: Image.Image, width=DEFAULT_COVER_SIZE, height=DEFAULT_COVER_SIZE, resize=True):
    if resize:
        image = ImageOps.fit(image, (width, height), method=Image.Resampling.LANCZOS)

    if image.mode in {"RGBA", "LA", "P"}:
        background = Image.new("RGB", image.size, "white")
        if image.mode == "P":
            image = image.convert("RGBA")
        background.paste(image, mask=image.getchannel("A") if image.mode in {"RGBA", "LA"} else None)
        image = background
    else:
        image = image.convert("RGB")

    output = BytesIO()
    image.save(output, format="JPEG", quality=92, optimize=True)
    return output.getvalue()


def embed_cover(path: Path, cover_data: bytes, mime=COVER_MIME):
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix in {".m4a", ".mp4"}:
        _embed_mp4_cover(path, cover_data)
        return

    if suffix == ".flac":
        _embed_flac_cover(path, cover_data, mime)
        return

    raise ValueError(f"Cover embedding is not supported for {suffix}")


def remove_cover(path: Path):
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix in {".m4a", ".mp4"}:
        _remove_mp4_cover(path)
        return

    if suffix == ".flac":
        _remove_flac_cover(path)
        return

    raise ValueError(f"Cover removal is not supported for {suffix}")


def _embed_mp4_cover(path: Path, cover_data: bytes):
    audio = MP4(path)

    if audio.tags is None:
        audio.tags = MP4Tags()

    audio.tags["covr"] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]
    audio.save()


def _embed_flac_cover(path: Path, cover_data: bytes, mime: str):
    audio = FLAC(path)

    picture = Picture()
    picture.type = 3
    picture.mime = mime
    picture.desc = "Cover"
    picture.data = cover_data

    audio.clear_pictures()
    audio.add_picture(picture)
    audio.save()


def _remove_mp4_cover(path: Path):
    audio = MP4(path)

    if audio.tags is None or "covr" not in audio.tags:
        return

    del audio.tags["covr"]
    audio.save()


def _remove_flac_cover(path: Path):
    audio = FLAC(path)
    if not audio.pictures:
        return

    audio.clear_pictures()
    audio.save()
