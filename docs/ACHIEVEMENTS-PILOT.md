# Local achievements pilot — October 11, 2026

Historical record of the owner-tested five-achievement pilot. The subsequent
owner request expands it to the public [46-achievement set](ACHIEVEMENTS.md) in
[dev.34](RELEASE-dev34.md). The statements below describe the earlier local pilot.

Explicit owner-requested feature work on `feature/companion-achievements`, based
on platform preview commit `06aef537a15baf1ea51eda10224330e908f4299e`.
Published Windows dev.33 and platform previews are unchanged. This branch is a
local pilot; it does not reopen unrelated feature work or the broad patch audit.

## Implemented

A small independently MIT-licensed C event engine is vendored under
`Achievements/Core`. EarthBound's native adapter, launcher and surrounding code
retain their existing license. The engine has no platform, renderer or network
dependency. A second game supplies its own definitions, events and storage host.

| Achievement | Completed action |
|---|---|
| Morning, Onett | Onett daybreak story flag 422 |
| Meteor Patrol | Victory containing Starman Junior, enemy 214 |
| Arcade Peacekeeper | Frank's completed challenge, story flag 64; partial flag 515 does not count |
| First Fight, First Win | One normal or instant victory |
| Getting the Hang of It | Five normal or instant victories; replayed battles count |

Names, descriptions and code are original. No RetroAchievements badge, set or
achievement logic was copied. This is a five-achievement casual starter set.

The Windows and portable launchers have an Achievements page with progress,
unlock dates, edition selection, refresh and a tracking switch. The switch applies
on the next game launch. Notifications last four real-time seconds and stay
inside the centered 234×179 area shared by the supported crops and Zoom In.
The popup uses the host scanline overlay and does not write to game VRAM.

## Progress and saves

Profiles live in this project's `UserData/Achievements` directory. Windows uses
the installation's existing user-data folder; portable previews use their
existing platform data root. Android uses its app-private project directory.
Each edition writes `earthbound-<edition>.json`, where edition is `original`,
`redux`, `shuffle-original` or `shuffle-redux`. Story Shuffle progress is shared
across seeds within that edition. Each installation/project owns its local
progress. The owner selected standalone per-game achievements; accounts,
servers and cloud synchronization are outside the planned scope.

Progress is separate from phone saves and quick states. Already unlocked
achievements stay unlocked after reload. Existing saves can silently credit
daybreak and Frank from their verified story flags during gameplay; historical
battle counts and Starman Junior victories are not invented from a late save.

The adapter holds an OS lock, validates schema and records, then writes flushed
temporary snapshots before atomic replacement. Notifications follow successful
storage commits. An unavailable, locked, corrupt or newer-format profile disables
tracking for that session without stopping the game or overwriting its profile.

Direct desktop launches use the same default achievement directory. Options:

```text
--achievements-dir ABSOLUTE_DIRECTORY
--no-achievements
--achievement-shuffle
```

`--achievement-shuffle` is passed automatically for launcher-generated seeds.
Existing headless checks default to tracking disabled unless given an explicit
achievement directory. Launcher test launches also explicitly disable tracking.

## Build and focused verification

Prepare a fresh native tree with `scripts/prepare_port_sources.py`. It applies
the Companion, portable and additive achievements patches in that order. Build
the native game normally; CMake links the vendored core. Do not reset an existing
modified native checkout. The core's upstream files and hashes are recorded in
`Achievements/Core/SOURCE.json`.

Run the core CMake/CTest suite in the standalone CompanionAchievements project,
or compile the vendored test against its header and source. The native smoke tool
requires a **new private output directory** and local packs:

```text
python Achievements/tests/native_smoke.py --game /path/to/earthbound --original-pak /private/assets.pak --redux-pak /private/redux/assets.pak --output /new/private/test-directory
dotnet run --project Ports/Tests/Companion.Portable.Tests.csproj -c Release
```

`--selftest-achievements` exercises actual story setters, the normal victory
phase, a defeat negative control and the instant-win setup. It requires an
explicit private achievement directory. `--achievement-demo` is a visual fixture
that uses the same checks and continues rendering; it also requires a private
directory. These fixtures synthesize results for QA and must not be used with a
player's real achievement profile.

Executed locally on Windows:

- Shared C engine: 24 checks, including commit failure, saturation, silent restore
  and isolation between engine instances; compiled with warnings treated as errors.
- Native Original and Redux: story flags, partial-Frank negative control, Starman
  membership, real normal/instant victory consumers, defeat rejection, duplicate
  milestones, restart persistence, shuffle isolation and scanline bounds.
- Storage: corrupted/unsupported profiles preserved, unavailable storage,
  tracking disabled, headless default, concurrent writer refusal and lock release.
- Windows launcher publish and portable desktop compile; common parser checks
  for missing, valid, inconsistent and unsupported profiles. Achievements page
  visually reviewed at the launcher's minimum window size.
- Six existing production launcher configurations, including Original/Redux,
  Shuffle and title-presentation options, pass with the new native arguments.
  Direct Windows launch selects its own project's achievement directory.
- Popup captures at 4:3, 16:9 and 21:9 on the owner's Windows monitor.
- Copied latest Redux checkpoint cold-load; existing story credit is silent.
  All 46 protected live installation/data hashes remained unchanged.

These are bounded fixtures, not a new full campaign. They do not establish
natural reachability of every achievement in every mod/seed. Linux, macOS and
Android execution is not verified for this pilot. A full achievement set and
other actual game integrations remain future work. Competitive anti-cheat is
not implemented. No private packs, ROMs, saves, screenshots or fixture progress belong
in a public source/package release.
