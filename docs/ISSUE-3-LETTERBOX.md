# Issue 3: cinematic bars and scene timing (Windows1.0.9 / platform preview.21)

Display now has **Cinematic letterboxing**, available in the Windows launcher and
shared Linux/macOS/Android launcher. It controls Redux story-scene bars, not normal
screen-aspect borders or battle presentation. Existing settings retain Redux bars;
the Classic preset disables them. Saved preferences and exported profiles include
the option. Direct native launches can use `disable_cinematic_letterbox=1` in INI.

Hiding bars retains scripted opening/closing durations. Battles retain their own
masks. Quick dialogue no longer auto-cancels scripted text-speed waits used for
scene/music timing. Original button cancellation remains available.

Both-edition focused native fixtures, Windows launcher build and portable settings
tests passed. Exact reporter battle scene and physical Android were not reproduced.
No full campaign was repeated. Receipt: validation/issue3-cinematic-option.json.

Published in Windows1.0.9 and platform preview.21 on all platforms.
See [release notes](RELEASE-1.0.9.md) and [verified packages](../validation/release-1.0.9.json).
