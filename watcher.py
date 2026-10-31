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

CATEGORY_NAMES_EN = {
    "01. Разработка и Код": "01. Development & Code",
    "02. Базы данных": "02. Databases",
    "03. Нейросети и ИИ": "03. AI & Neural Networks",
    "04. Интернет и Браузеры": "04. Internet & Browsers",
    "05. Мессенджеры и Связь": "05. Communication & Chat",
    "06. Удаленный доступ и Сеть": "06. Remote Access & Network",
    "07. Медиа и Звук": "07. Media & Audio",
    "08. Игры и Развлечения": "08. Games & Entertainment",
    "09. Офис и Документы": "09. Office & Documents",
    "10. Графика и Дизайн": "10. Graphics & Design",
    "11. Железо и Мониторинг": "11. Hardware & Monitoring",
    "12. Система и Обслуживание": "12. System & Maintenance",
    "13. Безопасность и Архивы": "13. Security & Utilities"
}

def notify_discovered_app(app_name, cat_clean, desc_clean, is_portable=False):
    lang = catalog_manager.load_user_data().get("settings", {}).get("language", "ru")
    if lang == "en":
        cat_disp = CATEGORY_NAMES_EN.get(cat_clean, cat_clean)
        title = "Portable Application Discovered" if is_portable else "New Application Added"
        msg = f"{app_name} added to «{cat_disp}».\n{desc_clean}"
    else:
        title = "Обнаружена портативная программа" if is_portable else "Новая программа добавлена"
        msg = f"{app_name} распределена в «{cat_clean}».\n{desc_clean}"
    show_toast(title, msg)

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
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        subprocess.Popen(
            ['powershell', '-NoProfile', '-NonInteractive', '-WindowStyle', 'Hidden', '-Command', ps_cmd],
            creationflags=subprocess.CREATE_NO_WINDOW,
            startupinfo=startupinfo,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass

def process_discovered_file(file_path, notify=True, save_now=True, delay=True):
    global known_targets, known_files
    
    file_path_lower = file_path.lower()
    with lock:
        if file_path_lower in known_files:
            return None
        if "smartcatalog" in file_path_lower or "backup" in file_path_lower:
            return None
        known_files.add(file_path_lower)
        
    if delay:
        time.sleep(1.2)
        
    if not os.path.exists(file_path):
        return None
        
    base_name = os.path.basename(file_path)
    
    pythoncom.CoInitialize()
    try:
        # 1. Handle .lnk files
        if file_path_lower.endswith(".lnk"):
            app_name = os.path.splitext(base_name)[0]
            if is_junk_or_uninstaller(app_name, file_path):
                return None
                
            try:
                shell = win32com.client.Dispatch("WScript.Shell")
                lnk = shell.CreateShortCut(file_path)
                target = lnk.TargetPath
            except Exception:
                return None
                
            if not target or (not os.path.exists(target) and "explorer.exe" not in target.lower()):
                return None
                    
            if is_junk_or_uninstaller(app_name, target):
                return None
                
            target_lower = target.lower()
            with lock:
                if target_lower in known_targets and "explorer.exe" not in target_lower:
                    return None
                known_targets.add(target_lower)
            
            entry = add_new_software(app_name, target, source_lnk=file_path, save_now=save_now)
            if entry and notify:
                cat_clean = entry["category"]
                desc_clean = entry["description"]
                print(f"[Watcher] Discovered and added: {app_name} -> {cat_clean}", flush=True)
                notify_discovered_app(app_name, cat_clean, desc_clean, is_portable=False)
            return entry
                
        # 2. Handle standalone / portable .exe
        elif file_path_lower.endswith(".exe"):
            app_name = os.path.splitext(base_name)[0]
            if is_junk_or_uninstaller(app_name, file_path):
                return None
            if any(term in app_name.lower() for term in ["setup", "install", "update", "patch"]):
                return None
                
            target_lower = file_path.lower()
            with lock:
                if target_lower in known_targets:
                    return None
                known_targets.add(target_lower)
            
            entry = add_new_software(app_name, file_path, save_now=save_now)
            if entry and notify:
                cat_clean = entry["category"]
                desc_clean = entry["description"]
                print(f"[Watcher] Added portable application: {app_name} -> {cat_clean}", flush=True)
                notify_discovered_app(app_name, cat_clean, desc_clean, is_portable=True)
            return entry
    finally:
        pythoncom.CoUninitialize()
    return None

def scan_watch_dirs(is_initial_scan=False):
    """Manual fallback and sync scan. In initial scan mode, operates in fast batch without per-item notifications."""
    pythoncom.CoInitialize()
    discovered_entries = []
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
                                entry = process_discovered_file(
                                    fp, 
                                    notify=not is_initial_scan, 
                                    save_now=not is_initial_scan,
                                    delay=not is_initial_scan
                                )
                                if entry:
                                    discovered_entries.append(entry)
            except Exception:
                pass

        if is_initial_scan and discovered_entries:
            existing = load_catalog_data()
            existing_ids = {x["id"] for x in existing}
            for e in discovered_entries:
                if e["id"] not in existing_ids:
                    existing.append(e)
                    existing_ids.add(e["id"])
            save_catalog_data(existing)
            count = len(discovered_entries)
            print(f"[Watcher] Initial scan complete: {count} applications indexed.", flush=True)
            lang = catalog_manager.load_user_data().get("settings", {}).get("language", "ru")
            if lang == "en":
                show_toast(
                    "SmartCatalog is Ready",
                    f"Initial system scan complete: {count} applications indexed."
                )
            else:
                show_toast(
                    "Каталог готов к работе",
                    f"Первичное сканирование завершено: обнаружено {count} программ."
                )
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
        threading.Thread(target=scan_watch_dirs, args=(True,), daemon=True).start()
    
    # Low-frequency fallback scan (every 60s) just in case
    while True:
        try:
            time.sleep(60)
            scan_watch_dirs()
        except Exception:
            pass

if __name__ == "__main__":
    start_watcher_loop()
