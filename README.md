# Tag Ripper

A small Streamlit app for previewing and cleaning audio metadata.

## Run

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run streamlit_app.py
```

## Project Structure

```text
.
├── streamlit_app.py      # Streamlit entrypoint
├── tagripper.py          # CLI/backwards-compatible wrapper
├── rip_tags/
│   ├── __init__.py
│   ├── cleaner.py        # Audio metadata cleaning logic
│   └── ui.py             # Streamlit UI
├── requirements.txt
└── target/               # Local sample/input files
```

## Supported Files

- `.flac`
- `.m4a`
- `.mp4`

Preview mode is enabled by default in the app. Turn it off and enable metadata writes when you are ready to clean files.
