# EarthBound Companion 1.0.0

The supported Companion feature set is complete. Future updates focus on
reported bugs. Windows 1.0.0 uses the same tested native player, setup helpers,
game data and save formats as dev.38; the launcher and documentation now show
the official release status.

Included: Original EarthBound, the pinned native MaternalBound Redux adaptation,
widescreen and ultrawide scenery, smooth scrolling, keyboard/controller support,
MSU music support, Story Shuffle v4, save recovery, and 46 offline achievements
with an in-game browser and optional unlock sound.

## Redux version

The conversion input remains `897d00833f4a08a0a92f106abf631629a6a6a041`.
Newer revision `0659fdfc54ec962859af27deb5b04c49c6024a55` was used for the
dev.38 portrait comparison and separate ROM-side research, not a new conversion.
The subsequent upstream commits add cinematic framing/camera staging and also
change some dialogue, NPCs and boss behavior. Native execution does not make
those script/data changes irrelevant; they are outside this tested baseline.
No upstream update or save/seed migration is included in 1.0.0.

The owner completed Redux through the credits; community testers also report
completing Original and Redux. Exhaustive campaign parity, every optional
branch/effect and full randomized progression remain unverified. These are
coverage limits, not a requirement for another owner playthrough or broad audit.

## Release verification

The native player retains dev.38 SHA-256
`a6de0138a33e3754915a5985ad7395ac83e3c85dad11794ddbcc4d48c20a5cad`.
The release package and updated launcher receive their own hash, file-manifest,
profile and isolated runtime checks. Dev.38's original source/pixel tests remain
[recorded as dev.38 evidence](RELEASE-dev38.md), not relabeled as a new campaign.
Current package results are in [the 1.0.0 release record](../validation/release-1.0.0.json).

Linux, macOS and Android remain [community preview.9](PORTABILITY.md), sharing
the tested game core but requiring broader platform/device testing. Deluxe is
separate unfinished research and is not included.

[Latest Windows release](https://github.com/rages4calm/earthbound-companion/releases/latest)
· [Supported scope and limits](../MAINTENANCE.md)
· [Report a bug](https://github.com/rages4calm/earthbound-companion/issues/new?template=bug-report.yml)
