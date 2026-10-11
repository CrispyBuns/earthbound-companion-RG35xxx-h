# Dev.34 — standalone achievements

Owner-requested expansion of the tested five-achievement pilot, October 11, 2026.
Adds 46 original offline achievements spanning the opening, all eight Sanctuaries,
main bosses and chapters, the final prayers, staff credits, photography,
exploration, levels and battle victories. [Player guide and full set](ACHIEVEMENTS.md).

The Windows and portable launchers share a catalog and category filters. Native
notifications use an overlay inside the smallest supported crop; they do not
write game graphics memory. Progress stays outside game saves and is separate
per installation/edition. Tracking can be disabled for the next launch.

## Compatibility and verification

- The five owner-tested IDs, progress and exact unlock dates survive the upgrade.
  New counters inherit only the minimum victories actually recorded.
- Game save/state layouts, pack identities and Shuffle recipes are unchanged.
  Older game saves cannot revoke achievements. Loaded story/level/photo credit
  is silent; unrecorded historical battles are not fabricated.
- All 46 definitions pass native Original and Redux fixtures through actual
  event setters, normal/instant victories and the staff-credit consumer. Negative
  controls cover defeat, partial Frank progress, Bionic Kraken, premature credits,
  repeated photos, three-member parties and levels below the target.
- Photos use the active pack's 32 photographer records. Story flags are named
  in the pinned native source; Sanctuary victories use permanent boss flags,
  rather than the temporary melody-display flags. Giygas uses its completed-story
  flag, after the final prayers.
- Persistence, edition/Shuffle isolation, corrupt/future-profile preservation and
  unavailable storage pass. The C core passes 24 checks; shared parser tests,
  Windows publish and portable desktop compilation pass.
- A copy of the newest owner pilot checkpoint loads with its five unlocks and
  dates intact. The actual completed Redux checkpoint credits Giygas, all melodies
  and credits without inventing historical battles. All 32 protected owner data
  hashes remain unchanged.

Release checks also cover fresh patch application, packaging, launcher paths and
supported crop captures. Public packages exclude ROMs, packs, soundtrack payloads,
saves and synthetic achievement progress.

The full set is checked with bounded fixtures and copied checkpoints, not another
natural campaign. New-platform gameplay remains a community preview. Competitive
verification, anti-cheat, online services and other game integrations are out of
scope for this release.
