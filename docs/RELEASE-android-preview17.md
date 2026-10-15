# Android preview.17 - stuck cinematic borders

Fix Redux cinematic black bars remaining over ordinary overworld scenery after a map transition. The force-blank transition now stops the stale cinematic mask. Normal scripted letterbox animations and battle interruption state are preserved.

If an existing quick-save still shows the bars immediately after updating, enter and leave a building once to clear them. No restart or new game is needed.

Includes the battle-color fixes and game icon by princeofdalaam (Discord). Install the ARM64 APK over your current app to preserve saves.

One focused before/after native handler check on Windows reproduced the failure and passed with the fix. No full intro replay or Android device tests were run; community testing is needed. Windows 1.0.5 and Linux/macOS preview.15 downloads are unchanged.
