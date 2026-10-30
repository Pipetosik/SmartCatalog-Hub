import os
import sys
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")
BUILD_DIR = os.path.join(BASE_DIR, "build")

def main():
    print("=" * 60)
    print("  SmartCatalog Hub - Standalone Executable Builder")
    print("=" * 60)
    
    # 1. Ensure pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("[*] Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
    icon_path = os.path.join(BASE_DIR, "assets", "icon.ico")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(BASE_DIR, "SmartCatalog_v3.ico")
        
    # 2. Build SmartCatalog Service executable
    print("[*] Building SmartCatalogService.exe...")
    cmd_service = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "SmartCatalogHub",
        f"--icon={icon_path}",
        "--add-data", f"{os.path.join(BASE_DIR, 'static')};static",
        "--add-data", f"{os.path.join(BASE_DIR, 'assets')};assets",
        "--hidden-import", "win32timezone",
        "--hidden-import", "win32file",
        "--hidden-import", "win32gui",
        "--hidden-import", "win32con",
        "--hidden-import", "win32process",
        "--hidden-import", "win32clipboard",
        "--hidden-import", "win32com.client",
        "--hidden-import", "pythoncom",
        "--hidden-import", "psutil",
        "--hidden-import", "PIL",
        "--hidden-import", "keyboard",
        os.path.join(BASE_DIR, "service.py")
    ]
    subprocess.check_call(cmd_service)
    
    # 3. Build Client App launcher
    print("[*] Building SmartCatalogClient.exe...")
    cmd_app = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "SmartCatalogClient",
        f"--icon={icon_path}",
        os.path.join(BASE_DIR, "app.py")
    ]
    subprocess.check_call(cmd_app)
    
    # Merge client exe into main dist folder
    client_exe = os.path.join(DIST_DIR, "SmartCatalogClient", "SmartCatalogClient.exe")
    target_client = os.path.join(DIST_DIR, "SmartCatalogHub", "SmartCatalog.exe")
    if os.path.exists(client_exe):
        shutil.copy2(client_exe, target_client)
        print(f"[*] Placed client launcher: {target_client}")
        
    print("\n[SUCCESS] Standalone build complete!")
    print(f"Output folder: {os.path.join(DIST_DIR, 'SmartCatalogHub')}")

if __name__ == "__main__":
    main()
