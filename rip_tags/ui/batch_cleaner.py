from pathlib import Path

import streamlit as st

from rip_tags.cleaner import SUPPORTED_SUFFIXES, CleanResult, clean_file, scan


ALL_PREF_TAGS = [
    # Core (Most Common)
    "title",
    "artist",
    "album",
    "albumartist",
    "date",
    "genre",
    "tracknumber",
    "disk",
    "cover",
    # Secondary
    "composer",
    "copyright",
    "compilation",
    # Technical / Metadata
    "encoder",
    "lyrics",
    "comment",
    "grouping",
    # iTunes specific / Personal identifiers
    "purchase date",
    "apple id",
    "catalog id",
    "storefront",
    "media type",
    "explicit rating",
    "gapless playback",
    # Sorting tags
    "sort title",
    "sort artist",
    "sort album",
    "sort albumartist",
    "sort composer",
]


@st.dialog("Clean Preferences")
def show_preferences_modal():
    st.write("Choose which tags you want to **keep** during the cleaning process. Unchecked tags will be removed.")

    # Initialize checkbox widget keys from persistent dict if not present
    for tag in ALL_PREF_TAGS:
        key = f"pref_checkbox_{tag}"
        if key not in st.session_state:
            st.session_state[key] = st.session_state.keep_tags_preference.get(tag, True)

    col_sel, col_desel, col_rec = st.columns([1, 1, 1.2])
    with col_sel:
        if st.button("Select All", key="pref_select_all", use_container_width=True):
            for tag in ALL_PREF_TAGS:
                st.session_state.keep_tags_preference[tag] = True
                st.session_state[f"pref_checkbox_{tag}"] = True
    with col_desel:
        if st.button("Deselect All", key="pref_deselect_all", use_container_width=True):
            for tag in ALL_PREF_TAGS:
                st.session_state.keep_tags_preference[tag] = False
                st.session_state[f"pref_checkbox_{tag}"] = False
    with col_rec:
        if st.button("Recommended", key="pref_recommended", use_container_width=True):
            recommended_tags = {
                "title", "artist", "album", "date", "tracknumber", "genre",
                "albumartist", "copyright", "composer", "encoder", "cover"
            }
            for tag in ALL_PREF_TAGS:
                st.session_state.keep_tags_preference[tag] = (tag in recommended_tags)
                st.session_state[f"pref_checkbox_{tag}"] = (tag in recommended_tags)

    st.divider()

    # Scrollable container for checkboxes
    with st.container(height=350):
        col_left, col_right = st.columns(2)
        half = (len(ALL_PREF_TAGS) + 1) // 2
        for idx, tag in enumerate(ALL_PREF_TAGS):
            display_name = tag.replace("_", " ").title()
            target_col = col_left if idx < half else col_right
            with target_col:
                val = st.checkbox(
                    display_name,
                    key=f"pref_checkbox_{tag}"
                )
                st.session_state.keep_tags_preference[tag] = val

    st.divider()
    if st.button("Close & Apply", type="primary", use_container_width=True):
        st.rerun()


def render_batch_cleaner(folder_path: Path):
    st.subheader("Batch Tag Cleaner")

    if not folder_path.exists() or not folder_path.is_dir():
        st.info("Choose a valid folder in the sidebar to scan for music files.")
        return

    # Scan the folder to find supported audio files
    files = sorted([
        f for f in folder_path.rglob("*")
        if f.is_file() and f.suffix.lower() in SUPPORTED_SUFFIXES and not f.name.startswith("._")
    ])

    if not files:
        st.info("No supported music files found in this folder.")
        return

    # Initialize persistent preferences dictionary
    recommended_tags = {
        "title", "artist", "album", "date", "tracknumber", "genre",
        "albumartist", "copyright", "composer", "encoder", "cover"
    }
    if "keep_tags_preference" not in st.session_state:
        st.session_state.keep_tags_preference = {
            tag: (tag in recommended_tags) for tag in ALL_PREF_TAGS
        }

    st.write(f"Found **{len(files)}** supported files.")

    # Initialize checkbox states if not present
    for f in files:
        key = f"clean_checkbox:{f}"
        if key not in st.session_state:
            st.session_state[key] = True

    st.write("### Choose Files to Clean")

    # Select all / Deselect all buttons positioned below the title
    col_sel_all, col_desel_all, _ = st.columns([1.5, 1.5, 5])
    with col_sel_all:
        if st.button("Select All", use_container_width=True):
            for f in files:
                st.session_state[f"clean_checkbox:{f}"] = True
            st.rerun()

    with col_desel_all:
        if st.button("Deselect All", use_container_width=True):
            for f in files:
                st.session_state[f"clean_checkbox:{f}"] = False
            st.rerun()

    # Checklist container (scrollable) containing the checkboxes
    with st.container(height=200):
        for f in files:
            rel_path = f.relative_to(folder_path)
            st.checkbox(
                str(rel_path),
                key=f"clean_checkbox:{f}"
            )

    st.divider()

    # Dry run and writes checkboxes
    col1, col2 = st.columns([1, 1])
    with col1:
        dry_run = st.toggle("Preview only", value=True)
    with col2:
        confirm_write = st.checkbox("Allow metadata writes", disabled=dry_run)

    # Gear Settings button (triggers st.dialog) on the left of execution button
    col_gear, col_btn = st.columns([1, 5])
    with col_gear:
        if st.button("", icon=":material/settings:", use_container_width=True, key="settings_dialog_btn"):
            show_preferences_modal()

    with col_btn:
        run = st.button("Clean Files", type="primary", use_container_width=True)

    if run:
        if not dry_run and not confirm_write:
            st.warning("Enable metadata writes before cleaning files.")
            return

        # Filter files to clean based on user selections
        files_to_clean = [f for f in files if st.session_state.get(f"clean_checkbox:{f}", True)]
        if not files_to_clean:
            st.warning("No files selected to clean.")
            return

        # Collect user-selected tags to keep from persistent dict
        keep_tags = {tag for tag, keep in st.session_state.keep_tags_preference.items() if keep}

        messages: list[str] = []
        with st.spinner("Processing selected files..."):
            results = []
            for file in files_to_clean:
                res = clean_file(file, dry_run=dry_run, log_func=messages.append, keep_tags=keep_tags)
                if res:
                    results.append(res)

        _render_summary(results)

        if not results:
            st.info("No files processed.")
            return

        _render_results_table(results, folder_path)
        _render_log(messages, results)
    else:
        st.info("Choose files and configure preferences above, then click Clean Files.")


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
