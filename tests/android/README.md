# Touch input regressions

`../java/TouchStickTest.java` runs without Android, game data or a ROM:

```powershell
javac -d build/touch-tests Ports/AndroidManaged/Java/TouchStick.java tests/java/TouchStickTest.java
java -cp build/touch-tests TouchStickTest
```

`TouchControlsHarness.java` is a separate ROM-free Android Activity. Build it with the production `TouchControls.java` and `TouchStick.java` against Android API 26 or newer, package its classes using the Android SDK tools, and launch `org.earthbound.companion.test.TouchControlsHarness` in a disposable emulator. Its package must be separate from Companion. It reports `TouchChecks: PASS` or an assertion with `TouchChecks: FAIL` in logcat. It is deliberately outside the Android application's source glob and must never be added to the shipping manifest.

Run at phone and tablet landscape sizes, including font scale 1.3. The activity dispatches events through the actual View hierarchy, including two fingers whose pointer array indices change. This complements the host model test and manual checks of the actual game activity's hide preference, Back behavior and focus lifecycle.
