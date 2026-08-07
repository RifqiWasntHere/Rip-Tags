![Rip Tags Logo](Rip-Tags.png)

# Rip Tags


A desktop audio metadata tag cleaner for macOS and Windows. Strip unnecessary tags from your music files and manage cover art without touching the terminal.

## Why?

So uhh.. i'm having this problem where, everytime i bought a music from Itunes Store, the tags metadata were bloating my Fiio x Snowsky Echo DAP. 
Thus why, i'm trying to build this tool to automate the solution. Rip Tags lets you keep only the tags you want and embed clean, resized cover art.

## Features

- **Batch tag cleaning** for `.flac`, `.m4a`, and `.mp4` files
- **Keep-list presets**, including a recommended set of essential tags
- **Cover art embedding** for individual tracks, with automatic resize to 500×500
- **Native desktop UI** built with PySide6
- **Standalone `.app` / `.exe` bundles** via PyInstaller

## Downloads

Pre-built binaries are available on the [Releases](https://github.com/RifqiWasntHere/Rip-Tags/releases) page.

| Platform | Status |
|----------|--------|
| macOS `.app` | Available |
| Windows `.exe` | In development |

> macOS builds are unsigned, so Gatekeeper may warn you on first launch. Right-click the app and choose **Open**, or allow it in **System Settings → Privacy & Security**.

## Run from source

```bash
bash MacOs/setup.sh   # creates .venv and installs dependencies
bash MacOs/run.sh     # launches the PySide6 UI
```

## Build the macOS app

```bash
bash MacOs/build.sh
```

The compiled `.app` will appear at `dist/Rip Tags.app`.

## Supported files

- `.flac`
- `.m4a`
- `.mp4`

Preview mode is enabled by default. Disable it when you are ready to write changes to your files.
