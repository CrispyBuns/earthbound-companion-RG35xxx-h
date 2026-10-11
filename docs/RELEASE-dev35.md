# Dev.35 — camera position during dialogue

A tester reported that opening an overworld textbox nudged the scenery and
closing it snapped the camera back. Dev.33's fractional camera presentation was
disabled whenever a window was open or a dialogue child mode was running.
The integer camera coordinates and player position remained unchanged, while
the displayed fractional phase switched to zero.

The fix retains that phase through ordinary overworld dialogue and menu
cascades. BG3 text/window pixels are separated from the moving scenery, using
the renderer's actual winning layer. Borders, opaque fill and glyphs remain at
fixed screen coordinates, including pixels matching the scenery's color.
The temporary background pass restores its layer masks and OAM positions.

Battles, transitions, dedicated map/music screens and scripted camera framing
retain their separate presentation rules. The drawing masks are outside the
serialized PPU state. Pack identities, saves, achievement definitions and
randomizer recipes are unchanged.

Focused verification and package identities are recorded in
`validation/dialogue-camera-dev35.json` when the release checks finish.
Prepared scenes and copied checkpoints do not cover every NPC, map, display or
platform's natural gameplay.
