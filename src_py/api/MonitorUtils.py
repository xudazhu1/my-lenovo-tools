import ctypes
from ctypes import wintypes
import win32con

user32 = ctypes.WinDLL("user32", use_last_error=True)

# --- 常量 ---
DM_DISPLAYFREQUENCY = 0x00400000
ENUM_CURRENT_SETTINGS = -1
CCHDEVICENAME = 32
CCHFORMNAME = 32
DISP_CHANGE_SUCCESSFUL = 0


# --- 结构体 ---
class DEVMODEW(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", wintypes.WCHAR * CCHDEVICENAME),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),

        ("dmPosition_x", wintypes.LONG),
        ("dmPosition_y", wintypes.LONG),
        ("dmDisplayOrientation", wintypes.DWORD),
        ("dmDisplayFixedOutput", wintypes.DWORD),

        ("dmColor", wintypes.SHORT),
        ("dmDuplex", wintypes.SHORT),
        ("dmYResolution", wintypes.SHORT),
        ("dmTTOption", wintypes.SHORT),
        ("dmCollate", wintypes.SHORT),
        ("dmFormName", wintypes.WCHAR * CCHFORMNAME),
        ("dmLogPixels", wintypes.WORD),
        ("dmBitsPerPel", wintypes.DWORD),
        ("dmPelsWidth", wintypes.DWORD),
        ("dmPelsHeight", wintypes.DWORD),
        ("dmDisplayFlags", wintypes.DWORD),
        ("dmDisplayFrequency", wintypes.DWORD),
        ("dmICMMethod", wintypes.DWORD),
        ("dmICMIntent", wintypes.DWORD),
        ("dmMediaType", wintypes.DWORD),
        ("dmDitherType", wintypes.DWORD),
        ("dmReserved1", wintypes.DWORD),
        ("dmReserved2", wintypes.DWORD),
        ("dmPanningWidth", wintypes.DWORD),
        ("dmPanningHeight", wintypes.DWORD),
    ]


class DISPLAY_DEVICEW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("DeviceName", wintypes.WCHAR * 32),
        ("DeviceString", wintypes.WCHAR * 128),
        ("StateFlags", wintypes.DWORD),
        ("DeviceID", wintypes.WCHAR * 128),
        ("DeviceKey", wintypes.WCHAR * 128),
    ]


# --- 函数声明 ---
user32.EnumDisplayDevicesW.restype = wintypes.BOOL
user32.EnumDisplayDevicesW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(DISPLAY_DEVICEW),
                                       wintypes.DWORD]

user32.EnumDisplaySettingsExW.restype = wintypes.BOOL
user32.EnumDisplaySettingsExW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(DEVMODEW), wintypes.DWORD]

user32.ChangeDisplaySettingsExW.restype = ctypes.c_long
user32.ChangeDisplaySettingsExW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(DEVMODEW), wintypes.HWND, wintypes.DWORD,
                                            ctypes.c_void_p]


# =========================
#   API 函数
# =========================

# 定义 DISPLAY_DEVICE 结构
class DISPLAY_DEVICE(ctypes.Structure):
    _fields_ = [
        ('cb', wintypes.DWORD),
        ('DeviceName', wintypes.WCHAR * 32),
        ('DeviceString', wintypes.WCHAR * 128),
        ('StateFlags', wintypes.DWORD),
        ('DeviceID', wintypes.WCHAR * 128),
        ('DeviceKey', wintypes.WCHAR * 128),
    ]


# 获取主显示器适配器信息
def get_primary_monitor_adapter():
    i = 0
    user32 = ctypes.windll.user32
    while True:
        device = DISPLAY_DEVICE()
        device.cb = ctypes.sizeof(DISPLAY_DEVICE)

        if not user32.EnumDisplayDevicesW(None, i, ctypes.byref(device), 0):
            break

        if device.StateFlags & win32con.DISPLAY_DEVICE_PRIMARY_DEVICE:
            # print(f"主显示器设备名: {device.DeviceName}")
            # print(f"描述信息（显卡名）: {device.DeviceString}")
            # print(f"设备ID: {device.DeviceID}")
            # print(f"设备Key: {device.DeviceKey}")
            return {
                "Name": device.DeviceName,
                "Adapter": device.DeviceString,
                "DeviceID": device.DeviceID,
                "DeviceKey": device.DeviceKey,
            }

        i += 1


def get_current_mode(device_name):
    """获取当前模式对象"""
    dm = DEVMODEW()
    dm.dmSize = ctypes.sizeof(DEVMODEW)
    ok = user32.EnumDisplaySettingsExW(device_name, ENUM_CURRENT_SETTINGS, ctypes.byref(dm), 0)
    return dm if ok else None


def set_refresh_rate(device_name, hz, persist=True):
    """保持分辨率不变，仅修改刷新率"""
    dm = get_current_mode(device_name)
    if not dm:
        raise RuntimeError("无法读取当前显示模式")
    dm.dmDisplayFrequency = int(hz)
    dm.dmFields |= DM_DISPLAYFREQUENCY
    flags = 1 if persist else 0  # 1 = CDS_UPDATEREGISTRY
    r = user32.ChangeDisplaySettingsExW(device_name, ctypes.byref(dm), None, flags, None)
    if r != DISP_CHANGE_SUCCESSFUL:
        raise RuntimeError(f"设置失败，返回码 {r}")
    return True

import win32api
import win32con

def get_current_refresh_rate(display=None):
    """
    获取当前显示器的刷新率
    :param display: 显示器设备名 (默认主显示器 \\\\.\\DISPLAY1)
    :return: 当前刷新率 (Hz)
    """
    if not display:
        display = get_primary_monitor_adapter().get("Name")
    devmode = win32api.EnumDisplaySettings(display, win32con.ENUM_CURRENT_SETTINGS)
    return devmode.DisplayFrequency


def get_supported_refresh_rates(display=None):
    """
    获取当前显示器支持的刷新率列表
    :param display: 显示器设备名 (默认主显示器 \\\\.\\DISPLAY1)
    :return: list[int] 刷新率列表
    """
    if not display:
        display = get_primary_monitor_adapter().get("Name")
    i = 0
    rates = set()
    while True:
        try:
            devmode = win32api.EnumDisplaySettings(display, i)
        except Exception:
            break
        rates.add(devmode.DisplayFrequency)
        i += 1
    return sorted(rates)


if __name__ == "__main__":
    print(get_current_refresh_rate(None))
    print(get_supported_refresh_rates(None))