# EarthBound Companion 1.0.4 / platform preview.15

Fix incorrect brown/gray battle backgrounds and orange HP/PP card borders in Original and MaternalBound Redux. SNES Mode 0 background layers now select their own color banks. New games initialize the normal HP/PP border palette; affected existing saves display normally without restarting.

The Windows game executable now uses the Companion icon, matching the launcher. Saves, achievements, game data and the pinned Redux source remain compatible. No ROM or game assets are included.

Focused before/after battle fixtures reproduced the palette problems locally on Windows with both editions. Additional gameplay, Android-device and emulator tests were skipped at the owner's request; community testing is needed on the rebuilt packages.

[Focused checks](../validation/palette-banks-2026-10-14.json).

For Windows source builds, generate the resource with `python scripts/prepare_windows_icon.py <build-directory>/companion-icon.rc` and pass its absolute path as `-DEB_WINDOWS_ICON_RC=...` to CMake.
