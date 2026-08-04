import os
import sys
import glob

block_cipher = None

ROOT = os.path.abspath('.')
VENV = os.path.join(ROOT, '.venv')

# Find the correct site-packages directory regardless of Python version
SITE_PACKAGES = None
for py_dir in os.listdir(os.path.join(VENV, 'lib')):
    candidate = os.path.join(VENV, 'lib', py_dir, 'site-packages')
    if os.path.isdir(candidate):
        SITE_PACKAGES = candidate
        break

if SITE_PACKAGES is None:
    raise RuntimeError("Could not find virtual environment site-packages")

import PySide6

pyside_pkg = os.path.dirname(PySide6.__file__)

# Use platform-specific icon formats for best results
if sys.platform == 'darwin':
    APP_ICON = os.path.join(ROOT, 'Rip-Tags.icns')
elif sys.platform == 'win32':
    APP_ICON = os.path.join(ROOT, 'Rip-Tags.ico')
else:
    APP_ICON = os.path.join(ROOT, 'Rip-Tags.png')

def collect_dist_info(package_name):
    pattern = os.path.join(SITE_PACKAGES, f'{package_name}*.dist-info')
    matches = glob.glob(pattern)
    if matches:
        return [(matches[0], os.path.basename(matches[0]))]
    return []

dist_info_datas = []
for pkg in ['mutagen', 'pillow', 'PySide6', 'PySide6_Addons', 'PySide6_Essentials', 'shiboken6']:
    dist_info_datas.extend(collect_dist_info(pkg))

pyside_plugins = os.path.join(pyside_pkg, 'Qt6', 'plugins')
pyside_translations = os.path.join(pyside_pkg, 'Qt6', 'translations')

datas = [
    (os.path.join(ROOT, 'Rip-Tags.png'), '.'),
    (os.path.join(ROOT, 'rip_tags'), 'rip_tags'),
]

if os.path.isdir(pyside_plugins):
    datas.append((pyside_plugins, 'PySide6/Qt6/plugins'))
if os.path.isdir(pyside_translations):
    datas.append((pyside_translations, 'PySide6/Qt6/translations'))

datas.extend(dist_info_datas)

hiddenimports = [
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'mutagen',
    'mutagen.flac',
    'mutagen.mp4',
    'mutagen.id3',
    'PIL',
    'PIL.Image',
    'PIL.ImageOps',
]

a = Analysis(
    ['app_entry.py'],
    pathex=[ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'tkinter', 'pytest', 'IPython', 'jupyter', 'streamlit', 'pandas', 'numpy', 'pyarrow', 'tornado', 'protobuf'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Rip Tags',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=APP_ICON,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Rip Tags',
)

app = BUNDLE(
    coll,
    name='Rip Tags.app',
    icon=APP_ICON,
    bundle_identifier='com.riptags.app',
    info_plist={
        'CFBundleShortVersionString': '0.1.0',
        'CFBundleVersion': '1',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15',
    },
)
