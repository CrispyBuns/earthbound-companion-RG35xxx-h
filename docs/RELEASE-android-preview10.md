# Android preview.10: ROM setup on the device

Android handhelds, tablets and phones can now set up Original and the supported
MaternalBound Redux edition directly from a clean EarthBound (USA) ROM. Choose
the matching **Set up … from ROM** button in **Game & setup**, pick the ROM,
wait for completion, then press **Play**. A computer is no longer required.

Original conversion works offline. Redux downloads the checksum-pinned source
archive for `897d00833f4a08a0a92f106abf631629a6a6a041` over verified HTTPS, then
compiles and converts it on the device. It also supplies Original data when
needed. Headered clean ROMs are accepted. Existing game packs, profiles and
saves are preserved; unsupported or patched ROMs produce an error. The setup
log can be exported from the same page.

The APK embeds Python 3.13 and Chaquopy 17.0, with cross-compiled CCScript and
compression extensions. The same audited Original pack, compiled Redux ROM
and current Redux pack checks remain enforced. No ROM or generated game data
is distributed. The game engine and SDL libraries are byte-identical to
Android preview.9; this update changes setup and the launcher.

## Verification

- Both ARM64 and x64 APKs build, pass manifest/payload/signature checks and use
  the existing project signing certificate.
- Android 15 x64 emulator: normal Android file picker conversion of Original
  and Redux, automatic edition selection, and game launch/rendering passed.
- Android 17 x64 emulator: embedded imports/native compiler ordering,
  settings/recipe serialization, SDL/native startup, exact conversion hashes,
  headered-ROM setup and invalid-ROM rejection passed. Existing packs, profile
  metadata and a sentinel file remained unchanged; setup staging was removed.
- Host rejection tests cover truncated, invalid-sized and headered invalid
  inputs. Windows builds without warnings/errors; portable path, settings and
  phone-save recovery checks pass. HTTPS verification regressions pass.

These are focused setup/startup checks. ARM64 physical devices, controllers,
audio quality, long sessions and full Android campaigns still need community
testing. The Android 17 emulator uses compatibility mode for existing graphics
dependencies on 16 KB page-size systems; native 16 KB device support is not
claimed by this preview.

Windows **1.0.0** remains the official Latest release. Linux/macOS remain on
**preview.9**. Android uses **preview.10**. Install the new APK over the existing
preview to retain app data; uninstalling removes app-private saves.

See [PORTABILITY.md](PORTABILITY.md), [the converter build instructions](../Ports/AndroidSetup/README.md)
and [the validation receipt](../validation/android-rom-setup-preview10.json).
