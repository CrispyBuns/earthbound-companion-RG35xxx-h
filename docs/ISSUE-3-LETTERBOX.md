# Issue 3: cinematic bars and scene timing (unreleased source)

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

Source update only: existing Windows1.0.8 / preview.20 downloads do not include it.
