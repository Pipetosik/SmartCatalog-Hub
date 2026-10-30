import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "service.log")

# In pythonw.exe, sys.stdout and sys.stderr are None. Redirect them to avoid print() crashes!
if sys.stdout is None:
    try:
        sys.stdout = open(os.path.join(BASE_DIR, "service_stdout.log"), "a", encoding="utf-8")
    except Exception:
        sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    try:
        sys.stderr = open(os.path.join(BASE_DIR, "service_stderr.log"), "a", encoding="utf-8")
    except Exception:
        sys.stderr = open(os.devnull, "w")

import time
import threading
import traceback
from server import create_server
import watcher

PORT = 48123


def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

def run_server():
    log("Starting HTTP Server on 127.0.0.1:48123...")
    while True:
        try:
            httpd = create_server(host="127.0.0.1", port=PORT)
            log("HTTP Server listening on 127.0.0.1:48123.")
            httpd.serve_forever()
        except Exception as e:
            log(f"HTTP Server crashed: {e}. Restarting in 2s...")
            time.sleep(2)

def run_watcher():
    log("Starting Watcher thread...")
    while True:
        try:
            watcher.start_watcher_loop()
        except Exception as e:
            log(f"Watcher crashed: {e}. Restarting in 3s...")
            time.sleep(3)

def run_tray_and_hotkey():
    log("Starting Tray and Hotkey thread...")
    while True:
        try:
            import tray_and_hotkey
            tray_and_hotkey.start_tray_and_hotkey_service()
        except Exception as e:
            log(f"Tray and Hotkey crashed: {e}. Restarting in 3s...")
            time.sleep(3)

def run_playtime_and_clipboard_tracker():
    log("Starting Playtime and Clipboard Tracker thread...")
    import ctypes
    import psutil
    import win32clipboard
    import win32con
    import catalog_manager

    last_clipboard_seq = -1
    last_clipboard_text = None
    tick_interval = 2.5

    while True:
        try:
            settings = catalog_manager.load_user_data().get("settings", {})
            enable_playtime = settings.get("enable_playtime_tracking", True)
            enable_clipboard = settings.get("enable_clipboard_history", True)

            # 1. Screen Time Tracking for Active Foreground Window
            if enable_playtime:
                attach_to_default_desktop()
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                if hwnd:
                    pid = ctypes.c_ulong()
                    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    if pid.value:
                        try:
                            proc = psutil.Process(pid.value)
                            pname = (proc.name() or "").lower()
                            mapping = catalog_manager.build_process_to_app_map()
                            matched_aid = mapping.get(pname)
                            if not matched_aid:
                                try:
                                    pexe = proc.exe().lower()
                                    for a in catalog_manager.load_catalog_data():
                                        tgt = (a.get("target") or "").lower()
                                        if tgt and os.path.dirname(tgt) in pexe:
                                            matched_aid = a["id"]
                                            break
                                except Exception:
                                    pass
                            if matched_aid:
                                catalog_manager.record_playtime_tick(matched_aid, int(tick_interval))
                        except Exception:
                            pass

            # 2. Clipboard Text Capture (Zero-overhead via sequence number check)
            if enable_clipboard:
                try:
                    seq_num = win32clipboard.GetClipboardSequenceNumber()
                    if seq_num != last_clipboard_seq:
                        last_clipboard_seq = seq_num
                        win32clipboard.OpenClipboard()
                        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                            text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                            if text and text != last_clipboard_text:
                                last_clipboard_text = text
                                catalog_manager.add_clipboard_entry(text)
                        win32clipboard.CloseClipboard()
                except Exception:
                    try:
                        win32clipboard.CloseClipboard()
                    except Exception:
                        pass

        except Exception:
            pass

        time.sleep(tick_interval)

def attach_to_default_desktop():
    try:
        import ctypes
        hDesk = ctypes.windll.user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if hDesk:
            ctypes.windll.user32.SetThreadDesktop(hDesk)
    except Exception:
        pass

def main():
    attach_to_default_desktop()
    log("=== SmartCatalog Background Service Starting ===")
    
    # Start watcher in separate thread
    t_watcher = threading.Thread(target=run_watcher, daemon=True)
    t_watcher.start()
    
    # Start system tray and global hotkey thread
    t_tray = threading.Thread(target=run_tray_and_hotkey, daemon=True)
    t_tray.start()

    # Start screen time and clipboard tracker thread
    t_tracker = threading.Thread(target=run_playtime_and_clipboard_tracker, daemon=True)
    t_tracker.start()
    
    # Run server in main thread
    run_server()

if __name__ == "__main__":
    main()
