# -*- coding: utf-8 -*-
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
import time
import oappium
import pymongo
from settings import *
import random
import func_timeout
from PyQt5.QtWidgets import QApplication

# 超时时间
TIMEOUT = 60

# 待添加的QQ号列表
ADD_QQ_LIST = [
    # {'name':'测试','qq':'195627250'},
    # {'name':'煤油','qq':'123456'}, # 4
    # {'name':'巨田','qq':'654321'}, # 5

    {'name':'张三','qq':'615215416'}, # 4
    # {'name':'李四','qq':'498546235'}, # 0
    # {'name':'王五','qq':'845125164'}, # 0
    {'name':'小红','qq':'698565421'}, # 4
    {'name':'小蓝','qq':'265215421'}, # 4
    # {'name':'小绿','qq':'123525461'}, # 0
    {'name':'小橙','qq':'135246952'}, # 4
    {'name':'小黄','qq':'265425187'}, # 4
    # {'name':'小青','qq':'236965451'}, # 0
    # {'name':'小紫','qq':'285421542'}, # 0

]

# 验证消息列表
VERIFY_MSG_LIST = ['你好','可以加个好友吗？']

# 加好友间隔
ADD_FRIENDS_INTERVAL = (10,20)

# Qt信号
QT_SIGNAL = None


class QQAFAutoTool(oappium.AppiumAutoTool):
    def __init__(self,deviceName,serial,port,driver,desired_caps,shuffle_list=None):
        super().__init__(deviceName,serial,port,driver,desired_caps)
        self.wait = WebDriverWait(self.driver, TIMEOUT)
        self.current_qq = ''
        self.current_qq_name = ''
        self.client = pymongo.MongoClient(MONGO_CLIENT)
        self.client.admin.authenticate('root', 'csdjgs9B15BS')
        self.db = self.client[MONGO_DB]
        self.collection = self.db[MONGO_COLLECTION]
        self.shuffle_list = shuffle_list
        self.init_shuffle_list()


    def init_shuffle_list(self):
        '''
        初始化待添加QQ的乱序列表
        :return:
        '''
        if self.shuffle_list == None:
            self.shuffle_list = ADD_QQ_LIST.copy()
            random.shuffle(self.shuffle_list)

    def filter_shuffle_list(self):
        '''
        过滤乱序列表，从列表中移除数据库存在的数据
        :return:
        '''
        db_results = self.collection.find({'device_qq':self.current_qq})
        results_qq = [result['add_qq'] for result in db_results]
        for add_qq in self.shuffle_list:
            if add_qq['qq'] in results_qq:
                self.shuffle_list.remove(add_qq)

    def get_current_account_info(self):
        '''
        获取当前账号信息
        :return:
        '''
        el_head = self.wait.until(EC.element_to_be_clickable((By.ID,'com.tencent.mobileqq:id/conversation_head')))
        el_head.click()

        time.sleep(5)

        el_account_manage = self.click_unstable_el_by_xpath('xpath','//android.widget.Button[@content-desc="设置"]/android.widget.TextView','id','com.tencent.mobileqq:id/account_switch')
        el_account_manage.click()

        el_name = self.wait.until(EC.presence_of_element_located((By.XPATH,'//android.widget.ImageView[@resource-id="com.tencent.mobileqq:id/icon"]/following-sibling::android.widget.RelativeLayout/android.widget.TextView[@resource-id="com.tencent.mobileqq:id/name"]')))
        el_qq = self.wait.until(EC.presence_of_element_located((By.XPATH,'//android.widget.ImageView[@resource-id="com.tencent.mobileqq:id/icon"]/following-sibling::android.widget.RelativeLayout/android.widget.TextView[@resource-id="com.tencent.mobileqq:id/account"]')))

        self.current_qq_name = el_name.text
        self.current_qq = el_qq.text

        self.emit_to_qt('当前账号',self.current_qq)

        self.press_back(3)
        self.press_back(3)
        self.press_back(3)

    def if_qq_in_db(self,qq):
        '''
        检测QQ是否在数据库中存在
        :param qq: 待添加的QQ
        :return:
        '''
        result = self.collection.find_one({'$and':[{'device_qq':self.current_qq},{'add_qq':qq}]})
        return True if result else False

    def if_qq_refuse_to_add(self):
        '''
        检测QQ是否拒绝任何人添加
        :return:
        '''
        if not self.is_el_exist('xpath','//android.widget.LinearLayout/android.widget.EditText[@resource-id="com.tencent.mobileqq:id/name"]',5):
            return True

    @func_timeout.func_set_timeout(10)
    def check_if_qq_not_found(self):
        '''
        为此方法添加超时机制,因为Appium的Bug导致该页面有时无法加载完成
        :return:
        '''
        if not self.is_el_exist('xpath','//android.widget.FrameLayout[@content-desc="查看大头像"]/android.widget.ImageView[2]',5):
            return True

    def if_qq_not_found(self):
        '''
        检测QQ是否不存在
        :return:
        '''
        try:
            if_not_found = self.check_if_qq_not_found()
            return if_not_found
        except func_timeout.exceptions.FunctionTimedOut:
            # logging.info('timeout')
            return True

    def if_qq_already_friend(self):
        '''
        检测QQ是否已添加为好友
        :return:
        '''
        if self.is_el_exist('xpath','//android.widget.Button[@content-desc="发消息"]'):
            return True

    def if_need_answer_question(self):
        '''
        检测QQ是否需要回答问题
        :return:
        '''
        if self.is_el_exist('xpath','//android.widget.EditText[@resource-id="com.tencent.mobileqq:id/name" and @text="输入答案"]'):
            return True

    def save_to_mongo(self,item):
        '''
        保存至数据库
        :param item: 数据项
        :return:
        '''
        item['device_serial'] = self.serial
        item['device_qq'] = self.current_qq
        item['device_qq_name'] = self.current_qq_name
        item['add_time'] = time.time()

        self.collection.update_one({'device_qq':item['device_qq'],'add_qq':item['add_qq'],'add_qq_type':item['add_qq_type']},{'$set':item},True)

    def add_friends(self):
        '''
        添加好友主流程
        :return:
        '''
        el_plus = self.wait.until(EC.element_to_be_clickable((By.XPATH,'//android.widget.ImageView[@content-desc="快捷入口"]')))
        el_plus.click()

        el_add_friends = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//android.widget.LinearLayout[@content-desc="加好友/群 按钮"]')))
        el_add_friends.click()

        el_search_bar1 = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//android.widget.EditText[@content-desc="搜索栏、QQ号、手机号、群、公众号"]')))
        el_search_bar1.click()

        self.filter_shuffle_list()
        wait_to_add = len(self.shuffle_list)
        self.emit_to_qt('待添加',str(wait_to_add))

        time.sleep(3)

        for friend in self.shuffle_list:
            wait_to_add -= 1
            self.emit_to_qt('待添加', str(wait_to_add))

            name,qq = friend['name'],friend['qq']
            if self.if_qq_in_db(qq):
                continue

            item = {'add_qq':qq,'add_qq_name':name,'verify_msg':''}

            el_search_bar2 = self.wait.until(EC.presence_of_element_located((By.ID, 'com.tencent.mobileqq:id/et_search_keyword')))
            el_search_bar2.send_keys(qq)

            el_find_person = self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//android.widget.LinearLayout[@content-desc="找人:{qq}"]')))
            el_find_person.click()

            time.sleep(2)

            if self.if_qq_not_found():
                # 添加类型4：QQ号不存在
                item['add_qq_type'] = 4

                self.save_to_mongo(item)
                self.press_back_adb()

                el_search_bar1 = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//android.widget.EditText[@content-desc="搜索栏、QQ号、手机号、群、公众号"]')))
                el_search_bar1.click()
                continue

            if self.if_qq_already_friend():
                # 添加类型3：已添加为好友
                item['add_qq_type'] = 3
                self.save_to_mongo(item)
                self.press_back()
                continue

            el_add = self.wait.until(EC.element_to_be_clickable((By.ID, 'com.tencent.mobileqq:id/txt')))
            el_add.click()

            if self.if_qq_refuse_to_add():
                # 添加类型5：拒绝任何人添加
                item['add_qq_type'] = 5
                self.save_to_mongo(item)
                self.press_back()
                continue

            if self.if_need_answer_question():
                # 添加类型1：问题限制
                item['add_qq_type'] = 1
                self.save_to_mongo(item)
                self.press_back()
                continue

            el_verify_msg = self.is_el_exist('xpath','//android.widget.RelativeLayout/android.widget.EditText[@resource-id="com.tencent.mobileqq:id/name"]')
            if el_verify_msg:
                msg = random.choice(VERIFY_MSG_LIST)
                el_verify_msg.clear()
                el_verify_msg.send_keys(msg)
                # 添加类型0：正常验证
                item['add_qq_type'] = 0
                item['verify_msg'] = msg
            else:
                # 添加类型2：允许任何人添加
                item['add_qq_type'] = 2

            el_remark = self.wait.until(EC.presence_of_element_located((By.XPATH, '//android.widget.LinearLayout/android.widget.EditText[@resource-id="com.tencent.mobileqq:id/name"]')))
            el_remark.clear()
            el_remark.send_keys(name)

            el_send = self.wait.until(EC.element_to_be_clickable((By.ID, 'com.tencent.mobileqq:id/ivTitleBtnRightText')))
            el_send.click()

            self.save_to_mongo(item)

            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//android.widget.TextView[@resource-id="com.tencent.mobileqq:id/ivTitleBtnLeft" and @text="返回"]')))
            self.press_back(3)

            time.sleep(random.randint(*ADD_FRIENDS_INTERVAL))

    def run(self):
        self.get_current_account_info()

        self.add_friends()

        self.quit()

    def restart(self):
        try:
            self.driver.quit()
        except:
            pass

        for i in range(3):
            try:
                self.driver = webdriver.Remote(f'http://localhost:{self.port}/wd/hub', self.desired_caps)
                self.__init__(self.deviceName,self.serial,self.port,self.driver,self.desired_caps,self.shuffle_list)
                break
            except Exception as e:
                time.sleep(5)
                logging.warning(f'Restart to Get Driver Failed:{e} {self.serial} Retrying:{i+1}')

    def start(self):
        # 更新设备状态为'运行中'
        self.emit_to_qt('状态', DEVICE_STATE_DICT[4])

        max_retry = 100
        sleep_time = 60

        for i in range(max_retry):
            try:
                self.run()
                logging.info(f'Finished.{self.serial}')
                # 更新设备状态为'运行完成'
                self.emit_to_qt('状态', DEVICE_STATE_DICT[5])
                return
            except Exception as e:
                time.sleep(sleep_time)
                logging.error(f'Running Error:{e} {self.serial} Retrying:{i+1}')
                self.restart()

        # 更新设备状态为'运行异常'
        self.emit_to_qt('状态', DEVICE_STATE_DICT[6])

    def emit_to_qt(self,field_name,data):
        '''
        发送信号至Qt
        :param field_name: 要更新的字段名
        :param data: 更新的数据内容
        :return:
        '''
        if QT_SIGNAL:
            QT_SIGNAL.emit(self.serial,field_name,data)
            QApplication.processEvents()


def run_driver(deviceName, serial, port, driver, desired_caps):
    auto_tool = QQAFAutoTool(deviceName, serial, port, driver, desired_caps)
    auto_tool.start()





def test():
    desired_caps = {
        "platformName": "Android",
        "deviceName": 'Redmi_Note_4X',
        "appPackage": "com.tencent.mobileqq",
        "appActivity": ".activity.SplashActivity",
        "noReset": True,
        'unicodeKeyboard': True,
        'newCommandTimeout': 86400,
    }

    driver = webdriver.Remote(f'http://localhost:4723/wd/hub', desired_caps)
    auto_tool = QQAFAutoTool('Redmi_Note_4X','2dd9d6319804',4723,driver,desired_caps)
    auto_tool.get_current_account_info()
    auto_tool.add_friends()
    auto_tool.quit()

if __name__ == '__main__':
    test()










