from pathlib import Path
import platform
import subprocess

import streamlit as st

from rip_tags.cleaner import SUPPORTED_SUFFIXES


def render_sidebar() -> Path:
    with st.sidebar:
        st.header("Select Folder")

        if "target_folder" not in st.session_state:
            st.session_state.target_folder = str(Path("target"))

        folder = st.session_state.target_folder
        st.code(folder, language=None)

        if st.button("Browse folder", use_container_width=True):
            selected_folder = _browse_folder(st.session_state.target_folder)

            if selected_folder:
                st.session_state.target_folder = selected_folder
                st.session_state.pop("selected_file", None)

        st.caption("Supported: " + ", ".join(sorted(SUPPORTED_SUFFIXES)))

        st.divider()

        folder_path = Path(folder).expanduser()
        st.header("Folder Tree")

        if not folder_path.exists() or not folder_path.is_dir():
            st.info("Select a valid folder.")
        else:   
            _render_folder_tree(folder_path)

    return folder_path


def _browse_folder(initial_folder: str) -> str:
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
