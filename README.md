![Rip Tags Logo](Rip-Tags.png)
# Rip-Tags (In-Development)

So uhh.. i'm having this problem where, everytime i bought a music from Itunes Store, the tags metadata were overwhelming my Fiio x Snowsky Echo DAP. 
Thus why, i'm trying to build this tool to automate the solution. I initially had no visions for a full audio file kit whatsoever, but let's see what i can do.

## To Run :

```bash
python -m venv .venv (
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run streamlit_app.py
```

## Project Structure (Thank you GPT for the help on writing this pain in the ass)

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

Also, preview mode is enabled by default in the app. Turn it off to enable metadata writes when you are ready to clean files.
