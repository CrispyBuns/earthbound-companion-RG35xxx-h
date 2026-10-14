"""Check portable control labels and the Android Settings button against the native enum."""
import argparse
import json
from pathlib import Path
import re

REPO = Path(__file__).resolve().parents[1]


def validate(native_header, managed_ui, android_activity):
    block = re.search(r"enum\s*\{(.*?)PC_ACTIONS", native_header, re.S)
    if block is None:
        raise ValueError("Native PC action enum not found")
    actions = re.findall(r"\bPC_[A-Z_]+\b", block[1])
    ids = {name: index for index, name in enumerate(actions)}
    names = re.search(r"string\[\]\s+names\s*=\s*(\[.*?\]);", managed_ui, re.S)
    if names is None:
        raise ValueError("Portable control labels not found")
    labels = json.loads(names[1])
    aliases = {"PC_FAST": "Fast-forward", "PC_FPS": "FPS"}
    expected = [aliases.get(name, name.removeprefix("PC_").title()) for name in actions]
    if labels != expected:
        raise ValueError(f"Portable labels differ from native action order: {labels} != {expected}")
    settings = re.search(r"\bACTION_SETTINGS\s*=\s*(\d+)\s*;", android_activity)
    if settings is None or int(settings[1]) != ids["PC_SETTINGS"]:
        raise ValueError("Android Settings button action does not match native PC_SETTINGS")
    row = r'new String\[\]\{\s*"R"\s*,\s*"Settings"\s*\}\s*,\s*new int\[\]\[\]\{\s*\{\s*5\s*\}\s*,\s*\{\s*ACTION_SETTINGS\s*\}\s*\}'
    if not re.search(row, android_activity):
        raise ValueError("Android Settings row is not wired to ACTION_SETTINGS")
    return dict(passed=True, nativeActions=len(actions), settingsAction=ids["PC_SETTINGS"], zoomAction=ids["PC_ZOOM"], portableLabelsMatchNative=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-source", type=Path, required=True)
    args = parser.parse_args()
    result = validate((args.native_source / "src/platform/pc_options.h").read_text(encoding="utf-8"),
                      (REPO / "Ports/UI/MainView.cs").read_text(encoding="utf-8"),
                      (REPO / "Ports/AndroidManaged/Java/GameActivity.java").read_text(encoding="utf-8"))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
