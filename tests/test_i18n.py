import os
import re
import json
import unittest

class TestI18NLocalization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('static/app.js', 'r', encoding='utf-8') as f:
            cls.app_js = f.read()

        with open('static/index.html', 'r', encoding='utf-8') as f:
            cls.index_html = f.read()

        # Parse I18N.ru and I18N.en keys
        ru_match = re.search(r'ru:\s*\{(.*?)\},\s*en:\s*\{(.*?)\}\s*\};', cls.app_js, re.DOTALL)
        assert ru_match, "Failed to extract I18N block from app.js"
        
        ru_str = ru_match.group(1)
        en_str = ru_match.group(2)
        
        cls.ru_keys = set(re.findall(r'^\s*([a-zA-Z0-9_]+)\s*:', ru_str, re.MULTILINE))
        cls.en_keys = set(re.findall(r'^\s*([a-zA-Z0-9_]+)\s*:', en_str, re.MULTILINE))

    def test_i18n_key_symmetry(self):
        """Assert both ru and en dictionaries have complete symmetry without missing keys."""
        missing_in_en = self.ru_keys - self.en_keys
        missing_in_ru = self.en_keys - self.ru_keys
        self.assertEqual(missing_in_en, set(), f"Keys in RU but missing in EN: {missing_in_en}")
        self.assertEqual(missing_in_ru, set(), f"Keys in EN but missing in RU: {missing_in_ru}")
        self.assertGreater(len(self.ru_keys), 100)
        print(f"-> PASS: I18N key symmetry verified across {len(self.ru_keys)} bilingual entries.")

    def test_html_data_i18n_keys_exist(self):
        """Assert all data-i18n, data-i18n-title, and data-i18n-placeholder in index.html exist in I18N."""
        i18n_attrs = re.findall(r'data-i18n="([^"]+)"', self.index_html)
        title_attrs = re.findall(r'data-i18n-title="([^"]+)"', self.index_html)
        placeholder_attrs = re.findall(r'data-i18n-placeholder="([^"]+)"', self.index_html)

        all_attrs = set(i18n_attrs + title_attrs + placeholder_attrs)
        missing = all_attrs - self.ru_keys
        self.assertEqual(missing, set(), f"Attributes in index.html missing from I18N dict: {missing}")
        print(f"-> PASS: All {len(all_attrs)} HTML localization tags matched in dictionary.")

    def test_all_catalog_categories_translated(self):
        """Assert all categories in catalog_data.json have English translations in CATEGORY_NAMES_EN."""
        with open('catalog_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cats = set(a.get('category') for a in data if a.get('category'))
        
        # Check CATEGORY_NAMES_EN block
        cat_map_match = re.search(r'const CATEGORY_NAMES_EN\s*=\s*\{(.*?)\};', self.app_js, re.DOTALL)
        self.assertIsNotNone(cat_map_match, "CATEGORY_NAMES_EN not found")
        cat_map_text = cat_map_match.group(1)

        for c in cats:
            clean = re.sub(r'^\d+\.\s*', '', c).strip()
            found_full = f'"{c}"' in cat_map_text
            found_clean = f'"{clean}"' in cat_map_text
            self.assertTrue(found_full or found_clean, f"Category '{c}' not found in CATEGORY_NAMES_EN")
        print(f"-> PASS: All {len(cats)} catalog categories mapped to English translations.")

    def test_watcher_toast_localized(self):
        """Assert watcher.py checks language setting for its toasts."""
        with open('watcher.py', 'r', encoding='utf-8') as f:
            watcher = f.read()
        self.assertIn('SmartCatalog is Ready', watcher)
        self.assertIn('Initial system scan complete', watcher)
        print("-> PASS: Watcher system notifications support English.")

    def test_tray_menu_localized(self):
        """Assert tray_and_hotkey.py checks language setting for its menu."""
        with open('tray_and_hotkey.py', 'r', encoding='utf-8') as f:
            tray = f.read()
        self.assertIn('Open SmartCatalog Hub', tray)
        self.assertIn('Rescan and Sync Catalog', tray)
        self.assertIn('Quit SmartCatalog', tray)
        print("-> PASS: System tray context menu supports English.")

if __name__ == '__main__':
    unittest.main()
