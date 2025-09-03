import psutil
import time
from collections import defaultdict


def monitor_processes():
    # 初始进程列表
    current_processes = {p.pid: p.name() for p in psutil.process_iter(['pid', 'name'])}

    while True:
        # 获取当前进程列表
        new_processes = {p.pid: p.name() for p in psutil.process_iter(['pid', 'name'])}

        # 检测新进程
        started = set(new_processes.keys()) - set(current_processes.keys())
        for pid in started:
            print(f"进程启动: {new_processes[pid]} (PID: {pid})")

        # 检测终止的进程
        ended = set(current_processes.keys()) - set(new_processes.keys())
        for pid in ended:
            print(f"进程终止: {current_processes[pid]} (PID: {pid})")

        # 更新当前进程列表
        current_processes = new_processes

        # 减少轮询频率
        time.sleep(0.5)


# 在单独的线程中运行监控
import threading

monitor_thread = threading.Thread(target=monitor_processes)
monitor_thread.daemon = True
monitor_thread.start()

print("进程监控已启动，主程序继续执行...")

# 保持主程序运行
try:
    while True:
        # 主程序可以做其他事情
        time.sleep(500)
        pass
except KeyboardInterrupt:
    print("程序结束")