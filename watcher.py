import os
import sys
import time
import threading
import subprocess
import pythoncom
import win32com.client
import win32file
import win32con
from classifier import is_junk_or_uninstaller, classify_app, get_app_description
from catalog_manager import add_new_software, load_catalog_data, SMART_CATALOG_ROOT

# Monitored locations in Windows
WATCH_DIRS = [
    r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
    os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
    os.path.expandvars(r"%USERPROFILE%\Desktop"),
    r"C:\Users\Public\Desktop"
]

known_targets = set()
known_files = set()
lock = threading.Lock()

def init_known_targets():
    global known_targets, known_files
    with lock:
        data = load_catalog_data()
        for item in data:
            t = item.get("target", "").lower()
            if t:
                known_targets.add(t)
                
        if len(data) > 0:
            for wdir in WATCH_DIRS:
                if os.path.exists(wdir):
                    for root, _, files in os.walk(wdir):
                        if "backup" in root.lower() or "smartcatalog" in root.lower():
                            continue
                        for f in files:
                            if f.lower().endswith(('.lnk', '.exe')):
                                known_files.add(os.path.join(root, f).lower())

def show_toast(title, message):
    clean_title = title.replace("'", "’").replace('"', "”")
    clean_msg = message.replace("'", "’").replace('"', "”")[:200]
    ps_cmd = f"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
$textNodes = $template.GetElementsByTagName('text')
$textNodes.Item(0).AppendChild($template.CreateTextNode('{clean_title}')) | Out-Null
$textNodes.Item(1).AppendChild($template.CreateTextNode('{clean_msg}')) | Out-Null
$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('SmartCatalog Hub')
$notification = [Windows.UI.Notifications.ToastNotification]::new($template)
$notifier.Show($notification)
"""
    try:
        subprocess.Popen(['powershell', '-NoProfile', '-WindowStyle', 'Hidden', '-Command', ps_cmd],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def process_discovered_file(file_path):
    global known_targets, known_files
    
    file_path_lower = file_path.lower()
    with lock:
        if file_path_lower in known_files:
            return
        if "smartcatalog" in file_path_lower or "backup" in file_path_lower:
            return
        known_files.add(file_path_lower)
        
    time.sleep(1.2)
    if not os.path.exists(file_path):
        return
        
    base_name = os.path.basename(file_path)
    
    pythoncom.CoInitialize()
    try:
        # 1. Handle .lnk files
        if file_path_lower.endswith(".lnk"):
            app_name = os.path.splitext(base_name)[0]
            if is_junk_or_uninstaller(app_name, file_path):
                return
                
            try:
                shell = win32com.client.Dispatch("WScript.Shell")
                lnk = shell.CreateShortCut(file_path)
                target = lnk.TargetPath
            except Exception:
                return
                
            if not target or (not os.path.exists(target) and "explorer.exe" not in target.lower()):
                return
                    
            if is_junk_or_uninstaller(app_name, target):
                return
                
            target_lower = target.lower()
            with lock:
                if target_lower in known_targets and "explorer.exe" not in target_lower:
                    return
                known_targets.add(target_lower)
            
            entry = add_new_software(app_name, target, source_lnk=file_path)
            if entry:
                cat_clean = entry["category"]
                desc_clean = entry["description"]
                print(f"[Watcher] Discovered and added: {app_name} -> {cat_clean}", flush=True)
                show_toast(
                    "Новая программа добавлена",
                    f"{app_name} распределена в «{cat_clean}».\n{desc_clean}"
                )
                
        # 2. Handle standalone / portable .exe
        elif file_path_lower.endswith(".exe"):
            app_name = os.path.splitext(base_name)[0]
            if is_junk_or_uninstaller(app_name, file_path):
                return
            if any(term in app_name.lower() for term in ["setup", "install", "update", "patch"]):
                return
                
            target_lower = file_path.lower()
            with lock:
                if target_lower in known_targets:
                    return
                known_targets.add(target_lower)
            
            entry = add_new_software(app_name, file_path)
            if entry:
                cat_clean = entry["category"]
                desc_clean = entry["description"]
                print(f"[Watcher] Added portable application: {app_name} -> {cat_clean}", flush=True)
                show_toast(
                    "Обнаружена портативная программа",
                    f"{app_name} добавлена в «{cat_clean}».\n{desc_clean}"
                )
    finally:
        pythoncom.CoUninitialize()

def scan_watch_dirs():
    """Manual fallback and sync scan"""
    pythoncom.CoInitialize()
    try:
        for wdir in WATCH_DIRS:
            if not os.path.exists(wdir):
                continue
            try:
                for root, _, files in os.walk(wdir):
                    if "backup" in root.lower() or "smartcatalog" in root.lower():
                        continue
                    for f in files:
                        if f.lower().endswith(('.lnk', '.exe')):
                            fp = os.path.join(root, f)
                            if fp.lower() not in known_files:
                                process_discovered_file(fp)
            except Exception:
                pass
    finally:
        pythoncom.CoUninitialize()

def _watch_worker(dir_path):
    """Event-driven ReadDirectoryChangesW loop with 0% CPU consumption"""
    while True:
        try:
            if not os.path.exists(dir_path):
                time.sleep(5)
                continue
                
            hDir = win32file.CreateFile(
                dir_path,
                win32con.GENERIC_READ,
                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
                None,
                win32con.OPEN_EXISTING,
                win32con.FILE_FLAG_BACKUP_SEMANTICS,
                None
            )
            
            while True:
                results = win32file.ReadDirectoryChangesW(
                    hDir,
                    8192,
                    True, # bWatchSubtree
                    win32con.FILE_NOTIFY_CHANGE_FILE_NAME | win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
                    None,
                    None
                )
                for action, filename in results:
                    # action: 1 = Added, 3 = Modified, 5 = Renamed new name
                    if action in (1, 3, 5):
                        full_path = os.path.join(dir_path, filename)
                        if full_path.lower().endswith(('.lnk', '.exe')):
                            # Process in background thread to avoid blocking change events
                            threading.Thread(target=process_discovered_file, args=(full_path,), daemon=True).start()
                            
        except Exception as e:
            time.sleep(3)

def start_watcher_loop():
    print("[Watcher] Initializing event-driven Windows filesystem monitors...", flush=True)
    init_known_targets()
    
    # Launch ReadDirectoryChangesW thread for each watch directory
    for wdir in WATCH_DIRS:
        if os.path.exists(wdir):
            t = threading.Thread(target=_watch_worker, args=(wdir,), daemon=True)
            t.start()
            print(f"[Watcher] Event listener attached to: {wdir}", flush=True)
            
    print(f"[Watcher] Active. Monitoring filesystem changes with 0% CPU...", flush=True)
    
    # If starting on a fresh installation with empty catalog, run initial discovery scan immediately
    data = load_catalog_data()
    if len(data) == 0:
        print("[Watcher] Empty catalog detected. Running initial discovery scan...", flush=True)
        threading.Thread(target=scan_watch_dirs, daemon=True).start()
    
    # Low-frequency fallback scan (every 60s) just in case
    while True:
        try:
            time.sleep(60)
            scan_watch_dirs()
        except Exception:
            pass

if __name__ == "__main__":
    start_watcher_loop()
