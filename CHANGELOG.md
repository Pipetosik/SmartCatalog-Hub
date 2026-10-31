# Changelog

All notable changes to **SmartCatalog Hub** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.0] - 2026-11-01

### Added
- **In-App Auto-Updater for SmartCatalog Hub (Self-Updater)**:
  - Integrated GitHub Releases API (`/api/app_update/check`) with Semantic Versioning comparison.
  - Background streaming chunked downloader (`/api/app_update/download`, `/api/app_update/progress`) with real-time download speed calculation, atomic `.part` verification, and progress bar.
  - Robust SSL certificate handling: extracts Windows system root certificates via `ssl.enum_certificates("ROOT")` with automatic unverified fallback, resolving `CERTIFICATE_VERIFY_FAILED` errors in clean Windows Sandbox environments.
  - Safe handover to Inno Setup installer (`/api/app_update/install`).
  - Interactive "About / О программе" update card in Settings and header version badge alert (`v1.1.0 ↑`).
- **System Software Package Updater via `winget` (Windows Package Manager)**:
  - Automatic PC-wide software upgrade auditing with dynamic column parsing supporting Russian and English Windows locales.
  - High-precision correlation engine mapping `winget` package IDs to `catalog_data.json` applications using executable paths and word-boundary matching (tested and matched 28 catalog apps on host).
  - Glowing update badges on catalog application cards displaying target versions (e.g. `↑ 1.143.1`, `↑ 26.2.0`, `↑ 5.125.3`).
  - Header notification button with glowing counter pill (`28`).
  - Dedicated "Software Updates / Обновления программ" modal dialog with instant search filtering, single app updates, and 1-click "Update All" batch action.
  - UAC elevation auto-escalation handler via PowerShell `Start-Process winget -Verb RunAs` for packages requiring Administrator privileges.
- **Full Bilingual Localization**:
  - 344 synchronized entries in the `I18N` dictionary across Russian and English.

### Fixed
- **System Tray Drive Path Bug**:
  - Replaced hardcoded reference `F:\SmartCatalog` in `tray_and_hotkey.py` with localized `"Открыть папку каталога" / "Open Catalog Folder"`, opening the dynamically detected catalog path.

## [1.1.0] - 2026-10-31

### Added
- **Visual Version Badges**: Displayed active application version `v1.1.0` directly in the header adjacent to brand title, in the footer status bar, and in the new "About / О программе" settings module.
- **Multilingual Support (i18n)**: Seamless instant runtime switching between **Russian (RU)** and **English (EN)** without page reload. All UI text, category names (e.g. `01. Разработка и Код` $\leftrightarrow$ `01. Development & Code`), toasts, hints, and modal dialogs are localized.
- **Accent Color Themes**: Added Accent Color Picker in Settings featuring 6 curated Windows 11 Fluent themes: *Sky Blue*, *Ultraviolet Purple*, *Emerald Green*, *Amber Sunset*, *Ruby Rose*, and *Steel Slate*.
- **macOS-style Quick Look (`Space`)**: Pressing `Space` while navigating the catalog grid opens an instant preview card with high-res icon, full path, total screen playtime, launch counter, last launched timestamp, and direct actions (`↵ Launch`, `Alt+↵ Folder`, `F Favorite`, `Space Close`).
- **In-App Community & Feedback Loop**: Added dedicated "О программе / About" section with direct links to Star on GitHub (`⭐ Star on GitHub`), file bug reports or feature requests via GitHub issue templates, and view the release changelog.
- **Shortcut Cold-Start Auto-Resurrection**: Double-clicking the Desktop, Start Menu, or Taskbar shortcut now verifies that the background catalog service is alive via `/api/version` (<1ms probe) and automatically resurrects `service.py` silently in a detached process if stopped, preventing `ERR_CONNECTION_REFUSED`.

### Fixed
- **Desktop Shortcut & System Tray Blank Icons**: Re-encoded `.ico` assets with native Windows DIB 32-bit bitmaps (16x16, 24x24, 32x32, 48x48, 64x64, 128x128, 256x256) instead of PNG-compressed streams, resolving Windows Explorer shortcut icon fallback to white sheet and Win32 tray fallback to generic window.
- **Header Action Bar Responsive Layout**: Increased label collapse threshold to `<= 1550px`, collapsing action buttons to compact 34x34px icon buttons with tooltips, guaranteeing that the Settings button (`#settingsBtn`) is always visible in full at any display resolution.
- **Favorites Counter Discrepancy**: Fixed initial scan state by enforcing `validAppIds` check and ensuring `userData.favorites` starts completely empty (`[]`) on clean installations without stale mock identifiers.
- **Socket Disconnect Exception Handling**: Caught `ConnectionAbortedError` and `ConnectionResetError` during HTTP response streaming in `server.py` to eliminate socket noise when browser tabs close.

## [1.0.2] - 2026-10-30

### Fixed
- **Desktop Shortcut & System Tray Icons**: Embedded and bundled multi-resolution `icon.ico` (16x16 through 256x256) directly in installer root and PyInstaller distribution, ensuring crisp display across Desktop shortcuts, Start Menu, and System Tray.
- **Initial Clean State**: Removed legacy development mock seeds from `user_data.json` and `playtime_data.json`. On a fresh installation, Favorites and Frequently Used counters start at 0 and accurately reflect user activity.
- **Responsive Header & Settings Button Visibility**: Added responsive layout rules collapsing header action button labels into compact icon buttons on screens `<= 1350px`, guaranteeing the Settings button (`#settingsBtn`) and Rescan button (`#rescanBtn`) remain visible at any window scale.
- **Line Endings Normalization**: Normalized CRLF line formatting across client assets.

## [1.0.1] - 2026-10-30

### Fixed
- **PowerShell Window Flashing**: Replaced external powershell shortcut resolver subprocesses with in-process COM `WScript.Shell` and win32 APIs.
- **Notification Spam**: Silenced redundant Windows balloon toast cascades during bulk initial indexing.
- **Visual Catalog Loader**: Added dedicated progress state while the initial scan completes.
- **Windows System Tools Categorization**: Refined classification heuristics for Administrative Tools, Registry Editor, Performance Monitor, and Resource Monitor.
- **Diagnostic Logging**: Added classification debug log viewer accessible from Settings.

## [1.0.0] - 2026-10-30

### Added
- **Windows 11 Fluent 2 Acrylic Design**: native window backdrop with Mica/Acrylic effects, micro-borders, and responsive layout.
- **Automated Kernel File Monitoring (`ReadDirectoryChangesW`)**: real-time detection of newly installed software with 0% CPU consumption in idle.
- **Smart App Classifier**: 13 categorical engines (Development, Databases, AI/LLMs, Browsers, Communication, Remote Access, Media, Games, Office, Graphics, Utilities, Security, Misc).
- **High-Resolution Icon Extraction**: multi-resolution PE header icon extractor producing crisp 128x128 / 256x256 PNGs.
- **Global Hotkey & Tray Coordinator**: `Alt+C` global launcher with tray icon, desktop restoration, and minimized window activation.
- **System Resource Monitor & Task Manager**: continuous delta-based CPU, RAM, and Disk telemetry with safe process termination.
- **Insights & Screen Time Analytics**: passive, high-efficiency window foreground tracking with daily metrics and category breakdowns.
- **Workspaces (App Stacks)**: grouped single-click launch for development, gaming, and productivity setups.
- **Clipboard History & Snippets**: fast clipboard history manager with quick snippet templates.
- **Search Engine**: fuzzy search with auto-correction for mismatched keyboard layouts (RU $\leftrightarrow$ EN) and acronyms.
- **Security Hardening**: strict origin validation (CORS/CSRF), realpath Path Traversal protections, and payload size bounds.
