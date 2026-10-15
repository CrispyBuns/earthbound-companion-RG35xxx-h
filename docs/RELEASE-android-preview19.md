# Android preview.19 — sliding touch controls

The old movement grid handled presses and releases but ignored finger movement. Preview.19 replaces it with one circular thumbstick that updates direction throughout the gesture. Its output is the game's eight digital directions, with a neutral center and a small hysteresis zone to avoid jitter at direction boundaries.

The overlay tracks pointer IDs rather than array positions. Another finger can hold Run or an action; lifting it does not steal movement from the first finger. Native input receives balanced press/release transitions rather than repeated presses for every motion event. Cancellation, hiding, detaching and loss of game focus release touch inputs.

The face buttons now use a spaced SNES diamond, readable utility labels and a drawn Settings icon. Short landscape screens put L/R alongside the diamond; tablets use the shoulder row. Buttons retain at least 48dp targets and respect system/cutout insets. **Controls → Show touch controls** still hides the whole overlay, and Android Back temporarily reveals it. Existing hardware-controller bindings remain available.

This is an Android Java/UI update. Both native libraries are byte-identical to the matching preview.18 APK. The persistent app ID and signing certificate are retained for in-place updates. Windows 1.0.6 and Linux/macOS preview.18 remain current on their platforms.

## Focused verification

- ROM-free Java checks cover continuous direction changes, eight directions, neutral/dead-zone behavior, ownership, cancellation and balanced native hold counts.
- A separate, non-shipping Android test activity dispatches actual multi-pointer MotionEvents through the production overlay. It checks movement plus Run, pointer reindexing, action cancellation/reentry, hide cleanup, accessibility activation, original action IDs, target bounds and overlap.
- The production x64 APK is exercised on a disposable Android API 37 emulator using isolated game sessions, with phone/tablet landscape sizes, dark mode and 1.3 system font scale. Screenshots remain private because they contain game imagery.
- ARM64 and x64 APK packaging, version, signatures and unchanged native-library bytes are checked. The test activity is excluded from both shipping APKs.

Emulation does not certify physical touchscreen feel, every display cutout, hardware controllers or a full game campaign. Community handheld/phone testing remains useful.

Implementation follows Android's [multi-touch pointer guidance](https://developer.android.com/develop/ui/views/touch-and-input/gestures/multi). The user's mobile-game HUD references informed placement; no third-party control artwork or code was copied.
