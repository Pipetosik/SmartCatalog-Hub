import os
import sys
import re
import json
import time
import shutil
import threading
import subprocess

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
SOFTWARE_UPDATES_PATH = os.path.join(WORKSPACE_DIR, "software_updates.json")
CATALOG_JSON_PATH = os.path.join(WORKSPACE_DIR, "catalog_data.json")

# Strict validation for winget package IDs to prevent command injection
PKG_ID_REGEX = re.compile(r'^[a-zA-Z0-9.\-_+]+$')

# Zero-ambiguity mapping between Executable Name -> Winget Package ID
EXE_TO_PACKAGE_ID = {
    'chrome.exe': 'Google.Chrome',
    'code.exe': 'Microsoft.VisualStudioCode',
    'telegram.exe': 'Telegram.TelegramDesktop',
    'discord.exe': 'Discord.Discord',
    'steam.exe': 'Valve.Steam',
    'dbeaver.exe': 'DBeaver.DBeaver.Community',
    'docker desktop.exe': 'Docker.DockerDesktop',
    'docker.exe': 'Docker.DockerDesktop',
    'postman.exe': 'Postman.Postman',
    'vlc.exe': 'VideoLAN.VLC',
    '7zfm.exe': '7zip.7zip',
    '7z.exe': '7zip.7zip',
    'git-bash.exe': 'Git.Git',
    'git.exe': 'Git.Git',
    'obsidian.exe': 'Obsidian.Obsidian',
    'node.exe': 'OpenJS.NodeJS',
    'aida64.exe': 'FinalWire.AIDA64.Extreme',
    'crystaldiskinfo.exe': 'CrystalDewWorld.CrystalDiskInfo',
    'crystaldiskinfo64.exe': 'CrystalDewWorld.CrystalDiskInfo',
    'diskinfo.exe': 'CrystalDewWorld.CrystalDiskInfo',
    'termius.exe': 'Termius.Termius',
    'airexplorer.exe': 'AirExplorer.AirExplorer',
    'anydesk.exe': 'AnyDesk.AnyDesk',
    'bcuninstaller.exe': 'Klocman.BulkCrapUninstaller',
    'zoom.exe': 'Zoom.Zoom.EXE',
    'yandexmusic.exe': 'Yandex.Music',
    'browser.exe': 'Yandex.Browser',
    'yandex.exe': 'Yandex.Browser',
    'wt.exe': 'Microsoft.WindowsTerminal',
    'windowsterminal.exe': 'Microsoft.WindowsTerminal',
    'lm studio.exe': 'ElementLabs.LMStudio',
    'hydra.exe': 'HydraLauncher.Hydra',
    'fancontrol.exe': 'Rem0o.FanControl',
    'epicgameslauncher.exe': 'EpicGames.EpicGamesLauncher',
    'jackett.exe': 'Jackett.Jackett',
    'jackettservice.exe': 'Jackett.Jackett',
    'jellyfin.exe': 'Jellyfin.Server',
    'lghub.exe': 'Logitech.GHUB',
    'msteams.exe': 'Microsoft.Teams',
    'teams.exe': 'Microsoft.Teams',
    'mobaxterm.exe': 'Mobatek.MobaXterm',
    'netbird-ui.exe': 'Netbird.Netbird',
    'netbird.exe': 'Netbird.Netbird',
    'opencode.exe': 'SST.OpenCodeDesktop',
    'sqlitestudio.exe': 'PawelSalawa.SQLiteStudio',
    'teamspeak.exe': 'XPDCJ80KGNRVSS',
    'ts3client_win64.exe': 'XPDCJ80KGNRVSS',
    'firefox.exe': 'Mozilla.Firefox',
    'brave.exe': 'Brave.Brave',
    'notepad++.exe': 'Notepad++.Notepad++',
    'sublime_text.exe': 'SublimeHQ.SublimeText.4',
    'audacity.exe': 'Audacity.Audacity',
    'obs64.exe': 'OBSProject.OBSStudio',
    'obs.exe': 'OBSProject.OBSStudio',
    'blender.exe': 'BlenderFoundation.Blender',
    'gimp-2.10.exe': 'GIMP.GIMP',
    'gimp.exe': 'GIMP.GIMP',
    'inkscape.exe': 'Inkscape.Inkscape',
    'qbittorrent.exe': 'qBittorrent.qBittorrent',
    'transmission-qt.exe': 'Transmission.Transmission',
    'wireguard.exe': 'Wireguard.Wireguard',
    'amneziavpn.exe': 'AmneziaVPN.AmneziaVPN',
    'powertoys.exe': 'Microsoft.PowerToys'
}

# Aliases for package IDs matching catalog app names
PACKAGE_ID_TO_APP_NAMES = {
    '7zip.7zip': ['7-zip', '7zip'],
    'DBeaver.DBeaver.Community': ['dbeaver'],
    'Docker.DockerDesktop': ['docker desktop', 'docker'],
    'Microsoft.VisualStudioCode': ['visual studio code', 'vscode'],
    'VideoLAN.VLC': ['vlc media player', 'vlc'],
    'Yandex.Music': ['яндекс музыка', 'yandex music'],
    'Git.Git': ['git'],
    'ElementLabs.LMStudio': ['lm studio'],
    'Obsidian.Obsidian': ['obsidian'],
    'Postman.Postman': ['postman'],
    'CrystalDewWorld.CrystalDiskInfo': ['crystaldiskinfo'],
    'FinalWire.AIDA64.Extreme': ['aida64 extreme', 'aida64'],
    'HydraLauncher.Hydra': ['hydra launcher', 'hydra'],
    'Google.Chrome': ['google chrome', 'chrome'],
    'Valve.Steam': ['steam'],
    'Discord.Discord': ['discord'],
    'Telegram.TelegramDesktop': ['telegram desktop', 'telegram'],
    'OpenJS.NodeJS': ['node.js', 'node'],
    'OpenJS.NodeJS.22': ['node.js', 'node'],
    'Termius.Termius': ['termius'],
    'AirExplorer.AirExplorer': ['air explorer', 'airexplorer'],
    'AnyDesk.AnyDesk': ['anydesk'],
    'Klocman.BulkCrapUninstaller': ['bulk crap uninstaller', 'bcuninstaller'],
    'Zoom.Zoom.EXE': ['zoom'],
    'Yandex.Browser': ['яндекс браузер', 'yandex browser'],
    'Microsoft.WindowsTerminal': ['терминал windows', 'windows terminal', 'terminal'],
    'Rem0o.FanControl': ['fancontrol'],
    'EpicGames.EpicGamesLauncher': ['epic games launcher', 'epic games'],
    'Jackett.Jackett': ['jackett'],
    'Jellyfin.Server': ['jellyfin server', 'jellyfin'],
    'Logitech.GHUB': ['logitech g hub', 'g hub'],
    'Microsoft.Teams': ['microsoft teams', 'teams'],
    'Mobatek.MobaXterm': ['mobaxterm'],
    'Netbird.Netbird': ['netbird'],
    'SST.OpenCodeDesktop': ['opencode'],
    'PawelSalawa.SQLiteStudio': ['sqlitestudio'],
    'XPDCJ80KGNRVSS': ['teamspeak'],
    'Mozilla.Firefox': ['firefox', 'mozilla firefox'],
    'Brave.Brave': ['brave', 'brave browser'],
    'Notepad++.Notepad++': ['notepad++'],
    'SublimeHQ.SublimeText.4': ['sublime text'],
    'Audacity.Audacity': ['audacity'],
    'OBSProject.OBSStudio': ['obs studio', 'obs'],
    'BlenderFoundation.Blender': ['blender'],
    'GIMP.GIMP': ['gimp'],
    'Inkscape.Inkscape': ['inkscape'],
    'qBittorrent.qBittorrent': ['qbittorrent'],
    'Transmission.Transmission': ['transmission'],
    'Wireguard.Wireguard': ['wireguard'],
    'AmneziaVPN.AmneziaVPN': ['amnezia vpn', 'amnezia'],
    'Microsoft.PowerToys': ['powertoys', 'power toys']
}

# In-memory scan state
_scan_lock = threading.Lock()
_is_scanning = False
_scan_thread = None
_last_scan_time = None
_scan_error = None
_cached_updates = []
_all_winget_packages = []

# Active upgrades state
_upgrade_lock = threading.Lock()
_active_upgrades = {}  # pkg_id -> { "status": "running"|"success"|"failed", "log": ..., "error": ..., "exit_code": ... }
_is_batch_upgrading = False

def is_winget_available():
    """Checks whether the winget executable is installed and reachable."""
    path = shutil.which('winget')
    if path:
        return True
    # Check default WindowsApps location
    local_app_data = os.environ.get('LOCALAPPDATA', '')
    if local_app_data:
        wa_path = os.path.join(local_app_data, 'Microsoft', 'WindowsApps', 'winget.exe')
        if os.path.exists(wa_path):
            return True
    return False

def get_winget_version():
    """Returns the installed winget version string, or None if unavailable."""
    if not is_winget_available():
        return None
    try:
        proc = subprocess.run(
            ['winget', '--version'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=5
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except Exception:
        pass
    return None

def validate_package_id(pkg_id):
    """Ensures package ID contains only safe alphanumeric/dots/dashes characters."""
    if not pkg_id or not isinstance(pkg_id, str):
        return False
    if len(pkg_id) > 128:
        return False
    return bool(PKG_ID_REGEX.match(pkg_id.strip()))

def parse_winget_table(output_text):
    """
    Parses `winget upgrade --include-unknown` table output.
    Handles Russian and English column headers and dynamic column widths.
    """
    if not output_text or not isinstance(output_text, str):
        return []

    lines = [l for l in output_text.splitlines() if l.strip()]
    if len(lines) < 2:
        return []

    # Find the header line containing 'Name' or 'Имя'
    header_idx = -1
    for idx, l in enumerate(lines[:10]):
        l_lower = l.lower()
        if ('name' in l_lower or 'имя' in l_lower) and ('id' in l_lower or 'ид' in l_lower):
            header_idx = idx
            break

    if header_idx == -1:
        return []

    header_line = lines[header_idx]

    # Map column headers to positions
    candidates = [
        ('name', ['имя', 'name']),
        ('id', ['ид', 'id']),
        ('version', ['версия', 'version']),
        ('available', ['доступно', 'available']),
        ('source', ['источник', 'source'])
    ]

    cols = []
    for col_key, names in candidates:
        pos = -1
        for n in names:
            p = header_line.lower().find(n)
            if p != -1:
                pos = p
                break
        if pos != -1:
            cols.append((pos, col_key))

    cols.sort(key=lambda x: x[0])
    if len(cols) < 4:
        return []

    parsed_items = []
    # Lines after header (skip separator line like '-----')
    for l in lines[header_idx + 1:]:
        if '---' in l or not l.strip():
            continue
        # Skip summary lines like '56 upgrades available.' or 'Доступных обновлений: 56.'
        l_low = l.lower()
        if 'upgrades available' in l_low or 'доступных обновлений' in l_low or 'обновление пакета' in l_low:
            continue

        item = {}
        for i in range(len(cols)):
            start = cols[i][0]
            end = cols[i + 1][0] if i + 1 < len(cols) else None
            val = l[start:end].strip() if end else l[start:].strip()
            item[cols[i][1]] = val

        pkg_id = item.get('id', '')
        available = item.get('available', '')
        # Basic validity check
        if pkg_id and available and ' ' not in pkg_id:
            parsed_items.append(item)

    return parsed_items

def find_catalog_app(pkg_id, winget_name, catalog_apps):
    """
    Correlates a winget package to a catalog application item.
    Uses executable matching, exact package mappings, and word-boundary alias matching.
    """
    pkg_id_clean = (pkg_id or '').strip()
    w_name_clean = (winget_name or '').strip()

    # Strategy 1: Check executable target from catalog apps
    for app in catalog_apps:
        target = app.get('target', '').lower()
        exe = target.split('\\')[-1] if target else ''
        if exe and exe in EXE_TO_PACKAGE_ID:
            if EXE_TO_PACKAGE_ID[exe].lower() == pkg_id_clean.lower():
                return app

    # Strategy 2: Package ID aliases with word boundary check
    aliases = PACKAGE_ID_TO_APP_NAMES.get(pkg_id_clean, [])
    if not aliases:
        for k, v in PACKAGE_ID_TO_APP_NAMES.items():
            if k.lower() == pkg_id_clean.lower():
                aliases = v
                break

    if aliases:
        for app in catalog_apps:
            app_name = app.get('name', '').lower()
            for alias in aliases:
                pattern = r'(?:\b|^)' + re.escape(alias.lower()) + r'(?:\b|$)'
                if re.search(pattern, app_name):
                    return app

    # Strategy 3: Normalized name match with word boundary
    clean_winget = re.sub(r'[\d\.\(\)\+x]+', '', w_name_clean).strip()
    if len(clean_winget) >= 3:
        for app in catalog_apps:
            app_name = app.get('name', '')
            clean_app = re.sub(r'[\d\.\(\)\+x]+', '', app_name).strip()
            if clean_winget.lower() == clean_app.lower():
                return app
            if len(clean_winget) >= 4 and len(clean_app) >= 4:
                pattern = r'(?:\b|^)' + re.escape(clean_winget.lower()) + r'(?:\b|$)'
                if re.search(pattern, clean_app.lower()):
                    return app

    return None

def correlate_with_catalog(winget_items, catalog_apps):
    """
    Returns list of correlated updates enriched with catalog app metadata.
    """
    correlated = []
    seen_app_ids = set()

    for item in winget_items:
        pkg_id = item.get('id', '')
        w_name = item.get('name', '')
        c_ver = item.get('version', '')
        a_ver = item.get('available', '')
        source = item.get('source', 'winget')

        matched_app = find_catalog_app(pkg_id, w_name, catalog_apps)
        if matched_app and matched_app['id'] not in seen_app_ids:
            seen_app_ids.add(matched_app['id'])
            correlated.append({
                "app_id": matched_app['id'],
                "catalog_name": matched_app['name'],
                "icon": matched_app.get('icon', ''),
                "category": matched_app.get('category', ''),
                "package_id": pkg_id,
                "winget_name": w_name,
                "current_version": c_ver,
                "available_version": a_ver,
                "source": source
            })

    return correlated

def load_cached_updates():
    """Loads cached updates from software_updates.json."""
    global _cached_updates, _all_winget_packages, _last_scan_time
    if os.path.exists(SOFTWARE_UPDATES_PATH):
        try:
            with open(SOFTWARE_UPDATES_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                _cached_updates = data.get('updates', [])
                _all_winget_packages = data.get('all_winget_packages', [])
                _last_scan_time = data.get('last_scan', None)
                return data
        except Exception:
            pass
    return {
        "last_scan": None,
        "total_updates": 0,
        "updates": [],
        "all_winget_packages": []
    }

def save_cached_updates(updates, all_pkgs, scan_time=None):
    """Saves updates to software_updates.json atomically."""
    global _cached_updates, _all_winget_packages, _last_scan_time
    _cached_updates = updates
    _all_winget_packages = all_pkgs
    _last_scan_time = scan_time or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    data = {
        "last_scan": _last_scan_time,
        "total_updates": len(updates),
        "updates": _cached_updates,
        "all_winget_packages": _all_winget_packages
    }
    tmp_path = SOFTWARE_UPDATES_PATH + ".tmp"
    try:
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if os.path.exists(SOFTWARE_UPDATES_PATH):
            os.remove(SOFTWARE_UPDATES_PATH)
        os.rename(tmp_path, SOFTWARE_UPDATES_PATH)
    except Exception as e:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        print(f"[WingetManager] Error saving cache: {e}")

def _run_scan_thread():
    """Background worker for winget upgrade check."""
    global _is_scanning, _scan_error
    try:
        if not is_winget_available():
            _scan_error = "winget is not available on this system"
            return

        cmd = ['winget', 'upgrade', '--include-unknown']
        proc = subprocess.run(
            cmd,
            capture_output=True,
            timeout=120
        )

        stdout_text = proc.stdout.decode('utf-8', errors='replace')
        parsed = parse_winget_table(stdout_text)

        catalog_apps = []
        if os.path.exists(CATALOG_JSON_PATH):
            try:
                with open(CATALOG_JSON_PATH, 'r', encoding='utf-8') as f:
                    catalog_apps = json.load(f)
            except Exception:
                pass

        correlated = correlate_with_catalog(parsed, catalog_apps)
        save_cached_updates(correlated, parsed)
        _scan_error = None
    except Exception as e:
        _scan_error = str(e)
        print(f"[WingetManager] Scan error: {e}")
    finally:
        _is_scanning = False

def start_scan(force=False):
    """Starts a non-blocking background scan if not already running."""
    global _is_scanning, _scan_thread
    with _scan_lock:
        if _is_scanning:
            return {"status": "scanning", "message": "Scan already in progress"}
        _is_scanning = True
        _scan_thread = threading.Thread(target=_run_scan_thread, daemon=True)
        _scan_thread.start()
        return {"status": "started", "message": "Software updates scan started"}

def get_status():
    """Returns the full status of winget software updates."""
    # Ensure cache is loaded if in-memory is empty
    if not _cached_updates and os.path.exists(SOFTWARE_UPDATES_PATH):
        load_cached_updates()

    return {
        "winget_available": is_winget_available(),
        "winget_version": get_winget_version(),
        "scanning": _is_scanning,
        "last_scan": _last_scan_time,
        "total_updates": len(_cached_updates),
        "updates": _cached_updates,
        "active_upgrades": _active_upgrades,
        "is_batch_upgrading": _is_batch_upgrading,
        "error": _scan_error
    }

def _run_upgrade_worker(pkg_id, elevated=False):
    """Executes upgrade for a single package."""
    global _active_upgrades
    with _upgrade_lock:
        _active_upgrades[pkg_id] = {
            "status": "running",
            "start_time": time.time(),
            "output": "",
            "error": None,
            "exit_code": None
        }

    try:
        if elevated:
            # Execute with PowerShell RunAs elevation
            ps_cmd = (
                f"Start-Process winget -ArgumentList 'upgrade', '--exact', '--id', '{pkg_id}', "
                f"'--accept-source-agreements', '--accept-package-agreements', '--disable-interactivity' "
                f"-Verb RunAs -Wait"
            )
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=600
            )
            exit_code = proc.returncode
            output = proc.stdout + proc.stderr
        else:
            cmd = [
                'winget', 'upgrade', '--exact', '--id', pkg_id,
                '--accept-source-agreements', '--accept-package-agreements',
                '--disable-interactivity'
            ]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                stdin=subprocess.DEVNULL,
                timeout=600
            )
            exit_code = proc.returncode
            output = proc.stdout.decode('utf-8', errors='replace') + proc.stderr.decode('utf-8', errors='replace')

            # Check for elevation requirement: 0x800702e4 (signed: -2147023644) or code 1603 / UAC error
            if exit_code in (-2147023644, 2147942405, 1603) or 'requires elevation' in output.lower() or 'администратора' in output.lower():
                # Attempt automatic RunAs escalation
                ps_cmd = (
                    f"Start-Process winget -ArgumentList 'upgrade', '--exact', '--id', '{pkg_id}', "
                    f"'--accept-source-agreements', '--accept-package-agreements', '--disable-interactivity' "
                    f"-Verb RunAs -Wait"
                )
                elev_proc = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_cmd],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=600
                )
                exit_code = elev_proc.returncode
                output += "\n[Elevated RunAs Execution]:\n" + elev_proc.stdout + elev_proc.stderr

        with _upgrade_lock:
            if exit_code == 0:
                _active_upgrades[pkg_id]["status"] = "success"
                # Remove upgraded item from cache
                global _cached_updates
                _cached_updates = [u for u in _cached_updates if u.get('package_id') != pkg_id]
                save_cached_updates(_cached_updates, _all_winget_packages, _last_scan_time)
            else:
                _active_upgrades[pkg_id]["status"] = "failed"
                _active_upgrades[pkg_id]["error"] = f"Exit code {exit_code}"
            _active_upgrades[pkg_id]["output"] = output[-1000:]
            _active_upgrades[pkg_id]["exit_code"] = exit_code

    except Exception as e:
        with _upgrade_lock:
            _active_upgrades[pkg_id]["status"] = "failed"
            _active_upgrades[pkg_id]["error"] = str(e)
            _active_upgrades[pkg_id]["exit_code"] = -1

def upgrade_package(pkg_id, elevated=False):
    """Triggers background upgrade for a specific package."""
    if not validate_package_id(pkg_id):
        return {"status": "error", "message": f"Invalid package ID: {pkg_id}"}

    with _upgrade_lock:
        if pkg_id in _active_upgrades and _active_upgrades[pkg_id].get("status") == "running":
            return {"status": "running", "message": f"Upgrade for {pkg_id} is already in progress"}

    t = threading.Thread(target=_run_upgrade_worker, args=(pkg_id, elevated), daemon=True)
    t.start()
    return {"status": "started", "package_id": pkg_id}

def _run_batch_upgrade_thread(elevated=False):
    """Sequentially upgrades all cached packages."""
    global _is_batch_upgrading
    try:
        # Snapshot current list of updates
        packages = [u.get('package_id') for u in _cached_updates if u.get('package_id')]
        for pkg_id in packages:
            if not validate_package_id(pkg_id):
                continue
            _run_upgrade_worker(pkg_id, elevated=elevated)
            time.sleep(1)
    finally:
        _is_batch_upgrading = False

def upgrade_all(elevated=False):
    """Triggers background batch upgrade of all available updates."""
    global _is_batch_upgrading
    with _upgrade_lock:
        if _is_batch_upgrading:
            return {"status": "running", "message": "Batch upgrade already in progress"}
        _is_batch_upgrading = True

    t = threading.Thread(target=_run_batch_upgrade_thread, args=(elevated,), daemon=True)
    t.start()
    return {"status": "started", "total": len(_cached_updates)}
