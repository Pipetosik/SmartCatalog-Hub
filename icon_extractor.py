import os
import io
import struct
import ctypes
from ctypes import wintypes
import win32gui
import win32api
import win32con
from PIL import Image

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', wintypes.DWORD),
        ('biWidth', wintypes.LONG),
        ('biHeight', wintypes.LONG),
        ('biPlanes', wintypes.WORD),
        ('biBitCount', wintypes.WORD),
        ('biCompression', wintypes.DWORD),
        ('biSizeImage', wintypes.DWORD),
        ('biXPelsPerMeter', wintypes.LONG),
        ('biYPelsPerMeter', wintypes.LONG),
        ('biClrUsed', wintypes.DWORD),
        ('biClrImportant', wintypes.DWORD)
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ('bmiHeader', BITMAPINFOHEADER),
        ('bmiColors', wintypes.DWORD * 3)
    ]

class BITMAP(ctypes.Structure):
    _fields_ = [
        ('bmType', wintypes.LONG),
        ('bmWidth', wintypes.LONG),
        ('bmHeight', wintypes.LONG),
        ('bmWidthBytes', wintypes.LONG),
        ('bmPlanes', wintypes.WORD),
        ('bmBitsPixel', wintypes.WORD),
        ('bmBits', wintypes.LPVOID)
    ]

class SHFILEINFO(ctypes.Structure):
    _fields_ = [
        ('hIcon', wintypes.HICON),
        ('iIcon', ctypes.c_int),
        ('dwAttributes', wintypes.DWORD),
        ('szDisplayName', ctypes.c_wchar * 260),
        ('szTypeName', ctypes.c_wchar * 80)
    ]

class GUID(ctypes.Structure):
    _fields_ = [
        ('Data1', wintypes.DWORD),
        ('Data2', wintypes.WORD),
        ('Data3', wintypes.WORD),
        ('Data4', ctypes.c_byte * 8)
    ]

IID_IImageList = GUID(0x46EB5926, 0x582E, 0x4017, (ctypes.c_byte * 8)(0x9F, 0xDF, 0xE8, 0x99, 0x8D, 0xAA, 0x09, 0x50))
SHGFI_SYSICONINDEX = 0x000004000
SHIL_JUMBO = 4        # 256x256
SHIL_EXTRALARGE = 2   # 48x48

ImageList_GetIcon = ctypes.windll.comctl32.ImageList_GetIcon
ImageList_GetIcon.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_uint]
ImageList_GetIcon.restype = wintypes.HICON

def _hicon_to_image_hd(hicon, target_size=256):
    if not hicon:
        return None
    try:
        info = win32gui.GetIconInfo(hicon)
        hbmColor = int(info[4]) if info[4] else None
        hbmMask = int(info[3]) if info[3] else None
        
        hdc = win32gui.GetDC(0)
        bm = BITMAP()
        handle_to_check = hbmColor if hbmColor else hbmMask
        ctypes.windll.gdi32.GetObjectW(handle_to_check, ctypes.sizeof(BITMAP), ctypes.byref(bm))
        w = bm.bmWidth
        h = bm.bmHeight if hbmColor else bm.bmHeight // 2
        
        if w <= 0 or h <= 0:
            win32gui.DestroyIcon(hicon)
            return None
            
        bmi = BITMAPINFO()
        bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = w
        bmi.bmiHeader.biHeight = -h
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = 0
        
        final_img = None
        if hbmColor:
            buf = ctypes.create_string_buffer(w * h * 4)
            ctypes.windll.gdi32.GetDIBits(hdc, hbmColor, 0, h, buf, ctypes.byref(bmi), 0)
            img = Image.frombuffer('RGBA', (w, h), buf.raw, 'raw', 'BGRA', 0, 1)
            r, g, b, a = img.split()
            if a.getextrema()[1] > 0:
                final_img = img
            else:
                if hbmMask:
                    mask_buf = ctypes.create_string_buffer(w * h * 4)
                    ctypes.windll.gdi32.GetDIBits(hdc, hbmMask, 0, h, mask_buf, ctypes.byref(bmi), 0)
                    mask_img = Image.frombuffer('RGBA', (w, h), mask_buf.raw, 'raw', 'BGRA', 0, 1)
                    gray_mask = mask_img.convert('L')
                    alpha = gray_mask.point(lambda p: 0 if p > 128 else 255)
                    img.putalpha(alpha)
                final_img = img
                
        win32gui.DestroyIcon(hicon)
        if final_img:
            if final_img.size != (target_size, target_size):
                final_img = final_img.resize((target_size, target_size), Image.Resampling.LANCZOS)
            return final_img
    except Exception:
        pass
    return None

def extract_raw_pe_png(file_path):
    if not file_path or not os.path.exists(file_path):
        return None
    try:
        hmod = win32api.LoadLibraryEx(file_path, 0, 2)
        groups = win32api.EnumResourceNames(hmod, win32con.RT_GROUP_ICON)
        for g in groups:
            data = win32api.LoadResource(hmod, win32con.RT_GROUP_ICON, g)
            _, _, count = struct.unpack('<HHH', data[:6])
            best_png = None
            best_len = 0
            for i in range(count):
                entry = data[6 + i*14 : 6 + (i+1)*14]
                bW, bH, _, _, _, _, dwBytes, nID = struct.unpack('<BBBBHHIH', entry)
                icon_data = win32api.LoadResource(hmod, win32con.RT_ICON, nID)
                if icon_data[:8] == b'\x89PNG\r\n\x1a\n' and len(icon_data) > best_len:
                    best_len = len(icon_data)
                    best_png = icon_data
            if best_png:
                im = Image.open(io.BytesIO(best_png))
                if im.mode != 'RGBA':
                    im = im.convert('RGBA')
                return im
    except Exception:
        pass
    return None

def extract_icon_best(target_path, lnk_path, out_png_path, icon_size=256):
    os.makedirs(os.path.dirname(os.path.abspath(out_png_path)), exist_ok=True)
    
    # 1. Native PE PNG
    if target_path and target_path.lower().endswith(('.exe', '.dll', '.ico')) and os.path.exists(target_path):
        im = extract_raw_pe_png(target_path)
        if im:
            if im.size != (icon_size, icon_size):
                im = im.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            im.save(out_png_path, 'PNG', optimize=True)
            return True
            
    # 2. Store / UWP assets
    if target_path and "windowsapps" in target_path.lower():
        parts = target_path.split(os.sep)
        pkg_dir = None
        for i, part in enumerate(parts):
            if "windowsapps" in part.lower() and i + 1 < len(parts):
                pkg_dir = os.sep.join(parts[:i + 2])
                break
        if pkg_dir:
            from rebuild_all_icons import extract_store_asset
            im = extract_store_asset(pkg_dir, icon_size)
            if im:
                im.save(out_png_path, 'PNG', optimize=True)
                return True
                
    # 3. PrivateExtractIconsW with GetDIBits
    if target_path and target_path.lower().endswith(('.exe', '.dll', '.ico')) and os.path.exists(target_path):
        for req_size in [256, 128, 48, 32]:
            try:
                hicon = wintypes.HICON()
                iid = wintypes.UINT()
                res = ctypes.windll.user32.PrivateExtractIconsW(target_path, 0, req_size, req_size,
                                                               ctypes.byref(hicon), ctypes.byref(iid), 1, 0)
                if res > 0 and hicon.value:
                    im = _hicon_to_image_hd(hicon.value, icon_size)
                    if im:
                        im.save(out_png_path, 'PNG', optimize=True)
                        return True
            except Exception:
                pass
                
    # 4. Shell ImageList Jumbo
    p_to_try = lnk_path if (lnk_path and os.path.exists(lnk_path)) else target_path
    if p_to_try and os.path.exists(p_to_try):
        try:
            sfi = SHFILEINFO()
            res = ctypes.windll.shell32.SHGetFileInfoW(p_to_try, 0, ctypes.byref(sfi), ctypes.sizeof(sfi), SHGFI_SYSICONINDEX)
            if res:
                iimage_list = wintypes.HANDLE()
                hr = ctypes.windll.shell32.SHGetImageList(SHIL_JUMBO, ctypes.byref(IID_IImageList), ctypes.byref(iimage_list))
                if hr == 0 and iimage_list.value:
                    hicon = ImageList_GetIcon(iimage_list, sfi.iIcon, 0)
                    if hicon:
                        im = _hicon_to_image_hd(hicon, icon_size)
                        if im:
                            im.save(out_png_path, 'PNG', optimize=True)
                            return True
        except Exception:
            pass
            
    return False
