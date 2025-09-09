import clr
import sys
import os
import pythoncom

import System
# from System import String
from System.Reflection import BindingFlags

script_dir = os.path.dirname(os.path.abspath(__file__))
# 加载 DLL
dll_path = os.path.join("config", "dll", "SmartEngine", "1.0.70.10091", "Views", "UIKeypadBacklight.dll")

keyboard_status_map = {
    "0": "不支持!",
    "1": "OFF",
    "2": "LOW",
    "3": "HIGH",
    "4": "AUTO"
}


def set_status_int(status_int):
    if status_int == 0:
        return 0
    return set_status(keyboard_status_map.get(str(status_int)))


def set_status(str_status):
    # 初始化为 STA 模式
    pythoncom.CoInitialize()  # 必须加！
    clr.AddReference(dll_path)

    # 获取类型
    from UIKeypadBacklight import UCKeypadBacklight

    # 获取单例对象：UCKeypadBacklight.Instance
    instance = UCKeypadBacklight.get_Instance()

    # 获取私有字段 "KbdBackLightVM"
    field_info = instance.GetType().GetField(
        "KbdBackLightVM",
        BindingFlags.NonPublic | BindingFlags.Instance
    )

    kbdBackLightVM = field_info.GetValue(instance)

    # 调用 SetKbdledMode("HIGH") KbdBackLightModel.EnumKbdBackLightStatus
    enum_type_str = "UIKeypadBacklight.Model.KbdBackLightModel+EnumKbdBackLightStatus, UIKeypadBacklight"
    enum_type = System.Type.GetType(enum_type_str)
    mode_new = System.Enum.Parse(enum_type, str_status)

    result = kbdBackLightVM.SetKbdledMode(mode_new)
    print(f"SetKbdledMode 返回值: {result}")

    # 可选：调用 GetPluginStatus 方法
    get_plugin_status = instance.GetType().GetMethod("GetPluginStatus")
    status = get_plugin_status.Invoke(instance, None)
    print(f"KeyBoard插件状态: {status}")
    return status


def get_status():
    # 初始化为 STA 模式
    pythoncom.CoInitialize()  # 必须加！
    clr.AddReference(dll_path)

    # 获取类型
    from UIKeypadBacklight import UCKeypadBacklight
    # 获取单例对象：UCKeypadBacklight.Instance
    instance = UCKeypadBacklight.get_Instance()
    # 可选：调用 GetPluginStatus 方法
    get_plugin_status = instance.GetType().GetMethod("GetPluginStatus")
    status = get_plugin_status.Invoke(instance, None)
    print(f"KeyBoard插件状态: {status}")
    return int(status)
