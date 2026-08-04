from pathlib import Path

import streamlit as st

from rip_tags.ui.batch_cleaner import render_batch_cleaner
from rip_tags.ui.file_viewer import render_selected_file
from rip_tags.ui.sidebar import render_sidebar
from rip_tags.ui.styles import apply_app_shell_styles

_ICON_PATH = str(Path(__file__).resolve().parent.parent.parent / "Rip-Tags.png")


def run_app():
    st.set_page_config(
        page_title="Rip-Tags",
        page_icon=_ICON_PATH,
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_app_shell_styles()

    folder_path = render_sidebar()

    if st.session_state.get("selected_file"):
        render_selected_file()
    else:
        render_batch_cleaner(folder_path)
