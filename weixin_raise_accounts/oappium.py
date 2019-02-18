# -*- coding: utf-8 -*-

import os
import ctypes
import re
import logging
import socket
import threading
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import subprocess
from copy import deepcopy


def execute_cmd(cmd, type=0):
    '''
    使用subprocess执行系统命令
    :param cmd: 命令
    :param type: 类型 0:不需要返回值 1:返回执行结果 2:返回子进程
    :return:
    '''
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if type == 0:
        p.wait()
        p.terminate()

    elif type == 1:
        infos = [str(i, encoding='utf-8') for i in p.stdout.readlines()]
        p.wait()
        p.terminate()

        return infos

    elif type == 2:
        return p


class AppiumAutoTool():
    def __init__(self,deviceName,serial,port,driver,desired_caps):
        self.deviceName = deviceName
        self.serial = serial
        self.port = port
        self.driver = driver
        self.desired_caps = desired_caps
        self.x = self.driver.get_window_size()['width']
        self.y = self.driver.get_window_size()['height']

    def awake_and_unlock_screen(self):
        for i in range(3):
            screen_state = self.get_screen_lock_state()

            if screen_state == 0:
                self.driver.press_keycode(26)
                self.driver.swipe(1 / 2, 9 / 10, 1 / 2, 1 / 10, 1000)

            elif screen_state == 1:
                self.driver.swipe(1 / 2, 9 / 10, 1 / 2, 1 / 10, 1000)

            elif screen_state == 2:
                return

            time.sleep(2)

        logging.warning(f'Screen Unlock Failed:{self.serial}')


    # 获取屏幕锁定状态 0:暗屏未解锁 1:亮屏未解锁 2:亮屏已解锁
    def get_screen_lock_state(self):
        result1 = ''.join(execute_cmd(f'adb -s {self.serial} shell "dumpsys window policy|grep isStatusBarKeyguard"',type=1))

        result2 = ''.join(execute_cmd(f'adb -s {self.serial} shell "dumpsys window policy|grep mShowingLockscreen"',type=1))

        result3 = ''.join(execute_cmd(f'adb -s {self.serial} shell "dumpsys window policy|grep mScreenOnEarly"', type=1))

        if 'isStatusBarKeyguard=true' in result1 or 'mShowingLockscreen=true' in result2:
            if 'mScreenOnEarly=false' in result3:
                state = 0
            else:
                state = 1

        else:
            state = 2

        return state



    # 按下返回键
    def press_back(self,sleep=2):
        self.driver.press_keycode(4)
        time.sleep(sleep)

    # 判断元素是否存在
    def is_el_exist(self, type, selector, timeout=3):
        wait_for_el = WebDriverWait(self.driver, timeout)
        if type == 'id':
            try:
                el = wait_for_el.until(EC.presence_of_element_located((By.ID, selector)))
                return el
            except:
                return False
        elif type == 'xpath':
            try:
                el = wait_for_el.until(EC.presence_of_element_located((By.XPATH, selector)))
                return el
            except:
                return False

    # 判断元素是否可点击
    def is_el_clickable(self, type, selector, timeout=3):
        wait_for_el = WebDriverWait(self.driver, timeout)
        if type == 'id':
            try:
                el = wait_for_el.until(EC.element_to_be_clickable((By.ID, selector)))
                return el
            except:
                return False
        elif type == 'xpath':
            try:
                el = wait_for_el.until(EC.element_to_be_clickable((By.XPATH, selector)))
                return el
            except:
                return False

    # 判断元素是否出现在当前页面
    def is_el_displayed(self, type, selector, y_ratio, timeout=3):
        wait_for_el = WebDriverWait(self.driver, timeout)
        if type == 'id':
            try:
                el = wait_for_el.until(EC.visibility_of_element_located((By.ID, selector)))
                loc = el.location_once_scrolled_into_view
                if loc and loc['y'] < y_ratio * self.y:
                    return el
                else:
                    return False
            except:
                return False
        elif type == 'xpath':
            try:
                el = wait_for_el.until(EC.visibility_of_element_located((By.XPATH, selector)))
                loc = el.location_once_scrolled_into_view
                if loc and loc['y'] < y_ratio * self.y:
                    return el
                else:
                    return False
            except:
                return False

    # 点击不稳定元素(点击一次可能无效,一直点击到下一个元素出现)
    def click_unstable_el(self, el, next_el_type, next_el_selector, timeout=3):
        for i in range(10):
            el.click()

            next_el = self.is_el_exist(next_el_type, next_el_selector, timeout)
            if next_el:
                return next_el

        raise Exception('Click Unstable Element Error',el)

    # 通过xpath点击不稳定元素(点击一次可能无效,一直点击到下一个元素出现)
    def click_unstable_el_by_xpath(self, current_el_type,current_el_selector, next_el_type, next_el_selector, timeout=3):
        wait = WebDriverWait(self.driver, timeout)
        by = By.XPATH if current_el_type=='xpath' else By.ID

        for i in range(10):
            el = wait.until(EC.element_to_be_clickable((by,current_el_selector)))
            el.click()
            time.sleep(5)

            next_el = self.is_el_exist(next_el_type, next_el_selector, timeout)
            if next_el:
                return next_el

        raise Exception('Click Unstable Element Error', current_el_selector)

    # 根据屏幕比例进行滑动
    def swipe(self, ratio_x1, ratio_y1, ratio_x2, ratio_y2, duration):
        self.driver.swipe(ratio_x1 * self.x, ratio_y1 * self.y, ratio_x2 * self.x, ratio_y2 * self.y, duration)

    # 切换为搜狗输入法并退出driver
    def quit(self):
        execute_cmd(f'adb -s {self.serial} shell ime set com.sohu.inputmethod.sogou.xiaomi/.SogouIME')

        self.driver.quit()


class MultiAppium():
    TODAY = time.strftime('%Y-%m-%d')
    logging.basicConfig(filename=f'{TODAY}.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def __init__(self):
        self.devices = []
        self.appium_port = 30000
        self.bp_port = 40000
        self.socket_obj = socket.socket()
        self.socket_hostname = socket.getfqdn(socket.gethostname())
        self.socket_addr = socket.gethostbyname(self.socket_hostname)
        self.server_threads = []
        self.task_threads = []
        self.target = None
        self.desired_caps = None
        self.server_processes = []

    def showMessagebox(self,title, text, style=0):
        return ctypes.windll.user32.MessageBoxW(0, text, title, style)

    def check_environment(self):
        try:
            result = execute_cmd('adb devices -l',type=1)
            devices = [i for i in result if 'model' in i]

            if devices:
                return True
            else:
                self.showMessagebox('提示', '当前无设备连接,请检查设备连接情况!')

        except:
            self.showMessagebox('提示','运行失败,端口被占用!请关闭360手机助手的后台进程!')

    def get_devices(self):
        device_serial = []
        result = execute_cmd('adb devices -l', type=1)
        devices_info = [i for i in result if 'model' in i]

        logging.info('Devices Info:')
        for i, info in enumerate(devices_info):
            serial = str(re.search(r'(.*?)device', info).group(1).strip())
            deviceName = re.search(r'model:(.*?) device', info).group(1).strip()
            port = str(self.get_available_port_by_socket())

            self.devices.append(
                {
                    'deviceName': deviceName,
                    'serial': serial,
                    'port': port,
                }
            )

            device_serial.append(serial)


            logging.info(serial+' '+deviceName+' '+port+' ')

        return device_serial

    # 获取屏幕大小
    def get_window_size(self,device):
        result = ''.join(execute_cmd(f'adb -s {device} shell wm size',type=1))

        if result:
            clear_btn_loc = re.search(r'Physical size: (\d+)x(\d+)', result)
            x = int(clear_btn_loc.group(1))
            y = int(clear_btn_loc.group(2))

            return x, y

    # 唤醒并解锁屏幕
    def awake_and_unlock_screen(self,devices):
        for device in devices:
            result1 = ''.join(execute_cmd(f'adb -s {device} shell "dumpsys window policy|grep isStatusBarKeyguard"', type=1))

            result2 = ''.join(execute_cmd(f'adb -s {device} shell "dumpsys window policy|grep mShowingLockscreen"', type=1))

            result3 = ''.join(execute_cmd(f'adb -s {device} shell "dumpsys window policy|grep mScreenOnEarly"', type=1))

            if 'isStatusBarKeyguard=true' in result1 or 'mShowingLockscreen=true' in result2:
                x, y = self.get_window_size(device)
                x1, y1, x2, y2 = 1 / 2 * x, 9 / 10 * y, 1 / 2 * x, 1 / 10 * y

                if 'mScreenOnEarly=false' in result3:
                    execute_cmd(f'adb -s {device} shell input keyevent 26')

                execute_cmd(f'adb -s {device} shell input swipe {x1} {y1} {x2} {y2}')

    def get_available_port_by_socket(self):
        while True:
            try:
                self.socket_obj.connect((self.socket_addr, self.appium_port))
                self.socket_obj.close()
                self.appium_port += 1
            except:
                port = self.appium_port
                self.appium_port += 1
                return port

    def get_available_bp_port_by_socket(self):
        while True:
            try:
                self.socket_obj.connect((self.socket_addr, self.bp_port))
                self.socket_obj.close()
                self.bp_port += 1
            except:
                port = self.bp_port
                self.bp_port += 1
                return port

    def kill_all_appium(self):
        execute_cmd('taskkill /f /t /im node.exe')

    def start_server(self,serial, port):
        logging.info(f'Thread Start-{serial}')
        bp_port = self.get_available_bp_port_by_socket()
        logging.info(f'Start Server:{serial} {port} {bp_port}')

        # cmd = r'node C:\Users\ethan\AppData\Local\Programs\Appium\resources\app\node_modules\appium\build\lib\main.js -p {} -bp {} -U {}'.format(port, bp_port, serial)
        cmd = r'appium -p {} -bp {} -U {}'.format(port, bp_port, serial)
        process = subprocess.Popen(cmd,shell=True)
        self.server_processes.append(process)

        logging.info(f'Server Start Succeed:{process.pid} {serial} {port} {bp_port}')

    def get_server_threads(self):
        for device in self.devices:
            serial = device['serial']
            port = device['port']

            t = threading.Thread(target=self.start_server,args=(serial,port))
            self.server_threads.append(t)

    def get_task_threads(self):
        get_driver_threads = []
        for device in self.devices:
            deviceName = device['deviceName']
            serial = device['serial']
            port = device['port']

            caps = deepcopy(self.desired_caps)

            caps['deviceName'] = deviceName
            caps['udid'] = serial

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
                t = threading.Thread(target=target, args=(deviceName, serial, port, driver, desired_caps))
                self.task_threads.append(t)
                return
            except Exception as e:
                logging.error(f'Driver Start Failed:{e} Retring:{i+1}')

        logging.warning(f'Get Driver Failed:{deviceName} {serial}')

    def run(self):
        if_env_ok = self.check_environment()
        if if_env_ok:
            task_list = []
            # 获取设备
            devices = self.get_devices()

            # 唤醒并解锁
            self.awake_and_unlock_screen(devices)

            # 终止所有appium
            self.kill_all_appium()

            # 启动server线程
            self.get_server_threads()
            for t1 in self.server_threads:
                t1.setDaemon(True)
                t1.start()

            time.sleep(len(self.server_threads))

            # 启动driver线程
            self.get_task_threads()
            for t2 in self.task_threads:
                task_list.append(t2)
                t2.setDaemon(True)
                t2.start()

            # 等待所有任务执行完成
            for task in task_list:
                task.join()

            # 关闭所有appium服务器进程
            for process in self.server_processes:
                process.terminate()
                logging.info(f'Server End Succeed:{process.pid}')

            # 终止所有appium
            self.kill_all_appium()

