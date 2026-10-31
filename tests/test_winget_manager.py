import os
import unittest
import winget_manager

SAMPLE_RU_OUTPUT = """
Имя                                              ИД                                              Версия               Доступно             Источник
---------------------------------------------------------------------------------------------------------------------------------------------------
7-Zip 24.09 (x64)                                7zip.7zip                                       24.09                26.05                winget
Adobe Acrobat (64-bit)                           XPDP273C0XHQH2                                  26.001.21691         26.002.22031         msstore
Visual Studio Code                               Microsoft.VisualStudioCode                      1.130.0              1.143.1              winget
VLC media player                                 VideoLAN.VLC                                    3.0.23               3.0.24               winget
Доступных обновлений: 4.
"""

SAMPLE_EN_OUTPUT = """
Name                             Id                              Version      Available    Source
-------------------------------------------------------------------------------------------------
Google Chrome                    Google.Chrome                   129.0.6668.7 130.0.6723.5 winget
Visual Studio Code               Microsoft.VisualStudioCode      1.94.2       1.95.0       winget
Git                              Git.Git                         2.46.0       2.47.0       winget
3 upgrades available.
"""

class TestWingetManager(unittest.TestCase):

    def test_validate_package_id(self):
        # Valid package IDs
        self.assertTrue(winget_manager.validate_package_id("Google.Chrome"))
        self.assertTrue(winget_manager.validate_package_id("Microsoft.VisualStudioCode"))
        self.assertTrue(winget_manager.validate_package_id("7zip.7zip"))
        self.assertTrue(winget_manager.validate_package_id("XPDP273C0XHQH2"))
        self.assertTrue(winget_manager.validate_package_id("Rem0o.FanControl"))
        self.assertTrue(winget_manager.validate_package_id("SublimeHQ.SublimeText.4"))

        # Dangerous or malformed inputs
        self.assertFalse(winget_manager.validate_package_id(""))
        self.assertFalse(winget_manager.validate_package_id(None))
        self.assertFalse(winget_manager.validate_package_id("Google.Chrome; calc.exe"))
        self.assertFalse(winget_manager.validate_package_id("Google.Chrome & whoami"))
        self.assertFalse(winget_manager.validate_package_id("Google.Chrome | dir"))
        self.assertFalse(winget_manager.validate_package_id("Google Chrome"))
        self.assertFalse(winget_manager.validate_package_id("`reboot`"))
        self.assertFalse(winget_manager.validate_package_id("a" * 200))

    def test_parse_winget_table_ru(self):
        items = winget_manager.parse_winget_table(SAMPLE_RU_OUTPUT)
        self.assertEqual(len(items), 4)

        item0 = items[0]
        self.assertEqual(item0['id'], '7zip.7zip')
        self.assertEqual(item0['version'], '24.09')
        self.assertEqual(item0['available'], '26.05')
        self.assertEqual(item0['source'], 'winget')

        item2 = items[2]
        self.assertEqual(item2['id'], 'Microsoft.VisualStudioCode')
        self.assertEqual(item2['version'], '1.130.0')
        self.assertEqual(item2['available'], '1.143.1')

    def test_parse_winget_table_en(self):
        items = winget_manager.parse_winget_table(SAMPLE_EN_OUTPUT)
        self.assertEqual(len(items), 3)

        self.assertEqual(items[0]['id'], 'Google.Chrome')
        self.assertEqual(items[1]['id'], 'Microsoft.VisualStudioCode')
        self.assertEqual(items[2]['id'], 'Git.Git')

    def test_parse_winget_table_empty(self):
        self.assertEqual(winget_manager.parse_winget_table(""), [])
        self.assertEqual(winget_manager.parse_winget_table(None), [])
        self.assertEqual(winget_manager.parse_winget_table("No packages found"), [])

    def test_correlate_with_catalog_and_avoid_false_positives(self):
        catalog = [
            {
                "id": "vscode_123",
                "name": "Visual Studio Code",
                "target": r"C:\Users\user\AppData\Local\Programs\Microsoft VS Code\Code.exe",
                "category": "01. Разработка и Код"
            },
            {
                "id": "logitune_456",
                "name": "LogiTune",
                "target": r"C:\Program Files\LogiTune\LogiTune.exe",
                "category": "11. Железо и Мониторинг"
            },
            {
                "id": "gitbash_789",
                "name": "Git Bash",
                "target": r"C:\Program Files\Git\git-bash.exe",
                "category": "01. Разработка и Код"
            }
        ]

        winget_items = [
            {
                "name": "Visual Studio Code",
                "id": "Microsoft.VisualStudioCode",
                "version": "1.94.2",
                "available": "1.95.0",
                "source": "winget"
            },
            {
                "name": "Git",
                "id": "Git.Git",
                "version": "2.46.0",
                "available": "2.47.0",
                "source": "winget"
            }
        ]

        correlated = winget_manager.correlate_with_catalog(winget_items, catalog)
        self.assertEqual(len(correlated), 2)

        matched_app_ids = {c['app_id'] for c in correlated}
        self.assertIn("vscode_123", matched_app_ids)
        self.assertIn("gitbash_789", matched_app_ids)
        # CRITICAL: LogiTune must NOT be matched for Git.Git!
        self.assertNotIn("logitune_456", matched_app_ids)

    def test_status_structure(self):
        status = winget_manager.get_status()
        self.assertIn("winget_available", status)
        self.assertIn("winget_version", status)
        self.assertIn("scanning", status)
        self.assertIn("total_updates", status)
        self.assertIn("updates", status)
        self.assertIn("active_upgrades", status)

if __name__ == '__main__':
    unittest.main()
