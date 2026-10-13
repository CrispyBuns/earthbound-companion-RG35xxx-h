# Embedded Android ROM setup

The Android launcher runs the existing Original extractor and the pinned Redux
compiler/converters inside Chaquopy 17.0 / Python 3.13. No executable is launched
from writable app storage. Original works offline; Redux downloads and verifies
the same `897d0083` source archive as desktop setup.

The package contains code, schemas, tool libraries and notices. It contains no
ROM, generated game pack, upstream Project graphics, music or save data.

After preparing the native source with `scripts/prepare_port_sources.py`:

```sh
python scripts/prepare_android_setup.py --native native-source
python -m unittest discover -s scripts -p test_android_rom_setup.py -v
python scripts/build_android_setup_extensions.py --ndk "$ANDROID_HOME/ndk/28.2.13676358"
cd Ports/AndroidSetup
EB_BUILD_PYTHON=python3.13 gradle :setup:exportRuntime
```

Use Gradle 8.13, JDK 17+, Android SDK 36 and the .NET 10 Android workload. The
generated `build/android-setup/aar/setup-release.aar` includes the Java bridge,
Python runtime, converter sources and requirements. The managed Android project
includes it without generating .NET bindings; `AndroidRomSetup` invokes its
static bridge and validates packs again before installation. Build each managed
ABI sequentially, as in `platform-preview.yml`.

CoilSnake compression and the repaired CCScript compiler are cross-compiled for
ARM64/x64 against checksum-pinned Android Python headers. Pydantic's pure Python
v1 compatibility package supplies model validation; `android_models.py` adapts
only the v2 methods used by ebtools. Exact Original pack, compiled Redux ROM and
current Redux pack checks remain mandatory. The public BPS is not substituted
for the audited compiler output.

CI uses invented ROM bytes for rejection and compiler-order tests. Private
emulator tests use the owner's ROM locally and compare the actual generated
checksums. Passing these tests does not certify a campaign or physical device.
