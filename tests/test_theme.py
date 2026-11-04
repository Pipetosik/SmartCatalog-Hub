import re
import unittest

class TestCraftStudioTheme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('static/index.html', 'r', encoding='utf-8') as f:
            cls.index_html = f.read()
        with open('static/app.js', 'r', encoding='utf-8') as f:
            cls.app_js = f.read()
        with open('static/style.css', 'r', encoding='utf-8') as f:
            cls.style_css = f.read()

    def test_theme_select_options_in_html(self):
        """Assert themeSelect in index.html contains Craft Studio and all standard themes."""
        self.assertIn('<option value="craft"', self.index_html)
        self.assertIn('<option value="win11"', self.index_html)
        self.assertIn('<option value="obsidian"', self.index_html)
        self.assertIn('<option value="acrylic"', self.index_html)
        self.assertIn('<option value="mica"', self.index_html)
        self.assertIn('<option value="oled"', self.index_html)
        print("-> PASS: All 6 themes present in index.html #themeSelect.")

    def test_theme_registration_in_app_js(self):
        """Assert validThemes in app.js includes 'craft'."""
        self.assertIn("'craft'", self.app_js)
        self.assertIn("const validThemes = ['craft', 'win11', 'obsidian', 'acrylic', 'mica', 'oled'];", self.app_js)
        print("-> PASS: Theme 'craft' registered in validThemes in app.js.")

    def test_craft_studio_css_definitions(self):
        """Assert body.theme-craft defines graphite ramp, tabular nums, and nested radii."""
        self.assertIn('body.theme-craft {', self.style_css)
        self.assertIn('--bg-base: #0b0d11;', self.style_css)
        self.assertIn('--bg-surface: #11141a;', self.style_css)
        self.assertIn('--bg-card: #131720;', self.style_css)
        self.assertIn('--radius-pill: 8px;', self.style_css)
        self.assertIn('tabular-nums', self.style_css)
        print("-> PASS: body.theme-craft properly defined in style.css with anti-slop standards.")

if __name__ == '__main__':
    unittest.main()
