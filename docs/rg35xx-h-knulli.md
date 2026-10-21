# MaternalBound Redux — RG35XX-H / KNULLI native port

This port targets the **native C game engine** from the repository's pinned
`earthboundRecompLinux2026` source, with the repository's existing native
Companion/Redux patches applied. It does not use the Windows Forms, Avalonia,
or .NET launchers.

## Install

1. Download the `maternalbound-redux-rg35xx-h-knulli-arm64` artifact from the
   successful **RG35XX-H KNULLI native build** GitHub Actions run.
2. Extract the `maternalbound-redux` folder into the device's PortMaster
   ports directory.
3. Put your privately generated MaternalBound Redux `assets.pak` at
   `Ports/maternalbound-redux/gamedata/assets.pak`.
4. Launch `maternalbound-redux.sh` through KNULLI/PortMaster.

Expected layout:

```text
maternalbound-redux/
├── maternalbound-redux       # ARM64 native executable
├── maternalbound-redux.sh
├── README.txt
└── gamedata/
    └── assets.pak            # supplied privately by the user
```

The launcher resolves the pack from its own directory and exports its absolute
path as `EB_ASSETS_PAK`. It does not depend on the process's original working
directory.

## Code-only build

The workflow builds the native C engine for ARM64 using SDL2 and packages only
the executable, launcher, and documentation. It deliberately does not upload
ROMs, generated asset packs, music, or saves. No .NET build or launcher is used
by this workflow.

## Current status and testing

A successful CI compile confirms that the pinned native engine compiles for
the runner's ARM64 Linux environment; it does **not** by itself prove that the
binary matches every library/ABI detail of a particular KNULLI image. Test
startup, video, sound, controls, saves, and long-session stability on the
RG35XX-H. If it reports a missing shared library, capture the exact error and
the KNULLI version so the build can be adjusted to the device's runtime.

The engine's redistribution terms are not fully resolved in the repository's
upstream provenance review. Treat generated builds as personal testing builds
until that is clarified; this workflow does not publish a GitHub Release.
