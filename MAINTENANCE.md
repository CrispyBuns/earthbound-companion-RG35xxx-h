October 16, 2026: **Windows1.0.9 / platform preview.21** add a cinematic-letterbox toggle and preserve scripted timing waits with Quick dialogue. All six packages published and verified. [Release notes](docs/RELEASE-1.0.9.md).

October 15, 2026: **Windows 1.0.8 / platform preview.20** fix Instant text ignoring character delays and names appearing all at once. The shared fix covers Original and pinned Redux. [Focused checks](docs/RELEASE-1.0.8.md).

October 15, 2026: **Windows 1.0.7** fixes optional soundtrack downloads blocking game setup, adds verified retry/fallback sources and records useful host/track diagnostics. Native gameplay is unchanged. [Focused checks](docs/RELEASE-1.0.7.md).

# Completed feature set and maintenance

## 1.0.4 / platform preview.15 - battle palettes and Windows icon

Fix incorrect brown/gray battle backgrounds and orange HP/PP card borders in Original and MaternalBound Redux. SNES Mode 0 background layers now select their own color banks. New games initialize the normal HP/PP border palette; affected existing saves display normally without restarting.

The Windows game executable now uses the Companion icon, matching the launcher. Saves, achievements, game data and the pinned Redux source remain compatible. No ROM or game assets are included.

Focused before/after battle fixtures reproduced the palette problems locally on Windows with both editions. Additional gameplay, Android-device and emulator tests were skipped at the owner's request; community testing is needed on the rebuilt packages.


## 1.0.3 / platform preview.14 — Tessie save recovery

Fix a save-loading repair that marked Jeff as having reunited with Ness during his solo Winters chapter. That made the tent cook skip enabling Tessie. Existing affected Redux phone saves and quick-saves recover on loading: visit the cook, accept the stew/sleep again, then walk onto the shore tip.

The fix is shared across Windows, Linux/SteamOS, macOS Intel/Apple Silicon and Android ARM64/x64. Game data, saves, achievements and the pinned Redux source remain compatible. No ROM or game assets are included.

The fix was reproduced and checked locally on Windows before publication. This release rebuild runs no additional gameplay or runtime tests, as requested; community testing is needed on the other platforms. Prior releases' test results are not presented as tests of these packages.


October 13, 2026: **Windows 1.0.2 / platform preview.13** extend Redux battle Lifeup across widescreen and correct Android Settings/portable control labels. Wide FOV On keeps the wide view through dialogue and menus. [Focused checks](docs/RELEASE-1.0.2.md).

October 13, 2026: 1.0.1 addresses reported NPC/foreground overlap, the scripted Onett intro pan and fast-forward music. [Focused checks](docs/RELEASE-1.0.1.md). No campaign replay or broad audit was started.

October 13, 2026: **Windows 1.0.1 was the first maintenance release** following the official
1.0.0 feature set, retaining the pinned Redux input
`897d00833f4a08a0a92f106abf631629a6a6a041`. The launcher and release wording
reflect completion; game data, saves, seed identities and earned achievements
retain their existing formats. Future work is focused fixes for reported bugs.
Linux/macOS/Android now use community preview.13 with optional Android touch controls. Newer upstream Redux
changes and Deluxe are separate work. [Release record](docs/RELEASE-1.0.0.md).

October 13, 2026: dev.38 corrects the Redux battle portrait padding/priority reported by **raid_rgb on Discord**. [Focused checks](docs/RELEASE-dev38.md). Shadow's widescreen CCS was reviewed and a native source map prepared; no widescreen redesign or full campaign audit was started.

October 12, 2026: dev.37 addresses two remaining community reports: shared black outlines during sprite overlap and scenery phase during scripted event fades. Additional testers report completing both editions. [Focused checks](docs/RELEASE-dev37.md); no new feature expansion or broad audit.

October 11, 2026: dev.36 addresses community sprite-overlap and doorway/fade camera reports, and adds the requested controller hold-fast-forward and in-game achievement browser with optional sound. The 46-entry set is unchanged. [Focused checks](docs/RELEASE-dev36.md).

October 11 maintenance: dev.35 fixes a tester-reported fractional-camera snap
when overworld dialogue opens/closes. This is a focused display regression fix;
the feature freeze and achievement set remain unchanged. See docs/RELEASE-dev35.md.

October 11, 2026: the owner earned all five pilot achievements and explicitly
requested the full-game expansion and public release. Dev.34 adds 46 standalone
achievements; [set and coverage](docs/ACHIEVEMENTS.md), [release checks](docs/RELEASE-dev34.md).
The rest of the maintenance scope remains unchanged. This does not reopen a
broad gameplay/patch audit or require another owner full playthrough.

Active feature development was first wrapped at **v0.5.0-redux-dev.32** on
October 8, 2026. The requested follow-ups through dev.38 are included in the
official 1.0.0 feature set. Completion does not certify exhaustive compatibility.

[Latest Windows release](https://github.com/rages4calm/earthbound-companion/releases/latest) · [Other platforms](docs/PORTABILITY.md) · [Frozen baseline](https://github.com/rages4calm/earthbound-companion/releases/tag/v0.5.0-redux-dev.32) · [Community testing](docs/COMMUNITY-TESTING.md) · [Developer tools](docs/TESTING.md)

October 9 maintenance update: **dev.33** implements the owner-requested scrolling, widescreen encounter and shader preset work. The original freeze and campaign limits remain; [dev.33 evidence](docs/RELEASE-dev33.md) records the new bounded tests.

## Frozen scope

The scope includes Original EarthBound and the pinned native MaternalBound Redux adaptation, Windows launcher/setup, display and input settings, MSU music, save recovery, native mod profiles and Story Shuffle v4. The [README](README.md#game-features) lists the included features; [randomizer rules](RANDOMIZER.md) distinguish v4 from preserved legacy recipes.

Dev.32 keeps the dev.31 native player and setup helpers. This documentation closeout does not rebuild or replace the game, launcher, packs, release ZIP or installed saves. Baseline ZIP: `EarthBound-Companion-Redux-Tester-v0.5.0-redux-dev.32.zip`; SHA256: `c78d87e7d2c52afa26e1766668bcb6886978825937289c2d0745d69e053d8264`.

Reproducible defects in this scope can receive fixes. New gameplay modes, engine migration, netplay, HD replacement artwork and new general-purpose utilities require an explicitly reopened feature scope. [Toolkit research](research/game-porting-toolkit-reference.md) is a future reference, not a remaining-work commitment.

## What the evidence supports

| Area | Evidence and limit |
|---|---|
| Redux campaign | The owner completed the story through Giygas and credits, reporting defects subsequently addressed. Final testing used equipment/stat boosts. This is real playthrough evidence, not an unboosted or independently automated full-campaign certification. |
| Redux features | No whole normal-play feature is currently confirmed absent in the status records. Exact equivalence of every upstream patch and complete developer/debug-menu parity remain unverified. The target is pinned active source, not the official v1.1 BPS release. |
| Focused regressions | Native menus, equipment, Tools, PSI, story/presentation scenarios, credits/photos and recovery have bounded checks. Reports retain their tested binary/pack identities. Prepared scenes do not establish every natural quest route. |
| Story Shuffle v4 | Four reviewed Original/Redux pack identities each pass 1,000 seeds, 62 combinations and corruption controls. Native consumers, opening/cold restores and selected prepared encounters are covered. A full randomized campaign and every new lineup terrain/render combination remain unverified. |
| Display, input and audio | Automated presentation and soundtrack boundary checks exist. Broader physical hardware/controller behavior, complete listening and every story/music transition remain unverified. |
| Unavailable features | Native Open mode, Ancient Cave, Keysanity and earthbound.app seed compatibility are not included. Arbitrary IPS/BPS game-code patches need their own native adaptations. |
| Distribution terms | Recorded native-foundation licensing and combined GPL distribution questions remain unresolved. Feature freeze does not change that status; see [LEGAL.md](LEGAL.md). |

Details: [Redux status](MATERNALBOUND-NATIVE.md), [dev.31](docs/RELEASE-dev31.md), [dev.32](docs/RELEASE-dev32.md), and [validation records](validation/). Exhaustive coverage is documented uncertainty, not a mandatory queue keeping active development open.

## How maintenance works

1. Collect a report with release, edition/seed, location, smallest reproduction steps and expected/actual behavior. Use the [bug form](https://github.com/rages4calm/earthbound-companion/issues/new?template=bug-report.yml).
2. Reproduce in an isolated session or copied checkpoint. Preserve owner progress and record the exact build, pack, seed and settings.
3. Investigate the reported subsystem. Use an existing focused fixture or add a small regression that detects the actual defect. Do not automatically start a whole-project source audit, agent review or full campaign.
4. Fix the cause and run the affected checks. Broaden only if evidence shows a shared risk. Preserve legacy seed semantics and save compatibility, or document an explicit migration requirement.
5. Publish the fix with exact coverage and uncertainty. New binaries still need appropriate package/setup/recovery checks; this documentation-only closeout does not replace them.

The owner and volunteers do not need another full playthrough. Short reports during ordinary play are useful. Reports are handled when brought to the project; no automatic issue monitor or scheduled audit has been enabled.

## Historical audits

Earlier scripts, source comparisons, release notes and failed diagnostic evidence remain available for specific reproductions. They are historical tools and records, not instructions to rerun all suites or finish every theoretical comparison. A broad audit requires an explicit new request with a bounded scope.
