"""Write the game icon resource for -DEB_WINDOWS_ICON_RC=<output>."""
import argparse
from pathlib import Path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    icon = Path(__file__).resolve().parents[1] / 'Companion/Assets/earthbound-game.ico'
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text('1 ICON "' + icon.as_posix() + '"\n', encoding='utf-8')
    print(args.output.resolve())
