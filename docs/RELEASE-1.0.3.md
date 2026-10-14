# EarthBound Companion 1.0.3 / platform preview.14

Fix a save-loading repair that marked Jeff as having reunited with Ness during his solo Winters chapter. That made the tent cook skip enabling Tessie. Existing affected Redux phone saves and quick-saves recover on loading: visit the cook, accept the stew/sleep again, then walk onto the shore tip.

The fix is shared across Windows, Linux/SteamOS, macOS Intel/Apple Silicon and Android ARM64/x64. Game data, saves, achievements and the pinned Redux source remain compatible. No ROM or game assets are included.

The fix was reproduced and checked locally on Windows before publication. This release rebuild runs no additional gameplay or runtime tests, as requested; community testing is needed on the other platforms. Prior releases' test results are not presented as tests of these packages.

[Focused diagnosis and earlier local checks](../validation/tessie-save-repair-2026-10-14.json).

[Package builds and upload checksums](../validation/release-1.0.3.json).
