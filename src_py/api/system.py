#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Description: 系统类
usage: 调用window.pywebview.api.<methodname>(<parameters>)从Javascript执行
'''

import os
import json
import sys

import webview


def get_base_path():
    if getattr(sys, 'frozen', False):  # 打包后
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_path(*relative_parts):
    base = get_base_path()
    return os.path.join(base, *relative_parts)


# 加载 DLL
# config_path = get_path("..", "..", "macros.config.json")


class System():
    '''系统类'''
    window = None

    def system_py2js(self, func, info):
        '''调用js中挂载到window的函数'''
        infoJson = json.dumps(info)
        System.window.evaluate_js(f"{func}('{infoJson}')")

    def system_pyCreateFileDialog(self, file_types=['全部文件 (*.*)'], directory=''):
        '''打开文件对话框'''
        # file_types = ['Excel表格 (*.xlsx;*.xls)']
        file_types = tuple(file_types)
        result = System.window.create_file_dialog(dialog_type=webview.OPEN_DIALOG, directory=directory,
                                                  allow_multiple=True, file_types=file_types)
        result_list = list()
        if result is not None:
            for res in result:
                file_path_list = os.path.split(res)
                dir = file_path_list[0]
                filename = file_path_list[1]
                ext = os.path.splitext(res)[-1]
                result_list.append({
                    'filename': filename,
                    'ext': ext,
                    'dir': dir,
                    'path': res
                })
        return result_list
