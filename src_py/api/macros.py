import importlib
import json
import multiprocessing
import os
import signal
import threading
import time
import traceback

import psutil
import win32gui
import win32process
from pynput import keyboard as pynput_kb
from pynput import mouse as pm
import src_py.api.util.keyMap as keyMapUtil
from src_py.api import system

# ===================== 全局状态 =====================
mouse_ctrl = pm.Controller()
keyboard_ctrl = pynput_kb.Controller()

# noinspection PyTypeChecker
ctrl_map = {chr(i): chr(96 + i) for i in range(1, 27)}

# 预加载常用模块以减少子进程初始化时间
PRELOAD_MODULES = ['time', 'json', 'psutil', 'win32gui', 'win32process']
for module in PRELOAD_MODULES:
    importlib.import_module(module)


# ===================== 执行动作 =====================
def perform_actions(actions, macro_name, task_pid_dict_val, macros_press_map_val):
    # 最新要执行的pid
    lasted_pid = task_pid_dict_val[macro_name].get(macro_name, -1)
    now_pid = os.getpid()
    # print(f"lasted pid: {lasted_pid}; now pid: {now_pid}")
    # 如果最新的pid和现在的pid不相等 说明该任务已被丢弃 主动停止执行
    if now_pid != lasted_pid:
        return
    i = 0
    while i < len(actions):
        # 最新要执行的pid
        lasted_pid = task_pid_dict_val[macro_name].get(macro_name, -1)
        now_pid = os.getpid()
        # 如果最新的pid和现在的pid不相等 说明该任务已被丢弃 主动停止执行
        if now_pid != lasted_pid:
            return
        act = actions[i]
        # 等待
        if "wait" in act:
            time.sleep(act["wait"])
        # 键盘
        elif "keyboard_release" in act:
            key = act["keyboard_release"]
            key_obj = None
            # 如果 key 是 <space> 格式 那就转化为 Key 对象
            if "<" in key and ">" in key:
                key_obj = keyMapUtil.str_to_key(key)
            try:
                # 标记是宏按下的按键
                macros_press_map_val[key] = 2
                keyboard_ctrl.release(key_obj or key) # 优先传入 key_obj
            except Exception as e:
                print(f"[{macro_name}] 键盘动作错误: {e}")
        # 键盘
        elif "keyboard_press" in act:
            key = act["keyboard_press"]
            key_obj = None
            # 如果 key 是 <space> 格式 那就转化为 Key 对象
            if "<" in key and ">" in key:
                key_obj = keyMapUtil.str_to_key(key)
            try:
                # 标记是宏按下的按键
                macros_press_map_val[key] = 1
                keyboard_ctrl.press(key_obj or key)
            except Exception as e:
                print(f"[{macro_name}] 键盘动作错误: {e}")
        # 键盘
        elif "keyboard" in act:
            key = act["keyboard"]
            key_obj = None
            # 如果 key 是 <space> 格式 那就转化为 Key 对象
            if "<" in key and ">" in key:
                key_obj = keyMapUtil.str_to_key(key)
            hold = act.get("hold", 0.0005)
            try:
                # 标记是宏按下的按键
                macros_press_map_val[key] = 1
                # print("macros_press_map_val状态: " + key + '==1')
                keyboard_ctrl.press(key_obj or key)
                time.sleep(hold)
                macros_press_map_val[key] = 2
                keyboard_ctrl.release(key_obj or key)
                # 标记是宏按下的按键
                # print("macros_press_map_val状态: " + key + '==2')

            except Exception as e:
                print(f"[{macro_name}] 键盘动作错误: {e}")
        # 鼠标
        elif "mouse" in act:
            btn = act["mouse"]
            hold = act.get("hold", 0.005)
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
                # 最新要执行的pid
                lasted_pid = task_pid_dict_val[macro_name].get(macro_name, -1)
                now_pid = os.getpid()
                # 如果最新的pid和现在的pid不相等 说明该任务已被丢弃 主动停止执行
                if now_pid != lasted_pid:
                    return
                # if not running_flags.get(macro_name, False):
                #     break
                perform_actions([sub], macro_name, task_pid_dict_val, macros_press_map_val)

        # loop
        elif "loop" in act:
            n = act["loop"]["count"]
            sub_actions = act["loop"]["actions"]
            count = 0
            # while running_flags.get(macro_name, False) and (n == 0 or count < n):
            while n == 0 or count < n:
                # 最新要执行的pid
                lasted_pid = task_pid_dict_val[macro_name].get(macro_name, -1)
                now_pid = os.getpid()
                # 如果最新的pid和现在的pid不相等 说明该任务已被丢弃 主动停止执行
                if now_pid != lasted_pid:
                    return
                perform_actions(sub_actions, macro_name, task_pid_dict_val, macros_press_map_val)
                count += 1

        i += 1


def is_program_foreground(programs):
    """
    判断目标程序是否在前台（兼容普通窗口和大部分全屏程序）
    programs: ["notepad.exe", "game.exe"]
    """
    # noinspection PyBroadException
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
    return is_program_foreground(programs)



class Macro:
    def __init__(self, manager_temp, task_pid_dict_temp, macros_press_map_temp):
        self.task_pid_dict_val = task_pid_dict_temp
        self.macros_press_map_val = macros_press_map_temp
        self.config_path = system.get_path("..", "..", "macros.config.json")
        # 记录各个按键的按下状态 key 为 按键的 name value 是 是否按下
        self.my_key_map = {}
        self.hotkey_macros_map = {}
        self.stop_key_macros_map = {}
        self.multiprocessing_map = {} # 存储 正在运行的宏的线程对象的
        self.config = {}
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.listener = pynput_kb.Listener(
            on_press=self._my_on_press,
            on_release=self._my_on_release,
        )
        # 创建进程池以减少进程创建开销
        self.process_pool = multiprocessing.Pool(processes=len(self.config.get("macros", [])))
        # 为每个 macro创建一个key 为name的共享dict
        for macro in self.config.get("macros", []):
            name = macro["name"]
            self.task_pid_dict_val[name] = manager_temp.dict()

    def _register_macro(self):
        # 这里做单纯的 config 格式化逻辑 挑出所有 macros 的 关系
        # 关系1 hotkey: [macro] 通过触发的hotkey去寻找 macro 通过 macro 去寻找programs 然后判断现在这个program在不在前台
        macros = self.config.get("macros", [])
        for macro in macros:
            for hotkey in macro["hotkey"]:
                # 如果是空 先 new list
                if not self.hotkey_macros_map.get(hotkey, False):
                    self.hotkey_macros_map[hotkey] = []
                self.hotkey_macros_map[hotkey].append(macro)
            # 配置停止映射
            if not self.stop_key_macros_map.get(macro["stop_key"], False):
                self.stop_key_macros_map[macro["stop_key"]] = []
            self.stop_key_macros_map[macro["stop_key"]].append(macro)
        # print(self.config)

    def update_config(self, config_temp):
        with open(self.config_path, "w", encoding="utf-8") as f:
            # noinspection PyTypeChecker
            json.dump(config_temp, f, indent=4)
            self.config = config_temp

    def get_config(self):
        return self.config

    def start_Macro(self):
        # 整理注册关系
        self._register_macro()
        # 开始监听
        self.listener.start()
        print("宏系统已启动...")
    def stop_Macro(self):
        self.listener.stop()
        print("宏系统已停止!!!")

    def _my_on_press(self, event):
        # print("my_on_press 按下 = ")
        name = ''
        if isinstance(event, pynput_kb.Key):
            name = f"<{event.name}>"
        else:
            name = event.char
            if name in ctrl_map:
                name = ctrl_map[name]
        print(f"my_on_press 按下 = {name}")
        self.my_key_map[name] = True
        # 判断name是不是已经按下
        if not self.macros_press_map_val.get(name, False):
            # self.handler_event(name)
            # 在新线程中执行长时间任务
            thread = threading.Thread(target=self.handler_event, args=(name,))
            thread.daemon = True  # 设置为守护线程，确保程序退出时线程也会结束
            thread.start()
            # print("假装从犯on_press调用handler_event")


    def _my_on_release(self, event):
        # print("my_on_release 释放 = ")
        name = ''
        if isinstance(event, pynput_kb.Key):
            name = f"<{event.name}>"
        else:
            name = event.char
            if name in ctrl_map:
                name = ctrl_map[name]
        print(f"_my_on_release 抬起 = {name}")
        self.my_key_map[name] = False
        # 判断name是不是已经按下
        if self.macros_press_map_val.get(name, False):
            # 由我取消此标记
            self.macros_press_map_val[name] = 0
            # print("由我取消此标记 macros_press_map_val." + name + "=0")

    def handler_event(self, name):
        # 当所有按键抬起 或者没有任何宏运行的时候 主动终止循环?
        all_key_released = True
        for e in self.my_key_map:
            if not self.my_key_map[e]:
                all_key_released = False
            print(f"hotkey_macros_map. {e} = {self.my_key_map[e]}")
        print(f"handler_event: {name}")


        # 根据 所有的 hotkey <space>+f 直接判断 是否触发?
        for hotkey in self.hotkey_macros_map.keys():

            all_key_pressed = True
            for key in hotkey.split('+'):
                if not self.my_key_map.get(key, False):
                    all_key_pressed = False
            # 如果所有的key都被按下
            if all_key_pressed:
                for macro in self.hotkey_macros_map[hotkey]:
                    # 寻找要触发的宏!
                    print("尝试触发宏: " + macro["name"])
                    if not is_program_running(macro["programs"]):
                        print(f"[{name}] 目标程序未运行，跳过宏执行!。")
                        continue

                    # 使用进程池异步执行，减少启动延迟
                    self.multiprocessing_map[macro["name"]] = self.process_pool.apply_async(
                        run_macro, (macro,self.task_pid_dict_val, self.macros_press_map_val)
                    )
                    print(f"主进程调用了start = {time.time()}")
        # 判断是否停止?
        for stop_key in self.stop_key_macros_map.keys():
            if self.my_key_map.get(stop_key, False):
                macros = self.stop_key_macros_map[stop_key]
                for macro in macros:
                    if self.multiprocessing_map.get(macro["name"], None):
                        print("发现 stop_key, 主动停止宏: " + macro["name"])
                        thread = threading.Thread(target=self.stop_macro, args=(macro["name"],))
                        thread.daemon = True  # 设置为守护线程，确保程序退出时线程也会结束
                        thread.start()
                        self.multiprocessing_map[macro["name"]] = None



    def stop_macro(self, macro_name):

        now = time.time()
        print("尝试停止任务?")
        try:
            self.task_pid_dict_val[macro_name][macro_name] = -1
            for key in  self.task_pid_dict_val[macro_name].keys():
                print(f"key: {key}, value: {self.task_pid_dict_val[macro_name][key]}")
            print(f"停止完成: {macro_name}")
        except KeyError:
            print(f"尝试停止任务错误 KeyError: {self.task_pid_dict_val.get(macro_name, False)}")


def run_macro(macro, task_pid_dict_val, macros_press_map_val):
    print(f"run_macro: {time.time()}")
    # 设置信号处理器
    def handle_signal(signum, frame):
        signal_time = time.time()
        print(f"[{time.time()}] 进程 {os.getpid()} 接收到信号 {signum}，正在退出")
        raise SystemExit(f"[{time.time()}] 由信号终止，信号响应延迟: {time.time() - signal_time:.3f}秒")

    signal.signal(signal.SIGTERM, handle_signal)

    # 将当前进程的PID存入字典，键为宏的名称
    # if not task_pid_dict_val.get(macro["name"], False):
    #     task_pid_dict_val[macro['name']] = {}
    # 存入时间戳-pid
    time_str = str(time.time())
    task_pid_dict_val[macro['name']][time_str] = os.getpid()
    print(f"[{time.time()}] 任务 {macro['name']} 启动，进程PID: {os.getpid()}")
    # 记录最后一个子进程的pid 用于终止标记 ?
    task_pid_dict_val[macro['name']][macro['name']] = os.getpid()

    try:
        print(f"子进程开始执行! = {time.time()}")
        name = macro["name"]
        actions = macro["actions"]

        if not is_program_running(macro["programs"]):
            print(f"[{name}] 目标程序未运行，宏未执行。")
            return

        print(f"[{name}] 宏启动")
        perform_actions(actions, name, task_pid_dict_val, macros_press_map_val)
        print(f"[{name}] 宏结束")
    except SystemExit as e:
        print(f"[{time.time()}] 任务 {macro['name']} 被信号中断: {e}")
    except Exception as e:
        traceback.print_exc()
        print(e)
    finally:
        # 任务完成后，从字典中删除PID
        if task_pid_dict_val[macro['name']].get(time_str, False):
            if psutil.pid_exists(task_pid_dict_val[macro['name']][time_str]):
                print(f"主动删除pid === {task_pid_dict_val[macro['name']][time_str]}")
                del task_pid_dict_val[macro['name']][time_str]


# ===================== 主程序 =====================
if __name__ == "__main__":
    manager = multiprocessing.Manager()
    task_pid_dict = manager.dict()
    macros_press_map = manager.dict()
    mac = Macro(manager, task_pid_dict, macros_press_map)
    mac.start_Macro()
    # 等待线程结束（阻塞）
    while True:
        time.sleep(10)