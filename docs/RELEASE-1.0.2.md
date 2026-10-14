# EarthBound Companion 1.0.2 / platform preview.13

Android's touch **Settings** button was sending the native Zoom action. This
could select close-up zoom, which temporarily pulls back to fit dialogue and
menus. The button now pauses and opens Settings. Android also resumes correctly when Save/Return is processed before the game Activity returns to the foreground. Ordinary backgrounding still preserves an intentional Pause. The portable Controls page
also labels actions in their actual native order; Windows bindings are unchanged.

For the zoomed-out widescreen view, keep **Wide FOV On**. If the old button
already zoomed in, open the game's own **Set Up → Wide FOV** and switch Off, then On once. The launcher checkbox alone does not reset an existing close-up camera. This restores the wide
view without changing the touch-overlay preference. Dialogue and menus retain
the wide framing and show their complete windows.

Redux's full-field battle Lifeup animation now covers the widescreen gutters.
Only that supported full-field effect is widened. Single-target Freeze and
other effects retain their target bounds. The tested pinned Redux scripts use
a pause, rather than a visible Lifeup animation, outside battle; a reported
overworld effect has not yet been identified.

## Focused checks

- Fourteen private Original/Redux cases cover dialogue, Goods, Equip, Status,
  Crisp Pixels/integer scaling, antialiasing/noninteger, 4:3 and ultrawide.
  The wide crop remains constant and tested menu pixels stay visible.
- Actual SDL actions reproduce the old Zoom/menu pullback and verify Settings
  preserves the wide view. A shared action guard checks portable labels and
  Android's touch action against the native enum in platform CI.
- Final production PSI checks cover 204 Original and 408 Redux prepared cases.
  All six Redux Lifeup cases fill the gutters; every other effect stays bounded.
  Separate PPU comparisons retain all original 256x224 pixels and all 67 other
  Redux effects. Cold pointer rebinding and edge-target Freeze are checked.
- Both editions' save serialization, screen transitions and achievements pass;
  Redux battle portrait/motion checks and all five source patches pass.

These are focused prepared/cold-restore checks. No new full campaign or physical
handheld/controller testing is claimed. Existing game packs, saves, settings and
earned achievements retain their formats. Redux remains pinned to 897d0083.

Package, Android emulator and publication receipts are recorded in
[the validation record](../validation/release-1.0.2.json).

## Android replay and publication

On the Android API 37 x64 emulator, actual touch Settings/Save/Return flows pass
in startup, a private synthetic Onett party, Goods and item dialogue. Rendering
continues in the same native Activity/process. WideFOV remains enabled; tested
background and Goods-window regions are pixel-identical across Settings.
Hidden controls persist through return and cold restart; Back reveals all 20
buttons temporarily, and saving restores the hidden choice. APK update retained
all 83 checked private app files. Both APKs retain the project signing certificate.

The exact signed x64 APK also passes an independent API 35 ROM-free startup and
rotation replay. The rebuild's original rotation assertion counted a cold-boot
display recreation before the rotation test; the corrected test compares against
its own baseline and still rejects any new recreation during rotation.

Windows 1.0.2 is installed and GitHub Latest; preview.13 is a community prerelease.
All six uploaded package digests match the verified files. Windows/desktop packages
were built from 69166a3; Android from 657856a4, adding only the Android pause-return
fix. A private compile confirms that change leaves the Windows input object byte
identical. Source reconstruction retains all five patches and the portrait fix.

These checks do not qualify physical ARM handhelds/controllers, predictive Back,
another complete campaign or a fresh ROM-conversion run. Same-process game relaunch
after quitting was not requalified; cold app restart was used. User pause retention
is covered by the 16-case host SDL event-order fixture, not an emulator claim.
