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

## Focused verification

- The dev.34 baseline switches the displayed fractional phase to zero during
  dialogue despite unchanged integer coordinates. Opening/closing changes 4,895
  pixels in the chosen stationary scenery region. The fixed candidate changes
  zero pixels in that region at both boundaries. Its textbox interior matches
  the baseline, retaining glyph placement and colors.
- Ten rendered Original/Redux cases cover crisp, Scale2x and smooth filtering,
  plus 4:3, 16:9 and 21:9 framing. The production pause-menu cascade also retains
  the same camera phase in both editions. `scripts/dialogue_camera_qa.py` provides
  a reusable isolated fixture; it copies its input checkpoint or starts a fresh
  prepared sandbox and never writes an owner achievement profile.
- Save-state and screen-transition checks pass in both editions. The
  Redux-specific movement and PSI checks pass in Redux.
- The extracted Windows package passes all 46 achievement checks in both
  editions and six production launcher scenarios. It contains no private game
  content. The installed program cold-loads a copy of the latest owner checkpoint;
  all 52 protected save/settings/progress files remain unchanged. The package
  manifest is intentionally updated and backed up with the prior programs.
- All five [platform CI jobs](https://github.com/rages4calm/earthbound-companion/actions/runs/38181647412)
  pass, including Android emulator startup. All five downloaded platform
  packages pass the content/license check. The runtime code is verified at
  `01d1fb0`; subsequent changes add documentation, validation and the QA tool.

[Package hashes and recorded results](../validation/dialogue-camera-dev35.json).
Prepared scenes and copied checkpoints do not cover every NPC, map, display or
platform's natural gameplay. The rendered dialogue checks ran on Windows;
broader new-platform gameplay remains community testing.
