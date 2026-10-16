# 1.0.9 / platform preview.21: cinematic letterboxing and scene timing

**Display > Cinematic letterboxing** now controls Redux story-scene black bars on
Windows, Linux, macOS and Android. Switch it off to keep scenery visible during
those scenes. Classic preset disables it; other existing settings retain Redux's
presentation. Ordinary aspect-ratio borders and battle masks are unchanged.

Quick dialogue still skips letter typing, but no longer automatically cancels
scripted text-speed waits. This preserves scene/music timing before battles;
original button cancellation remains available. Disabling cinematic bars preserves
their scripted opening/closing durations.

Focused fixtures passed with both editions (Original513 / Redux570 checks), including
hidden bars, live re-enabling, battle-mask ownership, close completion, scripted
waits and the earlier dialogue/save checks. Windows launcher build and shared
portable settings checks passed. The reporter's exact battle-entry scene was not
reproduced, and physical Android gameplay/full campaigns were not repeated.
Existing saves, packs, achievements, touch controls and setup fixes are retained.

Addresses [issue #3](https://github.com/rages4calm/earthbound-companion/issues/3).
Deluxe is not part of this update.
