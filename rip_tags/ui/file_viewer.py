from pathlib import Path
from typing import Optional

import streamlit as st

from rip_tags.metadata import AudioInfo, read_audio_info
from rip_tags.ui.cover_editor import render_cover_editor


def render_selected_file() -> bool:
    selected_file = st.session_state.get("selected_file")

    if not selected_file:
        return False

    info = read_audio_info(Path(selected_file))

    st.subheader(info.path.name)
    _render_cover_status(info.path)

    if info.error:
        st.error(info.error)
        return True

    cover_col, info_col = st.columns([1, 2])

    with cover_col:
        render_cover_editor(info)

    with info_col:
        _render_audio_overview(info)

    st.dataframe(
        [{"tag": key, "value": value} for key, value in info.tags.items()],
        use_container_width=True,
        hide_index=True,
    )

    return True


def _render_cover_status(path: Path):
    cover_status = st.session_state.pop("cover_status", None)

    if not cover_status or cover_status.get("path") != str(path):
        return

    if cover_status["type"] == "success":
        st.success(cover_status["message"])
    else:
        st.error(cover_status["message"])


def _render_audio_overview(info: AudioInfo):
    rows = [
        ("Path", str(info.path)),
        ("Type", info.file_type),
        ("Duration", _format_duration(info.duration)),
        ("Bitrate", _format_bitrate(info.bitrate)),
        ("Sample rate", _format_sample_rate(info.sample_rate)),
        ("Bit depth", _format_bit_depth(info.bit_depth)),
        ("Channels", str(info.channels) if info.channels is not None else "-"),
    ]

    for label, value in rows:
        st.write(f"**{label}:** {value}")


def _format_duration(value: Optional[float]) -> str:
    if value is None:
        return "-"

    minutes, seconds = divmod(round(value), 60)
    return f"{minutes}:{seconds:02d}"


def _format_bitrate(value: Optional[int]) -> str:
    if value is None:
        return "-"

    return f"{round(value / 1000)} kbps"


def _format_sample_rate(value: Optional[int]) -> str:
    if value is None:
        return "-"

    return f"{value / 1000:g} kHz"


def _format_bit_depth(value: Optional[int]) -> str:
    if value is None:
        return "-"

    return f"{value}-bit"
