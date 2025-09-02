#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Description: 业务层API,供前端JS调用
usage: 在Javascript中调用 window.pywebview.api.<methodname>(<parameters>)
'''

from src_py.api.system import System
from src_py.api.ComputerInfo import ComputerInfo


import inspect


class API(System):
    def __init__(self):
        self.pc = ComputerInfo()

        # 自动把 ComputerInfo 的方法挂到 API 上
        for name, method in inspect.getmembers(self.pc, predicate=inspect.ismethod):
            if not name.startswith("_"):  # 跳过私有方法
                setattr(self, name, method)

    def setWindow(self, window):
        System.window = window


