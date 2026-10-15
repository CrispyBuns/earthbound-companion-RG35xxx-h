# Windows 1.0.6 / platform preview.18

Fixes reported on Android preview.17, including shared renderer faults reproduced with both Original and Redux on Windows.

- Battle color math now halves the full sum before saturation and uses fixed color without halving when the subscreen is empty. This restores bright overlapping backgrounds instead of washing them toward gray.
- Distortion belongs to each physical background layer, including vertical compression. Background scrolling no longer doubles its base offset or warps the PSI scratch layer. Separate layer tables preserve the original alternating 30fps distortion timing.
- Save restoration rebuilds distortion only for its current scene owner, including Sound Stone, coffee/tea and the gas-station prologue. Old background data cannot reapply it to the overworld or game-over screen.
- Redux game-over entry stops an abandoned cinematic mask producer, preventing its bars from returning after a loss. Normal cutscenes and temporary battle interruptions retain their masks.
- Holding Run on an escalator retains the standing ride pose rather than freezing a running sprite. Ordinary walking and stair running remain unchanged.

Focused checks cover both editions: 12,288 blend inputs against the vendored LakeSnes pixel routine; four distortion styles on all physical targets; eight real background representatives per edition in single/paired layouts; all 204 packed PSI/layout cases; selected save restores; death-choice branch checkpoints; four stair orientations per edition; and escalator pose selection for all four party members. Captain Strong, Frank and Hippie scenes were rendered for comparison. See [numeric receipt](../validation/render-lifecycle-20261015.json).

These are prepared native fixtures, not a full campaign or a physical Android performance test. The Hippie recording alone does not establish low device FPS; source background distortion intentionally updates alternate frames. Please report any remaining device-specific lag after updating. Existing saves and the pinned Redux source are unchanged. A previously saved stuck cinematic mask can still be cleared by a normal building transition.

The community game icon remains credited to **princeofdalaam on Discord**. Windows launcher artwork remains unchanged.
