# EarthBound Companion 1.0.1

This maintenance update fixes four community reports: distorted NPCs/map objects
when Ness passes them, bush outlines disappearing behind the party, the opening
Onett building pan after New Game, and music behaving badly during fast-forward.
The feature set and pinned Redux revision remain unchanged.

NPCs and foreground backgrounds stay in world coordinates. Party pixels are
composited using the original BG priority and OAM ordering at displayed
coordinates. Black palette pixels remain opaque. Fixed dialogue windows keep
their screen position. The scripted entity-following camera now uses its existing
fractional position and moves the whole scene during the Onett tour.

The audio device advances native SPC and HQ music at its own sample rate while
gameplay accelerates. Hold and toggle fast-forward work; pause still silences
audio. Music changes and game effects still follow game events.

## Focused verification

- Reproduced the old NPC face distortion in a prepared Onett overlap and reviewed
  the candidate's rendered result. Bush/map-object and four-character cases also
  compare against original PPU pixel priorities; opaque-black coverage is tested.
- Crisp Pixels/integer scaling, antialiasing/noninteger scaling, linear filtering
  and SDL software rendering are exercised. Normal timing stays around 60 FPS on
  the development machine; captures are excluded from performance claims.
- The production prologue is queued in a private new-game scene. In a stable
  building-pan segment, old presentation alternates 0/1-pixel steps; the candidate
  follows the intended ~0.7071-pixel step. Black cuts are checked separately.
- A minute of normal, continuously fast-forwarded and repeated hold/release
  playback produces identical music samples, separately for native SPC and a
  generated MSU fixture. A 16-effect-per-tick stress case drains after release.
- Dialogue/menu camera phase, both editions' save serialization/transitions and
  achievements, and Redux battle portraits/motion pass. Five public native patches
  reconstruct every changed source file, including the prior portrait correction.

Existing asset packs and save formats are retained. Tests use private sessions.
Detailed receipts and platform coverage limits are in
[the release record](../validation/release-1.0.1.json).

These are focused prepared/cold-restore checks, not another full playthrough or a
claim that every NPC, cutscene, sound combination or physical device was tested.

## Publication and preservation

The Windows ZIP passes all 50 file-manifest hashes and launcher/profile checks.
Both retained installations use 1.0.1; all 113 checked owner data files remained
unchanged and a copied existing checkpoint loads. All five platform CI jobs pass
at source commit `ada105cfc93a055b4eb502bf458e3711fcbd8838`
([CI run](https://github.com/rages4calm/earthbound-companion/actions/runs/38487267926)).
All five platform architectures/content checks pass. All six uploaded package
digests match the verified local packages. Windows 1.0.1 is GitHub Latest;
preview.11 remains a community prerelease.
