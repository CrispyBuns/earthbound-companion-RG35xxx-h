# 1.0.8 / platform preview.20: dialogue typing

Companion's **Instant text** option now skips ordinary character typing delays.
Previously it skipped a separate text wait while the normal letter delay still
ran. With Instant text off, the game's Fast, Medium and Slow choices retain their
original two-, three- and four-frame letter cadence.

Player names, battle attacker/target names, item names, teleport destinations and
PSI names now type letter by letter at that same cadence. They previously passed
through immediate-print helpers, making the rest of the sentence feel slower.
Scripted instant-print menus remain immediate, and explicit scene pauses remain.

The fix is shared by Windows, Linux, macOS and Android, for Original and the
pinned Redux adaptation. Existing saves, asset packs and Redux input are retained.
The inline substitution queue fits the existing save-state reserve; the state
layout and earlier fields are unchanged.

Focused native fixtures cover both editions, all three speeds with Instant text
on/off, substitutions, whole-name wrapping, save/reload halfway through a name,
script instant-print commands, explicit pauses and the Tessie windowless-padding
case. See [the receipt](../validation/text-typing-1.0.8.json).
These are isolated checks, not another campaign or physical Android-device test.

The additional Giant Step cave encounter report is separate and is not claimed
fixed by this release. No encounter tables or no-enemy gameplay option were added.
