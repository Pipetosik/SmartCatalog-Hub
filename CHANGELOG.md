# Changelog

All notable changes to **SmartCatalog Hub** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

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
