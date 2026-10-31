import os
import sys
import time
import threading
import subprocess
import ctypes
from ctypes import wintypes
import keyboard
import win32gui
import win32con
import win32api
import catalog_manager
from catalog_manager import get_setting

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_tray_icon_path():
    exe_dir = os.path.dirname(sys.executable)
    parent_dir = os.path.dirname(BASE_DIR)
    candidates = [
        os.path.join(BASE_DIR, "assets", "icon.ico"),
        os.path.join(BASE_DIR, "icon.ico"),
        os.path.join(BASE_DIR, "_internal", "assets", "icon.ico"),
        os.path.join(parent_dir, "assets", "icon.ico"),
        os.path.join(parent_dir, "icon.ico"),
        os.path.join(exe_dir, "assets", "icon.ico"),
        os.path.join(exe_dir, "icon.ico"),
        os.path.join(BASE_DIR, "SmartCatalog_v3.ico"),
        os.path.join(BASE_DIR, "SmartCatalog.ico"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

WM_TRAY_NOTIFY = win32con.WM_USER + 20
TRAY_ID = 100

CMD_OPEN = 1001
CMD_RESCAN = 1002
CMD_OPEN_FOLDER = 1003
CMD_EXIT = 1004

_tray_hwnd = None
_current_hotkey = None
_hotkey_hook = None

def attach_to_default_desktop():
    try:
        user32 = ctypes.windll.user32
        hDesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if hDesk:
            user32.SetThreadDesktop(hDesk)
    except Exception:
        pass

def find_hub_window():
    attach_to_default_desktop()
    found = []
    def enum_cb(h, _):
        try:
            if win32gui.IsWindowVisible(h):
                t = win32gui.GetWindowText(h)
                if 'smartcatalog hub' in t.lower():
                    found.append(h)
        except Exception:
            pass
        return True
    try:
        win32gui.EnumWindows(enum_cb, None)
    except Exception:
        pass
    return found[0] if found else None

def toggle_launcher_window():
    attach_to_default_desktop()
    hwnd = find_hub_window()
    if hwnd:
        fg = win32gui.GetForegroundWindow()
        if fg == hwnd:
            # If already in foreground, minimize/hide it
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        else:
            # Bring to front & position at center-bottom
            from server import position_hub_window
            position_hub_window()
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            catalog_manager.force_foreground(hwnd)
    else:
        # Launch Chrome app
        from app import open_ui
        open_ui()

def _on_hotkey_triggered():
    toggle_launcher_window()

def update_global_hotkey():
    global _current_hotkey
    desired = get_setting("global_hotkey", "alt+space")
    
    if _current_hotkey:
        try:
            keyboard.remove_hotkey(_current_hotkey)
        except Exception:
            pass
        _current_hotkey = None
        
    if desired and desired.lower() != "none" and desired.lower() != "off":
        try:
            keyboard.add_hotkey(desired, _on_hotkey_triggered, suppress=True)
            _current_hotkey = desired
            print(f"[Hotkey] Registered global hotkey: {desired}", flush=True)
        except Exception as e:
            print(f"[Hotkey] Failed to register {desired}: {e}", flush=True)

class TrayIconWindow:
    def __init__(self):
        self.class_name = "SmartCatalogTrayWindowClass"
        self.hwnd = None
        self.hicon = None
        self.tray_active = False

    def create_window(self):
        wc = win32gui.WNDCLASS()
        wc.lpszClassName = self.class_name
        wc.lpfnWndProc = self.wnd_proc
        wc.hInstance = win32api.GetModuleHandle(None)
        
        try:
            atom = win32gui.RegisterClass(wc)
        except Exception:
            pass
            
        self.hwnd = win32gui.CreateWindow(
            self.class_name,
            "SmartCatalogTray",
            0, 0, 0, 0, 0, 0, 0,
            wc.hInstance,
            None
        )
        global _tray_hwnd
        _tray_hwnd = self.hwnd
        return self.hwnd

    def add_tray_icon(self):
        if self.tray_active or not self.hwnd:
            return
        try:
            icon_p = get_tray_icon_path()
            if icon_p:
                try:
                    cx = win32api.GetSystemMetrics(win32con.SM_CXSMICON)
                    cy = win32api.GetSystemMetrics(win32con.SM_CYSMICON)
                    self.hicon = win32gui.LoadImage(
                        0, icon_p, win32con.IMAGE_ICON, cx, cy, win32con.LR_LOADFROMFILE
                    )
                except Exception:
                    self.hicon = None

            if not self.hicon:
                try:
                    h_inst = win32api.GetModuleHandle(None)
                    self.hicon = win32gui.LoadIcon(h_inst, 1)
                except Exception:
                    pass

            if not self.hicon:
                self.hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
                
            flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
            nid = (self.hwnd, TRAY_ID, flags, WM_TRAY_NOTIFY, self.hicon, "SmartCatalog Hub")
            win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
            self.tray_active = True
            print("[Tray] Icon added to system tray.", flush=True)
        except Exception as e:
            print(f"[Tray] Error adding icon: {e}", flush=True)

    def remove_tray_icon(self):
        if not self.tray_active or not self.hwnd:
            return
        try:
            nid = (self.hwnd, TRAY_ID)
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
            self.tray_active = False
            print("[Tray] Icon removed from system tray.", flush=True)
        except Exception as e:
            print(f"[Tray] Error removing icon: {e}", flush=True)

    def sync_tray_state(self):
        enabled = get_setting("enable_tray", True)
        if enabled and not self.tray_active:
            self.add_tray_icon()
        elif not enabled and self.tray_active:
            self.remove_tray_icon()

    def show_context_menu(self):
        lang = get_setting("language", "ru")
        menu = win32gui.CreatePopupMenu()
        if lang == "en":
            win32gui.AppendMenu(menu, win32con.MF_STRING | win32con.MF_DEFAULT, CMD_OPEN, "Open SmartCatalog Hub")
            win32gui.AppendMenu(menu, win32con.MF_STRING, CMD_RESCAN, "Rescan and Sync Catalog")
            win32gui.AppendMenu(menu, win32con.MF_STRING, CMD_OPEN_FOLDER, "Open Catalog Folder")
            win32gui.AppendMenu(menu, win32con.MF_SEPARATOR, 0, "")
            win32gui.AppendMenu(menu, win32con.MF_STRING, CMD_EXIT, "Quit SmartCatalog")
        else:
            win32gui.AppendMenu(menu, win32con.MF_STRING | win32con.MF_DEFAULT, CMD_OPEN, "Открыть SmartCatalog Hub")
            win32gui.AppendMenu(menu, win32con.MF_STRING, CMD_RESCAN, "Синхронизировать каталог")
            win32gui.AppendMenu(menu, win32con.MF_STRING, CMD_OPEN_FOLDER, "Открыть папку F:\\SmartCatalog")
            win32gui.AppendMenu(menu, win32con.MF_SEPARATOR, 0, "")
            win32gui.AppendMenu(menu, win32con.MF_STRING, CMD_EXIT, "Закрыть лаунчер")
        pos = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(self.hwnd)
        cmd = win32gui.TrackPopupMenu(
            menu,
            win32con.TPM_RETURNCMD | win32con.TPM_NONOTIFY,
            pos[0], pos[1], 0, self.hwnd, None
        )
        win32gui.DestroyMenu(menu)

        if cmd == CMD_OPEN:
            toggle_launcher_window()
        elif cmd == CMD_RESCAN:
            import watcher
            threading.Thread(target=watcher.scan_watch_dirs, daemon=True).start()
            threading.Thread(target=catalog_manager.scan_and_rebuild_catalog, daemon=True).start()
        elif cmd == CMD_OPEN_FOLDER:
            subprocess.Popen(f'explorer.exe "{catalog_manager.SMART_CATALOG_ROOT}"')
        elif cmd == CMD_EXIT:
            hwnd = find_hub_window()
            if hwnd:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            self.remove_tray_icon()
            os._exit(0)

    def wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == WM_TRAY_NOTIFY:
            if lparam in (win32con.WM_LBUTTONUP, win32con.WM_LBUTTONDBLCLK):
                toggle_launcher_window()
            elif lparam in (win32con.WM_RBUTTONUP, win32con.WM_CONTEXTMENU):
                self.show_context_menu()
            return 0
        elif msg == win32con.WM_DESTROY:
            self.remove_tray_icon()
            return 0
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

_tray_app = None

def start_tray_and_hotkey_service():
    global _tray_app
    attach_to_default_desktop()
    update_global_hotkey()
    
    _tray_app = TrayIconWindow()
    _tray_app.create_window()
    _tray_app.sync_tray_state()
    
    # Message loop for tray messages
    win32gui.PumpMessages()

def reload_tray_and_hotkey_settings():
    update_global_hotkey()
    if _tray_app:
        _tray_app.sync_tray_state()

if __name__ == "__main__":
    start_tray_and_hotkey_service()
