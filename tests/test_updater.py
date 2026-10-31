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
            "tag_name": "v1.3.0",
            "name": "SmartCatalog Hub v1.3.0",
            "body": "Changelog details",
            "html_url": "https://github.com/Pipetosik/SmartCatalog-Hub/releases/tag/v1.3.0",
            "published_at": "2026-11-01T12:00:00Z",
            "assets": [
                {
                    "name": "SmartCatalog-Setup-v1.3.0.exe",
                    "browser_download_url": "https://github.com/Pipetosik/SmartCatalog-Hub/releases/download/v1.3.0/SmartCatalog-Setup-v1.3.0.exe",
                    "size": 42000000
                }
            ]
        }'''
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = updater.check_for_updates(force=True)
        self.assertTrue(res["success"])
        self.assertTrue(res["update_available"])
        self.assertEqual(res["latest_version"], "1.3.0")
        self.assertEqual(res["download_url"], "https://github.com/Pipetosik/SmartCatalog-Hub/releases/download/v1.3.0/SmartCatalog-Setup-v1.3.0.exe")
        self.assertEqual(res["asset_name"], "SmartCatalog-Setup-v1.3.0.exe")

    @patch("urllib.request.urlopen")
    def test_check_for_updates_none_available(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'''{
            "tag_name": "v1.2.1",
            "name": "SmartCatalog Hub v1.2.1",
            "body": "Current release",
            "assets": []
        }'''
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = updater.check_for_updates(force=True)
        self.assertTrue(res["success"])
        self.assertFalse(res["update_available"])
        self.assertEqual(res["latest_version"], "1.2.1")

    def test_start_download_untrusted_domain(self):
        ok, msg = updater.start_download("https://malicious-site.com/setup.exe")
        self.assertFalse(ok)
        self.assertIn("Untrusted", msg)

    def test_ssl_cert_verify_failed_fallback(self):
        calls = []
        mock_resp = MagicMock()
        mock_resp.status = 200

        def fake_urlopen(req, timeout=10, context=None):
            calls.append(context)
            if len(calls) == 1:
                import ssl
                import urllib.error
                raise urllib.error.URLError("[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1006)")
            return mock_resp

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            res = updater.urlopen_robust("https://api.github.com/test", timeout=5)
            self.assertEqual(res, mock_resp)
            self.assertEqual(len(calls), 2)
            # The second call should use an unverified context
            self.assertFalse(calls[1].check_hostname)

    def test_install_update_security_rejection(self):
        # Non-existent file
        ok, msg = updater.install_update(r"C:\Windows\System32\cmd.exe")
        self.assertFalse(ok)
        # Attempt to escape temp directory
        outside_temp = os.path.abspath("installer.iss")
        ok, msg = updater.install_update(outside_temp)
        self.assertFalse(ok)
        self.assertIn("Invalid installer path", msg)

    @patch("os.startfile", create=True)
    @patch("threading.Timer")
    def test_install_update_launch_clean(self, mock_timer, mock_startfile):
        temp_dir = tempfile.gettempdir()
        fake_installer = os.path.join(temp_dir, "SmartCatalog-Setup-test.exe")
        with open(fake_installer, "wb") as f:
            f.write(b"MZfake")

        try:
            ok, msg = updater.install_update(fake_installer, silent=True)
            self.assertTrue(ok)
            self.assertIn("Installer launched", msg)
            mock_startfile.assert_called_once_with(fake_installer, "open", arguments="/SILENT /CLOSEAPPLICATIONS")
        finally:
            if os.path.exists(fake_installer):
                os.remove(fake_installer)

if __name__ == "__main__":
    unittest.main()
