import os
import sys
import re
import json
import time
import threading
import urllib.request
import urllib.parse
import urllib.error
import tempfile
import subprocess

CURRENT_VERSION = "1.1.0"
GITHUB_REPO = "Pipetosik/SmartCatalog-Hub"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

download_lock = threading.Lock()
download_state = {
    "status": "idle",       # idle | downloading | ready | error
    "percent": 0,
    "downloaded_bytes": 0,
    "total_bytes": 0,
    "speed_kbps": 0.0,
    "target_file": "",
    "asset_name": "",
    "latest_version": "",
    "error": None
}

last_check_cache = {
    "timestamp": 0,
    "result": None
}

def parse_semver(ver_str):
    """
    Parses a version string like '1.1.0', 'v1.2.0', 'v1.2.0-beta' into a tuple (major, minor, patch).
    """
    if not ver_str:
        return (0, 0, 0)
    clean = re.sub(r'^[^\d]*', '', str(ver_str).strip())
    base = re.split(r'[-+]', clean)[0]
    parts = base.split('.')
    nums = []
    for p in parts[:3]:
        try:
            nums.append(int(p))
        except ValueError:
            nums.append(0)
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums)

def is_newer_version(latest_str, current_str=CURRENT_VERSION):
    return parse_semver(latest_str) > parse_semver(current_str)

def check_for_updates(force=False):
    """
    Queries GitHub API for the latest release. Caches result for 60 seconds unless force=True.
    """
    now = time.time()
    if not force and last_check_cache["result"] and (now - last_check_cache["timestamp"] < 60):
        return last_check_cache["result"]

    req = urllib.request.Request(
        GITHUB_API_URL,
        headers={
            "User-Agent": f"SmartCatalog-Hub/{CURRENT_VERSION}",
            "Accept": "application/vnd.github.v3+json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=7) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                tag_name = data.get("tag_name", "").lstrip("v")
                latest_version = tag_name or data.get("name", "").lstrip("v")
                update_available = is_newer_version(latest_version, CURRENT_VERSION)

                download_url = ""
                asset_name = ""
                file_size = 0
                for asset in data.get("assets", []):
                    aname = asset.get("name", "")
                    if aname.endswith(".exe") or "Setup" in aname:
                        download_url = asset.get("browser_download_url", "")
                        asset_name = aname
                        file_size = asset.get("size", 0)
                        break

                result = {
                    "success": True,
                    "update_available": update_available,
                    "current_version": CURRENT_VERSION,
                    "latest_version": latest_version,
                    "release_name": data.get("name", f"v{latest_version}"),
                    "release_notes": data.get("body", ""),
                    "release_url": data.get("html_url", f"https://github.com/{GITHUB_REPO}/releases/latest"),
                    "download_url": download_url,
                    "asset_name": asset_name,
                    "file_size": file_size,
                    "published_at": data.get("published_at", "")
                }
                last_check_cache["timestamp"] = now
                last_check_cache["result"] = result
                return result
            else:
                return {
                    "success": False,
                    "error": f"GitHub returned HTTP {response.status}",
                    "current_version": CURRENT_VERSION,
                    "update_available": False
                }
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "error": f"GitHub API error: {e.code} {e.reason}",
            "current_version": CURRENT_VERSION,
            "update_available": False
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Network error: {str(e)}",
            "current_version": CURRENT_VERSION,
            "update_available": False
        }

def start_download(download_url=None):
    with download_lock:
        if download_state["status"] == "downloading":
            return False, "Download already in progress"

        if not download_url:
            check = check_for_updates()
            download_url = check.get("download_url")
            if not download_url:
                return False, "No downloadable installer found in release"

        parsed = urllib.parse.urlparse(download_url)
        if parsed.netloc not in ("github.com", "objects.githubusercontent.com"):
            return False, "Untrusted download source"

        download_state["status"] = "downloading"
        download_state["percent"] = 0
        download_state["downloaded_bytes"] = 0
        download_state["total_bytes"] = 0
        download_state["speed_kbps"] = 0.0
        download_state["error"] = None

        t = threading.Thread(target=_download_worker, args=(download_url,), daemon=True)
        t.start()
        return True, "Download started"

def _download_worker(url):
    try:
        temp_dir = tempfile.gettempdir()
        filename = os.path.basename(urllib.parse.urlparse(url).path) or "SmartCatalog-Setup.exe"
        target_path = os.path.join(temp_dir, filename)
        part_path = target_path + ".part"

        req = urllib.request.Request(
            url,
            headers={"User-Agent": f"SmartCatalog-Hub/{CURRENT_VERSION}"}
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            total_size = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            start_time = time.time()
            last_calc_time = start_time
            bytes_since_last = 0

            with open(part_path, "wb") as out_file:
                while True:
                    chunk = response.read(65536)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    downloaded += len(chunk)
                    bytes_since_last += len(chunk)

                    now = time.time()
                    elapsed = now - last_calc_time
                    if elapsed >= 0.4:
                        speed = (bytes_since_last / 1024.0) / elapsed
                        percent = int((downloaded / total_size) * 100) if total_size > 0 else 0
                        with download_lock:
                            download_state["percent"] = percent
                            download_state["downloaded_bytes"] = downloaded
                            download_state["total_bytes"] = total_size
                            download_state["speed_kbps"] = round(speed, 1)
                        last_calc_time = now
                        bytes_since_last = 0

            if os.path.exists(target_path):
                try:
                    os.remove(target_path)
                except Exception:
                    pass
            os.rename(part_path, target_path)

            with download_lock:
                download_state["status"] = "ready"
                download_state["percent"] = 100
                download_state["downloaded_bytes"] = downloaded
                download_state["total_bytes"] = downloaded
                download_state["target_file"] = target_path
                download_state["asset_name"] = filename

    except Exception as e:
        with download_lock:
            download_state["status"] = "error"
            download_state["error"] = str(e)

def get_download_progress():
    with download_lock:
        return dict(download_state)

def install_update(installer_path=None, silent=False):
    """
    Executes the downloaded setup executable and initiates graceful shutdown.
    """
    with download_lock:
        target = installer_path or download_state.get("target_file")

    if not target or not os.path.exists(target):
        return False, "Installer file not found on disk"

    temp_dir = os.path.realpath(tempfile.gettempdir())
    resolved_target = os.path.realpath(target)
    if not resolved_target.startswith(temp_dir):
        return False, "Invalid installer path"

    try:
        flags = "/SILENT /CLOSEAPPLICATIONS" if silent else ""
        cmd = f'timeout /t 2 /nobreak >nul & start "" "{resolved_target}" {flags}'
        subprocess.Popen(["cmd.exe", "/c", cmd], shell=True)
        threading.Timer(2.0, lambda: os._exit(0)).start()
        return True, "Installer launched. SmartCatalog is restarting..."
    except Exception as e:
        return False, str(e)
