# Widescreen source reference for Shadow

Companion runs the native C engine documented in [UPSTREAM.md](../UPSTREAM.md).
Its widescreen view uses C gameplay and renderer changes, rather than an ASM
patch applied to the ROM. There is no Companion widescreen ASM file to translate
directly into CCS. The base engine already supplies an expanded viewport;
Companion extends its presentation, spawning, UI and scene handling.

The reference bundle contains complete relevant C/H files, the desktop CMake
configuration, and the five public patches. These are source references, not a
standalone build or a ROM patch. The public bootstrap reconstructs the complete
native source using the pinned foundation and patches. No ROM, extracted art,
soundtrack, executable or save is included.

## His October 13 CCS file

The supplied `eb_widescreen.ccs` credits Raid and GiovannyGB. It expands the
horizontal map span from 34 to 49 tiles, adjusts both scroll triggers, and hooks
the sprite-bound check. Its conditional sprite-bound handler is active; the
older pinned Redux copy instead forces `$FF` at that hook. The map/scroll logic
has the same effective parameters. The supplied file was reviewed as source
and was not applied to Companion's ROM or native code.

[Raid's public CCS](https://github.com/Raid-rgb/Earthbound-Widescreen-patch-for-BSNES-HD/blob/main/eb_widescreen.ccs)
is a ROM-side reference. Its README requires bsnes-hd's expanded display and
sprite support; an ordinary SNES still has its hardware display dimensions.

## Companion code map

Paths below are relative to the reconstructed native source, and to `native/`
inside the source bundle. Consult the actual snapshot files for the full logic.

| Area | Files / entry points | What to study for a ROM-side adaptation |
| --- | --- | --- |
| View dimensions | `src/core/types.h`, `port/unix/CMakeLists.txt` | Native desktop canvas is 512×256; central SNES content remains 256×224. Separate viewport center from central-screen padding. |
| Map load / room limits | `src/game/map_loader.c`: `fill_tilemaps`, `load_map_at_position` | Center BG scroll before loading actors; populate the expanded tilemap, retain collision and room limits, and avoid exposing neighboring rooms. |
| Camera / map scroll | `src/game/overworld.c`, `src/game/map_loader.c`, `src/entity/callbacks.c` | Keep the world, camera, tilemap-ring origin and scroll triggers consistent. |
| NPC and entity bounds | `src/game/map_loader.c`, `src/entity/entity.c`, `src/entity/callbacks.c` | Expand both activation and drawing bounds. Preserve full signed coordinates when actors leave the central screen. |
| Enemy spawning | `src/game/overworld_spawn.c`: `spawn_horizontal`, `spawn_vertical` | Wider drawing alone does not populate the side areas. The horizontal scan covers the viewport plus its original margin: `x_start + 1 + (width + 63) / 64`. Keep original encounter rules. |
| Wider sprite positions | `src/snes/ppu.h`, `src/entity/sprite.c`, `src/snes/ppu_render.c` | The native engine retains full signed OAM coordinates instead of relying only on the hardware's wrapped bytes. This needs emulator-side support or an appropriate representation in a ROM patch. |
| BG / window policy | `src/snes/ppu.h`, `src/snes/ppu_render.c` | World and battle BGs can fill the viewport; menus/title/effects use centered or clamped layers. Keep window masks and scene padding in the same coordinate space. |
| Battle and PSI | `src/game/battle_bg.c`, `src/game/battle_ui.c`, `src/game/battle_psi.c` | Center enemy artwork and the original battle slice. PSI arrangements are a single screen and must not inherit background repetition into the side areas. |
| HP/PP boxes / portraits | `src/game/window.c`, `src/game/window.h`, `src/game/maternalbound_battle_sprites.c` | Keep the boxes inside their tilemap, center the group, and preserve the upstream padded portrait layout and sprite priority. |
| Output framing / smooth camera | `port/unix/platform/sdl2_video.c`, `src/platform/pc_options.c`, `src/platform/pc_options.h` | Aspect ratios, FOV crops and fractional camera presentation happen outside the ROM. Dialogue, menus and event fades retain their appropriate scene phase. |

The most transferable pieces are viewport-aware map loading, entity activation,
spawn coverage, centered battle/UI coordinates and per-scene bounds. The C
renderer-specific full-width OAM, layer policy and fractional presentation need
equivalents in the target emulator; CCS by itself does not enlarge hardware.

## Source and credits

- [Companion patches](https://github.com/rages4calm/earthbound-companion/tree/main/patches) — ordered Companion, portability, achievements, dialogue-camera, render/input patches.
- [Pinned native foundation](https://github.com/seanstaggsQU/earthboundRecompLinux2026/tree/76eacab54b05766b82c98da9c55d94d1236ece03) — Sean Staggs fork → BrianPugh/earthbound → Herringway/ebsrc.
- [MaternalBound Redux](https://github.com/ShadowOne333/MaternalBound-Redux) — ShadowOne333 and contributors; Bowspr by cooprocks123e.
- [Full credits](../CREDITS.md) and [recorded source/distribution terms](../UPSTREAM.md).

The original 256px gameplay logic and story scripts should stay separate from
expanded presentation bounds. Include tests for map entry and scrolling, party
overlap, doors and event fades, dedicated screens, credits, and large-art battles.
These notes do not claim that every possible scene has been certified.
