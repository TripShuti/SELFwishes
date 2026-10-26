# Item icons

This directory contains locally served Genshin Impact character and weapon PNGs.
Game artwork belongs to HoYoverse. Download source: https://enka.network/ui/,
using image filenames and item IDs from https://github.com/theBowja/genshin-db
(npm version 5.2.14). The catalog's MIT license is included alongside this file.

Refresh with `node scripts/update_item_icons.mjs [version]` from the repository
root (requires Node 20+, tar, and network access). No download is needed during
Docker builds or normal use. The refresh script preserves existing icons if an
upstream image is unavailable. Unknown items display a rarity-colored placeholder.

The UI matches item IDs first, then translated names for old imported records
without IDs. Images are lazy-loaded from this server, not external hosts.
