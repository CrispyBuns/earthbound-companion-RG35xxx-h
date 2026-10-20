# 1.0.12 / platform preview.24: SteamOS Redux setup

Fixes [issue #6](https://github.com/rages4calm/earthbound-companion/issues/6):
Redux setup could stop with "Select an ordinary installation folder, without
redirected paths" when a Unix home or application-data directory used symlinks.
The configured app-data root and its ancestors are now accepted on Unix.
Redirected files and folders inside a profile remain blocked. Windows path
checks are unchanged. Existing game data, saves and content identities are retained.

Focused synthetic path tests passed on Linux and Windows, including linked home
and data roots, blocked profile redirects and unchanged outside sentinel files.
The reporter's physical SteamOS handheld was not reproduced. Earlier maintenance
fixes remain included; full campaigns were not repeated.
