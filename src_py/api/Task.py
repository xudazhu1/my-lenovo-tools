import os
import json
import time
import psutil
import pythoncom
import wmi
import threading
import atexit
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from collections import defaultdict


# ------------------ 动作函数 ------------------
def func_1():
    print(f"[{datetime.now()}] 执行 func_1 (延时任务)")


def func_2():
    print(f"[{datetime.now()}] 执行 func_2 (cron任务)")


def func_3(event_type):
    print(f"[{datetime.now()}] 执行 func_3 (电源事件: {event_type})")


def func_4(process_name):
    print(f"[{datetime.now()}] 执行 func_4 (检测到{process_name}启动)")


def func_5(process_name):
    print(f"[{datetime.now()}] 执行 func_5 (检测到{process_name}终止)")


# ------------------ 事件监听器 ------------------
class EventListener:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventListener, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.power_listener_started = False
            self.process_listener_started = False
            self.power_handlers = defaultdict(list)
            self.process_start_handlers = defaultdict(list)
            self.process_stop_handlers = defaultdict(list)
            self._running = False
            self._initialized = True

    def start(self):
        """启动事件监听器"""
        if not self._running:
            self._running = True
            self._ensure_power_listener()
            self._ensure_process_listener()
            print("事件监听器已启动")

    def stop(self):
        """停止事件监听器"""
        self._running = False
        # 重置监听器状态
        self.power_listener_started = False
        self.process_listener_started = False
        print("事件监听器已停止")

    def is_running(self):
        """检查事件监听器是否运行中"""
        return self._running

    def clear_handlers(self):
        """清除所有处理器"""
        self.power_handlers.clear()
        self.process_start_handlers.clear()
        self.process_stop_handlers.clear()

    def register_power_handler(self, event_type, handler):
        """注册电源事件处理器"""
        self.power_handlers[event_type].append(handler)
        self._ensure_power_listener()

    def register_process_start_handler(self, process_name, handler):
        """注册进程启动事件处理器"""
        self.process_start_handlers[process_name].append(handler)
        self._ensure_process_listener()

    def register_process_stop_handler(self, process_name, handler):
        """注册进程终止事件处理器"""
        self.process_stop_handlers[process_name].append(handler)
        self._ensure_process_listener()

    def _ensure_power_listener(self):
        """确保电源事件监听器已启动"""
        if not self.power_listener_started and self.power_handlers and self._running:
            self._start_power_listener()
            self.power_listener_started = True

    def _ensure_process_listener(self):
        """确保进程事件监听器已启动"""
        if not self.process_listener_started and (
                self.process_start_handlers or self.process_stop_handlers) and self._running:
            self._start_process_listener()
            self.process_listener_started = True

    def _start_power_listener(self):
        """启动电源事件监听器"""

        def power_listener():
            pythoncom.CoInitialize()
            c = wmi.WMI()
            watcher = c.Win32_PowerManagementEvent.watch_for()
            while self._running:
                try:
                    event = watcher()
                    event_type = event.EventType
                    if event_type == 10:
                        for handler in self.power_handlers.get("plugged", []):
                            handler("AC Power Plugged")
                    elif event_type == 11:
                        for handler in self.power_handlers.get("unplugged", []):
                            handler("AC Power Unplugged")
                except Exception as e:
                    print(f"电源事件监听错误: {e}")
                    time.sleep(5)

        threading.Thread(target=power_listener, daemon=True).start()

    def _start_process_listener(self):
        """启动进程事件监听器"""

        def process_watcher():
            # 初始进程列表
            current_processes = {p.pid: p.name() for p in psutil.process_iter(['pid', 'name'])}

            while self._running:
                time.sleep(0.5)  # 减少轮询频率

                try:
                    # 获取当前进程列表
                    new_processes = {p.pid: p.name() for p in psutil.process_iter(['pid', 'name'])}

                    # 检测新进程 (启动)
                    started_pids = set(new_processes.keys()) - set(current_processes.keys())
                    for pid in started_pids:
                        process_name = new_processes[pid]
                        if process_name in self.process_start_handlers:
                            for handler in self.process_start_handlers[process_name]:
                                handler(process_name)

                    # 检测终止的进程
                    ended_pids = set(current_processes.keys()) - set(new_processes.keys())
                    for pid in ended_pids:
                        process_name = current_processes[pid]
                        if process_name in self.process_stop_handlers:
                            for handler in self.process_stop_handlers[process_name]:
                                handler(process_name)

                    # 更新当前进程列表
                    current_processes = new_processes

                except Exception as e:
                    print(f"进程监控错误: {e}")
                    time.sleep(5)

        threading.Thread(target=process_watcher, daemon=True).start()


# ------------------ 管理器 ------------------
class TaskManager:
    def __init__(self):
        self.scheduler = None
        self.triggers = {}
        self.actions = {}
        self.relations = {}
        self.event_listener = EventListener()
        self._running = False
        atexit.register(self._cleanup)

    def _cleanup(self):
        """清理资源"""
        if self._running:
            self.stop()

    def _create_scheduler(self):
        """创建新的调度器实例"""
        if self.scheduler and not self.scheduler.running:
            self.scheduler = None

        if self.scheduler is None:
            self.scheduler = BackgroundScheduler(jobstores={'default': MemoryJobStore()})
        return self.scheduler

    def load_config(self):
        """加载配置文件"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            with open(os.path.join(script_dir, "config", "triggers.json"), "r", encoding="utf-8") as f:
                self.triggers = json.load(f)
            with open(os.path.join(script_dir, "config", "actions.json"), "r", encoding="utf-8") as f:
                self.actions = json.load(f)
            with open(os.path.join(script_dir, "config", "relations.json"), "r", encoding="utf-8") as f:
                self.relations = json.load(f)
            return True
        except Exception as e:
            print(f"加载配置失败: {e}")
            return False

    def save_config(self):
        """保存配置文件"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            with open(os.path.join(script_dir, "config", "triggers.json"), "w", encoding="utf-8") as f:
                json.dump(self.triggers, f, ensure_ascii=False, indent=2)
            with open(os.path.join(script_dir, "config", "actions.json"), "w", encoding="utf-8") as f:
                json.dump(self.actions, f, ensure_ascii=False, indent=2)
            with open(os.path.join(script_dir, "config", "relations.json"), "w", encoding="utf-8") as f:
                json.dump(self.relations, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def get_config(self):
        """获取当前配置"""
        return {
            "triggers": self.triggers,
            "actions": self.actions,
            "relations": self.relations
        }

    def update_config(self, triggers=None, actions=None, relations=None):
        """更新配置"""
        if triggers is not None:
            self.triggers = triggers
        if actions is not None:
            self.actions = actions
        if relations is not None:
            self.relations = relations

        # 如果正在运行，重新启动以应用新配置
        if self._running:
            self.restart()

        return True

    def start(self):
        """启动任务管理器"""
        if self._running:
            print("任务管理器已在运行中")
            return False

        if not self.load_config():
            print("配置加载失败，无法启动")
            return False

        try:
            # 创建新的调度器实例
            self._create_scheduler()
            self.scheduler.start()
            self._register_triggers()
            self.event_listener.start()
            self._running = True
            print("任务调度器已启动")
            return True
        except Exception as e:
            print(f"启动失败: {e}")
            return False

    def stop(self):
        """停止任务管理器"""
        if not self._running:
            print("任务管理器未运行")
            return False

        try:
            # 停止调度器
            if self.scheduler and self.scheduler.running:
                self.scheduler.shutdown(wait=False)

            # 停止事件监听器
            self.event_listener.stop()
            self.event_listener.clear_handlers()

            self._running = False
            print("任务调度器已停止")
            return True
        except Exception as e:
            print(f"停止失败: {e}")
            return False

    def restart(self):
        """重启任务管理器"""
        if self._running:
            self.stop()
        return self.start()

    def is_running(self):
        """检查任务管理器是否运行中"""
        return self._running

    def _register_triggers(self):
        """注册所有触发器"""
        # 清除所有现有作业
        if self.scheduler.running:
            self.scheduler.remove_all_jobs()

        for trig in self.triggers:
            trig_id = trig["id"]
            trig_name = trig["name"]
            trig_type = trig["type"]

            if trig_type == "delay":
                run_time = datetime.now() + timedelta(**trig["params"])
                self.scheduler.add_job(
                    self._run_actions, "date",
                    run_date=run_time, args=[trig_id], id=trig_id
                )

            elif trig_type == "cron":
                self.scheduler.add_job(
                    self._run_actions, "cron",
                    args=[trig_id], id=trig_id, **trig["params"]
                )

            elif trig_type == "power":
                self._register_power_event(trig_id, trig.get("params", {}))

            elif trig_type == "process_start":
                self._register_process_start_monitor(trig_id, trig.get("params", {}))

            elif trig_type == "process_stop":
                self._register_process_stop_monitor(trig_id, trig.get("params", {}))

    def _run_actions(self, trig_id, *args):
        """执行触发器对应的动作"""
        for rel in self.relations:
            if rel["trigger_id"] == trig_id:
                action_id = rel["action_id"]
                # action_info = self.actions[action_id]
                action_info = {}
                # 查询符合action_id的动作
                for action in self.actions:
                    if action["id"] == action_id:
                        action_info = action
                        break
                func_name = action_info["func"]
                params = action_info.get("params", {})

                if func_name == "func_1":
                    func_1()
                elif func_name == "func_2":
                    func_2()
                elif func_name == "func_3":
                    func_3(*args if args else ["unknown"])
                elif func_name == "func_4":
                    process_name = args[0] if args else "unknown"
                    func_4(process_name)
                elif func_name == "func_5":
                    process_name = args[0] if args else "unknown"
                    func_5(process_name)

    def _register_power_event(self, trig_id, params):
        """注册电源事件监听"""
        event_type = params.get("event_type", "both")  # plugged, unplugged, both

        def power_handler(event_data):
            self._run_actions(trig_id, event_data)

        if event_type in ["plugged", "both"]:
            self.event_listener.register_power_handler("plugged", power_handler)
        if event_type in ["unplugged", "both"]:
            self.event_listener.register_power_handler("unplugged", power_handler)

    def _register_process_start_monitor(self, trig_id, params):
        """注册进程启动事件监听"""
        process_name = params.get("process_name", "notepad.exe")

        def process_handler(process_name):
            self._run_actions(trig_id, process_name)

        self.event_listener.register_process_start_handler(process_name, process_handler)

    def _register_process_stop_monitor(self, trig_id, params):
        """注册进程终止事件监听"""
        process_name = params.get("process_name", "notepad.exe")

        def process_handler(process_name):
            self._run_actions(trig_id, process_name)

        self.event_listener.register_process_stop_handler(process_name, process_handler)


# ------------------ pywebview 接口 ------------------
class TaskManagerAPI:
    def __init__(self):
        self.task_manager = TaskManager()

    def start(self):
        """启动任务管理器"""
        return self.task_manager.start()

    def stop(self):
        """停止任务管理器"""
        return self.task_manager.stop()

    def restart(self):
        """重启任务管理器"""
        return self.task_manager.restart()

    def is_running(self):
        """检查任务管理器是否运行中"""
        return self.task_manager.is_running()

    def get_config(self):
        """获取当前配置"""
        return self.task_manager.get_config()

    def update_config(self, triggers=None, actions=None, relations=None):
        """更新配置"""
        return self.task_manager.update_config(triggers, actions, relations)

    def save_config(self):
        """保存配置到文件"""
        return self.task_manager.save_config()

    def load_config(self):
        """从文件加载配置"""
        return self.task_manager.load_config()


# ------------------ 示例 JSON ------------------
"""
triggers.json:
[
  {"id": "t1", "name": "t1Name", "type": "delay", "params": {"seconds": 30}},
  {"id": "t2", "name": "t2Name", "type": "cron", "params": {"hour": 8, "minute": 0}},
  {"id": "t3", "name": "t3Name", "type": "power", "params": {"event_type": "both"}},
  {"id": "t4", "name": "t4Name", "type": "process_start", "params": {"process_name": "Notepad.exe"}},
  {"id": "t5", "name": "t5Name", "type": "process_stop", "params": {"process_name": "Notepad.exe"}},
  {"id": "t6", "name": "t6Name", "type": "process_start", "params": {"process_name": "chrome.exe"}},
  {"id": "t7", "name": "t7Name", "type": "process_stop", "params": {"process_name": "chrome.exe"}}
]

actions.json:
[
  {"id": "a1", "name": "a1Name", "func": "func_1"},
  {"id": "a2", "name": "a2Name", "func": "func_2"},
  {"id": "a3", "name": "a3Name", "func": "func_3"},
  {"id": "a4", "name": "a4Name", "func": "func_4"},
  {"id": "a5", "name": "a5Name", "func": "func_5"}
]

relations.json:
[
  {"trigger_id": "t1", "action_id": "a1"},
  {"trigger_id": "t2", "action_id": "a2"},
  {"trigger_id": "t3", "action_id": "a3"},
  {"trigger_id": "t4", "action_id": "a4"},
  {"trigger_id": "t5", "action_id": "a5"}
]
"""

if __name__ == "__main__":
    # 创建API实例供pywebview使用 window.pywebview.api.start() window.pywebview.api.stop() window.pywebview.api.restart()
    api = TaskManagerAPI()

    # 示例：启动任务管理器
    api.start()

    try:
        # 保持主线程运行
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("退出中...")
        api.stop()