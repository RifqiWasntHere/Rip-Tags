import streamlit as st


def apply_app_shell_styles():
    st.markdown(
        """
        <style>
            [data-testid="stHeader"] {
                display: none;
            }

            [data-testid="stToolbar"] {
                display: none;
            }

            /* 
               FORCE SIDEBAR VISIBILITY:
               Even if the browser state is 'collapsed', we force the sidebar 
               to be visible and positioned correctly.
            */
            section[data-testid="stSidebar"] {
                transform: none !important;
                visibility: visible !important;
                min-width: 336px !important;
                max-width: 336px !important;
                left: 0 !important;
            }

            /* Force the main content to respect the sidebar width */
            [data-testid="stAppViewMain"] {
                margin-left: 336px !important;
            }

            /* Hide the toggle buttons entirely */
            [data-testid="stSidebarCollapseButton"], 
            [data-testid="collapsedControl"],
            button[kind="header"] {
                display: none !important;
                visibility: hidden !important;
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
