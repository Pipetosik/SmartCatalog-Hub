import os
import sys
import subprocess
import win32com.client

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
SERVICE_PY = os.path.join(WORKSPACE, "service.py")
python_dir = os.path.dirname(sys.executable)
cand_pythonw = os.path.join(python_dir, "pythonw.exe")
PYTHONW = cand_pythonw if os.path.exists(cand_pythonw) else sys.executable
ICON_PATH = os.path.join(WORKSPACE, "assets", "icon.ico")
if not os.path.exists(ICON_PATH):
    ICON_PATH = os.path.join(WORKSPACE, "SmartCatalog_v3.ico")

STARTUP_DIR = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
OLD_LNK = os.path.join(STARTUP_DIR, "SmartCatalog Watcher.lnk")
STARTUP_LNK = os.path.join(STARTUP_DIR, "SmartCatalog Service.lnk")

if os.path.exists(OLD_LNK):
    try:
        os.remove(OLD_LNK)
        print(f"Removed legacy shortcut: {OLD_LNK}")
    except Exception:
        pass

shell = win32com.client.Dispatch("WScript.Shell")
try:
    os.makedirs(STARTUP_DIR, exist_ok=True)
    shortcut = shell.CreateShortCut(STARTUP_LNK)
    shortcut.TargetPath = PYTHONW
    shortcut.Arguments = f'"{SERVICE_PY}"'
    shortcut.WorkingDirectory = WORKSPACE
    shortcut.IconLocation = f"{ICON_PATH},0"
    shortcut.Description = "Фоновая служба каталога и авто-детектор новых программ SmartCatalog"
    shortcut.Save()
    print(f"Service auto-start installed to: {STARTUP_LNK}")
except Exception as e:
    print(f"Failed to install auto-start: {e}")

# Start service now if not running
try:
    subprocess.Popen([PYTHONW, SERVICE_PY], cwd=WORKSPACE)
    print("Background service.py launched.")
except Exception as e:
    print(f"Failed to launch service: {e}")
