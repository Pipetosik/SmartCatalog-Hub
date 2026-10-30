import os
import json
import re
import hashlib
import subprocess
import time
import threading
import ctypes
from ctypes import wintypes
import psutil
import pythoncom
import win32com.client
from classifier import classify_app, get_app_description, is_junk_or_uninstaller, CATEGORY_RULES, get_app_search_aliases, KNOWN_APPS
from icon_extractor import extract_icon_best

SMART_CATALOG_ROOT = r"F:\SmartCatalog" if os.path.exists(r"F:\SmartCatalog") else os.path.join(
    os.environ.get("PROGRAMDATA", r"C:\ProgramData"),
    r"Microsoft\Windows\Start Menu\Programs\SmartCatalog"
)
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(WORKSPACE_DIR, "icons_cache")
CATALOG_JSON_PATH = os.path.join(WORKSPACE_DIR, "catalog_data.json")
USER_DATA_PATH = os.path.join(WORKSPACE_DIR, "user_data.json")
PLAYTIME_DATA_PATH = os.path.join(WORKSPACE_DIR, "playtime_data.json")
CLIPBOARD_DATA_PATH = os.path.join(WORKSPACE_DIR, "clipboard_history.json")
WORKSPACES_DATA_PATH = os.path.join(WORKSPACE_DIR, "workspaces_data.json")
SNIPPETS_DATA_PATH = os.path.join(WORKSPACE_DIR, "snippets_data.json")

os.makedirs(ICONS_DIR, exist_ok=True)

import time

_USER_DATA_CACHE = None
_USER_DATA_MTIME = 0

def load_user_data():
    global _USER_DATA_CACHE, _USER_DATA_MTIME
    if os.path.exists(USER_DATA_PATH):
        try:
            mtime = os.path.getmtime(USER_DATA_PATH)
            if _USER_DATA_CACHE is not None and mtime == _USER_DATA_MTIME:
                return _USER_DATA_CACHE
            with open(USER_DATA_PATH, "r", encoding="utf-8") as f:
                _USER_DATA_CACHE = json.load(f)
                _USER_DATA_MTIME = mtime
                return _USER_DATA_CACHE
        except Exception:
            pass
            
    if _USER_DATA_CACHE is not None:
        return _USER_DATA_CACHE

    data = {
        "favorites": [],
        "launch_stats": {}
    }
    save_user_data(data)
    return data

import tempfile
import shutil

CATALOG_VERSION = int(time.time())

def bump_catalog_version():
    global CATALOG_VERSION
    CATALOG_VERSION = int(time.time() * 1000)
    return CATALOG_VERSION

def get_catalog_version():
    return CATALOG_VERSION

def _atomic_save_json(file_path, data, bump_version=False):
    dir_name = os.path.dirname(os.path.abspath(file_path))
    try:
        with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tf:
            json.dump(data, tf, ensure_ascii=False, indent=2)
            temp_name = tf.name
        os.replace(temp_name, file_path)
        if bump_version:
            bump_catalog_version()
        return True
    except Exception:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            if bump_version:
                bump_catalog_version()
            return True
        except Exception:
            return False

def save_user_data(data):
    global _USER_DATA_CACHE, _USER_DATA_MTIME
    _USER_DATA_CACHE = data
    _USER_DATA_MTIME = time.time()
    return _atomic_save_json(USER_DATA_PATH, data, bump_version=False)

def save_catalog_data(data):
    global _CATALOG_CACHE, _CATALOG_CACHE_MTIME, _PROCESS_MAP_CACHE
    _CATALOG_CACHE = data
    _CATALOG_CACHE_MTIME = time.time()
    _PROCESS_MAP_CACHE = None
    return _atomic_save_json(CATALOG_JSON_PATH, data, bump_version=True)

def record_app_launch(app_id):
    data = load_user_data()
    stats = data.setdefault("launch_stats", {})
    entry = stats.setdefault(app_id, {"count": 0, "last_launched": 0})
    entry["count"] = entry.get("count", 0) + 1
    entry["last_launched"] = time.time()
    save_user_data(data)
    return entry

def toggle_favorite(app_id):
    data = load_user_data()
    favs = list(data.setdefault("favorites", []))
    if app_id in favs:
        favs.remove(app_id)
        is_fav = False
    else:
        favs.append(app_id)
        is_fav = True
    data["favorites"] = favs
    save_user_data(data)
    return is_fav, favs

def get_setting(key, default=None):
    data = load_user_data()
    return data.get("settings", {}).get(key, default)

def set_setting(key, value):
    data = load_user_data()
    settings = data.setdefault("settings", {})
    settings[key] = value
    save_user_data(data)
    return settings


TRANSLIT = {
    'а':'a', 'б':'b', 'в':'v', 'г':'g', 'д':'d', 'е':'e', 'ё':'yo', 'ж':'zh',
    'з':'z', 'и':'i', 'й':'y', 'к':'k', 'л':'l', 'м':'m', 'н':'n', 'о':'o',
    'п':'p', 'р':'r', 'с':'s', 'т':'t', 'у':'u', 'ф':'f', 'х':'kh', 'ц':'ts',
    'ч':'ch', 'ш':'sh', 'щ':'shch', 'ъ':'', 'ы':'y', 'ь':'', 'э':'e', 'ю':'yu', 'я':'ya'
}

def safe_app_id(name):
    lower = name.lower()
    res = []
    for ch in lower:
        if ch in TRANSLIT:
            res.append(TRANSLIT[ch])
        elif ch.isalnum() or ch == '_':
            res.append(ch)
        else:
            res.append('_')
    slug = re.sub(r'_+', '_', ''.join(res)).strip('_')
    h = hashlib.md5(name.encode('utf-8')).hexdigest()[:6]
    return f"{slug}_{h}"

_CATALOG_CACHE = None
_CATALOG_CACHE_MTIME = 0

def load_catalog_data():
    global _CATALOG_CACHE, _CATALOG_CACHE_MTIME
    if os.path.exists(CATALOG_JSON_PATH):
        try:
            mtime = os.path.getmtime(CATALOG_JSON_PATH)
            if _CATALOG_CACHE is not None and mtime == _CATALOG_CACHE_MTIME:
                return _CATALOG_CACHE
            with open(CATALOG_JSON_PATH, "r", encoding="utf-8") as f:
                apps = json.load(f)
                for a in apps:
                    if "aliases" not in a:
                        a["aliases"] = get_app_search_aliases(a.get("name", ""))
                _CATALOG_CACHE = apps
                _CATALOG_CACHE_MTIME = mtime
                return apps
        except Exception:
            pass
    if _CATALOG_CACHE is not None:
        return _CATALOG_CACHE
    return []

def scan_and_rebuild_catalog():
    pythoncom.CoInitialize()
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        apps = []
        
        if not os.path.exists(SMART_CATALOG_ROOT):
            os.makedirs(SMART_CATALOG_ROOT, exist_ok=True)
            
        for cat_dir in sorted(os.listdir(SMART_CATALOG_ROOT)):
            cat_path = os.path.join(SMART_CATALOG_ROOT, cat_dir)
            if not os.path.isdir(cat_path) or cat_dir.startswith('.'):
                continue
                
            for f in sorted(os.listdir(cat_path)):
                if not f.endswith(".lnk"):
                    continue
                    
                name = f[:-4]
                lnk_p = os.path.join(cat_path, f)

                # Auto-heal legacy misclassifications (e.g. administrative tools in browsers)
                name_l = name.strip().lower()
                effective_cat = cat_dir
                if cat_dir == "04. Интернет и Браузеры" and name_l in KNOWN_APPS:
                    correct_cat = KNOWN_APPS[name_l][0]
                    if correct_cat != cat_dir:
                        new_cat_dir = os.path.join(SMART_CATALOG_ROOT, correct_cat)
                        os.makedirs(new_cat_dir, exist_ok=True)
                        new_lnk_p = os.path.join(new_cat_dir, f)
                        try:
                            shutil.move(lnk_p, new_lnk_p)
                            lnk_p = new_lnk_p
                            effective_cat = correct_cat
                        except Exception:
                            pass
                
                try:
                    lnk = shell.CreateShortCut(lnk_p)
                    target = lnk.TargetPath
                    args = lnk.Arguments
                    working_dir = lnk.WorkingDirectory
                except Exception:
                    target = ""
                    args = ""
                    working_dir = ""
                    
                app_id = safe_app_id(name)
                icon_file = f"{app_id}.png"
                icon_full_path = os.path.join(ICONS_DIR, icon_file)
                
                if not os.path.exists(icon_full_path) or os.path.getsize(icon_full_path) == 0:
                    extract_icon_best(target, lnk_p, icon_full_path, 128)
                    
                desc = get_app_description(name, effective_cat, target)
                
                try:
                    added_at = os.path.getctime(lnk_p)
                except Exception:
                    added_at = time.time()
                
                apps.append({
                    "id": app_id,
                    "name": name,
                    "category": effective_cat,
                    "target": target,
                    "args": args,
                    "working_dir": working_dir,
                    "lnk_path": lnk_p,
                    "icon": f"/icons/{icon_file}" if os.path.exists(icon_full_path) else "/icons/default.png",
                    "description": desc,
                    "aliases": get_app_search_aliases(name),
                    "added_at": added_at
                })
                
        save_catalog_data(apps)
        return apps
    finally:
        pythoncom.CoUninitialize()

def add_new_software(name, target_path, source_lnk=None, save_now=True):
    if is_junk_or_uninstaller(name, target_path):
        return None
        
    pythoncom.CoInitialize()
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        
        cat = classify_app(name, target_path)
        target_cat_dir = os.path.join(SMART_CATALOG_ROOT, cat)
        os.makedirs(target_cat_dir, exist_ok=True)
        
        clean_name = re.sub(r'[\/:*?"<>|]', '', name).strip()
        dest_lnk = os.path.join(target_cat_dir, f"{clean_name}.lnk")
        
        if source_lnk and os.path.exists(source_lnk):
            try:
                src = shell.CreateShortCut(source_lnk)
                dest = shell.CreateShortCut(dest_lnk)
                dest.TargetPath = src.TargetPath
                dest.Arguments = src.Arguments
                dest.WorkingDirectory = src.WorkingDirectory
                dest.IconLocation = src.IconLocation if src.IconLocation else src.TargetPath
                dest.Save()
            except Exception:
                dest = shell.CreateShortCut(dest_lnk)
                dest.TargetPath = target_path
                dest.WorkingDirectory = os.path.dirname(target_path)
                dest.Save()
        else:
            dest = shell.CreateShortCut(dest_lnk)
            dest.TargetPath = target_path
            dest.WorkingDirectory = os.path.dirname(target_path)
            dest.Save()
            
        app_id = safe_app_id(clean_name)
        icon_file = f"{app_id}.png"
        icon_full_path = os.path.join(ICONS_DIR, icon_file)
        extract_icon_best(target_path, dest_lnk, icon_full_path, 128)
        
        desc = get_app_description(clean_name, cat, target_path)
        
        app_entry = {
            "id": app_id,
            "name": clean_name,
            "category": cat,
            "target": target_path,
            "args": "",
            "working_dir": os.path.dirname(target_path),
            "lnk_path": dest_lnk,
            "icon": f"/icons/{icon_file}" if os.path.exists(icon_full_path) else "/icons/default.png",
            "description": desc,
            "aliases": get_app_search_aliases(clean_name),
            "added_at": time.time()
        }
        
        if save_now:
            existing = load_catalog_data()
            existing = [x for x in existing if x["id"] != app_id]
            existing.append(app_entry)
            save_catalog_data(existing)
        
        return app_entry
    finally:
        pythoncom.CoUninitialize()

def launch_app_as_admin(app_id):
    apps = load_catalog_data()
    app = next((a for a in apps if a.get("id") == app_id), None)
    if not app:
        return False, "Программа не найдена в каталоге"

    target = app.get("target") or app.get("lnk_path")
    args = app.get("args") or None
    working_dir = app.get("working_dir") or (os.path.dirname(target) if target else None)

    if not target or not os.path.exists(target):
        target = app.get("lnk_path")

    try:
        attach_to_default_desktop()
        sei = SHELLEXECUTEINFOW()
        sei.cbSize = ctypes.sizeof(SHELLEXECUTEINFOW)
        sei.fMask = 0x00000040
        sei.lpVerb = "runas"
        sei.lpFile = target
        sei.lpParameters = args
        sei.lpDirectory = working_dir
        sei.nShow = 1

        res = ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(sei))
        if res:
            if sei.hProcess:
                ctypes.windll.kernel32.CloseHandle(sei.hProcess)
            record_app_launch(app_id)
            return True, f"Запущено с правами администратора: {app.get('name')}"
        else:
            err = ctypes.GetLastError()
            if err == 1223:
                return False, "Запрос UAC был отменен пользователем"
            return False, f"Код ошибки Windows: {err}"
    except Exception as e:
        return False, str(e)

def open_target_folder(app_id):
    apps = load_catalog_data()
    app = next((a for a in apps if a.get("id") == app_id), None)
    if not app:
        return False, "Программа не найдена"
    
    target = app.get("target")
    if target and os.path.exists(target):
        subprocess.Popen(["explorer.exe", f"/select,{target}"])
        return True, target
    
    lnk_p = app.get("lnk_path")
    if lnk_p and os.path.exists(lnk_p):
        subprocess.Popen(["explorer.exe", f"/select,{lnk_p}"])
        return True, lnk_p
    
    return False, "Файл не найден"

def move_app_category(app_id, new_category):
    apps = load_catalog_data()
    app = next((a for a in apps if a.get("id") == app_id), None)
    if not app:
        return False, "Программа не найдена"
    
    old_lnk = app.get("lnk_path")
    if not old_lnk or not os.path.exists(old_lnk):
        return False, "Ярлык программы не найден"
    
    target_dir = os.path.join(SMART_CATALOG_ROOT, new_category)
    os.makedirs(target_dir, exist_ok=True)
    
    file_name = os.path.basename(old_lnk)
    new_lnk = os.path.join(target_dir, file_name)
    
    try:
        shutil.move(old_lnk, new_lnk)
    except Exception as e:
        return False, f"Ошибка перемещения: {e}"
        
    app["category"] = new_category
    app["lnk_path"] = new_lnk
    save_catalog_data(apps)
    return True, f"Программа перемещена в категорию {new_category}"

def hide_app(app_id):
    data = load_user_data()
    hidden = set(data.setdefault("hidden_apps", []))
    hidden.add(app_id)
    data["hidden_apps"] = list(hidden)
    save_user_data(data)
    return True, list(hidden)

def unhide_app(app_id):
    data = load_user_data()
    hidden = set(data.get("hidden_apps", []))
    hidden.discard(app_id)
    data["hidden_apps"] = list(hidden)
    save_user_data(data)
    return True, list(hidden)

def get_hidden_apps():
    data = load_user_data()
    hidden_ids = set(data.get("hidden_apps", []))
    apps = load_catalog_data()
    return [a for a in apps if a.get("id") in hidden_ids]

def force_foreground(hwnd):
    if not hwnd:
        return False
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    try:
        user32.SystemParametersInfoW(0x2001, 0, 0, 0) # SPI_SETFOREGROUNDLOCKTIMEOUT = 0
    except Exception:
        pass
        
    curr_tid = kernel32.GetCurrentThreadId()
    fg_hwnd = user32.GetForegroundWindow()
    fg_tid = user32.GetWindowThreadProcessId(fg_hwnd, None) if fg_hwnd else 0
    target_tid = user32.GetWindowThreadProcessId(hwnd, None)
    
    if fg_tid and fg_tid != curr_tid:
        user32.AttachThreadInput(curr_tid, fg_tid, True)
    if target_tid and target_tid != curr_tid:
        user32.AttachThreadInput(curr_tid, target_tid, True)
        
    # Grant foreground permission via Alt key simulation
    user32.keybd_event(0x12, 0, 0, 0) # VK_MENU down
    
    # Restore window ONLY if it is minimized to the taskbar (IsIconic).
    # NEVER call ShowWindow(SW_SHOW) on a hidden window as that corrupts Electron/Chromium state!
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9) # SW_RESTORE
        
    user32.BringWindowToTop(hwnd)
    res = user32.SetForegroundWindow(hwnd)
    user32.SwitchToThisWindow(hwnd, True)
    
    user32.keybd_event(0x12, 0, 2, 0) # VK_MENU up
    
    if fg_tid and fg_tid != curr_tid:
        user32.AttachThreadInput(curr_tid, fg_tid, False)
    if target_tid and target_tid != curr_tid:
        user32.AttachThreadInput(curr_tid, target_tid, False)
        
    return bool(res)

def wake_up_tray(target, name):
    try:
        user32 = ctypes.windll.user32
        hDesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if hDesk:
            user32.SetThreadDesktop(hDesk)
            
        target_base = os.path.basename(target).lower() if target else ""
        name_lower = name.lower()
        
        kw_list = []
        if target_base:
            kw_list.append(target_base)
            kw_list.append(os.path.splitext(target_base)[0])
        for w in re.findall(r'[a-zA-Zа-яА-Я0-9]{3,}', name_lower):
            kw_list.append(w)
            
        matching_pids = set()
        for p in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                pn = (p.info['name'] or '').lower()
                pe = (p.info['exe'] or '').lower()
                p_base = os.path.basename(pe)
                if any(k in pn or k in p_base for k in kw_list):
                    matching_pids.add(p.info['pid'])
            except Exception:
                pass
                
        if not matching_pids or not hDesk:
            return False
            
        notify_hwnds = []
        def enum_cb(hwnd, lp):
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value in matching_pids:
                cls_buf = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(hwnd, cls_buf, 256)
                cls_name = cls_buf.value
                if 'Electron_NotifyIconHostWindow' in cls_name or 'QTrayIconMessageWindow' in cls_name or 'TrayIcon' in cls_name:
                    notify_hwnds.append((hwnd, cls_name))
            return True
            
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumDesktopWindows(hDesk, WNDENUMPROC(enum_cb), 0)
        
        for nhwnd, ncls in notify_hwnds:
            if 'Electron' in ncls:
                # Electron notify_icon_host.cc:
                # message = WM_APP + 1 (0x8001)
                # wparam = icon_id (starts at kBaseIconId = 2)
                # lparam = WM_LBUTTONDOWN (0x0201), WM_LBUTTONDBLCLK (0x0203)
                for icon_id in (2, 3, 4, 5, 6):
                    user32.PostMessageW(nhwnd, 0x8001, icon_id, 0x0201)
                    user32.PostMessageW(nhwnd, 0x8001, icon_id, 0x0203)
            elif 'Qt' in ncls:
                user32.PostMessageW(nhwnd, 0x0201, 1, 0x0201)
                user32.PostMessageW(nhwnd, 0x0202, 1, 0x0202)
                
        return len(notify_hwnds) > 0
    except Exception:
        return False

def focus_application_window(target, name):
    try:
        user32 = ctypes.windll.user32
        hDesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if hDesk:
            user32.SetThreadDesktop(hDesk)
            
        target_base = os.path.basename(target).lower() if target else ""
        name_lower = name.lower()
        
        kw_list = []
        if target_base:
            kw_list.append(target_base)
            kw_list.append(os.path.splitext(target_base)[0])
        for w in re.findall(r'[a-zA-Zа-яА-Я0-9]{3,}', name_lower):
            kw_list.append(w)
            
        matching_pids = set()
        for p in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                pn = (p.info['name'] or '').lower()
                pe = (p.info['exe'] or '').lower()
                p_base = os.path.basename(pe)
                if any(k in pn or k in p_base for k in kw_list):
                    matching_pids.add(p.info['pid'])
            except Exception:
                pass
                
        if not matching_pids or not hDesk:
            return False, None
            
        candidate_hwnds = []
        def enum_cb(hwnd, lp):
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value in matching_pids:
                cls_buf = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(hwnd, cls_buf, 256)
                cls_name = cls_buf.value
                if cls_name not in ['IME', 'MSCTFIME UI', 'Base_PowerMessageWindow', 'Electron_NotifyIconHostWindow', 'QTrayIconMessageWindow']:
                    txt_buf = ctypes.create_unicode_buffer(512)
                    user32.GetWindowTextW(hwnd, txt_buf, 512)
                    vis = user32.IsWindowVisible(hwnd)
                    candidate_hwnds.append((hwnd, cls_name, txt_buf.value, vis))
            return True
            
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumDesktopWindows(hDesk, WNDENUMPROC(enum_cb), 0)
        
        if not candidate_hwnds:
            return False, None
            
        best = sorted(candidate_hwnds, key=lambda x: (
            1 if x[3] else 0, # prefer visible windows
            1 if ('Chrome_WidgetWin_1' in x[1] or 'QWindow' in x[1]) else 0,
            1 if x[2] else 0  # has title
        ), reverse=True)[0]
        
        hwnd = best[0]
        force_foreground(hwnd)
        return True, hwnd
    except Exception:
        return False, None

class SHELLEXECUTEINFOW(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('fMask', ctypes.c_ulong),
        ('hwnd', wintypes.HWND),
        ('lpVerb', wintypes.LPCWSTR),
        ('lpFile', wintypes.LPCWSTR),
        ('lpParameters', wintypes.LPCWSTR),
        ('lpDirectory', wintypes.LPCWSTR),
        ('nShow', ctypes.c_int),
        ('hInstApp', wintypes.HINSTANCE),
        ('lpIDList', wintypes.LPVOID),
        ('lpClass', wintypes.LPCWSTR),
        ('hkeyClass', wintypes.HKEY),
        ('dwHotKey', wintypes.DWORD),
        ('hIconOrMonitor', wintypes.HANDLE),
        ('hProcess', wintypes.HANDLE)
    ]

def shell_execute_open(file_path, args=None, working_dir=None):
    try:
        user32 = ctypes.windll.user32
        hDesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if hDesk:
            user32.SetThreadDesktop(hDesk)
            
        sei = SHELLEXECUTEINFOW()
        sei.cbSize = ctypes.sizeof(SHELLEXECUTEINFOW)
        sei.fMask = 0x00000040 # SEE_MASK_NOCLOSEPROCESS
        sei.lpVerb = 'open'
        sei.lpFile = file_path
        sei.lpParameters = args
        sei.lpDirectory = working_dir
        sei.nShow = 1 # SW_SHOWNORMAL
        
        res = ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(sei))
        if res:
            if sei.hProcess:
                ctypes.windll.kernel32.CloseHandle(sei.hProcess)
            return True
    except Exception:
        pass
        
    try:
        os.startfile(file_path)
        return True
    except Exception:
        return False

def launch_application(app_id):
    record_app_launch(app_id)
    apps = load_catalog_data()
    match = next((a for a in apps if a["id"] == app_id), None)
    if not match:
        return False, "Программа не найдена в каталоге"
        
    name = match.get("name", "")
    lnk_p = match.get("lnk_path", "")
    target = match.get("target", "")
    args = match.get("args", "")
    working_dir = match.get("working_dir") or (os.path.dirname(target) if target else "")
    
    # 1. First: If in tray, send native tray wakeup events (Electron, Qt)
    wake_up_tray(target, name)
    
    # 2. Discord special handling for versioned update directories
    if "discord" in (target or '').lower() or "discord" in name.lower():
        disc_base = os.path.expandvars(r"%LOCALAPPDATA%\Discord")
        if os.path.exists(disc_base):
            for sub in sorted(os.listdir(disc_base), reverse=True):
                if sub.startswith("app-"):
                    cand = os.path.join(disc_base, sub, "Discord.exe")
                    if os.path.exists(cand):
                        target = cand
                        working_dir = os.path.dirname(cand)
                        break

    # 3. Launch via Shell shortcut or executable on Default desktop
    # For running apps, this triggers second-instance IPC wake-up inside the app itself!
    launched = False
    if lnk_p and os.path.exists(lnk_p):
        launched = shell_execute_open(lnk_p, args, working_dir)
    elif target and os.path.exists(target):
        launched = shell_execute_open(target, args, working_dir)
        
    # 4. Small pause for the app to unhide, process events and paint
    time.sleep(0.18)
    
    # 5. Bring window to absolute top and focus (safely without raw ShowWindow corruption)
    focus_application_window(target, name)
    
    return True, f"Запущено и активировано: {name}"

# Process Detection & Task Management
_running_apps_cache = {"time": 0, "data": {}}
_PROCESS_MAP_CACHE = None
_PROCESS_MAP_TIME = 0

def build_process_to_app_map():
    global _PROCESS_MAP_CACHE, _PROCESS_MAP_TIME
    now = time.time()
    if _PROCESS_MAP_CACHE is not None and (now - _PROCESS_MAP_TIME < 30.0):
        return _PROCESS_MAP_CACHE

    apps = load_catalog_data()
    mapping = {}
    for a in apps:
        aid = a["id"]
        tgt = (a.get("target") or "").lower()
        if tgt and tgt.endswith(".exe"):
            mapping[os.path.basename(tgt)] = aid
        clean_name = a["name"].lower().replace(" ", "")
        mapping[f"{clean_name}.exe"] = aid
        
    # Known special binary names
    mapping["code.exe"] = "visual_studio_code_d51a76"
    mapping["chrome.exe"] = "google_chrome_76868a"
    mapping["telegram.exe"] = "telegram_desktop_41622c"
    mapping["discord.exe"] = "discord_8f5cc6"
    mapping["steam.exe"] = "steam_4db456"
    mapping["dbeaver.exe"] = "dbeaver_fb2233"
    mapping["postman.exe"] = "postman_6f061e"
    mapping["docker desktop.exe"] = "docker_desktop_cb1cb8"
    mapping["playnite.desktopapp.exe"] = "playnite_9668b2"
    mapping["samsungmagician.exe"] = "samsung_magician_195fab"
    mapping["aida64.exe"] = "aida64_extreme_40497c"
    mapping["l2.bin"] = "lineage_2_multeria_6d37e0"
    mapping["l2.exe"] = "lineage_2_multeria_6d37e0"
    mapping["powershell.exe"] = "powershell_f1b0a8"
    mapping["cmd.exe"] = "komandnaya_stroka_95bb90"
    mapping["taskmgr.exe"] = "dispetcher_zadach_65a7a7"
    mapping["regedit.exe"] = "redaktor_reestra_1ad94d"
    mapping["devenv.exe"] = "visual_studio_code_d51a76"

    _PROCESS_MAP_CACHE = mapping
    _PROCESS_MAP_TIME = now
    return mapping

def get_running_apps():
    global _running_apps_cache
    now = time.time()
    if now - _running_apps_cache["time"] < 2.0 and _running_apps_cache["data"]:
        return _running_apps_cache["data"]

    mapping = build_process_to_app_map()
    running_map = {}
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            pname = (proc.info['name'] or '').lower()
            if pname in mapping:
                aid = mapping[pname]
                running_map.setdefault(aid, []).append(proc.info['pid'])
        except Exception:
            pass

    _running_apps_cache = {"time": now, "data": running_map}
    return running_map

def kill_application(app_id):
    running = get_running_apps()
    pids = running.get(app_id, [])
    if not pids:
        _running_apps_cache["time"] = 0
        running = get_running_apps()
        pids = running.get(app_id, [])

    if not pids:
        return False, "Программа не запущена"

    killed = 0
    for pid in pids:
        try:
            p = psutil.Process(pid)
            for child in p.children(recursive=True):
                try:
                    child.kill()
                except Exception:
                    pass
            p.kill()
            killed += 1
        except Exception:
            pass

    _running_apps_cache["time"] = 0
    return True, f"Завершено процессов: {killed}"

# Screen Time & Usage Tracking
_PLAYTIME_CACHE = None
_PLAYTIME_CACHE_MTIME = 0
_PLAYTIME_DIRTY = False
_PLAYTIME_LAST_FLUSH = 0
_PLAYTIME_LOCK = threading.RLock()

def load_playtime_data():
    global _PLAYTIME_CACHE, _PLAYTIME_CACHE_MTIME
    with _PLAYTIME_LOCK:
        if _PLAYTIME_CACHE is not None:
            return _PLAYTIME_CACHE
        if os.path.exists(PLAYTIME_DATA_PATH):
            try:
                mtime = os.path.getmtime(PLAYTIME_DATA_PATH)
                with open(PLAYTIME_DATA_PATH, "r", encoding="utf-8") as f:
                    _PLAYTIME_CACHE = json.load(f)
                    _PLAYTIME_CACHE_MTIME = mtime
                    return _PLAYTIME_CACHE
            except Exception:
                pass

        seed = {}
        _PLAYTIME_CACHE = seed
        _atomic_save_json(PLAYTIME_DATA_PATH, seed, bump_version=False)
        return seed

def flush_playtime_data():
    global _PLAYTIME_DIRTY, _PLAYTIME_LAST_FLUSH
    with _PLAYTIME_LOCK:
        if _PLAYTIME_DIRTY and _PLAYTIME_CACHE is not None:
            _atomic_save_json(PLAYTIME_DATA_PATH, _PLAYTIME_CACHE, bump_version=False)
            _PLAYTIME_DIRTY = False
            _PLAYTIME_LAST_FLUSH = time.time()

def save_playtime_data(data):
    global _PLAYTIME_CACHE, _PLAYTIME_DIRTY, _PLAYTIME_LAST_FLUSH
    with _PLAYTIME_LOCK:
        _PLAYTIME_CACHE = data
        _PLAYTIME_DIRTY = False
        _PLAYTIME_LAST_FLUSH = time.time()
        return _atomic_save_json(PLAYTIME_DATA_PATH, data, bump_version=False)

def record_playtime_tick(app_id, seconds):
    global _PLAYTIME_DIRTY, _PLAYTIME_LAST_FLUSH
    data = load_playtime_data()
    today_str = time.strftime("%Y-%m-%d")
    should_flush = False
    with _PLAYTIME_LOCK:
        entry = data.setdefault(app_id, {"total": 0, "today": 0, "last_date": today_str})
        if entry.get("last_date") != today_str:
            entry["today"] = 0
            entry["last_date"] = today_str
        entry["total"] = entry.get("total", 0) + seconds
        entry["today"] = entry.get("today", 0) + seconds
        _PLAYTIME_DIRTY = True
        if time.time() - _PLAYTIME_LAST_FLUSH > 30.0:
            should_flush = True

    if should_flush:
        flush_playtime_data()

def get_playtime_stats():
    playtime_data = load_playtime_data()
    apps = load_catalog_data()
    app_map = {a["id"]: a for a in apps}
    
    total_screen_time = 0
    today_screen_time = 0
    cat_time = {}
    top_apps = []

    for aid, st in playtime_data.items():
        tot = st.get("total", 0)
        tod = st.get("today", 0)
        total_screen_time += tot
        today_screen_time += tod
        app = app_map.get(aid)
        if app:
            cat = app.get("category", "Другое")
            cat_time[cat] = cat_time.get(cat, 0) + tot
            top_apps.append({
                "id": aid,
                "name": app.get("name"),
                "category": cat,
                "icon": app.get("icon"),
                "total": tot,
                "today": tod
            })

    top_apps.sort(key=lambda x: x["total"], reverse=True)
    return {
        "total_screen_time": total_screen_time,
        "today_screen_time": today_screen_time,
        "categories": cat_time,
        "top_apps": top_apps[:10],
        "apps_playtime": playtime_data
    }

# Workspaces (Рабочие пространства)
def load_workspaces():
    if os.path.exists(WORKSPACES_DATA_PATH):
        try:
            with open(WORKSPACES_DATA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    seed = [
        {
            "id": "ws_dev",
            "name": "Разработка",
            "icon": "💻",
            "description": "VS Code, Docker Desktop, Git Bash, DBeaver",
            "apps": ["visual_studio_code_d51a76", "docker_desktop_cb1cb8", "git_bash_819e60", "dbeaver_fb2233"]
        },
        {
            "id": "ws_gaming",
            "name": "Игры & Связь",
            "icon": "🎮",
            "description": "Steam, Discord, Telegram",
            "apps": ["steam_4db456", "discord_8f5cc6", "telegram_desktop_41622c"]
        },
        {
            "id": "ws_office",
            "name": "Офис & Продуктивность",
            "icon": "💼",
            "description": "Google Chrome, Telegram, Офисные утилиты",
            "apps": ["google_chrome_76868a", "telegram_desktop_41622c"]
        }
    ]
    _atomic_save_json(WORKSPACES_DATA_PATH, seed)
    return seed

def save_workspace(ws_data):
    workspaces = load_workspaces()
    ws_id = ws_data.get("id") or f"ws_{int(time.time())}"
    ws_data["id"] = ws_id
    existing_idx = next((i for i, w in enumerate(workspaces) if w["id"] == ws_id), None)
    if existing_idx is not None:
        workspaces[existing_idx] = ws_data
    else:
        workspaces.append(ws_data)
    _atomic_save_json(WORKSPACES_DATA_PATH, workspaces)
    return True, ws_data

def delete_workspace(ws_id):
    workspaces = load_workspaces()
    workspaces = [w for w in workspaces if w["id"] != ws_id]
    _atomic_save_json(WORKSPACES_DATA_PATH, workspaces)
    return True

def launch_workspace(ws_id):
    workspaces = load_workspaces()
    ws = next((w for w in workspaces if w["id"] == ws_id), None)
    if not ws:
        return False, "Рабочее пространство не найдено"

    launched_count = 0
    for app_id in ws.get("apps", []):
        ok, _ = launch_application(app_id)
        if ok:
            launched_count += 1
        time.sleep(0.3)
    return True, f"Запущено {launched_count} программ из пространства «{ws['name']}»"

# Clipboard History
def load_clipboard_history():
    if os.path.exists(CLIPBOARD_DATA_PATH):
        try:
            with open(CLIPBOARD_DATA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def add_clipboard_entry(text):
    if not text or not text.strip():
        return
    history = load_clipboard_history()
    clean = text.strip()
    if history and history[0].get("text") == clean:
        return
    history = [h for h in history if h.get("text") != clean]
    entry = {
        "id": hashlib.md5(clean.encode('utf-8')).hexdigest()[:8],
        "text": clean[:1500],
        "length": len(clean),
        "time": time.time()
    }
    history.insert(0, entry)
    history = history[:50]
    _atomic_save_json(CLIPBOARD_DATA_PATH, history)

def clear_clipboard_history():
    _atomic_save_json(CLIPBOARD_DATA_PATH, [])
    return True

def copy_text_to_clipboard(text):
    try:
        import win32clipboard
        import win32con
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        win32clipboard.CloseClipboard()
        return True, "Скопировано в буфер обмена"
    except Exception as e:
        return False, str(e)

# Snippets & Text Templates
def load_snippets():
    if os.path.exists(SNIPPETS_DATA_PATH):
        try:
            with open(SNIPPETS_DATA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    seed = [
        {
            "id": "snip_git",
            "title": "Git Commit & Push",
            "category": "Команды",
            "text": "git add . && git commit -m \"update\" && git push",
            "content": "git add . && git commit -m \"update\" && git push",
            "created_at": time.time()
        },
        {
            "id": "snip_docker",
            "title": "Docker Compose Restart",
            "category": "Команды",
            "text": "docker compose down && docker compose up -d",
            "content": "docker compose down && docker compose up -d",
            "created_at": time.time()
        },
        {
            "id": "snip_localhost",
            "title": "Localhost Port 8000",
            "category": "Ссылки",
            "text": "http://127.0.0.1:8000",
            "content": "http://127.0.0.1:8000",
            "created_at": time.time()
        },
        {
            "id": "snip_json",
            "title": "Тестовый JSON ответ",
            "category": "Шаблоны",
            "text": "{\n  \"status\": \"success\",\n  \"data\": {}\n}",
            "content": "{\n  \"status\": \"success\",\n  \"data\": {}\n}",
            "created_at": time.time()
        }
    ]
    _atomic_save_json(SNIPPETS_DATA_PATH, seed)
    return seed

def save_snippet(snip_data):
    snippets = load_snippets()
    snip_id = snip_data.get("id") or f"snip_{int(time.time() * 1000)}"
    snip_data["id"] = snip_id
    text_val = snip_data.get("content") or snip_data.get("text") or ""
    snip_data["text"] = text_val
    snip_data["content"] = text_val
    if "created_at" not in snip_data:
        snip_data["created_at"] = time.time()
    existing_idx = next((i for i, s in enumerate(snippets) if s["id"] == snip_id), None)
    if existing_idx is not None:
        snippets[existing_idx] = snip_data
    else:
        snippets.insert(0, snip_data)
    _atomic_save_json(SNIPPETS_DATA_PATH, snippets)
    return True, snip_data

def delete_snippet(snip_id):
    snippets = load_snippets()
    snippets = [s for s in snippets if s["id"] != snip_id]
    _atomic_save_json(SNIPPETS_DATA_PATH, snippets)
    return True

# System Resource Metrics
_SYS_METRICS_LOCK = threading.Lock()
_SYS_METRICS_DATA = None
_SYS_LAST_REQUESTED = 0
_SYS_METRICS_STARTED = False

def _sys_metrics_worker():
    global _SYS_METRICS_DATA
    try:
        psutil.cpu_percent(interval=None)
    except Exception:
        pass

    cores = psutil.cpu_count() or 1
    prev_procs = {}
    prev_time = time.time()

    for p in psutil.process_iter(['pid', 'name', 'cpu_times', 'memory_info']):
        try:
            pid = p.info['pid']
            if pid != 0 and p.info['name']:
                prev_procs[pid] = p.info
        except Exception:
            pass

    while True:
        try:
            is_active = (time.time() - _SYS_LAST_REQUESTED) < 20.0
            sleep_interval = 1.0 if is_active else 2.5
            time.sleep(sleep_interval)

            now = time.time()
            dt = max(0.2, now - prev_time)
            sys_cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("C:\\")

            curr_procs = {}
            res_procs = []

            for p in psutil.process_iter(['pid', 'name', 'cpu_times', 'memory_info']):
                try:
                    info = p.info
                    pid = info['pid']
                    name = info['name']
                    if pid == 0 or not name or name == 'System Idle Process':
                        continue
                    curr_procs[pid] = info

                    cpu_pct = 0.0
                    if pid in prev_procs and info.get('cpu_times') and prev_procs[pid].get('cpu_times'):
                        curr_t = info['cpu_times']
                        prev_t = prev_procs[pid]['cpu_times']
                        used = (curr_t.user - prev_t.user) + (curr_t.system - prev_t.system)
                        cpu_pct = round((used / dt / cores) * 100.0, 1)
                        cpu_pct = min(100.0, max(0.0, cpu_pct))

                    rss_mb = round(info['memory_info'].rss / (1024 * 1024), 1) if info.get('memory_info') else 0

                    res_procs.append({
                        "pid": pid,
                        "name": name,
                        "cpu_percent": cpu_pct,
                        "mem_mb": rss_mb
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                except Exception:
                    continue

            prev_procs = curr_procs
            prev_time = now

            top_cpu = sorted(res_procs, key=lambda x: x['cpu_percent'], reverse=True)[:6]
            top_ram = sorted(res_procs, key=lambda x: x['mem_mb'], reverse=True)[:6]

            metrics = {
                "cpu_percent": round(sys_cpu, 1),
                "cpu_count": cores,
                "ram_percent": round(mem.percent, 1),
                "ram_used_gb": round((mem.total - mem.available) / (1024**3), 1),
                "ram_total_gb": round(mem.total / (1024**3), 1),
                "disk_percent": round(disk.percent, 1),
                "disk_used_gb": round(disk.used / (1024**3), 1),
                "disk_total_gb": round(disk.total / (1024**3), 1),
                "top_ram": top_ram,
                "top_cpu": top_cpu,
                "timestamp": now
            }

            with _SYS_METRICS_LOCK:
                _SYS_METRICS_DATA = metrics

        except Exception:
            time.sleep(1.0)

def ensure_sys_metrics_started():
    global _SYS_METRICS_STARTED
    if not _SYS_METRICS_STARTED:
        _SYS_METRICS_STARTED = True
        t = threading.Thread(target=_sys_metrics_worker, daemon=True, name="SysMetricsWorker")
        t.start()

ensure_sys_metrics_started()

def get_system_stats():
    global _SYS_LAST_REQUESTED
    _SYS_LAST_REQUESTED = time.time()
    ensure_sys_metrics_started()
    with _SYS_METRICS_LOCK:
        if _SYS_METRICS_DATA:
            return _SYS_METRICS_DATA
    try:
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("C:\\")
        return {
            "cpu_percent": 0.0,
            "cpu_count": psutil.cpu_count() or 1,
            "ram_percent": round(mem.percent, 1),
            "ram_used_gb": round((mem.total - mem.available) / (1024**3), 1),
            "ram_total_gb": round(mem.total / (1024**3), 1),
            "disk_percent": round(disk.percent, 1),
            "disk_used_gb": round(disk.used / (1024**3), 1),
            "disk_total_gb": round(disk.total / (1024**3), 1),
            "top_ram": [],
            "top_cpu": []
        }
    except Exception:
        return {
            "cpu_percent": 0.0,
            "cpu_count": 1,
            "ram_percent": 0.0,
            "ram_used_gb": 0.0,
            "ram_total_gb": 0.0,
            "disk_percent": 0.0,
            "disk_used_gb": 0.0,
            "disk_total_gb": 0.0,
            "top_ram": [],
            "top_cpu": []
        }

PROTECTED_PIDS = {0, 4}
PROTECTED_PROCESS_NAMES = {
    "system", "system idle process", "registry", "smss.exe", "csrss.exe",
    "wininit.exe", "services.exe", "lsass.exe", "svchost.exe",
    "fontdrvhost.exe", "dwm.exe", "winlogon.exe", "sihost.exe"
}

def kill_process_by_pid(pid):
    try:
        pid = int(pid)
    except (ValueError, TypeError):
        return False, "Некорректный PID"

    if pid <= 4 or pid in PROTECTED_PIDS:
        return False, f"Отказано в доступе: PID {pid} является системным процессом Windows"

    current_pid = os.getpid()
    parent_pid = os.getppid() if hasattr(os, 'getppid') else 0
    if pid == current_pid or pid == parent_pid:
        return False, "Отказано в доступе: завершение процесса службы SmartCatalog запрещено"

    try:
        p = psutil.Process(pid)
        name = (p.name() or "").lower()
        if name in PROTECTED_PROCESS_NAMES:
            return False, f"Отказано в доступе: завершение критического процесса Windows ({name}) запрещено"

        for child in p.children(recursive=True):
            try:
                child.kill()
            except Exception:
                pass
        p.kill()
        return True, f"Процесс {name} (PID: {pid}) успешно завершен"
    except psutil.NoSuchProcess:
        return True, f"Процесс с PID {pid} уже завершен"
    except psutil.AccessDenied:
        return False, f"Недостаточно прав для завершения процесса PID {pid}"
    except Exception as e:
        return False, str(e)

