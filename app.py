import os
import sys
import time
import json
import subprocess
import urllib.request
import ctypes
import win32gui
import win32con

PORT = 48123
URL = f"http://127.0.0.1:{PORT}"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_PY = os.path.join(BASE_DIR, "service.py")
APP_PROFILE = os.path.join(BASE_DIR, ".app_profile")
LOG_FILE = os.path.join(BASE_DIR, "hub.log")

def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

def attach_to_default_desktop():
    try:
        user32 = ctypes.windll.user32
        hDesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if hDesk:
            user32.SetThreadDesktop(hDesk)
    except Exception:
        pass

def is_server_running():
    try:
        with urllib.request.urlopen(f"{URL}/api/version", timeout=0.6) as resp:
            return resp.status == 200
    except Exception:
        return False

def ensure_service_running():
    if is_server_running():
        return True
    log("Server not responding. Starting background service.py...")
    if getattr(sys, "frozen", False):
        service_exe = os.path.join(BASE_DIR, "SmartCatalogHub.exe")
        cmd = [service_exe]
    else:
        python_dir = os.path.dirname(sys.executable)
        cand_pythonw = os.path.join(python_dir, "pythonw.exe")
        pythonw = cand_pythonw if os.path.exists(cand_pythonw) else sys.executable
        cmd = [pythonw, SERVICE_PY]

    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    CREATE_BREAKAWAY_FROM_JOB = 0x01000000
    try:
        subprocess.Popen(
            cmd,
            cwd=BASE_DIR,
            creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB,
            close_fds=True
        )
    except Exception:
        try:
            subprocess.Popen(
                cmd,
                cwd=BASE_DIR,
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                close_fds=True
            )
        except Exception as e:
            log(f"Failed to spawn detached service: {e}")
            try:
                subprocess.Popen(cmd, cwd=BASE_DIR)
            except Exception:
                pass
        except Exception:
            pass
    
    # Wait up to 5 seconds for server to come up
    for _ in range(50):
        time.sleep(0.1)
        if is_server_running():
            log("Background service verified healthy.")
            return True
    log("Failed to start service within 5 seconds.")
    return False

def get_target_window_bounds():
    class RECT(ctypes.Structure):
        _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long), ('right', ctypes.c_long), ('bottom', ctypes.c_long)]
    wa = RECT()
    ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(wa), 0)

    target_vis_w = min(1180, wa.right - wa.left - 40)
    target_vis_h = min(780, wa.bottom - wa.top - 20)
    vis_x = wa.left + (wa.right - wa.left - target_vis_w) // 2
    vis_y = wa.bottom - target_vis_h

    win_x = vis_x - 7
    win_y = vis_y
    win_w = target_vis_w + 14
    win_h = target_vis_h + 7
    return win_x, win_y, win_w, win_h

def position_window(hwnd):
    try:
        attach_to_default_desktop()
        win_x, win_y, win_w, win_h = get_target_window_bounds()
        win32gui.SetWindowPos(hwnd, 0, win_x, win_y, win_w, win_h, win32con.SWP_NOZORDER | win32con.SWP_SHOWWINDOW)
    except Exception as e:
        log(f"Error positioning window: {e}")

def focus_existing_window():
    attach_to_default_desktop()
    found = []
    def enum_cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "smartcatalog hub" in title.lower():
                found.append(hwnd)
    try:
        win32gui.EnumWindows(enum_cb, None)
        if found:
            hwnd = found[0]
            log(f"Found existing window {hwnd}, bringing to front and positioning...")
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            position_window(hwnd)
            try:
                import catalog_manager
                catalog_manager.force_foreground(hwnd)
            except Exception:
                win32gui.SetForegroundWindow(hwnd)
            return True
    except Exception as e:
        log(f"Focus window error: {e}")
    return False

def ensure_browser_preferences(profile_dir):
    """
    Ensures that Chromium browser profile settings explicitly disable
    Google Translate and translation prompts.
    """
    try:
        default_dir = os.path.join(profile_dir, "Default")
        os.makedirs(default_dir, exist_ok=True)
        pref_file = os.path.join(default_dir, "Preferences")
        data = {}
        if os.path.exists(pref_file):
            try:
                with open(pref_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        
        modified = False
        if not isinstance(data.get("translate"), dict):
            data["translate"] = {}
            modified = True
        if data["translate"].get("enabled") is not False:
            data["translate"]["enabled"] = False
            modified = True
            
        blocked = data.get("translate_blocked_languages", [])
        if not isinstance(blocked, list):
            blocked = []
        for lang in ["ru", "en"]:
            if lang not in blocked:
                blocked.append(lang)
                modified = True
        data["translate_blocked_languages"] = blocked
        
        if modified:
            with open(pref_file, "w", encoding="utf-8") as f:
                json.dump(data, f)
    except Exception:
        pass

def open_ui():
    attach_to_default_desktop()
    os.makedirs(APP_PROFILE, exist_ok=True)
    ensure_browser_preferences(APP_PROFILE)
    win_x, win_y, win_w, win_h = get_target_window_bounds()
    
    # Try Chrome first
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ]
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    
    flags = [
        f"--app={URL}",
        f"--user-data-dir={APP_PROFILE}",
        "--profile-directory=Default",
        f"--window-position={win_x},{win_y}",
        f"--window-size={win_w},{win_h}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-translate",
        "--disable-features=Translate,TranslateUI,AvatarBadge,ProfilePicker,ProfileMenu"
    ]
    
    for cp in chrome_paths:
        if os.path.exists(cp):
            log(f"Launching Chrome App: {cp}")
            subprocess.Popen([cp] + flags)
            return
            
    for ep in edge_paths:
        if os.path.exists(ep):
            log(f"Launching Edge App: {ep}")
            subprocess.Popen([ep] + flags)
            return

    log("Falling back to default browser via os.startfile")
    os.startfile(URL)

def main():
    log("Launch requested.")
    try:
        import catalog_manager
        catalog_manager.heal_taskbar_shortcuts()
    except Exception:
        pass
    ensure_service_running()
    
    # If already running, focus & reposition
    if focus_existing_window():
        return
        
    open_ui()

if __name__ == "__main__":
    main()
