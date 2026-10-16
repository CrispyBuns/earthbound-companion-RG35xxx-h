# 1.0.10 / platform preview.22: Redux custom PSI names

Fixes the duplicated prefix in favourite-thing powers reported in
[issue #5](https://github.com/rages4calm/earthbound-companion/issues/5).
Redux now displays `PK Zoomin` instead of `PK PSI Zoomin`, retaining the chosen
name and ability suffix. Both immediate menu text and animated dialogue use the
fix. Original EarthBound keeps its original `PSI` prefix. Save data is unchanged.

Original534 / Redux590 focused native checks passed, including both text paths
and unchanged saved names. All twelve native patches apply in order. This is a
focused maintenance update; full campaigns and physical Android gameplay were
not repeated. Earlier cinematic letterboxing, dialogue, setup, touch controls,
achievements and icon fixes remain included.
