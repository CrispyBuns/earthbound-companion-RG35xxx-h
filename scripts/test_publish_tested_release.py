"""Keep official Windows releases ahead of development tags in Latest selection."""
import unittest

from publish_tested_release import identity


class ReleaseIdentityTests(unittest.TestCase):
    def test_official_and_development_share_windows_channel(self):
        self.assertEqual(identity("v1.0.0")[0], "windows")
        self.assertEqual(identity("v0.5.0-redux-dev.38")[0], "windows")
        self.assertEqual(identity("v0.5.0-ports-preview.9")[0], "ports-preview")

    def test_final_sorts_after_same_version_development(self):
        self.assertGreater(identity("v1.0.0")[1], identity("v1.0.0-redux-dev.999")[1])
        self.assertGreater(identity("v1.0.0")[1], identity("v0.5.0-redux-dev.38")[1])

    def test_newer_version_sorts_after_old_final(self):
        self.assertGreater(identity("v1.0.1-redux-dev.1")[1], identity("v1.0.0")[1])

    def test_invalid_tags_are_rejected(self):
        for tag in ("v1", "v1.0.0-other.1", "v1.0.0-ports-preview.bad"):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                identity(tag)


if __name__ == "__main__":
    unittest.main()
