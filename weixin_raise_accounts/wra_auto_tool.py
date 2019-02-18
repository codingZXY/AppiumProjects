# -*- coding: utf-8 -*-

from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
import time
import random
import oappium
from settings import *
from PyQt5.QtWidgets import QApplication


# region 全局设置

# 超时时间
TIMEOUT = 60

# 策略列表
TACTICS = []

# 是否熄屏
SCREEN_OFF = True

# Qt信号
QT_SIGNAL = None

# 是否切换账号
SWITCH_ACCOUNTS = False

# endregion


class WRAAutoTool(oappium.AppiumAutoTool):
    def __init__(self,deviceName,serial,port,driver,desired_caps,current_tactic=0):
        super().__init__(deviceName,serial,port,driver,desired_caps)
        self.wait = WebDriverWait(self.driver, TIMEOUT)
        self.current_wechat_name = ''

        # 记录当前策略号,重启时传入,重启后可继续当前的策略运行
        self.current_tactic = current_tactic

        # 记录运行完成的账号,避免异常重启时重复执行策略
        self.finished_accounts = []

    def emit_to_qt(self,serial,type,data):
        if QT_SIGNAL:
            QT_SIGNAL.emit(serial,type,data)
            QApplication.processEvents()

    # 点击搜索(需切换为搜狗输入法弹出搜索按键)
    def click_serach(self):
        oappium.execute_cmd(f'adb -s {self.serial} shell ime set com.sohu.inputmethod.sogou.xiaomi/.SogouIME')
        time.sleep(5)

        oappium.execute_cmd(f'adb -s {self.serial} shell input tap {0.92*self.x} {0.93*self.y}')

        ime_info = ''.join(oappium.execute_cmd(f'adb -s {self.serial} shell ime list -s',type=1))

        # 不同机型的appium输入法可能不同
        if 'io.appium.settings/.UnicodeIME' in ime_info:
            oappium.execute_cmd(f'adb -s {self.serial} shell ime set io.appium.settings/.UnicodeIME')

        elif 'io.appium.android.ime/.UnicodeIME' in ime_info:
            oappium.execute_cmd(f'adb -s {self.serial} shell ime set io.appium.android.ime/.UnicodeIME')

    # 返回首页
    def return_to_index_page(self):
        while 1:
            el = self.is_el_exist('xpath','//android.widget.RelativeLayout[@resource-id="com.tencent.mm:id/bn"]/android.widget.LinearLayout/android.widget.RelativeLayout[1]',1)
            if el:
                el.click()
                time.sleep(5)
                break
            else:
                self.press_back()

    # 关闭/开启消息提醒
    def close_open_notify(self,type):

        # 点击我 查找设置按钮
        el_setting = self.click_unstable_el_by_xpath('xpath','//android.widget.TextView[@resource-id="com.tencent.mm:id/d3t" and @text="我"]','xpath','//android.widget.TextView[@resource-id="android:id/title" and @text="设置"]')
        if self.current_wechat_name == '':
            el_wechat_name = self.wait.until(EC.presence_of_element_located((By.ID, 'com.tencent.mm:id/a5b')))
            self.current_wechat_name = el_wechat_name.text.strip()
            self.emit_to_qt(self.serial, '当前账号', self.current_wechat_name)

        time.sleep(5)
        el_setting.click()

        # 新消息提醒
        el_new_msg_notify = self.wait.until(EC.element_to_be_clickable((By.XPATH,'//android.widget.TextView[@resource-id="android:id/title" and @text="新消息提醒"]')))
        el_new_msg_notify.click()

        # 关闭/开启
        el_close_open = self.wait.until(EC.element_to_be_clickable((By.XPATH,'//android.widget.TextView[@resource-id="android:id/title" and @text="接收新消息通知"]/../following-sibling::android.view.View')))
        current_state = el_close_open.get_attribute("name")

        if type == 0 and current_state == '已开启':
            el_close_open.click()

        elif type == 1 and current_state == '已关闭':
            el_close_open.click()

        self.wait.until(EC.element_to_be_clickable((By.ID, 'com.tencent.mm:id/k5')))
        self.press_back()

        self.wait.until(EC.element_to_be_clickable((By.ID, 'com.tencent.mm:id/k5')))
        self.press_back()


    # 获取随机索引值（用于转发文章时获取随机公众号的文章）
    def get_random_num(self,exist_num,max_num):
        while True:
            n = random.randint(0,max_num)
            if n not in exist_num:
                return n

    # 通过adb点击搜索结果（针对找不到公众号查询结果元素的机型）
    def click_result_by_adb(self):
        time.sleep(5)
        oappium.execute_cmd(f'adb -s {self.serial} shell input tap {0.45*self.x} {0.25*self.y}')

    # 获取随机公众号列表（用于关注公众号时的随机关注）
    def get_random_official_accounts(self,concern_num,official_accounts):
        concern_num = len(official_accounts) if concern_num > len(official_accounts) else concern_num
        original = official_accounts[:]
        result = []
        cnt = 0

        while cnt < concern_num:
            index = random.randint(0,len(original) - 1)
            random_item = original.pop(index)
            result.append(random_item)
            cnt += 1

        return result

    # 判断是否点赞
    def if_thumbup(self,thumbup_ratio):
        if thumbup_ratio == 0:
            return False
        elif thumbup_ratio == 100:
            return True
        else:
            r = random.random() * 100
            if r <= thumbup_ratio:
                return True

    # 关注公众号
    def concern_official_accounts(self,tactic):
        concern_num = tactic['concern_num']
        official_accounts = tactic['official_accounts']
        concern_interval = tactic['concern_interval']
        random_oa = self.get_random_official_accounts(concern_num,official_accounts)

        succeed_num = 0
        self.return_to_index_page()

        # 点击搜索 点击公众号
        el_official_account = self.click_unstable_el_by_xpath('xpath','//android.view.ViewGroup[@resource-id="com.tencent.mm:id/j9"]//android.support.v7.widget.LinearLayoutCompat/android.widget.RelativeLayout[1]/android.widget.ImageView[@resource-id="com.tencent.mm:id/ij"]','xpath','//android.widget.TextView[@resource-id="com.tencent.mm:id/bvy" and @text="公众号"]')
        el_official_account.click()

        for oa in random_oa:
            el_search_bar = self.wait.until(EC.element_to_be_clickable((By.ID,'com.tencent.mm:id/ka')))
            el_search_bar.send_keys(oa)
            time.sleep(3)
            self.click_serach()

            el_search_result = self.is_el_exist('xpath','//android.view.View[@resource-id="search_list"]/android.widget.ListView/android.view.View[1]',timeout=10)
            if el_search_result:
                el_search_result.click()
            else:
                self.click_result_by_adb()

            if self.is_el_exist('xpath','//android.widget.TextView[@resource-id="android:id/title" and @text="关注公众号"]'):
                el_concern_official_account = self.wait.until(EC.element_to_be_clickable((By.XPATH,'//android.widget.TextView[@resource-id="android:id/title" and @text="关注公众号"]')))
                el_concern_official_account.click()

                while self.is_el_exist('xpath','//android.widget.ImageView[@resource-id="com.tencent.mm:id/jv"]'):
                    self.press_back()

            succeed_num += 1
            self.emit_to_qt(self.serial, '关注数', str(succeed_num))

            self.wait.until(EC.element_to_be_clickable((By.ID,'com.tencent.mm:id/k4')))
            self.press_back()

            time.sleep(random.randint(*concern_interval))

        self.wait.until(EC.element_to_be_clickable((By.ID, 'com.tencent.mm:id/k9')))
        self.press_back()

        self.press_back()

        self.return_to_index_page()


    # 文章阅读转发
    def read_share_articles(self,tactic):
        article_read_num = tactic['article_read_num']
        if_share = tactic['if_share']
        read_share_interval = tactic['read_share_interval']

        succeed_num = 0
        self.return_to_index_page()

        el_contacts = self.wait.until(EC.element_to_be_clickable((By.XPATH,'//android.widget.RelativeLayout[@resource-id="com.tencent.mm:id/bn"]/android.widget.LinearLayout/android.widget.RelativeLayout[2]')))
        el_contacts.click()

        el_official_accounts = self.wait.until(EC.element_to_be_clickable((By.ID,'com.tencent.mm:id/a50')))
        el_official_accounts.click()

        el_official_accounts_items = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,'//android.widget.LinearLayout[@resource-id="com.tencent.mm:id/a8p"]//android.widget.TextView[@resource-id="com.tencent.mm:id/a8s"]')))
        if el_official_accounts_items:
            exist_num = []
            max_num = len(el_official_accounts_items) - 1
            for i in range(article_read_num):
                if i >= len(el_official_accounts_items):
                    break

                random_num = self.get_random_num(exist_num,max_num)
                exist_num.append(random_num)

                el_item = el_official_accounts_items[random_num]
                self.click_unstable_el(el_item,'xpath','//android.widget.ImageButton[@content-desc="聊天信息"]')

                el_chat_info = self.wait.until(EC.element_to_be_clickable((By.XPATH,'//android.widget.ImageButton[@content-desc="聊天信息"]')))
                el_chat_info.click()

                el_latest_article = self.wait.until(EC.element_to_be_clickable((By.XPATH,'//android.support.v7.widget.RecyclerView[@resource-id="com.tencent.mm:id/b1x"]/android.widget.LinearLayout[1]')))
                el_latest_article.click()

                swipe_time = 0
                # 模拟阅读
                while True:
                    if self.is_el_displayed('id','js_toobar3',4/5) or swipe_time>=30:
                        break

                    self.swipe(1 / 2, 1 / 2, 1 / 2, 1 / 6, 1000)
                    swipe_time += 1
                    time.sleep(5 + random.random()*3)
                    # time.sleep(1)

                # 转发文章至朋友圈
                if if_share:
                    el_more = self.wait.until(EC.element_to_be_clickable((By.ID,'com.tencent.mm:id/jr')))
                    self.click_unstable_el(el_more,'xpath','//android.support.v7.widget.RecyclerView[@resource-id="com.tencent.mm:id/d3p"]//android.widget.TextView[@text="分享到朋友圈"]',1)

                    el_share_to_friend_circle = self.wait.until(EC.element_to_be_clickable((By.XPATH,'//android.support.v7.widget.RecyclerView[@resource-id="com.tencent.mm:id/d3p"]//android.widget.TextView[@text="分享到朋友圈"]')))
                    el_share_to_friend_circle.click()

                    el_publish = self.wait.until(EC.element_to_be_clickable((By.ID,'com.tencent.mm:id/jq')))
                    el_publish.click()

                succeed_num += 1
                self.emit_to_qt(self.serial, '阅读数', str(succeed_num))

                self.wait.until(EC.element_to_be_clickable((By.ID,'com.tencent.mm:id/k5')))
                self.press_back()

                self.wait.until(EC.element_to_be_clickable((By.ID, 'com.tencent.mm:id/k5')))
                self.press_back()

                self.wait.until(EC.element_to_be_clickable((By.ID, 'com.tencent.mm:id/jv')))
                self.press_back()

                time.sleep(random.randint(*read_share_interval))

                self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//android.widget.LinearLayout[@resource-id="com.tencent.mm:id/a8p"]//android.widget.TextView[@resource-id="com.tencent.mm:id/a8s"]')))


        self.return_to_index_page()


    # 朋友圈点赞
    def moments_thumbup(self,tactic):
        moments_swipe_num = tactic['moments_swipe_num']
        moments_thumbup_ratio = tactic['moments_thumbup_ratio']
        thumbup_interval = tactic['thumbup_interval']

        self.return_to_index_page()

        el_discover = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//android.widget.RelativeLayout[@resource-id="com.tencent.mm:id/bn"]/android.widget.LinearLayout/android.widget.RelativeLayout[3]')))
        el_discover.click()

        el_moments = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//android.widget.ListView[@resource-id="android:id/list"]/android.widget.LinearLayout[1]')))
        el_moments.click()

        swipe_num = 0
        while swipe_num < moments_swipe_num:
            if self.is_el_exist('xpath','//android.widget.FrameLayout[@resource-id="com.tencent.mm:id/efv"]'):
                moments_items = self.wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, '//android.widget.FrameLayout[@resource-id="com.tencent.mm:id/efv"]')))

                for item in moments_items:
                    if not self.if_thumbup(moments_thumbup_ratio):
                        continue

                    try:
                        # 查找评论按钮元素不稳定,放在循环里不断查找
                        while 1:
                            el_comment = item.find_element_by_xpath(
                                './/android.widget.ImageView[@resource-id="com.tencent.mm:id/eb6"]')
                            el_comment_height = el_comment.location['y']
                            if el_comment_height > 0.2 * self.y and el_comment_height < 0.9 * self.y:
                                el_comment.click()

                                el_thumbup = self.is_el_exist('id','com.tencent.mm:id/eae')
                                if el_thumbup:
                                    if el_thumbup.text.strip() == '赞':
                                        el_thumbup.click()
                                    else:
                                        el_comment.click()
                                        # 点击评论按钮时可能会点错位置跳到其他页面,判断当前页面是否为朋友圈,不是则按下返回
                                        time.sleep(3)
                                        if not self.is_el_exist('id', 'com.tencent.mm:id/ebi'):
                                            self.press_back()
                                            time.sleep(3)

                                    break

                                else:
                                    if not self.is_el_exist('id','com.tencent.mm:id/ebi'):
                                        self.press_back()
                                        time.sleep(3)

                            else:
                                break

                    except Exception as e:
                        continue

                    time.sleep(random.randint(*thumbup_interval))

            try:
                self.driver.find_element_by_id('com.tencent.mm:id/ah8')
                break
            except:
                self.swipe(1 / 2, 1 / 2, 1 / 2, 1 / 6, 1000)
                swipe_num += 1
                self.emit_to_qt(self.serial, '滑动数', str(swipe_num))

        self.return_to_index_page()


    # 发送消息
    def send_msg(self,tactic):
        chat_objects = tactic['chat_objects']
        msg_contents = tactic['msg_contents']
        send_msg_interval = tactic['send_msg_interval']

        friends = [obj['name'] for obj in chat_objects if obj['type'] == 1]
        groups = [obj['name'] for obj in chat_objects if obj['type'] == 2]
        filtered_friends = []

        succeed_num = 0
        self.return_to_index_page()

        # 过滤好友对象
        self.click_unstable_el_by_xpath('xpath','//android.widget.TextView[@resource-id="com.tencent.mm:id/d3t" and @text="通讯录"]','id','com.tencent.mm:id/m_')
        while len(filtered_friends) < len(friends):
            el_contacts = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,'//android.widget.ListView[@resource-id="com.tencent.mm:id/m_"]/android.widget.LinearLayout/android.widget.LinearLayout')))
            for el_friend in el_contacts:
                try:
                    el_friend_name = el_friend.find_element_by_xpath('.//android.view.View[@resource-id="com.tencent.mm:id/n8"]')
                    friend_name = el_friend_name.text
                    if friend_name in friends and friend_name not in filtered_friends:
                        filtered_friends.append(friend_name)

                except:
                    continue

            try:
                self.driver.find_element_by_id('com.tencent.mm:id/azr')
                break
            except:
                self.swipe(1 / 2, 1 / 2, 1 / 2, 1 / 6, 1000)

        chat_objs = groups + filtered_friends

        # 发送消息
        el_search = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//android.support.v7.widget.LinearLayoutCompat/android.widget.RelativeLayout[1]')))
        el_search.click()

        for chat_obj in chat_objs:
            el_search_bar = self.wait.until(EC.presence_of_element_located((By.ID,'com.tencent.mm:id/ka')))
            el_search_bar.send_keys(chat_obj)

            if self.is_el_exist('xpath','//android.widget.ListView[@resource-id="com.tencent.mm:id/buk"]/android.widget.RelativeLayout[2]'):
                el_first_result = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//android.widget.ListView[@resource-id="com.tencent.mm:id/buk"]/android.widget.RelativeLayout[2]')))
                el_first_result.click()

                el_msg_bar = self.wait.until(EC.presence_of_element_located((By.ID,'com.tencent.mm:id/alm')))
                el_msg_bar.send_keys(random.choice(msg_contents))

                el_send = self.wait.until(EC.element_to_be_clickable((By.ID,'com.tencent.mm:id/als')))
                el_send.click()

                succeed_num += 1
                self.emit_to_qt(self.serial, '消息数', str(succeed_num))

                self.wait.until(EC.presence_of_element_located((By.ID,'com.tencent.mm:id/jv')))
                self.press_back()

                time.sleep(random.randint(*send_msg_interval))

        self.return_to_index_page()

    def switch_accounts(self):
        '''
        切换账号并判断是否需要执行策略
        :return: True代表该设备存在多账号,且需要执行策略;False代表该设备不存在多账号或不需要执行策略
        '''
        # 点击我 点击设置
        el_setting = self.click_unstable_el_by_xpath('xpath','//android.widget.TextView[@resource-id="com.tencent.mm:id/d3t" and @text="我"]','xpath','//android.widget.TextView[@resource-id="android:id/title" and @text="设置"]')
        time.sleep(5)
        el_setting.click()

        # 点击切换账号
        el_switch_accounts = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//android.widget.TextView[@resource-id="android:id/title" and @text="切换帐号"]')))
        el_switch_accounts.click()

        # 点击知道了(首次进入会弹出)
        el_ok = self.is_el_exist('id','com.tencent.mm:id/ayb')
        if el_ok:
            el_ok.click()

        # 获取所有账号
        el_accounts = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,'//android.widget.GridLayout[@resource-id="com.tencent.mm:id/e46"]/android.widget.LinearLayout')))

        # 循环每个账号,查找‘当前账号’标志的元素,找不到表示该账号为待切换账号
        for el_account in el_accounts:
            try:
                el_account.find_element_by_id('com.tencent.mm:id/e4a')
            except:
                # 切换账号,判断该账号是否需要执行策略
                el_account_name = el_account.find_element_by_xpath('.//android.widget.TextView[@resource-id="com.tencent.mm:id/e4_"]')
                if el_account_name.text.strip() != '切换帐号':
                    el_account_pic = el_account.find_element_by_xpath('.//android.widget.ImageView[@resource-id="com.tencent.mm:id/e48"]')
                    el_account_pic.click()

                    # 检测是否需要输入密码
                    el_pwd = self.is_el_exist('id','com.tencent.mm:id/ka',30)
                    if el_pwd:
                        el_current_account = self.wait.until(EC.presence_of_element_located((By.ID,'com.tencent.mm:id/cmt')))
                        current_account = el_current_account.text.strip().replace(' ','')

                        el_pwd.send_keys(WECHAT_PASSWORD)
                        el_login = self.wait.until(EC.element_to_be_clickable((By.ID,'com.tencent.mm:id/cmw')))
                        el_login.click()

                        # 若密码错误,返回至切换账号界面,选择原账号并登录
                        el_pwd_error = self.is_el_exist('id', 'com.tencent.mm:id/ayb',5)
                        if el_pwd_error:
                            logging.warning(f'Wrong Password:{self.serial} {current_account}')

                            self.press_back(sleep=3)
                            self.press_back(sleep=3)
                            el_accounts_2 = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,
                                                                                               '//android.widget.GridLayout[@resource-id="com.tencent.mm:id/e46"]/android.widget.LinearLayout')))
                            for el_account_2 in el_accounts_2:
                                el_name = el_account.find_element_by_xpath('.//android.widget.TextView[@resource-id="com.tencent.mm:id/e4_"]')
                                if current_account not in el_name.text:
                                    el_pic = el_account_2.find_element_by_xpath('.//android.widget.ImageView[@resource-id="com.tencent.mm:id/e48"]')
                                    el_pic.click()

                                    self.wait.until(EC.presence_of_element_located((By.XPATH,
                                                                                    '//android.widget.RelativeLayout[@resource-id="com.tencent.mm:id/bn"]/android.widget.LinearLayout/android.widget.RelativeLayout[1]')))

                                    return False

                    self.wait.until(EC.presence_of_element_located((By.XPATH,'//android.widget.RelativeLayout[@resource-id="com.tencent.mm:id/bn"]/android.widget.LinearLayout/android.widget.RelativeLayout[1]')))
                    self.click_unstable_el_by_xpath('xpath','//android.widget.TextView[@resource-id="com.tencent.mm:id/d3t" and @text="我"]','xpath','//android.widget.TextView[@resource-id="android:id/title" and @text="设置"]')

                    el_wechat_name = self.wait.until(EC.presence_of_element_located((By.ID, 'com.tencent.mm:id/a5b')))
                    if el_wechat_name.text not in self.finished_accounts:
                        self.current_wechat_name = el_wechat_name.text
                        self.emit_to_qt(self.serial, '当前账号', self.current_wechat_name)
                        return True

                break

        self.return_to_index_page()

    def run_tactics(self):
        my_tactics = TACTICS[self.current_tactic:]

        for tactic in my_tactics:
            tactic_num = str(self.current_tactic + 1)
            if len(self.finished_accounts) >= 1:
                tactic_num += '*'
            self.emit_to_qt(self.serial, '策略号', tactic_num)

            if SCREEN_OFF:
                self.awake_and_unlock_screen()

            type = tactic['type']
            interval = tactic['tactic_interval']
            if type == 0:
                self.concern_official_accounts(tactic)

            elif type == 1:
                self.read_share_articles(tactic)

            elif type == 2:
                self.moments_thumbup(tactic)

            elif type == 3:
                self.send_msg(tactic)

            self.current_tactic += 1

            if SCREEN_OFF:
                self.driver.press_keycode(26)

            time.sleep(interval * 60)

        self.finished_accounts.append(self.current_wechat_name)

    def run(self):
        # 更新设备状态为'运行中'
        self.emit_to_qt(self.serial,'状态',DEVICE_STATE_DICT[4])

        # 唤醒屏幕
        self.awake_and_unlock_screen()

        # 关闭消息提醒
        self.close_open_notify(0)

        # 运行策略
        self.run_tactics()

        if SWITCH_ACCOUNTS:
            if self.switch_accounts():
                self.current_tactic = 0
                self.run_tactics()

        # 开启消息提醒
        self.close_open_notify(1)

        logging.info(f'Finished.{self.serial}')
        self.emit_to_qt(self.serial, '状态', DEVICE_STATE_DICT[5])

        self.quit()

    def restart(self):
        try:
            self.driver.quit()
        except:
            pass

        for i in range(3):
            try:
                logging.info(f'Restart port:{self.port} serial:{self.serial} desired_caps:{self.desired_caps}')
                self.driver = webdriver.Remote(f'http://localhost:{self.port}/wd/hub', self.desired_caps)
                self.__init__(self.deviceName,self.serial,self.port,self.driver,self.desired_caps,self.current_tactic)
                break
            except Exception as e:
                time.sleep(5)
                logging.warning(f'Restart to Get Driver Failed:{e} {self.serial} Retrying:{i+1}')


def run_driver(deviceName, serial, port, driver, desired_caps):
    auto_tool = WRAAutoTool(deviceName, serial, port, driver, desired_caps)

    retry_cnt = 0
    for i in range(100):
        try:
            auto_tool.run()
            return
        except Exception as e:
            time.sleep(60)
            retry_cnt += 1
            logging.error(f'Running Error:{e} {serial} Retrying:{retry_cnt}')
            auto_tool.restart()

    auto_tool.emit_to_qt(serial, '状态', DEVICE_STATE_DICT[6])





def test():
    desired_caps = {
        "platformName": "Android",
        "deviceName": 'MI_MAX',
        "appPackage": "com.tencent.mm",
        "appActivity": ".ui.LauncherUI",
        "noReset": True,
        'unicodeKeyboard': True,
        'newCommandTimeout': 86400,
    }

    driver = webdriver.Remote(f'http://localhost:4723/wd/hub', desired_caps)
    auto_tool = WRAAutoTool('MI_MAX','1b05e24e',4723,driver,desired_caps)
    auto_tool.awake_and_unlock_screen()
    auto_tool.close_open_notify(0)

    # auto_tool.quit()


if __name__ == '__main__':
    test()
