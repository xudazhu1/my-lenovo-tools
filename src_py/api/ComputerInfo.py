import ctypes
import socket
import subprocess

import psutil
import pythoncom
import screen_brightness_control as sbc
from ctypes import cast, POINTER, windll, c_uint, sizeof, byref

import win32com
import wmi
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from win32com.client import VARIANT


class ComputerInfo:
    def __init__(self):
        # 初始化音量接口
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        # 连接到 root\wmi 命名空间
        self.wmi_interface = wmi.WMI(namespace='root\\wmi')

    # 获取计算机名
    def get_computer_name(self):
        return socket.gethostname()

    # 获取电池信息
    def get_battery(self):
        battery = psutil.sensors_battery()
        if battery is None:
            return {
                "status": "No battery detected",
                "exist": False,
            }
        return {
            "status": "battery detected",
            "exist": True,
            "percent": battery.percent,
            "plugged": battery.power_plugged,
            "time_left": battery.secsleft
        }

    # 获取屏幕亮度
    def get_brightness_old(self):
        try:
            val2 = sbc.get_brightness()
            print(val2)
            return sbc.get_brightness()[0]  # 主屏幕亮度
        except Exception as e:
            return f"Error: {e}"

    # 设置屏幕亮度 (0-100)
    def set_brightness_old(self, value: int):
        value = max(0, min(100, value))
        sbc.set_brightness(value)

    # 获取屏幕亮度 新的 用于独显模式下使用 核显模式应该也有效果
    def get_brightness(self) -> int:
        """获取当前屏幕亮度 (0-100)"""
        cmd = [
            "powershell",
            "-NoProfile",  # 不加载用户配置，加快执行速度
            "-WindowStyle", "Hidden",  # 隐藏窗口
            "-Command",
            "(Get-WmiObject -Namespace root\\wmi -Class WmiMonitorBrightness).CurrentBrightness"
        ]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW  # 关键参数
            )
            return int(result.stdout.strip())
        except Exception as e:
            return self.get_brightness_old()

    def set_brightness(self, value: int) -> bool:
        """通过 WMI 调整亮度（0-100），避免 PowerShell"""
        value = max(0, min(100, int(value)))

        # 连接到 root\wmi
        loc = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        svc = loc.ConnectServer(".", "root\\wmi")

        # 只对内置屏幕有效；外接显示器通常不支持这个类
        items = svc.ExecQuery("SELECT * FROM WmiMonitorBrightnessMethods")
        ok = False

        for obj in items:
            # 关键：从对象的 Methods_ 里拿到方法的入参模板，再赋值
            in_params = obj.Methods_("WmiSetBrightness").InParameters.SpawnInstance_()
            in_params.Properties_.Item("Timeout").Value = 1  # UINT32
            in_params.Properties_.Item("Brightness").Value = value  # UINT8 (0-100)

            # 用 ExecMethod_ 调用（不要直接 obj.WmiSetBrightness(...)）
            obj.ExecMethod_("WmiSetBrightness", in_params)
            ok = True

        return ok


    # 设置屏幕亮度 (0-100) 新的 解决独显模式下不生效的问题
    def set_brightness_old2(self, value: int):
        """设置屏幕亮度 (0-100)"""
        cmd = [
            "powershell",
            "-NoProfile",  # 不加载用户配置，加快执行速度
            "-WindowStyle", "Hidden",  # 隐藏窗口
            "-Command",
            f"$methods = Get-WmiObject -Namespace root\\wmi -Class WmiMonitorBrightnessMethods; "
            f"$methods.WmiSetBrightness(1, {value})"
        ]
        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW  # 关键参数
            )
        except Exception as e:
            return self.set_brightness_old(value)

    # 获取音量 (0.0 - 1.0)
    def get_volume(self):
        return self.volume.GetMasterVolumeLevelScalar()

    # 设置音量 (0.0 - 1.0)
    def set_volume(self, value: float):
        value = max(0.0, min(1.0, value))
        self.volume.SetMasterVolumeLevelScalar(value, None)

    # 静音开关
    def mute(self, status: bool):
        self.volume.SetMute(status, None)

    # 切换静音
    def toggle_mute(self):
        current = bool(self.volume.GetMute())
        self.volume.SetMute(not current, None)

    # 获取是否静音
    def is_muted(self):
        return bool(self.volume.GetMute())

    # ===== 多媒体按键控制 =====
    # 模拟键盘输入 (虚拟键码)
    def _send_vk(self, key_code):
        user32 = windll.user32
        user32.keybd_event(key_code, 0, 0, 0)        # 按下
        user32.keybd_event(key_code, 0, 2, 0)        # 松开

    def play_pause(self):
        self._send_vk(0xB3)  # VK_MEDIA_PLAY_PAUSE

    def next_track(self):
        self._send_vk(0xB0)  # VK_MEDIA_NEXT_TRACK

    def prev_track(self):
        self._send_vk(0xB1)  # VK_MEDIA_PREV_TRACK


if __name__ == "__main__":
    pc = ComputerInfo()
    print("电脑名:", pc.get_computer_name())
    print("电池信息:", pc.get_battery())
    print("亮度:", pc.get_brightness())
    print("音量:", pc.get_volume())
    print("是否静音:", pc.is_muted())

    pc.set_brightness(83)

    # 示例
    # pc.mute(True)        # 静音
    # pc.toggle_mute()     # 切换静音
    # pc.play_pause()      # 播放/暂停
    # pc.next_track()      # 下一曲
    # pc.prev_track()      # 上一曲
