import os
import sys
import json
import urllib.parse
import subprocess
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import catalog_manager
import watcher
import updater
import winget_manager
from classifier import CATEGORY_RULES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
ICONS_DIR = os.path.join(BASE_DIR, "icons_cache")
APP_VERSION = "1.1.0"

def attach_to_default_desktop():
    try:
        import ctypes
        hDesk = ctypes.windll.user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if hDesk:
            ctypes.windll.user32.SetThreadDesktop(hDesk)
    except Exception:
        pass

def apply_window_glass_effect(hwnd):
    try:
        import ctypes
        import win32con
        user32 = ctypes.windll.user32
        dwmapi = ctypes.windll.dwmapi

        theme = catalog_manager.get_setting("theme", "win11")

        # 1. Dark mode (20)
        v_dark = ctypes.c_int(1)
        dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(v_dark), ctypes.sizeof(v_dark))

        # 2. Window rounded corners (33 = DWMWCP_ROUND)
        v_round = ctypes.c_int(3)
        dwmapi.DwmSetWindowAttribute(hwnd, 33, ctypes.byref(v_round), ctypes.sizeof(v_round))

        # 3. System Backdrop (38 = Acrylic 3, Mica 2, Mica Alt 4, None 1)
        btype = 3 if ("acrylic" in theme or "win11" in theme) else (4 if "mica" in theme else 1)
        v_backdrop = ctypes.c_int(btype)
        dwmapi.DwmSetWindowAttribute(hwnd, 38, ctypes.byref(v_backdrop), ctypes.sizeof(v_backdrop))

        # 4. Native Layered Translucency for Windows 11 Acrylic
        style_ex = user32.GetWindowLongW(hwnd, win32con.GWL_EXSTYLE)
        if "acrylic" in theme or "win11" in theme:
            user32.SetWindowLongW(hwnd, win32con.GWL_EXSTYLE, style_ex | win32con.WS_EX_LAYERED)
            # 248 / 255 = 97.2% opacity: desktop wallpaper and open windows softly blur through
            user32.SetLayeredWindowAttributes(hwnd, 0, 248, 0x02) # LWA_ALPHA
        else:
            if style_ex & win32con.WS_EX_LAYERED:
                user32.SetLayeredWindowAttributes(hwnd, 0, 255, 0x02)
                user32.SetWindowLongW(hwnd, win32con.GWL_EXSTYLE, style_ex & ~win32con.WS_EX_LAYERED)
    except Exception as e:
        print(f"[Glass] Error: {e}", flush=True)

def position_hub_window(mode="full"):
    try:
        import time
        import ctypes
        import ctypes.wintypes
        import win32gui
        import win32con

        attach_to_default_desktop()

        for attempt in range(12):
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

            if found:
                hwnd = found[0]

                class RECT(ctypes.Structure):
                    _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long), ('right', ctypes.c_long), ('bottom', ctypes.c_long)]
                wa = RECT()
                ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(wa), 0)

                if mode == "compact":
                    target_vis_w = min(720, wa.right - wa.left - 40)
                    target_vis_h = min(540, wa.bottom - wa.top - 20)
                else:
                    target_vis_w = min(1180, wa.right - wa.left - 40)
                    target_vis_h = min(780, wa.bottom - wa.top - 20)

                vis_x = wa.left + (wa.right - wa.left - target_vis_w) // 2
                vis_y = wa.bottom - target_vis_h

                rect_dwm = ctypes.wintypes.RECT()
                ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(rect_dwm), ctypes.sizeof(rect_dwm))
                rect_win = win32gui.GetWindowRect(hwnd)

                diff_l = rect_dwm.left - rect_win[0]
                diff_r = rect_win[2] - rect_dwm.right
                diff_t = rect_dwm.top - rect_win[1]
                diff_b = rect_win[3] - rect_dwm.bottom

                win_x = vis_x - diff_l
                win_y = vis_y - diff_t
                win_w = target_vis_w + diff_l + diff_r
                win_h = target_vis_h + diff_t + diff_b

                win32gui.SetWindowPos(hwnd, 0, win_x, win_y, win_w, win_h, win32con.SWP_NOZORDER | win32con.SWP_SHOWWINDOW)
                apply_window_glass_effect(hwnd)
                return True
            time.sleep(0.15)
        return False
    except Exception as e:
        print(f"Error positioning window: {e}", flush=True)
        return False

ALLOWED_HOSTS = {"127.0.0.1:48123", "localhost:48123"}
ALLOWED_ORIGINS = {
    "http://127.0.0.1:48123",
    "http://localhost:48123",
    "null"
}
MAX_BODY_SIZE = 2 * 1024 * 1024  # 2MB maximum payload

class CatalogHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress noisy console logs
        pass

    def send_json(self, data, status=200):
        try:
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            origin = self.headers.get('Origin')
            if origin in ALLOWED_ORIGINS:
                self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('X-Frame-Options', 'DENY')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.end_headers()
            self.wfile.write(body)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            pass

    def send_file_response(self, file_path, content_type):
        if not os.path.exists(file_path):
            self.send_error(404, "File Not Found")
            return
        with open(file_path, 'rb') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.end_headers()
        try:
            self.wfile.write(data)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            pass

    def do_GET(self):
        host = self.headers.get('Host', '')
        if host and host not in ALLOWED_HOSTS:
            self.send_error(400, "Invalid Host header")
            return

        url = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(url.path)

        if path == "/" or path == "/index.html":
            self.send_file_response(os.path.join(STATIC_DIR, "index.html"), "text/html; charset=utf-8")
            return

        if path == "/favicon.ico":
            self.send_file_response(os.path.join(STATIC_DIR, "favicon.ico"), "image/x-icon")
            return

        if path == "/api/apps":
            apps = catalog_manager.load_catalog_data()
            if not apps:
                apps = catalog_manager.scan_and_rebuild_catalog()
            
            # Check if hidden apps should be included
            query_params = urllib.parse.parse_qs(url.query)
            include_hidden = query_params.get("all", ["false"])[0].lower() in ("true", "1")
            if not include_hidden:
                user_data = catalog_manager.load_user_data()
                hidden_ids = set(user_data.get("hidden_apps", []))
                apps = [a for a in apps if a.get("id") not in hidden_ids]
                
            self.send_json(apps)
            return

        if path == "/api/version":
            self.send_json({
                "version": catalog_manager.get_catalog_version(),
                "total": len(catalog_manager.load_catalog_data()),
                "app_version": APP_VERSION
            })
            return

        if path == "/api/hidden_apps":
            hidden = catalog_manager.get_hidden_apps()
            self.send_json(hidden)
            return

        if path == "/api/user_data":
            user_data = catalog_manager.load_user_data()
            self.send_json(user_data)
            return

        if path == "/api/categories":
            apps = catalog_manager.load_catalog_data()
            counts = {}
            for a in apps:
                c = a.get("category", "12. Система и Обслуживание")
                counts[c] = counts.get(c, 0) + 1
            categories = []
            for cat_name, rules in sorted(CATEGORY_RULES.items()):
                categories.append({
                    "name": cat_name,
                    "icon": rules.get("icon", "📁"),
                    "count": counts.get(cat_name, 0),
                    "description": rules.get("default_desc", "")
                })
            self.send_json(categories)
            return

        if path == "/api/running_apps":
            running = catalog_manager.get_running_apps()
            self.send_json({"running": running})
            return

        if path == "/api/playtime":
            stats = catalog_manager.get_playtime_stats()
            self.send_json(stats)
            return

        if path == "/api/workspaces":
            workspaces = catalog_manager.load_workspaces()
            self.send_json(workspaces)
            return

        if path == "/api/clipboard":
            history = catalog_manager.load_clipboard_history()
            self.send_json(history)
            return

        if path == "/api/snippets":
            snippets = catalog_manager.load_snippets()
            self.send_json(snippets)
            return

        if path == "/api/system_stats":
            stats = catalog_manager.get_system_stats()
            self.send_json(stats)
            return

        if path == "/api/classification_log":
            log_path = os.path.join(BASE_DIR, "classification_debug.log")
            if os.path.exists(log_path):
                try:
                    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                        lines = f.readlines()
                        content = "".join(lines[-2000:])
                    self.send_json({"success": True, "log": content})
                except Exception as e:
                    self.send_json({"success": False, "error": str(e), "log": ""}, 500)
            else:
                self.send_json({"success": True, "log": "Лог классификации пока пуст. Запустите сканирование или добавьте приложение."})
            return

        if path == "/api/app_update/check":
            force = False
            if "?" in self.path:
                q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                force = q.get("force", ["0"])[0].lower() in ("1", "true", "yes")
            result = updater.check_for_updates(force=force)
            self.send_json(result)
            return

        if path == "/api/app_update/progress":
            progress = updater.get_download_progress()
            self.send_json(progress)
            return

        if path == "/api/software_updates/status":
            status = winget_manager.get_status()
            self.send_json(status)
            return

        # Secure icon file serving with realpath boundary check against Path Traversal
        if path.startswith("/icons/"):
            rel = path[len("/icons/"):].lstrip("/\\")
            resolved_icons_dir = os.path.realpath(ICONS_DIR)
            target_path = os.path.realpath(os.path.abspath(os.path.join(ICONS_DIR, rel)))
            if target_path.startswith(resolved_icons_dir) and os.path.exists(target_path) and os.path.isfile(target_path):
                self.send_file_response(target_path, "image/png")
            else:
                self.send_file_response(os.path.join(STATIC_DIR, "icons", "default.png"), "image/png")
            return

        # Secure static file serving with realpath boundary check against Path Traversal
        if path.startswith("/static/"):
            rel = path[len("/static/"):].lstrip("/\\")
            resolved_static_dir = os.path.realpath(STATIC_DIR)
            target_path = os.path.realpath(os.path.abspath(os.path.join(STATIC_DIR, rel)))
            if not (target_path.startswith(resolved_static_dir) and os.path.exists(target_path) and os.path.isfile(target_path)):
                self.send_error(404, "File Not Found")
                return
            ctype = "text/plain"
            if rel.endswith(".css"):
                ctype = "text/css; charset=utf-8"
            elif rel.endswith(".js"):
                ctype = "application/javascript; charset=utf-8"
            elif rel.endswith(".png"):
                ctype = "image/png"
            elif rel.endswith(".ico"):
                ctype = "image/x-icon"
            elif rel.endswith(".html"):
                ctype = "text/html; charset=utf-8"
            self.send_file_response(target_path, ctype)
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        host = self.headers.get('Host', '')
        if host and host not in ALLOWED_HOSTS:
            self.send_error(400, "Invalid Host header")
            return

        origin = self.headers.get('Origin')
        if origin and origin not in ALLOWED_ORIGINS:
            self.send_error(403, "Cross-Origin Request Blocked")
            return

        attach_to_default_desktop()
        url = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(url.path)
        
        try:
            length = int(self.headers.get('Content-Length', 0))
        except (ValueError, TypeError):
            self.send_error(400, "Invalid Content-Length")
            return

        if length > MAX_BODY_SIZE:
            self.send_error(413, "Payload Too Large")
            return

        body = self.rfile.read(length).decode('utf-8', errors='replace') if length > 0 else "{}"
        try:
            req_data = json.loads(body)
        except Exception:
            req_data = {}

        if path == "/api/launch":
            app_id = req_data.get("id", "")
            ok, msg = catalog_manager.launch_application(app_id)
            print(f"[/api/launch] app_id='{app_id}' ok={ok} msg='{msg}'", flush=True)
            self.send_json({"success": ok, "message": msg}, 200 if ok else 400)
            return

        if path == "/api/launch_admin":
            app_id = req_data.get("id", "")
            ok, msg = catalog_manager.launch_app_as_admin(app_id)
            print(f"[/api/launch_admin] app_id='{app_id}' ok={ok} msg='{msg}'", flush=True)
            self.send_json({"success": ok, "message": msg}, 200 if ok else 400)
            return

        if path == "/api/open_target_folder":
            app_id = req_data.get("id", "")
            ok, target_path = catalog_manager.open_target_folder(app_id)
            self.send_json({"success": ok, "path": target_path}, 200 if ok else 404)
            return

        if path == "/api/move_category":
            app_id = req_data.get("id", "")
            cat = req_data.get("category", "")
            ok, msg = catalog_manager.move_app_category(app_id, cat)
            self.send_json({"success": ok, "message": msg}, 200 if ok else 400)
            return

        if path == "/api/hide_app":
            app_id = req_data.get("id", "")
            ok, hidden = catalog_manager.hide_app(app_id)
            self.send_json({"success": ok, "hidden_apps": hidden})
            return

        if path == "/api/unhide_app":
            app_id = req_data.get("id", "")
            ok, hidden = catalog_manager.unhide_app(app_id)
            self.send_json({"success": ok, "hidden_apps": hidden})
            return

        if path == "/api/favorites/toggle":
            app_id = req_data.get("id", "")
            is_fav, favs = catalog_manager.toggle_favorite(app_id)
            self.send_json({"success": True, "is_favorite": is_fav, "favorites": favs})
            return

        if path == "/api/settings":
            k = req_data.get("key", "")
            v = req_data.get("value", "")
            if k:
                st = catalog_manager.set_setting(k, v)
                if k == "theme":
                    try:
                        position_hub_window()
                    except Exception:
                        pass
                try:
                    import tray_and_hotkey
                    tray_and_hotkey.reload_tray_and_hotkey_settings()
                except Exception as e:
                    print(f"[Settings] Error reloading tray/hotkey: {e}", flush=True)
                self.send_json({"success": True, "settings": st})
            else:
                self.send_json({"error": "Missing key"}, 400)
            return

        if path == "/api/open_folder":
            cat = str(req_data.get("category", "")).strip()
            p = str(req_data.get("path", "")).strip()
            target_dir = ""
            if cat:
                clean_cat = os.path.basename(cat)
                target_dir = os.path.join(catalog_manager.SMART_CATALOG_ROOT, clean_cat)
            elif p:
                target_dir = p if os.path.isdir(p) else os.path.dirname(p)
            else:
                target_dir = catalog_manager.SMART_CATALOG_ROOT
            if os.path.exists(target_dir):
                subprocess.Popen(["explorer.exe", target_dir])
                self.send_json({"success": True, "opened": target_dir})
            else:
                self.send_json({"success": False, "error": "Folder not found"}, 404)
            return

        if path == "/api/open_playnite":
            playnite_path = os.path.expandvars(r"%LOCALAPPDATA%\Playnite\Playnite.DesktopApp.exe")
            if os.path.exists(playnite_path):
                subprocess.Popen([playnite_path])
                self.send_json({"success": True})
            else:
                self.send_json({"success": False, "error": "Playnite не найден"}, 404)
            return

        if path == "/api/open_logs_folder":
            log_path = os.path.join(BASE_DIR, "classification_debug.log")
            try:
                if os.path.exists(log_path):
                    subprocess.Popen(["explorer.exe", f"/select,{log_path}"])
                else:
                    subprocess.Popen(["explorer.exe", BASE_DIR])
                self.send_json({"success": True})
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, 500)
            return

        if path == "/api/position_window":
            mode = req_data.get("mode", "full")
            ok = position_hub_window(mode)
            self.send_json({"success": ok})
            return

        if path == "/api/snippets/save":
            ok, saved = catalog_manager.save_snippet(req_data)
            self.send_json({"success": ok, "snippet": saved})
            return

        if path == "/api/snippets/delete":
            snip_id = req_data.get("id", "")
            ok = catalog_manager.delete_snippet(snip_id)
            self.send_json({"success": ok})
            return

        if path == "/api/kill_process":
            pid = req_data.get("pid", 0)
            ok, msg = catalog_manager.kill_process_by_pid(pid)
            self.send_json({"success": ok, "message": msg}, 200 if ok else 400)
            return

        if path == "/api/kill_app":
            app_id = req_data.get("id", "")
            ok, msg = catalog_manager.kill_application(app_id)
            self.send_json({"success": ok, "message": msg}, 200 if ok else 400)
            return

        if path == "/api/workspaces/launch":
            ws_id = req_data.get("id", "")
            ok, msg = catalog_manager.launch_workspace(ws_id)
            self.send_json({"success": ok, "message": msg}, 200 if ok else 400)
            return

        if path == "/api/workspaces/save":
            ok, saved = catalog_manager.save_workspace(req_data)
            self.send_json({"success": ok, "workspace": saved})
            return

        if path == "/api/workspaces/delete":
            ws_id = req_data.get("id", "")
            ok = catalog_manager.delete_workspace(ws_id)
            self.send_json({"success": ok})
            return

        if path == "/api/clipboard/copy":
            text = req_data.get("text", "")
            ok, msg = catalog_manager.copy_text_to_clipboard(text)
            self.send_json({"success": ok, "message": msg}, 200 if ok else 400)
            return

        if path == "/api/clipboard/clear":
            ok = catalog_manager.clear_clipboard_history()
            self.send_json({"success": ok})
            return

        if path == "/api/open_url":
            raw_url = str(req_data.get("url", "")).strip()
            if not raw_url:
                self.send_json({"success": False, "error": "Missing URL"}, 400)
                return

            parsed = urllib.parse.urlsplit(raw_url)
            if parsed.scheme:
                if parsed.scheme not in ("http", "https"):
                    self.send_json({"success": False, "error": "Invalid or disallowed protocol scheme"}, 400)
                    return
                target_url = raw_url
            else:
                target_url = "https://" + raw_url
                parsed = urllib.parse.urlsplit(target_url)

            if parsed.scheme in ("http", "https") and parsed.netloc and "." in parsed.netloc:
                try:
                    os.startfile(target_url)
                    self.send_json({"success": True, "url": target_url})
                except Exception as e:
                    self.send_json({"success": False, "error": str(e)}, 500)
            else:
                self.send_json({"success": False, "error": "Invalid web URL"}, 400)
            return

        if path == "/api/rescan":
            try:
                watcher.scan_watch_dirs()
            except Exception as e:
                print(f"[API Rescan] Watcher scan error: {e}", flush=True)
            apps = catalog_manager.scan_and_rebuild_catalog()
            self.send_json({"success": True, "total": len(apps)})
            return

        if path == "/api/app_update/download":
            url = req_data.get("url")
            ok, msg = updater.start_download(url)
            self.send_json({"success": ok, "message": msg}, 200 if ok else 400)
            return

        if path == "/api/app_update/install":
            silent = bool(req_data.get("silent", False))
            ok, msg = updater.install_update(silent=silent)
            self.send_json({"success": ok, "message": msg}, 200 if ok else 400)
            return

        if path == "/api/software_updates/scan":
            force = bool(req_data.get("force", False))
            res = winget_manager.start_scan(force=force)
            self.send_json(res)
            return

        if path == "/api/software_updates/upgrade":
            pkg_id = req_data.get("package_id", "")
            elevated = bool(req_data.get("elevated", False))
            res = winget_manager.upgrade_package(pkg_id, elevated=elevated)
            status_code = 200 if res.get("status") in ("started", "running") else 400
            self.send_json(res, status_code)
            return

        if path == "/api/software_updates/upgrade_all":
            elevated = bool(req_data.get("elevated", False))
            res = winget_manager.upgrade_all(elevated=elevated)
            self.send_json(res)
            return

        self.send_error(404, "Not Found")

def create_server(host="127.0.0.1", port=48123):
    return ThreadingHTTPServer((host, port), CatalogHTTPHandler)

if __name__ == "__main__":
    server = create_server()
    print("Serving on http://127.0.0.1:48123")
    server.serve_forever()
