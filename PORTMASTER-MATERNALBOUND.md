# PortMaster: MaternalBound Redux on RG35XX-H

Status: port investigation / implementation plan. This is not yet a playable PortMaster package.

## Target and scope

- Device: Anbernic RG35XX-H, KNULLI, ARM64 Cortex-A53.
- Game: MaternalBound Redux only; no Original EarthBound mode selector.
- Input ROM: the owner's clean EarthBound (USA) ROM at `ROM/` in the installed port directory.
- First-run setup: run on-device, validate the ROM, obtain the pinned Redux source, compile the Redux adaptation, generate the native asset pack, and retain generated assets for later launches.
- Runtime: native C game executable; Python is for first-run conversion only.
- Diagnostics: `log.txt` in the installed port directory. Never log or upload ROM bytes, generated asset packs, saves, or private working ROMs.
- Exit: standard PortMaster/KNULLI controller and process-exit behavior.

## Findings from the source audit

1. This repository's `scripts/prepare_port_sources.py` downloads a pinned native foundation and SDL source, then applies the repository's native patches. The native source is intentionally ignored by Git and is not vendored.
2. `scripts/build_portable_helpers.py` builds `redux-setup` with PyInstaller. It pins CoilSnake, CCScript, and CCScriptWriter, applies local compiler fixes, installs the native Python package and bundles dependency licenses.
3. `scripts/redux_setup_entry.py` provides a frozen setup entry point, downloads the checksum-pinned source archive over verified HTTPS, and delegates conversion to `build_redux_profile.py`. The download URL now uses `CrispyBuns/MaternalBound-Redux` at the existing audited revision `897d00833f4a08a0a92f106abf631629a6a6a041`; the latest `main` commit is not silently substituted because it has not been audited against the native converter.
4. The current setup profile expects the clean USA ROM SHA-256 `A8FE2226728002786D68C27DDDDF0B90A894DB52E4DFE268FDF72A68CAE5F02E`, then checks the pinned Redux revision and output checksums. The existing conversion pipeline should be reused rather than replaced with a generic IPS patch step.
5. The desktop packaging workflow is not a PortMaster build: its Linux target is x86-64, assumes a desktop session, and uses a glibc 2.38+ environment. We must make a separate ARM64 build and explicitly validate KNULLI graphics/input/runtime compatibility.
6. The upstream native foundation's redistribution and combined-license compatibility require review before publishing a binary package. The GPLv3 terms of MaternalBound Redux do not themselves settle the native foundation's license.

## Implementation sequence

1. Add a manual ARM64 CI build for the native game and setup helper; do not include any ROM or generated game data.
2. Configure SDL for the actual KNULLI/PortMaster display backend. Confirm whether the target should use PortMaster-provided SDL libraries or a statically built SDL with the required EGL/KMSDRM support; do not assume desktop X11 is available.
3. Add a PortMaster launcher that resolves paths relative to its own file, checks for `ROM/`, runs setup only when the validated Redux assets are absent, and starts the native game from the persistent data directory.
4. Capture stdout/stderr and setup stages into `log.txt`, preserving the log on failure and avoiding duplicate extraction on subsequent launches.
5. Package the game, setup helper, launcher, required licenses/notices and PortMaster metadata. Keep ROMs, asset packs, saves, source archives and build outputs out of Git and CI artifacts.
6. Test on the RG35XX-H: first-run valid ROM, invalid ROM, network/download failure, interrupted conversion, relaunch without re-extraction, controller input, audio, save persistence, and clean exit.

## Current blockers / verification gates

- No ARM64/KNULLI build has been run yet.
- PortMaster SDL/display backend and runtime library availability must be confirmed before declaring the binary compatible.
- PyInstaller's ARM64 Linux output must be built for a compatible userspace and tested on-device; a desktop Linux binary is not assumed portable to KNULLI.
- No ROM, copyrighted game assets, generated pack or save file may be committed or packaged.
