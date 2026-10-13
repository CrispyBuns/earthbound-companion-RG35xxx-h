# SPDX-License-Identifier: GPL-3.0-or-later
"""ROM-free rejection and preservation checks for the embedded setup entry."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO/'Ports/AndroidSetup/python'), str(REPO/'build/android-setup/python')]
from android_setup import build

class SetupRejectionTests(unittest.TestCase):
    def test_rejection_preserves_existing_adventure(self):
        for name, size in [('truncated', 12), ('patched-size', 3145728), ('headered-invalid', 3146240)]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                rom = root/'invalid.sfc'
                rom.write_bytes(bytes(size))
                existing = root/'existing-adventure'
                existing.mkdir()
                save = existing/'phone-save.srm'
                save.write_bytes(b'player checkpoint')
                before = hashlib.sha256(save.read_bytes()).hexdigest()
                error = build(str(rom), str(root/'new'), False, str(root/'progress.txt'))
                self.assertIn('clean EarthBound', error)
                self.assertFalse((root/'new').exists())
                self.assertEqual(before, hashlib.sha256(save.read_bytes()).hexdigest())
                self.assertFalse(hasattr(sys, '_MEIPASS'))

if __name__ == '__main__':
    unittest.main()
