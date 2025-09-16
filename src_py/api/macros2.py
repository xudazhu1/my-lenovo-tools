import threading
import time
from pynput import keyboard
from pynput.keyboard import Controller

controller = Controller()
lock = threading.Lock()
task_thread = None
task_version = 0
ignore_next = False

def task_t(my_version):
    global ignore_next, task_version


    print("开始20秒高频按5")
    start_time = time.time()
    while time.time() - start_time < 20:
        if my_version != task_version:
            print("任务被中断（5阶段）")
            return
        ignore_next = True

        # 快速 sequence
        sequence = '1234567890'
        for key in sequence:
            if my_version != task_version:
                print("任务被中断（sequence阶段）")
                return
            ignore_next = True
            controller.press(key)
            controller.release(key)
            ignore_next = False
            # 模拟耗时操作，拆分成小块循环
            for _ in range(5):  # 总共 0.005 秒
                if my_version != task_version:
                    return
                time.sleep(0.001)

        ignore_next = False
        # 高频 0.005 秒，拆分循环
        for _ in range(5):
            if my_version != task_version:
                return
            time.sleep(0.001)

def start_task():
    global task_thread, task_version
    with lock:
        task_version += 1
        my_version = task_version
        if task_thread and task_thread.is_alive():
            # 旧任务会看到 task_version != my_version 自动退出
            pass
        task_thread = threading.Thread(target=task_t, args=(my_version,))
        task_thread.start()

from pynput import keyboard as pynput_kb
ctrl_map = {chr(i): chr(96 + i) for i in range(1, 27)}


def on_press(key):
    global ignore_next
    if ignore_next:
        return

    print("my_on_release 按下 = ")
    name = ''
    if isinstance(key, pynput_kb.Key):
        name = f"<{key.name}>"
    else:
        name = key.char
        try:
            if name in ctrl_map:
                print("转换后:", ctrl_map[key.char])  # 把 '\x03' 转换为 'c'
                name = ctrl_map[key.char]
            else:
                print("普通键:", key.char)
        except AttributeError:
            print("特殊键:", key)  # 比如 shift, alt, f1 等
    print(name)


def on_release(key):
    global ignore_next
    if ignore_next:
        return

    print("my_on_release 释放 = ")
    name = ''
    if isinstance(key, pynput_kb.Key):
        name = f"<{key.name}>"
    else:
        name = key.char
        try:
            if name in ctrl_map:
                print("转换后:", ctrl_map[key.char])  # 把 '\x03' 转换为 'c'
                name = ctrl_map[key.char]
            else:
                print("普通键:", key.char)
        except AttributeError:
            print("特殊键:", key)  # 比如 shift, alt, f1 等
    print(name)


with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    print('start task')
    while True:
        time.sleep(10)
