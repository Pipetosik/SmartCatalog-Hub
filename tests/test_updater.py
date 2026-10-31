import os
import unittest
import tempfile
from unittest.mock import patch, MagicMock
import updater

class TestUpdater(unittest.TestCase):
    def test_parse_semver(self):
        self.assertEqual(updater.parse_semver("1.1.0"), (1, 1, 0))
        self.assertEqual(updater.parse_semver("v1.2.0"), (1, 2, 0))
        self.assertEqual(updater.parse_semver("v2.0.4-beta.1"), (2, 0, 4))
        self.assertEqual(updater.parse_semver("1.0"), (1, 0, 0))
        self.assertEqual(updater.parse_semver(""), (0, 0, 0))
        self.assertEqual(updater.parse_semver(None), (0, 0, 0))

    def test_is_newer_version(self):
        self.assertTrue(updater.is_newer_version("1.2.0", "1.1.0"))
        self.assertTrue(updater.is_newer_version("v1.1.1", "1.1.0"))
        self.assertTrue(updater.is_newer_version("2.0.0", "1.1.0"))
        self.assertFalse(updater.is_newer_version("1.1.0", "1.1.0"))
        self.assertFalse(updater.is_newer_version("1.0.9", "1.1.0"))
        self.assertFalse(updater.is_newer_version("0.9.5", "1.1.0"))

    @patch("urllib.request.urlopen")
    def test_check_for_updates_available(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'''{
            "tag_name": "v1.2.0",
            "name": "SmartCatalog Hub v1.2.0",
            "body": "Changelog details",
            "html_url": "https://github.com/Pipetosik/SmartCatalog-Hub/releases/tag/v1.2.0",
            "published_at": "2026-11-01T12:00:00Z",
            "assets": [
                {
                    "name": "SmartCatalog-Setup-v1.2.0.exe",
                    "browser_download_url": "https://github.com/Pipetosik/SmartCatalog-Hub/releases/download/v1.2.0/SmartCatalog-Setup-v1.2.0.exe",
                    "size": 42000000
                }
            ]
        }'''
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = updater.check_for_updates(force=True)
        self.assertTrue(res["success"])
        self.assertTrue(res["update_available"])
        self.assertEqual(res["latest_version"], "1.2.0")
        self.assertEqual(res["download_url"], "https://github.com/Pipetosik/SmartCatalog-Hub/releases/download/v1.2.0/SmartCatalog-Setup-v1.2.0.exe")
        self.assertEqual(res["asset_name"], "SmartCatalog-Setup-v1.2.0.exe")

    @patch("urllib.request.urlopen")
    def test_check_for_updates_none_available(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'''{
            "tag_name": "v1.1.0",
            "name": "SmartCatalog Hub v1.1.0",
            "body": "Current release",
            "assets": []
        }'''
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = updater.check_for_updates(force=True)
        self.assertTrue(res["success"])
        self.assertFalse(res["update_available"])
        self.assertEqual(res["latest_version"], "1.1.0")

    def test_start_download_untrusted_domain(self):
        ok, msg = updater.start_download("https://malicious-site.com/setup.exe")
        self.assertFalse(ok)
        self.assertIn("Untrusted", msg)

    def test_install_update_security_rejection(self):
        # Non-existent file
        ok, msg = updater.install_update(r"C:\Windows\System32\cmd.exe")
        self.assertFalse(ok)
        # Attempt to escape temp directory
        outside_temp = os.path.abspath("installer.iss")
        ok, msg = updater.install_update(outside_temp)
        self.assertFalse(ok)
        self.assertIn("Invalid installer path", msg)

if __name__ == "__main__":
    unittest.main()
