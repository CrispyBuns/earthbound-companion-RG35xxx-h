# Android preview.12

Android handheld users can hide the complete touch-control overlay in
**Controls → Show touch controls**. Save settings to apply the choice. Android
Back reveals the buttons temporarily so Settings remains accessible; the next
return to the game applies the saved preference again. Existing settings keep
touch controls visible until the user changes them.

The setting is stored in the launcher's existing JSON. It does not change the
native settings ABI, game data, saves, controller bindings or achievements.
Both APKs use the existing application ID and signing certificate. Install an
update over the existing app; uninstalling deletes its private data.

This is an Android-only release. Windows remains at 1.0.1 and Linux/macOS at
preview.11. The APKs retain byte-identical native game/SDL libraries from
preview.11, including its overlap, Onett intro and fast-forward music fixes.

Focused checks cover shared settings persistence and the old-JSON default,
display presets preserving the overlay choice, Windows/UI build guards, both
Android managed/Java builds, APK architecture/content/manifest checks and
persistent-key signature verification. Private emulator checks and package
hashes are recorded in [the validation receipt](../validation/android-overlay-preview12.json).

On the Android API 37 x64 emulator, the default overlay contained 20 buttons;
disabling the setting removed all 20. Cold app restart retained the choice.
Android Back revealed the buttons in the same game Activity; a second Back
returned to the launcher and wrote a checkpoint. Controlled return intents
changed visibility without restarting the native process. Reinstalling the APK
preserved all 78 checked private app files. All three existing ROM-free native,
managed JSON and embedded converter/compiler-order smoke checks passed.

The normal touch Settings pause/save/return chain was not observed during the
bounded intro replay; the live intent handling was tested separately. The
emulator also exposed an inherited same-process game relaunch failure after
quit; a cold app restart was used. Its existing 16 KB library compatibility mode
remains a device-testing limit. No emulator capture or game data is published.

No new native engine rebuild, physical handheld/controller test, full ROM setup
conversion or campaign replay is claimed for this overlay update. The existing
ROM-free embedded converter/native checks are retained. ROMs, game packs and
private emulator captures are excluded from the public release.
