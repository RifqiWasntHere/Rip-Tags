from pathlib import Path

import streamlit as st

from rip_tags.cleaner import CleanResult, scan


def render_batch_cleaner(folder_path: Path):
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
