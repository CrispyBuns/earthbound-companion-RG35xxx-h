# Dev.36 — sprite overlap, transitions and requested controls

Community testers reported transparent-looking edges when Ness overlapped other
sprites, and a small scenery jump at door/fade boundaries. The optimized renderer
used a compact sprite-list index to look up the party mask, instead of the
original OAM slot. This could separate the wrong pixels from the scenery. The
renderer now retains the original slot through optimization. Camera presentation
also keeps its fractional phase through ordinary overworld door/teleport fades;
force blank, scripted scrolling and dedicated camera scenes keep their guards.

The controller fast-forward binding now works while held. L2/LT and R2/RT can be
selected in Controls; the Gameplay multiplier controls the speed. Releasing the
controller restores normal speed unless keyboard fast-forward was already
latched. The keyboard remains a toggle.

The command menu's Set Up screen now includes Achievements. It shows the existing
46-entry catalog, earned stars, locked icons, progress and earned dates. Up/Down
selects entries, Left/Right pages, and B/Select returns. A generated two-note
unlock chime can be disabled in launcher audio settings. Existing progress loads
silently. These additions keep the achievement IDs, profile format, save ABI,
game assets and randomizer recipes unchanged.

## Focused verification

- A synthetic sparse-OAM overlap fixture fails 192 of 384 mask checks with the
  previous renderer and passes all 384 with the fix, including identical colors
  and both sprite orders. A copied checkpoint supplies four actual party sprites
  for an arranged overlap fixture; the source checkpoint stays unchanged.
- Prepared Onett door, teleport and brightness-fade drivers retain camera phase
  through their tested boundaries. The achievement screen retains phase while
  opening, paging and closing. Crisp, Scale2x and linear filters are exercised.
- Original and Redux achievement consumers pass all 46 definitions. Every browser
  selection is checked against framebuffer guards and the tightest 179-row crop.
  A rendered Redux browser uses a copy of the owner's profile and retains all
  five earned dates. The browser's transient state is outside saved game data.
- Input fixtures exercise both trigger bindings, hold/release, keyboard latch
  interaction and focus loss. The generated chime passes stereo, amplitude and
  completion checks. Physical controller and listening tests remain unverified.
- Save-state and screen-transition checks pass in both editions; Redux movement
  and PSI playback checks also pass. Launcher tests cover sound preference
  persistence and native INI output. The five public native patches reconstruct
  the changed files exactly from the pinned upstream source.

- The extracted Windows ZIP passes launcher self-tests, all six production
  launcher scenarios and the full 46-achievement consumers in both editions.
  Every packaged file matches its manifest; no game content is present in the ZIP.
  Both retained installs receive the tested programs. All 29 protected asset,
  save, settings and progress hashes remain unchanged, and the installed player
  cold-loads a copied endgame checkpoint.

- All five [platform CI jobs](https://github.com/rages4calm/earthbound-companion/actions/runs/38193083711) pass, including shared native input/chime tests, portable launcher tests, desktop startup, and Android emulator startup. Runtime code is verified at `33dcd11`; later changes record documentation and package evidence.

- All five downloaded platform packages pass content/path and native architecture checks. Desktop archives include their setup helpers and required license notices; both APKs contain the expected native/SDL/managed runtime libraries. Package hashes are recorded below.

These are focused fixtures on Windows, not a new campaign or every NPC/map.
Linux, macOS and Android remain community previews; build/startup evidence does
not establish natural gameplay on every platform or device.

[Recorded results and package checks](../validation/render-input-dev36.json).
