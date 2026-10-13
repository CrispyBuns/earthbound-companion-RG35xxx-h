# Dev.38 — Redux battle portraits

Reported by **raid_rgb on Discord**, the selected character's entire body was
visible above its HP/PP box. The upstream Bowspr loader pads a 24-pixel sprite
to 32 pixels with a blank first row. Companion's direct renderer omitted that
padding, placing the artwork eight pixels too high.

The native portrait renderer preserves the source padding and OBJ priority 2.
The lower body sits behind the HP/PP box, and UI/PSI layers retain their intended
priority. Selection, raising/lowering, victory and normal/Magicant/robot variants
retain the existing state layout. No game-data or save migration is required.

## Focused verification

- The source-derived comparison covers 240 raising cases: one to four party
  members, each selected slot, eight animation steps, and normal/Magicant/robot
  variants. All 215,040 pixel/color/priority comparisons pass.
- The dev.37 binary fails 102,032 comparisons. An explicit old-portrait-source
  control linked to the current library reproduces those same failures.
- The production native executable renders a prepared four-member battle menu
  with its real HP/PP boxes; its portrait occlusion was visually checked.
- Existing native portrait checks cover 12 variants, selection, victory and
  cleanup. Original/Redux save round-trip, cold perturbation, crash-safe and
  pointer-rebinding checks pass, as do 21 transition cases per edition.
- All five public patches reconstruct the 16 changed source files, including
  the portrait renderer, from the pinned native foundation.

The comparison uses the newest upstream ROM at revision
`0659fdfc54ec962859af27deb5b04c49c6024a55`, privately produced from the owner's
clean ROM and its checksum-verified BPS patch. The Companion conversion target
remains its existing pinned Redux revision. All 68 PSI animations' normalized
data match that latest ROM, but this does not certify every final rendered PSI
frame, palette interaction or natural battle/cutscene.

These are focused source/pixel checks and prepared scenes, not another campaign.
Linux, macOS and Android remain community previews. [Recorded results](../validation/battle-portraits-dev38.json).

## Widescreen source reference

Shadow's supplied CCS file was reviewed separately. Companion's expanded view
uses the native C engine rather than an ASM ROM patch. The [source map and
porting notes](WIDESCREEN-PORTING-NOTES.md) identify the relevant map/camera,
actor bounds, spawning, renderer, battle/UI and presentation code. The reference
bundle contains source only; no ROM, extracted game data or save is included.
