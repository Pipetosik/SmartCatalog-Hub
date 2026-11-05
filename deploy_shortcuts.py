import os
import sys
import ctypes
import win32com.client
from win32com.propsys import propsys, pscon

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
APP_PY = os.path.join(WORKSPACE, "app.py")
python_dir = os.path.dirname(sys.executable)
cand_pythonw = os.path.join(python_dir, "pythonw.exe")
PYTHONW = cand_pythonw if os.path.exists(cand_pythonw) else sys.executable

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
APP_PROFILE = os.path.join(WORKSPACE, ".app_profile")
ICON_PATH = os.path.join(WORKSPACE, "assets", "icon.ico")
if not os.path.exists(ICON_PATH):
    ICON_PATH = os.path.join(WORKSPACE, "SmartCatalog_v3.ico")
URL = "http://127.0.0.1:48123"
AUMID = "Chrome.127.0.0.1_/..appprofile.Default"

os.makedirs(APP_PROFILE, exist_ok=True)

# Calculate screen work area and dock to center-bottom (attached to taskbar)
class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long), ('right', ctypes.c_long), ('bottom', ctypes.c_long)]

wa = RECT()
ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(wa), 0)

target_vis_w = min(1180, wa.right - wa.left - 40)
target_vis_h = min(780, wa.bottom - wa.top - 20)
vis_x = wa.left + (wa.right - wa.left - target_vis_w) // 2
vis_y = wa.bottom - target_vis_h

# Invisible DWM frame borders in Windows 11 are 7px left/right/bottom
win_x = vis_x - 7
win_y = vis_y
win_w = target_vis_w + 14
win_h = target_vis_h + 7

print(f"Calculated Launcher Bounds: pos=({win_x}, {win_y}) size=({win_w}, {win_h}) -> visible center-bottom attached to taskbar")

taskbar_dir = os.path.expandvars(r"%APPDATA%\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar")
taskbar_shortcuts = []
if os.path.exists(taskbar_dir):
    for f in os.listdir(taskbar_dir):
        if f.lower().startswith("smartcatalog") and f.lower().endswith(".lnk"):
            taskbar_shortcuts.append(os.path.join(taskbar_dir, f))
if not taskbar_shortcuts:
    taskbar_shortcuts.append(os.path.join(taskbar_dir, "SmartCatalog Hub.lnk"))

TARGETS = [
    os.path.join(WORKSPACE, "SmartCatalog Hub.lnk"),
    os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\SmartCatalog Hub.lnk"),
    r"F:\SmartCatalog\SmartCatalog Hub.lnk"
] + taskbar_shortcuts

# Only update desktop shortcut if user currently has one (do not force recreate if deleted)
desktop_lnk = os.path.expandvars(r"%USERPROFILE%\Desktop\SmartCatalog Hub.lnk")
if os.path.exists(desktop_lnk):
    TARGETS.append(desktop_lnk)

shell = win32com.client.Dispatch("WScript.Shell")

for target_lnk in TARGETS:
    try:
        os.makedirs(os.path.dirname(target_lnk), exist_ok=True)
        shortcut = shell.CreateShortCut(target_lnk)
        shortcut.TargetPath = PYTHONW
        shortcut.Arguments = f'"{APP_PY}"'
        shortcut.WorkingDirectory = WORKSPACE
        shortcut.IconLocation = f"{ICON_PATH},0"
        shortcut.Description = "Умный лаунчер и каталог всех программ с авто-категоризацией"
        shortcut.Save()
        
        # Stamp AppUserModelID so Windows Taskbar groups running window into the pinned shortcut
        try:
            store = propsys.SHGetPropertyStoreFromParsingName(target_lnk, None, 2, propsys.IID_IPropertyStore)
            prop = propsys.PROPVARIANTType(AUMID)
            store.SetValue(pscon.PKEY_AppUserModel_ID, prop)
            store.Commit()
            print(f"Created shortcut & stamped AUMID: {target_lnk}")
        except Exception as e:
            print(f"Created shortcut {target_lnk}, but AUMID stamp error: {e}")
    except Exception as e:
        print(f"Failed to create {target_lnk}: {e}")

# Flush Windows Shell icon cache so Desktop and Taskbar immediately show the refreshed crisp icon
try:
    SHCNE_ASSOCCHANGED = 0x08000000
    SHCNF_IDLIST = 0x0000
    ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)
    print("Flushed Windows Shell icon cache via SHChangeNotify.")
except Exception as e:
    print(f"Could not notify shell of icon change: {e}")

