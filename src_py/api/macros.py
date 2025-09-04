import json
import time
import threading
import psutil
import win32gui
import win32process
from pynput import keyboard as pynput_kb
from pynput import mouse as pm

from src_py.api import system

# ===================== 全局状态 =====================
running_flags = {}  # 宏运行状态
mouse_ctrl = pm.Controller()
keyboard_ctrl = pynput_kb.Controller()

# ===================== 执行动作 =====================
def perform_actions(actions, macro_name):
    i = 0
    while i < len(actions):
        if not running_flags.get(macro_name, False):
            break

        act = actions[i]

        # 等待
        if "wait" in act:
            time.sleep(act["wait"])

        # 键盘
        elif "keyboard" in act:
            key = act["keyboard"]
            hold = act.get("hold", 0.0005)
            try:
                keyboard_ctrl.press(key)
                time.sleep(hold)
                keyboard_ctrl.release(key)
            except Exception as e:
                print(f"[{macro_name}] 键盘动作错误: {e}")

        # 鼠标
        elif "mouse" in act:
            btn = act["mouse"]
            hold = act.get("hold", 0.0005)
            amount = act.get("amount", 1)
            direction = act.get("direction", "vertical")

            if btn in ["left","right","middle","x1","x2"]:
                btn_map = {
                    "left": pm.Button.left,
                    "right": pm.Button.right,
                    "middle": pm.Button.middle,
                    "x1": pm.Button.x1,
                    "x2": pm.Button.x2
                }
                try:
                    mouse_ctrl.press(btn_map[btn])
                    time.sleep(hold)
                    mouse_ctrl.release(btn_map[btn])
                except Exception as e:
                    print(f"[{macro_name}] 鼠标动作错误: {e}")
            elif btn == "wheel":
                if direction == "vertical":
                    mouse_ctrl.scroll(0, amount)
                elif direction == "horizontal":
                    mouse_ctrl.scroll(amount, 0)

        # repeat
        elif "repeat" in act:
            n = act["repeat"]["count"]
            sub = act["repeat"]["action"]
            for _ in range(n):
                if not running_flags.get(macro_name, False):
                    break
                perform_actions([sub], macro_name)

        # loop
        elif "loop" in act:
            n = act["loop"]["count"]
            sub_actions = act["loop"]["actions"]
            count = 0
            while running_flags.get(macro_name, False) and (n == 0 or count < n):
                perform_actions(sub_actions, macro_name)
                count += 1

        i += 1


def is_program_foreground(programs):
    """
    判断目标程序是否在前台（兼容普通窗口和大部分全屏程序）
    programs: ["notepad.exe", "game.exe"]
    """
    try:
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            return False
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc = psutil.Process(pid)
        name = proc.name().lower()
        return name in [p.lower() for p in programs]
    except Exception:
        return False


# ===================== 宏管理 =====================
def is_program_running(programs):
    # procs = [p.name().lower() for p in psutil.process_iter(["name"])]
    # return any(prog.lower() in procs for prog in programs)
    return is_program_foreground(programs)


def run_macro(macro):
    name = macro["name"]
    actions = macro["actions"]
    stop_key = macro.get("stop_key")

    if not is_program_running(macro["programs"]):
        print(f"[{name}] 目标程序未运行，宏未执行。")
        return

    print(f"[{name}] 宏启动")
    running_flags[name] = True

    # 停止键
    if stop_key:
        def stop_cb():
            stop_macro(name)
        pynput_kb.GlobalHotKeys({stop_key: stop_cb}).start()

    perform_actions(actions, name)
    print(f"[{name}] 宏结束")
    running_flags[name] = False

# ===================== 注册宏 =====================
def register_macros(config):
    for macro in config["macros"]:
        hotkey_arr = macro["hotkey"]
        name = macro["name"]

        # 通用回调
        def handler(m=macro):
            if running_flags.get(m["name"], False):
                print(f"[{m['name']}] 已在运行中")
            else:
                threading.Thread(target=run_macro, args=(m,), daemon=True).start()

        # 最新版的话 hotkey 变成一个数组, 可以有 多个热键 触发同一个宏脚本, 所以需要遍历
        for hotkey in hotkey_arr:
            # 键盘+鼠标组合 触发不灵敏 最好不用~
            if "mouse" in hotkey.lower() and "+" in hotkey:
                parts = hotkey.split("+")
                mouse_btn = None
                keys = []
                for p in parts:
                    p = p.strip().lower()
                    if p.startswith("mouse:"):
                        mouse_btn = p.split(":")[1]
                    else:
                        keys.append(p)
                if mouse_btn:
                    def combo_handler(m=macro, keys=keys, btn=mouse_btn):
                        try:
                            if all(pynput_kb.Controller().pressed(k) for k in keys):
                                if pm.Controller().pressed(btn):
                                    threading.Thread(target=run_macro, args=(m,), daemon=True).start()
                        except Exception:
                            pass
                    # 注意 GlobalHotKeys 只支持键盘部分
                    keyboard_hotkey = "+".join([f"<{k}>" if k in ["ctrl","alt","shift","cmd"] else k for k in keys])
                    pynput_kb.GlobalHotKeys({keyboard_hotkey: combo_handler}).start()
                    print(f"[{name}] 已注册组合热键: {hotkey}")

            # 纯鼠标热键
            elif hotkey.lower().startswith("mouse:"):
                btn = hotkey.split(":")[1]
                # 用 Listener 实例注册
                pm.Listener(on_click=lambda x, y, button, pressed: handler() if pressed and button.name == btn else None).start()
                print(f"[{name}] 已注册鼠标热键: {hotkey}")

            # 纯键盘热键
            else:
                # formatted_hotkey = format_hotkey(hotkey)
                pynput_kb.GlobalHotKeys({hotkey: handler}).start()
                print(f"[{name}] 已注册键盘热键: {hotkey}")

def stop_macro(name):
    running_flags[name] = False
    print(f"[{name}] 已请求停止")

def unregister_macros(config):
    running_flags.clear()
    print("所有宏已取消注册")

def my_on_press(event):
    print(event)


config_path = system.get_path("..", "..", "macros.config.json")

# ===================== 主程序 =====================
if __name__ == "__main__":
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    register_macros(config)
    print("宏系统已启动，按 Ctrl+C 退出")
    listener = pynput_kb.Listener(on_press=my_on_press)
    listener.start()  # 开始监听线程
    listener.join()  # 等待线程结束（阻塞）
