import ctypes

def set_brightness(value):
    """
    设置屏幕亮度。
    :param value: 亮度值，范围从0（最低）到255（最高）。
    """
    # ctypes.windll.kernel32.SetThreadExecutionState(0)  # 防止系统休眠
    # ctypes.windll.kernel32.SetThreadExecutionState(2)  # 重新启用系统休眠
    # ctypes.windll.kernel32.SetThreadExecutionState(0x80000)  # 防止系统休眠
    GUID = ctypes.GUID.from_string("540C77A6-48FC-4CC9-8D59-EDAFA7DF21D2")
    # ctypes.windll.LoadLibrary("setupapi.dll")
    # ctypes.windll.kernel32.SetThreadExecutionState(0x80000)  # 防止系统休眠
    # ctypes.windll.kernel32.SetThreadExecutionState(2)  # 重新启用系统休眠
    # ctypes.windll.kernel32.SetThreadExecutionState(0)  # 防止系统休眠
    # ctypes.windll.powrprof.SetSuspendState(False, False, False)  # 唤醒系统（如果有必要）
    handle = ctypes.windll.powrprof.PowerRegisterSuspendResumeNotification(0, ctypes.byref(GUID), None)
    ctypes.windll.powrprof.PowerSetRequest(ctypes.c_void_p(handle), ctypes.c_ulong(0x80000000), None)  # 设置亮度请求
    ctypes.windll.powrprof.PowerSetRequest(ctypes.c_void_p(handle), ctypes.c_ulong(value), None)  # 应用亮度值
    # ctypes.windll.powrprof.PowerUnregisterSuspendResumeNotification(ctypes.c_void_p(handle))  # 注销通知

# 使用示例
set_brightness(128)  # 设置亮度为128（中等亮度）
