# Maintenance scope

The supported feature set is complete at Windows v1.0.0 as of October 13, 2026,
using the tested dev.38 native runtime and pinned Redux input. Linux/macOS/Android
remain community previews. Read MAINTENANCE.md for scope/coverage; historical
audit notes do not reopen development.

The explicit October 11 owner request adds the full-game standalone achievement
set in dev.34; see docs/RELEASE-dev34.md. This is a narrow feature exception.

- Default to focused fixes for reported defects. New features and broad audits require an explicit user request.
- Do not automatically launch whole-project audits, agent reviews or a full campaign. Do not ask the owner to replay the game as the default verification method.
- Preserve recipe algorithms and save namespaces. Use isolated sessions/copies; protect owner saves before installation or recovery changes.
- Never relabel historical checks as execution on a new build. Run checks appropriate to the actual change; broaden only for an evidenced risk.
- Keep ROMs, extracted packs, soundtrack payloads and personal saves private. Follow existing issue attachment rules.
- In the owner's workspace, github-repo is canonical; adjacent native-source is intentionally modified. Never reset, clean or bootstrap over that dirty source tree.
- Research and future-tool proposals are references, not requirements before closeout.
- After verifying uploaded packages, publish through `scripts/publish_tested_release.py`. Official Windows and Windows development releases must be non-prereleases and explicitly Latest; platform releases remain prereleases. Run its `--check` for the current Windows/platform tags and update version labels/platform links before reporting publication complete. Preserve historical release identities.

Later explicit user instructions can reopen or change this scope.
