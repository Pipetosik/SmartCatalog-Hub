# Project Backlog & Roadmap

This document outlines planned improvements, feature ideas, and release roadmaps for **SmartCatalog Hub**.

---

## ✅ Completed in Release v1.1.0 (2026-10-31)
- [x] **Visual Application Version Badges**: Displayed `v1.1.0` badge in the header, footer status bar, and in the new "About / О программе" settings module.
- [x] **Community Feedback Loop**: Added "⭐ Star on GitHub" button along with direct quick-links to file bug reports or feature suggestions.
- [x] **Multilingual UI (English & Russian / i18n)**: Full runtime language switching with zero page reload, localized category titles, tooltips, modals, and Windows Action Center balloon toasts.
- [x] **Accent Color Themes (Accent Color Picker)**: 6 curated Windows 11 Fluent palettes (*Sky Blue*, *Ultraviolet Purple*, *Emerald Green*, *Amber Sunset*, *Ruby Rose*, and *Steel Slate*) with instant CSS variable updates.
- [x] **macOS-style Quick Look (`Space`)**: Pressing `Space` while navigating the catalog grid opens an instant preview card with high-res icon, full path, screen time, launch counter, and quick action buttons.
- [x] **Shortcut Cold-Start Auto-Resurrection**: Double-clicking the Desktop or Start Menu shortcut verifies background service health via `/api/version` and automatically resurrects `service.py` if stopped.
- [x] **Desktop Shortcut & System Tray Blank Icons**: Native DIB 32-bit BMP encoding across all icon sizes (16x16 to 256x256) inside `.ico`, resolving blank sheet fallbacks.
- [x] **Responsive Header**: Guaranteed full visibility of the Settings button across all monitor resolutions and window sizes.

---

## 🎯 Planned for Upcoming Releases (v1.2.0)
- [ ] **Drag-and-Drop Card Reordering**: Manually reorder application cards within categories with persistent order state.
- [ ] **Package Manager Integration (winget / Chocolatey)**: Check for available software updates for installed applications with 1-click upgrade actions.
- [ ] **Workspace Sync (Export / Import)**: Export and import Workspace app stacks in JSON format to sync configurations across multiple PCs.
- [ ] **Extensible Classification Plugins**: Support custom user-defined Python rules and community classifiers.
- [ ] **Global Hotkey Customization**: Custom key chord configuration directly from the Settings UI.
