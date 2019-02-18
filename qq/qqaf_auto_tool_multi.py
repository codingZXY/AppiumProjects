# -*- coding: utf-8 -*-

import oappium
import qqaf_auto_tool
import logging
import threading
from settings import *
from appium import webdriver
from copy import deepcopy


# 待添加的QQ号列表
ADD_QQ_LIST = [
    {'name':'测试','qq':'195627250'},
    {'name':'煤油','qq':'123456'}, # 4
    {'name':'巨田','qq':'654321'}, # 5

    # {'name':'张三','qq':'615215416'}, # 4
    # {'name':'李四','qq':'498546235'}, # 0
    # {'name':'王五','qq':'845125164'}, # 0
    # {'name':'小红','qq':'698565421'}, # 4
    # {'name':'小蓝','qq':'265215421'}, # 4
    # {'name':'小绿','qq':'123525461'}, # 0
    # {'name':'小橙','qq':'135246952'}, # 4
    # {'name':'小黄','qq':'265425187'}, # 4
    # {'name':'小青','qq':'236965451'}, # 0
    # {'name':'小紫','qq':'285421542'}, # 0

]

# 验证消息列表
VERIFY_MSG_LIST = ['你好','可以加个好友吗？']

# 加好友间隔
ADD_FRIENDS_INTERVAL = 10

class QQAFAutoToolMulti(oappium.MultiAppium):
    def __init__(self,add_qq_list,verify_msg_list,add_friends_interval,qt_signal=None):
        super().__init__()
        self.target = qqaf_auto_tool.run_driver
        self.desired_caps = {
            "platformName": "Android",
            "deviceName": '',
            "appPackage": "com.tencent.mobileqq",
            "appActivity": ".activity.SplashActivity",
            "noReset": True,
            'unicodeKeyboard': True,
            'newCommandTimeout': 86400,
            "udid": '',
        }
        self.add_qq_list = add_qq_list
        self.verify_msg_list = verify_msg_list
        self.add_friends_interval = add_friends_interval
        self.qt_signal = qt_signal

    def init_settings(self):
        qqaf_auto_tool.ADD_QQ_LIST = self.add_qq_list
        qqaf_auto_tool.VERIFY_MSG_LIST = self.verify_msg_list
        qqaf_auto_tool.ADD_FRIENDS_INTERVAL = self.add_friends_interval
        qqaf_auto_tool.QT_SIGNAL = self.qt_signal

    def get_task_threads(self):
        get_driver_threads = []
        for device in self.devices:
            deviceName = device['deviceName']
            serial = device['serial']
            port = device['port']
            caps = deepcopy(self.desired_caps)

            caps['deviceName'] = deviceName
            caps['udid'] = serial

            # self.qt_signal.emit(serial, '状态', DEVICE_STATE_DICT[1])

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
                # self.qt_signal.emit(serial, '状态', DEVICE_STATE_DICT[2])

                t = threading.Thread(target=target, args=(deviceName, serial, port, driver, desired_caps))
                self.task_threads.append(t)

                return
            except Exception as e:
                logging.error(f'Driver Start Failed:{e} Retring:{i+1}')

        logging.warning(f'Get Driver Failed:{deviceName} {serial}')
        # self.qt_signal.emit(serial, '状态', DEVICE_STATE_DICT[3])

if __name__ == '__main__':
    auto_obj = QQAFAutoToolMulti(ADD_QQ_LIST,VERIFY_MSG_LIST,ADD_FRIENDS_INTERVAL)
    auto_obj.init_settings()
    auto_obj.run()