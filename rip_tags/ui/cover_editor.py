from pathlib import Path
from typing import Optional

import streamlit as st

from rip_tags.cover_art import (
    DEFAULT_COVER_SIZE,
    embed_cover,
    get_cover_dimensions,
    prepare_cover_image,
    remove_cover,
    resize_cover_image,
)
from rip_tags.metadata import AudioInfo

COVER_SIZE_OPTIONS = list(range(500, 1001, 100))


def render_cover_editor(info: AudioInfo):
    has_cover = bool(info.cover_data)
    size_options = [f"{size}x{size}" for size in COVER_SIZE_OPTIONS]

    action_cols = st.columns([6, 1])

    with action_cols[1]:
        with st.popover("", icon=":material/more_vert:"):
            st.markdown("### Cover")

            if has_cover:
                cover_action = st.radio(
                    "Choose cover action",
                    options=["Replace album cover", "Resize album cover"],
                    horizontal=True,
                    key=f"cover-action:{info.path}",
                )

                if cover_action == "Resize album cover":
                    _render_current_cover_resize(info, size_options)
                else:
                    _render_replacement_cover_upload(info, size_options)
                    st.divider()
                    _render_remove_cover_button(info)
            else:
                _render_replacement_cover_upload(info, size_options)

    with action_cols[0]:
        if has_cover:
            st.image(info.cover_data, use_container_width=True)
        else:
            st.markdown(
                '<div class="cover-empty-label">No album cover</div>',
                unsafe_allow_html=True,
            )


def _render_replacement_cover_upload(info: AudioInfo, size_options: list[str]):
    uploaded_cover = st.file_uploader(
        "Upload album cover",
        type=["jpg", "jpeg", "png", "webp"],
        key=f"cover-upload:{info.path}",
    )

    resize_cover = st.checkbox(
        "Resize uploaded cover",
        value=True,
        key=f"cover-resize:{info.path}",
    )
    selected_size = st.selectbox(
        "Uploaded cover size",
        options=size_options,
        index=size_options.index(f"{DEFAULT_COVER_SIZE}x{DEFAULT_COVER_SIZE}"),
        disabled=not resize_cover,
        key=f"cover-size:{info.path}",
    )

    if uploaded_cover:
        try:
            cover_size = int(selected_size.split("x", 1)[0])
            cover_data = prepare_cover_image(
                uploaded_cover,
                width=cover_size,
                height=cover_size,
                resize=resize_cover,
            )
        except Exception as e:
            st.error(f"Could not prepare cover image: {e}")
        else:
            caption = (
                f"Uploaded preview: {selected_size}"
                if resize_cover
                else "Uploaded preview: original size"
            )
            st.image(cover_data, caption=caption, use_container_width=True)

            apply_label = "Replace album cover" if info.cover_data else "Add album cover"
            if st.button(
                apply_label,
                type="primary",
                key=f"apply-cover:{info.path}",
                use_container_width=True,
            ):
                try:
                    embed_cover(info.path, cover_data)
                    st.session_state.cover_status = {
                        "path": str(info.path),
                        "type": "success",
                        "message": "Cover art embedded.",
                    }
                    st.rerun()
                except Exception as e:
                    st.session_state.cover_status = {
                        "path": str(info.path),
                        "type": "error",
                        "message": f"Could not embed cover art: {e}",
                    }
                    st.rerun()


def _render_current_cover_resize(info: AudioInfo, size_options: list[str]):
    try:
        current_width, current_height = get_cover_dimensions(info.cover_data)
    except Exception as e:
        st.caption(f"Current size: unknown ({e})")
        current_width = current_height = None
    else:
        st.caption(f"Current size: {current_width}x{current_height}")

    embedded_size = st.selectbox(
        "Embedded cover size",
        options=size_options,
        index=_default_cover_size_index(current_width, current_height, size_options),
        key=f"embedded-cover-size:{info.path}",
    )
    target_size = int(embedded_size.split("x", 1)[0])
    is_current_size = current_width == target_size and current_height == target_size
    is_upscaling = (
        current_width is not None
        and current_height is not None
        and (target_size > current_width or target_size > current_height)
    )

    allow_upscaling = False
    if is_current_size:
        st.caption(f"The current album cover is already {embedded_size}.")
    elif is_upscaling:
        st.warning(
            f"This will upscale the current {current_width}x{current_height} cover to {embedded_size}. "
            "It may look blurry."
        )
        allow_upscaling = st.checkbox(
            "Allow upscaling",
            key=f"allow-cover-upscale:{info.path}",
        )
    else:
        st.caption(f"Will resize current cover to {embedded_size}.")

    if st.button(
        "Resize embedded cover",
        disabled=is_current_size or (is_upscaling and not allow_upscaling),
        key=f"resize-embedded-cover:{info.path}",
        use_container_width=True,
    ):
        try:
            cover_data = resize_cover_image(
                info.cover_data,
                width=target_size,
                height=target_size,
            )
            embed_cover(info.path, cover_data)
            st.session_state.cover_status = {
                "path": str(info.path),
                "type": "success",
                "message": f"Cover art resized to {embedded_size}.",
            }
            st.rerun()
        except Exception as e:
            st.session_state.cover_status = {
                "path": str(info.path),
                "type": "error",
                "message": f"Could not resize cover art: {e}",
            }
            st.rerun()


def _render_remove_cover_button(info: AudioInfo):
    if st.button(
        "Remove album cover",
        key=f"remove-cover:{info.path}",
        use_container_width=True,
    ):
        try:
            remove_cover(info.path)
            st.session_state.cover_status = {
                "path": str(info.path),
                "type": "success",
                "message": "Cover art removed.",
            }
            st.rerun()
        except Exception as e:
            st.session_state.cover_status = {
                "path": str(info.path),
                "type": "error",
                "message": f"Could not remove cover art: {e}",
            }
            st.rerun()


def _default_cover_size_index(current_width: Optional[int], current_height: Optional[int], size_options: list[str]) -> int:
    if current_width is None or current_height is None:
        default_size = DEFAULT_COVER_SIZE
    else:
        current_size = min(current_width, current_height)
        default_size = max((size for size in COVER_SIZE_OPTIONS if size <= current_size), default=DEFAULT_COVER_SIZE)

    return size_options.index(f"{default_size}x{default_size}")
