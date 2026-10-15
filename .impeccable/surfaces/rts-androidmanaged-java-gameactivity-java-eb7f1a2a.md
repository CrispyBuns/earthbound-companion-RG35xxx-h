---
version: 1
slug: "rts-androidmanaged-java-gameactivity-java-eb7f1a2a"
primary_target: "Ports/AndroidManaged/Java/GameActivity.java"
related_targets: ["Ports/AndroidManaged/Java/TouchControls.java","Ports/AndroidManaged/Java/TouchStick.java"]
---

## Direction contract
THESIS: A quiet, thumb-friendly game overlay with continuous eight-way movement. The existing separate arrow-button grid is replaced within the established Companion visual world.
OWN-WORLD: Inherit night-violet surfaces, pale ink and warm-gold active feedback. Circular action buttons and a restrained drawn thumbstick use crisp native geometry, with no added artwork or web styling.
STORY: Left thumb moves without lifting; another finger holds Run or action buttons. Release, cancellation, pause and hiding always stop input. Existing button actions and handheld hide preference remain available.
FIRST VIEWPORT: A translucent stick at bottom-left; spaced SNES face buttons and L/R at bottom-right; readable Start/Select/Save/Load/Fast across the top, with a separate Settings icon. Keep the game center clear and respect cutouts/system insets on phones and tablets.
FORM: Code-led local Android game-overlay extension; no direction seed applies to this narrowly specified repair. Follow the supplied mobile-controller references, translated into digital EarthBound movement.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
