# Publishing tested packages

Create a draft and finish the package checks and upload-digest verification before
publishing. Then use the shared publishing step:

```powershell
python scripts/publish_tested_release.py v0.5.0-redux-dev.37
python scripts/publish_tested_release.py v0.5.0-ports-preview.8
```

Replace these example tags with the tested candidates. Windows releases are
published with `--prerelease=false --latest`; platform releases use
`--prerelease=true --latest=false`. The Windows build remains experimental as
described in its coverage notes. GitHub's Latest label selects the current
download; it is not a claim of complete gameplay certification.

The helper refuses an older candidate when a newer release of that kind exists,
requires completed uploads, and verifies `/releases/latest` after publishing.
It does not replace package testing or checksum verification.

Update current version labels in the README, portability guide and native-port
status, plus each platform's README link. Generic Windows download links use
`/releases/latest`; platform downloads link to the current preview tag. Keep
historical release notes and validation identities unchanged.

Before reporting publication complete, verify both tags:

```powershell
python scripts/publish_tested_release.py v0.5.0-redux-dev.37 --check
python scripts/publish_tested_release.py v0.5.0-ports-preview.8 --check
```
