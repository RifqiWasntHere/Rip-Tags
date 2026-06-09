from pathlib import Path
from typing import Optional

import streamlit as st

from rip_tags.cleaner import SUPPORTED_SUFFIXES, CleanResult, scan
from rip_tags.metadata import AudioInfo, read_audio_info


def run_app():
    st.set_page_config(
        page_title="Rip-Tags",
        layout="wide",
    )

    _apply_app_shell_styles()

    folder, dry_run, confirm_write, run = _render_sidebar()
    folder_path = Path(folder).expanduser()
    selected_file_rendered = _render_selected_file()

    if not run:
        if not selected_file_rendered:
            st.info("Choose a file from the sidebar or scan the target folder.")
        return

    if not folder_path.exists() or not folder_path.is_dir():
        st.error("Folder not found.")
        return

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

        dry_run = st.toggle("Preview only", value=True)
        confirm_write = st.checkbox("Allow metadata writes", disabled=dry_run)
        run = st.button("Scan", type="primary", use_container_width=True)

        st.caption("Supported: " + ", ".join(sorted(SUPPORTED_SUFFIXES)))
        st.divider()

        folder_path = Path(folder).expanduser()

        st.header("Folder Tree")

        if not folder_path.exists() or not folder_path.is_dir():
            st.info("Select a valid folder.")
            return folder, dry_run, confirm_write, run

        _render_folder_tree(folder_path)

    return folder, dry_run, confirm_write, run


def _browse_folder(initial_folder: str):
    try:
        from tkinter import Tk, filedialog

        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        selected_folder = filedialog.askdirectory(
            initialdir=str(Path(initial_folder).expanduser()),
            title="Choose target folder",
            mustexist=True,
        )

        root.destroy()
        return selected_folder

    except Exception as e:
        st.error(f"Could not open folder browser: {e}")
        return ""


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

    if info.error:
        st.error(info.error)
        return True

    cover_col, info_col = st.columns([1, 2])

    with cover_col:
        if info.cover_data:
            st.image(info.cover_data, use_container_width=True)
        else:
            st.info("No album cover.")

    with info_col:
        _render_audio_overview(info)

    st.dataframe(
        [{"tag": key, "value": value} for key, value in info.tags.items()],
        use_container_width=True,
        hide_index=True,
    )

    return True


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
        </style>
        """,
        unsafe_allow_html=True,
    )
