# Project Backlog & Roadmap

This document outlines planned improvements, feature ideas, and release roadmaps for **SmartCatalog Hub**.

---

## 🎯 Upcoming Milestones

### 🚀 Milestone v1.3.0 (User Experience, Personalization & Controls)
- [ ] **Drag-and-Drop Card Reordering (Кастомная сортировка карточек)**
  - Manually drag and drop application cards within categories to set custom card priorities.
  - Persist custom sorting order in `user_data.json` alongside launch frequency and alphabetical modes.
- [ ] **Global Hotkey Customization (Настройка глобального хоткея в UI)**
  - Rebind the global launcher shortcut (default `Alt + Space`) directly from the Settings dialog.
  - Key sequence recording input field with conflict validation and instant hotkey re-registration.
- [ ] **Workspace Sync & Backup (Экспорт и импорт рабочих пространств)**
  - One-click export and import of Workspaces (custom software stacks) to a portable `.json` file.
  - Enables easy backup and migration of custom workspace layouts across multiple computers.
- [ ] **Custom Classification Rules (Пользовательские правила классификации)**
  - Interface or editable rule-book in Settings to define custom keyword and folder patterns for niche or in-house applications.
  - Precedence over automatic heuristics for full user control over application grouping.

---

### 📊 Milestone v1.4.0 (Analytics, Automation & Portability)
- [ ] **Screen Time & Usage Analytics Dashboard (Аналитика экранного времени и активности)**
  - Dedicated analytics modal or tab with interactive bar charts and usage trends (daily, weekly, monthly).
  - Visualization of top most-used software and peak productivity hours based on `playtime_data.json`.
- [ ] **Scheduled Background Software Update Checks (Проверка обновлений по расписанию)**
  - Configurable silent update scanner (e.g. daily, weekly, or upon startup).
  - Unobtrusive Windows Action Center notifications when new software patches are available.
- [ ] **Portable Mode Support (Портативный режим)**
  - Setting / flag to keep all databases (`catalog_data.json`, `user_data.json`, `icons_cache`) localized within the portable application directory instead of Windows `%APPDATA%`.

---

## ✅ Completed Milestones

### Release v1.2.1 / v1.2.2 (System Polish, Reliability & Anti-Slop UI)
- [x] **Windows Taskbar Shortcut Resilience & Self-Healing**: Fixed shortcut launching from Windows 10/11 taskbar by embedding correct `AppUserModelID` and adding auto-healing in `app.py`, `service.py`, and `watcher.py` to auto-resurrect background service on demand.
- [x] **Single-Instance Named Mutex**: Implemented Windows Kernel Named Mutex (`Global\SmartCatalog_SingleInstance_Mutex_v1`) to prevent multiple background daemon instances and duplicate system tray icons.
- [x] **Silent Background Process Execution**: Enforced `CREATE_NO_WINDOW` and `SW_HIDE` across all subprocess calls (winget, powershell, git) to eliminate transient console flashes on app launch.
- [x] **Dynamic Adaptive Upgrade Progress**: Replaced static percentage jumps with real-time pipe streaming and smooth simulated progression during winget software upgrades.
- [x] **Administrator Elevation (UAC) Retry**: Integrated `RunAs` PowerShell elevation handler with UI retry button when software installers require elevated administrator rights.
- [x] **Update Metadata & Category Preservation**: Prevented catalog item resets, category displacement (e.g. Epic Games Launcher), and duplicate auxiliary entries (e.g. Git Release Notes) during winget upgrades.
- [x] **Anti-Slop "Craft" Visual Theme**: Introduced high-contrast graphite theme adhering strictly to 4px spacing grids, subtle hairlines, and purposeful typography without AI-vibecoded gradients.
- [x] **Google Translate Banner Suppression**: Added `translate="no"` attributes to prevent unwanted browser translation popups.

### Release v1.2.0 (Auto-Updater & Software Center)
- [x] **In-App Auto-Updater for SmartCatalog Hub**: Semantic Versioning comparison, GitHub Releases API integration (`/api/app_update/check`), background chunked streaming downloader with progress bar/speed metrics, silent handover to Inno Setup installer, and status card in Settings.
- [x] **System Software Updater via winget**: Detect available updates for installed PC applications via Windows Package Manager (`winget`), correlation engine connecting package IDs to catalog apps, card update badges with version targets, dedicated Software Updates modal with instant search, individual app upgrades, and 1-click "Update All" batch action.

### Release v1.1.0 (UX & Foundations)
- [x] **Visual Application Version Badges**: Displayed `v1.1.0` badge in the header, footer status bar, and in the new "About / О программе" settings module.
- [x] **Community Feedback Loop**: Added "⭐ Star on GitHub" button along with direct quick-links to file bug reports or feature suggestions.
- [x] **Multilingual UI (English & Russian / i18n)**: Full runtime language switching with zero page reload, localized category titles, tooltips, modals, and Windows Action Center balloon toasts.
- [x] **Accent Color Themes (Accent Color Picker)**: 6 curated Windows 11 Fluent palettes (*Sky Blue*, *Ultraviolet Purple*, *Emerald Green*, *Amber Sunset*, *Ruby Rose*, and *Steel Slate*) with instant CSS variable updates.
- [x] **macOS-style Quick Look (`Space`)**: Pressing `Space` while navigating the catalog grid opens an instant preview card with high-res icon, full path, screen time, launch counter, and quick action buttons.
- [x] **Desktop Shortcut & System Tray Blank Icons**: Native DIB 32-bit BMP encoding across all icon sizes (16x16 to 256x256) inside `.ico`, resolving blank sheet fallbacks.
- [x] **Responsive Header**: Guaranteed full visibility of the Settings button across all monitor resolutions and window sizes.
