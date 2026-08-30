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

## Version Log

### 1.0.1-beta.2 (2026-08-30)

**Bug fixes**

- **Sort tags are now merged into their regular counterparts on clean.** Previously the cleaner preserved the iTunes sort atoms (`sonm`/`soar`/`soal`/`soaa`/`soco`) and FLAC sort tags (`sort title`/`sort artist`/etc.) as-is, which many players can't read. Now, when a sort tag is kept, its value is written into the standard tag (Title/Artist/Album/Album Artist/Composer — overwriting any existing value) and the sort tag itself is removed, so the metadata is fully readable by any device.

### 1.0.1-beta.1 (2026-08-30)

**Bug fixes**

- **Preview mode now reports correct results.** Previously a dry-run always showed "0 cleaned" because preview results use a `would_clean` status that the summary counters didn't count. Preview now counts those as cleaned, and the details table shows "would clean".
- **Clicking anywhere on a Batch Cleaner row now toggles its selection.** Previously only the tiny checkbox at the left edge responded — clicking a track's row text jumped to the File Viewer and clicking the album row did nothing, so tracks/albums felt unselectable. Now a single click on any part of a track or album row toggles its checkbox, and a **double-click** on a track opens the File Viewer.
- **Fixed selection in folders with more than one track.** In a multi-track folder, toggling one track corrupted the rest (the group's intermediate "partially checked" state was being propagated down to every child, unchecking its neighbors and making re-clicking appear to do nothing). The tri-state is now only ever a group indicator and is never written to child tracks.
- **The version is now visible in the app.** The window title shows `Rip Tags 1.0.1-beta.1` and the status bar shows the version on launch, so you can always tell which build you're running. The `.app` bundle's `Info.plist` also reports the real version instead of the stale hardcoded `1.0.0`.
- **FLAC cover art is now removed when "cover" is deselected.** Previously the cleaner never touched FLAC pictures, so deselecting cover only worked for M4A/MP4. FLAC covers are now reported in preview and removed on a real clean.
- **Folder scanning moved off the UI thread.** Opening a large music library no longer freezes the window; scanning now runs in a background worker with a token guard so stale scans are ignored if you switch folders mid-scan.
- **Fixed a crash if you switched folders while a clean was running.** The results table now uses the folder captured when the clean started.
- **Search filter and selection are now consistent.** Filtering updates group checkboxes and the "N selected" count to match exactly what would be cleaned, and group checkboxes only affect visible files.
- **Sidebar folders are now clickable.** Clicking a folder in the sidebar tree navigates into it and loads it into the Batch Cleaner (previously only "Open Folder" and recent folders did). The sidebar tree depth limit was raised so deep iTunes library paths are reachable.
- **Fixed "Show in Explorer" on Windows.** The `explorer /select,<path>` argument was split incorrectly and would fail.

**iTunes Store purchases**

- **Sort tags are now treated as their base tags.** Purchased iTunes tracks sometimes store Title/Artist/Album/Composer only in the sort atoms (`sonm`/`soar`/`soal`/`soco`) with a "Sort" prefix. The cleaner treated these as unknown junk and would wipe the only copy of the metadata. They now map to `title`/`artist`/`album`/`composer` and are preserved. The now-redundant "Sorting Tags" preference group was removed, and the File Viewer deduplicates tags (e.g. one "Title" row even when both the normal and sort copies exist).

**Polish**

- **Cover info label now populated** with dimensions and file size after upload/resize/remove.
- **"Keep original size" cover uploads preserve the original format** (PNG stays PNG). Resized covers are still optimized to JPEG.
