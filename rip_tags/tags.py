"""Centralized tag definitions for Rip Tags.

Add or remove tags here to change what appears across the entire app.
No other files need to be edited.
"""

# All tags that appear in the Clean Preferences dialog.
# Order matters — they are displayed in this order in the UI.
ALL_SUPPORTED_TAGS = [
    # Core (Most Common)
    "title",
    "artist",
    "album",
    "albumartist",
    "date",
    "genre",
    "tracknumber",
    "tracktotal",
    "disk",
    "disctotal",
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
]

# Subset of tags kept when the "Recommended" button is clicked.
RECOMMENDED_TAGS = {
    "title", "artist", "album", "date", "tracknumber", "genre",
    "albumartist", "copyright", "composer", "encoder", "cover",
}
