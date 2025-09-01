#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Description: 业务层API,供前端JS调用
usage: 在Javascript中调用 window.pywebview.api.<methodname>(<parameters>)
'''

from src_py.api.system import System
from src_py.api.ComputerInfo import ComputerInfo


class API(System):
    '''业务层API,供前端JS调用'''
    ComputerInfo = ComputerInfo()

    def setWindow(self, window):
        '''获取窗口实例'''
        System.window = window
