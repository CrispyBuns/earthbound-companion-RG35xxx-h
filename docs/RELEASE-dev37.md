# Dev.37 — black outlines and event fades

Community testers reported that character outlines could disappear when Ness
overlapped another sprite, and that the scenery still shifted at the start of
some scripted fades. Ordinary building transitions were reported working well.

The presentation mask now retains opaque foreground sprite pixels over the
party, even when both render passes have the same color. This preserves shared
black outlines without changing the original sprite priority or palette. A black
palette entry remains opaque; only transparent sprite pixels are omitted.

Scripted brightness/mosaic fades can reuse the displayed sprites for several
frames. Their unchanged overworld now retains its fractional camera phase during
that wait. The initial coffee/tea fade receives the same treatment; the animated
cutscene keeps its separate framing. Dedicated screens, force blank and scripted
camera moves retain their guards. Save structures, assets, achievement progress,
controls and randomizer recipes are unchanged.

## Focused checks

- The dev.36 reference fails 96 of 384 shared-black overlap coverage checks and
  56 of 98 camera phase checks in the scripted fade fixture. Dev.37 passes them.
- Sparse sprite ordering, shared black outlines at three brightness levels, and
  146 actual pixel-color/priority checks pass. A copied full-party checkpoint
  supplies real sprite artwork for an arranged party/non-party overlap fixture.
- Prepared door, teleport, scripted fade, window fade and initial coffee fade
  drivers pass. The coffee cutscene's later independent screen stays unshifted.
- Crisp, Scale2x and linear presentation are exercised. Dialogue/menu phase and
  the achievement browser's tight Zoom In crop continue to pass.
- Original and Redux save round-trip, cold perturbation, crash-safe and asset
  pointer checks pass, along with 21 screen-transition cases in each edition.
- All five public native patches reconstruct the 15 changed source files from
  the pinned upstream revision exactly after normalizing line endings.

These are focused prepared fixtures and a copied checkpoint, not another full
campaign or every natural NPC/event. Community reports include completed Original
and Redux playthroughs; they are useful feedback, not exhaustive certification.
Linux, macOS and Android remain community previews.

[Recorded results](../validation/render-fades-dev37.json).
