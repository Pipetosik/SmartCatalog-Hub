<p align="center">
  <img src="assets/icon.ico" width="84" height="84" alt="SmartCatalog Hub Logo" />
</p>

<h1 align="center">SmartCatalog Hub</h1>

<p align="center">
  <b>Modern application launcher, Start Menu organizer, and system resource monitor for Windows 10 & 11</b>
</p>

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/Language-English-blue.svg" alt="English" /></a>
  <a href="README_RU.md"><img src="https://img.shields.io/badge/Language-Русский-lightgrey.svg" alt="Русский" /></a>
  <img src="https://img.shields.io/badge/Release-v1.2.0-emerald.svg?style=flat-square" alt="Version 1.2.0" />
  <img src="https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078d4?style=flat-square&logo=windows" alt="Platform" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776ab?style=flat-square&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/License-MIT-success?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/UI-Fluent%202%20Acrylic-6366f1?style=flat-square" alt="Fluent Design" />
  <img src="https://img.shields.io/badge/Idle%20CPU-0.0%25-brightgreen?style=flat-square" alt="Zero Idle CPU" />
</p>

---

## About the Project

**SmartCatalog Hub** is a lightweight, responsive, and aesthetic desktop command center for Windows. It automatically indexes installed software, organizes applications into 13 curated categories, tracks new software installations in real-time via Windows kernel filesystem notifications, and provides an instant quick-launch overlay with global hotkey support.

### Main Catalog Window
![SmartCatalog Hub Main Screen](assets/screenshots/main_grid.png)

---

## Key Features

### 🚀 Zero-Config Real-Time Cataloging
* **Kernel-Level Filesystem Monitoring (`ReadDirectoryChangesW`)**: Background service reacts instantly to newly created shortcuts whenever software is installed, without consuming CPU cycles while waiting (0% CPU idle).
* **13 Smart Categories**: Automatic grouping into Development, Databases, AI & Neural Networks, Browsers, Communication & Messengers, Network & VPN, Multimedia & Audio, Games, Game Launchers, Office, Graphics & Design, System Utilities, and Security.
* **Intelligent Noise Filtering**: Uninstaller wizards, manual links, and documentation shortcuts are automatically ignored.
* **High-Definition Icon Extraction**: Direct PE header extraction for sharp 128×128 and 256×256 PNGs with multi-resolution native DIB `.ico` encoding.

---

### 🌐 Multilingual Interface (English & Russian)
Seamless runtime language switching between **English (EN)** and **Russian (RU)** without reloading the page. All UI elements, category labels, tooltips, modal dialogs, and Windows Action Center balloon toasts are fully localized.

---

### 🎨 Windows 11 Fluent 2 Acrylic & Custom Accent Themes
* **5 Background Materials**: Start Menu (Windows 11 Acrylic Glass), Obsidian (Dark Slate), Fluent Acrylic (Deep Frosted Blur), Mica Alt, and OLED Pure Black.
* **6 Curated Accent Palettes**: Sky Blue, Ultraviolet Purple, Emerald Green, Amber Sunset, Ruby Rose, and Steel Slate with real-time CSS variable updates.

---

### ⚡ Integrated System Monitor & Task Manager
Built-in hardware telemetry and process monitor allows checking live system metrics and safely terminating unresponsive applications with a single click.

![System Monitor](assets/screenshots/system_monitor.png)

* **Hardware Metrics**: Real-time CPU load percentage, RAM usage, and C: drive free space.
* **Top Resource Consumers**: Separate top lists for highest memory and processor utilization.
* **OS Integrity Guard**: Hardcoded safeguards prevent accidental termination of critical Windows system processes (`System`, `csrss`, `dwm`, `lsass`, `services`, etc.).

---

### ⏱ Screen Time Analytics & Workspaces
| Screen Time Insights | Workspaces (App Stacks) |
| :---: | :---: |
| ![Screen Time Analytics](assets/screenshots/insights.png) | ![Workspaces](assets/screenshots/workspaces.png) |
| Passive tracking of foreground window activity, total screen time, launch counts, and category breakdowns. | Group related tools into custom stacks (Development, Gaming, Office) and launch them simultaneously with 1 click. |

---

### 👁 macOS-Style Quick Look (`Space`)
Navigate through the application grid using arrow keys and press <kbd>Space</kbd> to inspect an app with Quick Look: view its high-resolution icon, full executable path, total screen time, launch counter, last launched date, and trigger instant actions.

---

### 🔄 Shortcut Cold-Start Auto-Resurrection
Launching the app via its Desktop, Start Menu, or Taskbar shortcut performs an ultra-fast (<1ms) HTTP health check (`/api/version`). If the background daemon is not currently active, it is silently resurrected in an isolated detached process without throwing browser connection errors.

---

### ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| <kbd>Alt</kbd> + <kbd>Space</kbd> / <kbd>Alt</kbd> + <kbd>C</kbd> | Toggle SmartCatalog Hub visibility from any application |
| <kbd>Ctrl</kbd> + <kbd>K</kbd> / <kbd>Ctrl</kbd> + <kbd>F</kbd> | Focus the search bar |
| <kbd>Ctrl</kbd> + <kbd>M</kbd> | Toggle between Full Grid and Compact Search mode (Raycast / Spotlight style) |
| <kbd>Space</kbd> | Open Quick Look preview for the focused application |
| <kbd>Enter</kbd> | Launch the selected application |
| <kbd>Alt</kbd> + <kbd>Enter</kbd> | Open containing folder in Windows Explorer |
| <kbd>F</kbd> | Toggle Favorite status for the selected application |
| <kbd>,</kbd> (comma) | Open Settings panel |
| <kbd>Esc</kbd> | Close active modal dialog or hide the launcher window |

> **Typo & Layout Correction**: The search engine automatically corrects mismatched keyboard layouts (e.g. typing `ghbkj;tybt` finds `приложение`, `vsc` finds `Visual Studio Code`).

---

## Installation & Setup

### Option 1. Standalone Windows Installer (Recommended for Users)
1. Head over to the [Releases](https://github.com/Pipetosik/SmartCatalog-Hub/releases) page.
2. Download the latest installer executable: `SmartCatalog-Setup-v1.2.0.exe`.
3. Run the installer and follow the on-screen setup instructions.

---

### Option 2. Run from Source (Recommended for Developers)

**Prerequisites**: Windows 10/11 x64, Python 3.10 or higher.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Pipetosik/SmartCatalog-Hub.git
   cd SmartCatalog-Hub
   ```

2. **Run the automated setup script**:
   ```bat
   install.bat
   ```
   This script creates a Python virtual environment (`venv`), installs required dependencies (`requirements.txt`), registers the background daemon in the Windows Task Scheduler, and starts the client.

3. **Manual Execution (Optional)**:
   ```bash
   # Start the background daemon
   python service.py

   # Open the GUI client window
   python app.py
   ```

4. **Clean Uninstall**:
   ```bat
   uninstall.bat
   ```

---

## Project Structure

```
SmartCatalog-Hub/
├── assets/                  # Application icons, graphics, and release screenshots
├── static/                  # Web client frontend (HTML5, Vanilla JS, Fluent CSS)
│   ├── index.html           # Main UI layout with data-i18n bindings
│   ├── style.css            # Windows 11 Fluent 2 Acrylic design, animations, themes
│   └── app.js               # Client controller, search engine, shortcuts, and API client
├── app.py                   # Windowed client (Edge WebView2 / App mode) with auto-resurrection
├── service.py               # Background Windows daemon coordinator
├── server.py                # HTTP REST API server (Python http.server)
├── watcher.py               # ReadDirectoryChangesW kernel filesystem monitor
├── catalog_manager.py       # Catalog indexer, execution dispatcher, telemetry aggregation
├── classifier.py            # Categorization heuristics and metadata rules
├── icon_extractor.py        # Windows PE header multi-resolution icon extractor
├── tray_and_hotkey.py       # System tray integration and global hotkey listener
├── install_autostart.py     # Windows Task Scheduler autostart registrar
├── install.bat              # One-click deployment script
├── uninstall.bat            # Clean removal script
├── tests/                   # Automated test suite (security audits, i18n symmetry)
└── requirements.txt         # Python dependencies
```

---

## Security & Reliability

SmartCatalog Hub has undergone rigorous security testing and audit checks:
* **Path Traversal Protection (CWE-22)**: Strict `realpath` canonical boundary verification prevents access outside designated assets and icons cache directories.
* **CORS & CSRF Safeguards (CWE-346/352)**: Strict `Origin` and `Sec-Fetch-Site` validation blocks malicious cross-origin requests from external browsers.
* **Denial-of-Service Defense**: Inbound HTTP payload sizes are capped at 2 MB, and filesystem disk writes are debounced with atomic temp-file swaps.
* **Automated Verification**: Run test suite with:
  ```bash
  python -m unittest discover tests
  ```

---

## Contributing

Contributions are welcome! Please review [CONTRIBUTING.md](CONTRIBUTING.md) for details on code style, classifier rules submission, and testing guidelines.

If you encounter any issues or have feature suggestions, feel free to submit a [Bug Report](https://github.com/Pipetosik/SmartCatalog-Hub/issues/new?template=bug_report.md) or [Feature Request](https://github.com/Pipetosik/SmartCatalog-Hub/issues/new?template=feature_request.md).

---

## License

Distributed under the [MIT License](LICENSE). You are free to use, modify, and distribute this software for personal and commercial purposes.
