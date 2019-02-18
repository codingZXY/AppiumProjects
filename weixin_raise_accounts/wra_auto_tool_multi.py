# -*- coding: utf-8 -*-

import oappium
import wra_auto_tool
import logging
import threading
from settings import *
from appium import webdriver
from copy import deepcopy

TACTICS = [
    {
        'type':0,
        'name':'关注公众号',
        'official_accounts':['高效工具搜罗','一点厦门','刘备教授'],
        'concern_interval':(0,1)
    },
    {
        'type':1,
        'name':'文章阅读转发',
        'article_read_num':3,
        'if_share':False,
        'read_share_interval':(0,1)
    },
    {
        'type':2,
        'name':'朋友圈点赞',
        'moments_thumbup_num':5,
        'thumbup_interval':(0,1)
    },
    {
        'type':3,
        'name':'发送消息',
        'chat_objects':['安静的兰胖纸','hdkahsjkd','中国不讲生僻字','聊天群1','撒开了房间出来'],
        'msg_contents':['你好','hello','hi'],
        'send_msg_interval':(0,1)
    }
]


class WRAAutoToolMulti(oappium.MultiAppium):
    def __init__(self,tactics,qt_signal=None,screen_off=True,switch_accounts=False):
        super().__init__()
        self.target = wra_auto_tool.run_driver
        self.desired_caps = {
            "platformName": "Android",
            "deviceName": '',
            "appPackage": "com.tencent.mm",
            "appActivity": ".ui.LauncherUI",
            "noReset": True,
            'unicodeKeyboard': True,
            'newCommandTimeout': 86400,
            "udid": '',
        }
        self.tactics = tactics
        self.qt_signal = qt_signal
        self.screen_off = screen_off
        self.switch_accounts = switch_accounts

    def init_settings(self):
        wra_auto_tool.TACTICS = self.tactics
        wra_auto_tool.QT_SIGNAL = self.qt_signal
        wra_auto_tool.SCREEN_OFF = self.screen_off
        wra_auto_tool.SWITCH_ACCOUNTS = self.switch_accounts

    def get_task_threads(self):
        get_driver_threads = []
        for device in self.devices:
            deviceName = device['deviceName']
            serial = device['serial']
            port = device['port']
            caps = deepcopy(self.desired_caps)

            caps['deviceName'] = deviceName
            caps['udid'] = serial

            self.qt_signal.emit(serial, '状态', DEVICE_STATE_DICT[1])

            t = threading.Thread(target=self.get_driver,args=(serial,deviceName,port,self.target,caps))
            t.start()
            get_driver_threads.append(t)

        for t in get_driver_threads:
            t.join()

    def get_driver(self,serial,deviceName,port,target,desired_caps,try_time=3):
        for i in range(try_time):
            try:
                driver = webdriver.Remote(f'http://localhost:{port}/wd/hub', desired_caps)

                logging.info(f'Get Driver Succeed:{deviceName} {serial}')
                self.qt_signal.emit(serial, '状态', DEVICE_STATE_DICT[2])

                t = threading.Thread(target=target, args=(deviceName, serial, port, driver, desired_caps))
                self.task_threads.append(t)

                return
            except Exception as e:
                logging.error(f'Driver Start Failed:{e} Retring:{i+1}')

        logging.warning(f'Get Driver Failed:{deviceName} {serial}')
        self.qt_signal.emit(serial, '状态', DEVICE_STATE_DICT[3])

if __name__ == '__main__':
    auto_obj = WRAAutoToolMulti(TACTICS)
    auto_obj.init_settings()
    auto_obj.run()