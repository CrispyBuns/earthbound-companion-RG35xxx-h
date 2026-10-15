# Windows 1.0.7 — resilient optional soundtrack setup

An HTTP 500 from the soundtrack host could stop setup before MaternalBound Redux was built. Setup now builds the playable game data first. If optional music still fails, it completes with a clear warning and the game uses its original music for missing tracks. Explicit soundtrack repair still reports failure rather than claiming success.

Music downloads retry and try alternative Archive storage endpoints. Tracks retain pinned size, MD5 and SHA-1 checks; only a complete verified file replaces the final track. Failures name the track and host, with details saved to `UserData/msu-setup.log`. Existing verified tracks are reused on a later repair.

An optional HTTPS source-list file allows a separately hosted mirror to be added without changing accepted track contents. The included alternate endpoints share Archive's infrastructure; they are not protection against an outage of the entire provider. [Hosting and the creator's existing manual mirror](MSU-HOSTING.md).

Focused tests cover HTTP 500/503 failover, corrupt/oversized responses, cancellation, preserving existing files and game-first optional-download handling. The Windows launcher and portable shared core compile cleanly. Native game code, data recipes, saves, achievements and the pinned Redux input are unchanged. This release does not repeat a game campaign or certify new physical hardware. Android preview.19 and Linux/macOS preview.18 remain their current releases.
