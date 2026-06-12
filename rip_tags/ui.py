from pathlib import Path
import platform
import subprocess
from typing import Optional

import streamlit as st

from rip_tags.cleaner import SUPPORTED_SUFFIXES, CleanResult, scan
from rip_tags.cover_art import (
    DEFAULT_COVER_SIZE,
    embed_cover,
    get_cover_dimensions,
    prepare_cover_image,
    remove_cover,
    resize_cover_image,
)
from rip_tags.metadata import AudioInfo, read_audio_info


COVER_SIZE_OPTIONS = list(range(500, 1001, 100))


def run_app():
    st.set_page_config(
        page_title="Rip-Tags",
        layout="wide",
    )

    _apply_app_shell_styles()

    folder_path = _render_sidebar()

    if st.session_state.get("selected_file"):
        _render_selected_file()
    else:
        _render_batch_cleaner(folder_path)


def _render_batch_cleaner(folder_path: Path):
    st.subheader("Batch Tag Cleaner")

    if not folder_path.exists() or not folder_path.is_dir():
        st.info("Choose a valid folder in the sidebar to scan for music files.")
        return

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        dry_run = st.toggle("Preview only", value=True)
    with col2:
        confirm_write = st.checkbox("Allow metadata writes", disabled=dry_run)
    with col3:
        run = st.button("Scan Folder", type="primary", use_container_width=True)

    if run:
        if not dry_run and not confirm_write:
            st.warning("Enable metadata writes before cleaning files.")
            return

        messages: list[str] = []
        with st.spinner("Scanning files..."):
            results = scan(folder_path, dry_run=dry_run, log_func=messages.append)

        _render_summary(results)

        if not results:
            st.info("No supported files found.")
            return

        _render_results_table(results, folder_path)
        _render_log(messages, results)
    else:
        st.info("Choose a file from the sidebar to edit tags, or run a scan to clean the entire folder.")


def _render_sidebar():
    with st.sidebar:
        st.header("Target")

        if "target_folder" not in st.session_state:
            st.session_state.target_folder = str(Path("target"))

        if st.button("Browse folder", use_container_width=True):
            selected_folder = _browse_folder(st.session_state.target_folder)

            if selected_folder:
                st.session_state.target_folder = selected_folder
                st.session_state.pop("selected_file", None)

        folder = st.session_state.target_folder
        st.caption("Selected folder")
        st.code(folder, language=None)

        st.divider()

        folder_path = Path(folder).expanduser()
        st.header("Folder Tree")

        if not folder_path.exists() or not folder_path.is_dir():
            st.info("Select a valid folder.")
        else:
            _render_folder_tree(folder_path)
            st.caption("Supported: " + ", ".join(sorted(SUPPORTED_SUFFIXES)))

    return folder_path


def _browse_folder(initial_folder: str):
    if platform.system() != "Darwin":
        st.error("Folder browsing is currently only available on macOS.")
        return ""

    initial_path = Path(initial_folder).expanduser()

    if not initial_path.exists():
        initial_path = Path.home()
    else:
        initial_path = initial_path.resolve()

    initial_path_text = str(initial_path).replace('"', '\\"')

    script = (
        'POSIX path of (choose folder '
        f'with prompt "Choose target folder" default location POSIX file "{initial_path_text}")'
    )

    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            check=False,
            text=True,
        )
    except Exception as e:
        st.error(f"Could not open folder browser: {e}")
        return ""

    if result.returncode == 1 and "User canceled" in result.stderr:
        return ""

    if result.returncode != 0:
        st.error(result.stderr.strip() or "Could not open folder browser.")
        return ""

    return result.stdout.strip()


def _render_folder_tree(folder_path: Path):
    st.caption(str(folder_path))
    _render_directory(folder_path, depth=0)


def _render_directory(folder_path: Path, depth: int, max_depth=4, max_entries=160):
    if depth >= max_depth:
        st.caption("...")
        return

    try:
        entries = sorted(
            [entry for entry in folder_path.iterdir() if not entry.name.startswith(".")],
            key=lambda entry: (entry.is_file(), entry.name.lower()),
        )
    except OSError:
        st.caption("Cannot read folder.")
        return

    for entry in entries[:max_entries]:
        if entry.is_dir():
            with st.expander(entry.name, expanded=depth == 0):
                _render_directory(entry, depth + 1, max_depth=max_depth, max_entries=max_entries)
            continue

        if entry.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue

        selected = st.session_state.get("selected_file") == str(entry)
        label = entry.name

        if selected:
            label = f"> {label}"

        if st.button(label, key=f"file:{entry}", use_container_width=True):
            st.session_state.selected_file = str(entry)

    if len(entries) > max_entries:
        st.caption(f"{len(entries) - max_entries} more items hidden")


def _render_selected_file():
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
        _render_cover_editor(info)

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


def _render_cover_editor(info: AudioInfo):
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
                # st.markdown('<div class="cover-action-divider">', unsafe_allow_html=True)
                # st.divider()
                # st.markdown("</div>", unsafe_allow_html=True)

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


def _default_cover_size_index(current_width: Optional[int], current_height: Optional[int], size_options: list[str]):
    if current_width is None or current_height is None:
        default_size = DEFAULT_COVER_SIZE
    else:
        current_size = min(current_width, current_height)
        default_size = max((size for size in COVER_SIZE_OPTIONS if size <= current_size), default=DEFAULT_COVER_SIZE)

    return size_options.index(f"{default_size}x{default_size}")


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


def _format_duration(value: Optional[float]):
    if value is None:
        return "-"

    minutes, seconds = divmod(round(value), 60)
    return f"{minutes}:{seconds:02d}"


def _format_bitrate(value: Optional[int]):
    if value is None:
        return "-"

    return f"{round(value / 1000)} kbps"


def _format_sample_rate(value: Optional[int]):
    if value is None:
        return "-"

    return f"{value / 1000:g} kHz"


def _format_bit_depth(value: Optional[int]):
    if value is None:
        return "-"

    return f"{value}-bit"


def _render_summary(results: list[CleanResult]):
    supported_files = len(results)
    changed_files = len([item for item in results if item.status in {"would_clean", "cleaned"}])
    unchanged_files = len([item for item in results if item.status == "unchanged"])
    failed_files = len([item for item in results if item.status == "failed"])
    removed_tags = sum(len(item.removed) for item in results)

    metric_cols = st.columns(5)
    metric_cols[0].metric("Files", supported_files)
    metric_cols[1].metric("Cleanable", changed_files)
    metric_cols[2].metric("Unchanged", unchanged_files)
    metric_cols[3].metric("Failed", failed_files)
    metric_cols[4].metric("Tags removed", removed_tags)


def _render_results_table(results: list[CleanResult], folder_path: Path):
    rows = [
        {
            "file": str(item.path.relative_to(folder_path)),
            "status": item.status,
            "removed": ", ".join(item.removed),
            "kept": ", ".join(item.kept),
            "error": item.error,
        }
        for item in results
    ]

    st.dataframe(rows, use_container_width=True, hide_index=True)


def _render_log(messages: list[str], results: list[CleanResult]):
    failed_files = len([item for item in results if item.status == "failed"])

    with st.expander("Log", expanded=failed_files > 0):
        st.code("\n".join(messages) if messages else "No changes.")


def _apply_app_shell_styles():
    st.markdown(
        """
        <style>
            [data-testid="stHeader"] {
                display: none;
            }

            [data-testid="stToolbar"] {
                display: none;
            }

            .block-container {
                padding-top: 1.25rem;
            }

            [data-testid="stSidebarHeader"] {
                align-items: center;
                min-height: 3.25rem;
                padding-bottom: 0.5rem;
                padding-top: 0.5rem;
            }

            [data-testid="stSidebarHeader"]::before {
                content: "Rip-Tags";
                display: block;
                flex: 1;
                font-size: 1.35rem;
                font-weight: 700;
                line-height: 1.2;
                margin-left: 0.25rem;
                white-space: nowrap;
            }

            .cover-empty-label {
                align-items: center;
                aspect-ratio: 1 / 1;
                border: 1px dashed rgba(128, 128, 128, 0.65);
                border-radius: 8px;
                color: rgba(120, 120, 120, 0.95);
                display: flex;
                font-size: 0.95rem;
                justify-content: center;
                margin-bottom: 0.75rem;
                text-align: center;
            }

            .cover-dropzone {
                position: relative;
                width: 100%;
            }

            .cover-dropzone.empty-cover {
                margin-bottom: 0.5rem;
            }

            .cover-dropzone.has-cover [data-testid="stFileUploader"] {
                position: absolute;
                inset: 0;
                z-index: 3;
                margin: 0;
            }

            .cover-dropzone.has-cover [data-testid="stFileUploader"] section {
                min-height: 100%;
            }

            .cover-dropzone.has-cover [data-testid="stFileUploaderDropzone"] {
                min-height: 100%;
                border: 0;
                background: rgba(255, 255, 255, 0.02);
                opacity: 0.01;
            }

            .cover-dropzone.has-cover [data-testid="stFileUploaderDropzone"] > div {
                min-height: 100%;
            }

            .cover-dropzone.has-cover [data-testid="stFileUploaderDropzone"] label {
                display: none;
            }

            [data-testid="stFileUploaderDropzone"] {
                border-style: dashed;
                border-radius: 8px;
            }

            .cover-action-divider [data-testid="stMarkdownContainer"] hr {
                margin-bottom: 0.45rem;
                margin-top: 0.35rem;
            }

            [data-testid="stPopover"] {
                position: relative;
                z-index: 5;
            }

            [data-testid="stPopover"] button {
                margin-left: -3rem;
                margin-top: 0.5rem;
                padding-left: 0.72rem;
                opacity: 0.75;
                transition: opacity 120ms ease;
            }

            div[data-testid="stPopover"] button svg {
                display: none !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
