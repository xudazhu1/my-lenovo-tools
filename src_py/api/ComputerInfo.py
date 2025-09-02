import socket
import psutil
import screen_brightness_control as sbc
from ctypes import cast, POINTER, windll, c_uint, sizeof, byref
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class ComputerInfo:
    def __init__(self):
        # 初始化音量接口
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

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
    def get_brightness(self):
        try:
            return sbc.get_brightness(display=0)[0]  # 主屏幕亮度
        except Exception as e:
            return f"Error: {e}"

    # 设置屏幕亮度 (0-100)
    def set_brightness(self, value: int):
        value = max(0, min(100, value))
        sbc.set_brightness(value, display=0)

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

    # 示例
    # pc.mute(True)        # 静音
    # pc.toggle_mute()     # 切换静音
    # pc.play_pause()      # 播放/暂停
    # pc.next_track()      # 下一曲
    # pc.prev_track()      # 上一曲
