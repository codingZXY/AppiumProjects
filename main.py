# -*- coding: utf-8 -*-

from pytransform import pyarmor_runtime
import wra_auto_tool_ui
import oauth
from settings import *
from wra_auto_tool_multi import WRAAutoToolMulti
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json
import os
import re
# import usb.core
import logging
import time
import subprocess



class WRAQt(QtWidgets.QMainWindow, wra_auto_tool_ui.Ui_MainWindow):
    TableDataSignal = pyqtSignal(str, str, str)

    def __init__(self):
        self.tactics = []
        self.start_flag = 0
        self.default_tactics_filename = 'default.json'
        self.devices = []
        self.auto_reconnect = False

        QtWidgets.QMainWindow.__init__(self)
        wra_auto_tool_ui.Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.initUi()

    def initUi(self):

        # region 事件绑定

        # tab-关注公众号
        self.pb_add_official_accounts.clicked.connect(self.click_pb_add_official_accounts)
        self.pb_clear_official_accounts.clicked.connect(self.click_pb_clear_official_accounts)
        self.pb_add_tactic0.clicked.connect(self.click_pb_add_tactic0)

        # tab-文章阅读转发
        self.pb_add_tactic1.clicked.connect(self.click_pb_add_tactic1)

        # tab-朋友圈点赞
        self.pb_add_tactic2.clicked.connect(self.click_pb_add_tactic2)

        # tab-聊天消息
        self.pb_add_chat_objects.clicked.connect(self.click_pb_add_chat_objects)
        self.pb_clear_chat_objects.clicked.connect(self.click_pb_clear_chat_objects)

        self.pb_add_msg_contents.clicked.connect(self.click_pb_add_msg_contents)
        self.pb_clear_msg_contents.clicked.connect(self.click_pb_clear_msg_contents)

        self.pb_add_tactic3.clicked.connect(self.click_pb_add_tactic3)

        # 策略信息
        self.pb_import_tactics.clicked.connect(self.click_pb_import_tactics)
        self.pb_export_tactics.clicked.connect(self.click_pb_export_tactics)
        self.pb_clear_tactics.clicked.connect(self.click_pb_clear_tactics)
        self.pb_start.clicked.connect(self.click_pb_start)

        self.TableDataSignal.connect(self.update_device)

        # endregion

        # region 设置默认值

        # tab-关注公众号
        self.le_concern_num.setText('5')
        self.le_concern_interval_1.setText('5')
        self.le_concern_interval_2.setText('10')
        self.le_tactic0_interval.setText('5')

        # tab-文章阅读转发
        self.le_article_read_num.setText('3')
        self.cb_if_share.setChecked(False)
        self.le_read_share_interval_1.setText('5')
        self.le_read_share_interval_2.setText('10')
        self.le_tactic1_interval.setText('5')

        # tab-朋友圈点赞
        self.le_moments_swipe_num.setText('10')
        self.le_moments_thumbup_ratio.setText('70')
        self.le_thumbup_interval_1.setText('0')
        self.le_thumbup_interval_2.setText('2')
        self.le_tactic2_interval.setText('5')

        # tab-聊天消息
        self.le_send_msg_interval_1.setText('5')
        self.le_send_msg_interval_2.setText('10')
        self.le_tactic3_interval.setText('5')

        # 熄屏
        self.cb_screen_off.setChecked(False)
        self.cb_screen_off.setVisible(False)

        # endregion

        # region 公众号初始化
        if os.path.exists('oa.json'):
            try:
                oa_list = json.load(open('oa.json', 'r'))
                for oa in oa_list:
                    self.te_official_accounts.append(oa)
            except:
                logging.info('OA Json File Not Correct.')

        # endregion

        # region 策略初始化
        if os.path.exists(self.default_tactics_filename):
            try:
                self.tactics = json.load(open(self.default_tactics_filename, 'r'))
                self.bind_te_current_tactics()
            except:
                logging.info('Default Tactic Json File Not Correct.')

        # endregion

        # region 列表初始化
        self.model = QStandardItemModel(0,7)
        self.model.setHorizontalHeaderLabels(DEVICE_HEADERS)
        self.tableView.setModel(self.model)

        # 水平方向标签拓展剩下的窗口部分，填满表格
        self.tableView.horizontalHeader().setStretchLastSection(True)
        # 水平方向，表格大小拓展到适当的尺寸
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 禁止单元格编辑
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)


        # 绑定列表
        self.list_bind(type=1)

        # endregion

        # region 启动设备检测定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.list_bind)
        self.timer.start(10000)

        # endregion

    # 绑定列表
    def list_bind(self,type=0):
        current_devices = self.get_devices()

        # 添加原无现有的设备至设备列表
        self.append_devices(current_devices)

        # 将原有现无,且原状态不为连接中断的设备,更新为连接中断；将原有现有,且原状态为连接中断的设备,更新为连接成功
        if type == 0:
            self.update_devices(current_devices)

    def append_devices(self,current_devices):
        for device in current_devices:
            if device not in self.devices:
                device_model = DeviceInfo()
                device_model.device_serial = device

                state_item = MyQStandardItem(DEVICE_STATE_DICT[device_model.device_state])
                state_item.setForeground(QBrush(QColor(*CORLOR_GREEN)))

                self.model.appendRow([
                    MyQStandardItem(device_model.device_serial,align=Qt.AlignLeft|Qt.AlignVCenter),
                    state_item,
                    MyQStandardItem(str(device_model.current_tactic)),
                    MyQStandardItem(str(device_model.concern_num)),
                    MyQStandardItem(str(device_model.read_num)),
                    MyQStandardItem(str(device_model.moments_swipe_num)),
                    MyQStandardItem(str(device_model.send_num)),
                ])

                self.devices.append(device)

    def update_devices(self,current_devices):
        for device in self.devices:
            item = self.model.findItems(device, Qt.MatchExactly, column=HEADERS_INDEX_DICT['设备'])
            row = item[0].row()
            column = HEADERS_INDEX_DICT['状态']
            state = DEVICE_STATE_NAME_DICT[str(self.model.data(self.model.index(row, column)))]

            '''
            检测原设备是否存在当前连接的设备中,
            不存在代表该设备失去连接，需要重连;
            存在但设备状态为连接中断的,代表设备曾经断过,需要将状态改为重连成功
            '''
            if device not in current_devices:
                if self.auto_reconnect:
                    self.TableDataSignal.emit(device, '状态', DEVICE_STATE_DICT[8])
                    if self.reconnect_device(device):
                        self.TableDataSignal.emit(device, '状态', DEVICE_STATE_DICT[9])
                    else:
                        self.TableDataSignal.emit(device, '状态', DEVICE_STATE_DICT[7])
                else:
                    self.TableDataSignal.emit(device, '状态', DEVICE_STATE_DICT[7])
            else:
                if state == 7:
                    self.TableDataSignal.emit(device, '状态', DEVICE_STATE_DICT[9])

    def update_device(self,serial,type,data):
        item = self.model.findItems(serial, Qt.MatchExactly, column=HEADERS_INDEX_DICT['设备'])
        row = item[0].row()
        column = HEADERS_INDEX_DICT[type]

        self.update_item(row, column, data)

    def get_devices(self):
        devices = []
        p = subprocess.Popen("adb devices -l", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
        for i in p.stdout.readlines():
            info = str(i,encoding='utf-8')
            if 'model' in info:
                serial = str(re.search(r'(.*?)device', info).group(1).strip())
                devices.append(serial)

        p.wait()
        p.terminate()

        return devices

    # region 界面交互
    def click_pb_add_official_accounts(self):
        official_account = self.le_official_account.text().strip()
        if official_account == '':
            self.showMessageBox('请输入公众号')
            return

        current_official_accounts = list(filter(None, self.te_official_accounts.toPlainText().split('\n')))
        if official_account in current_official_accounts:
            self.showMessageBox('该公众号已存在')
            return

        self.te_official_accounts.append(official_account)

    def click_pb_clear_official_accounts(self):
        self.te_official_accounts.setText('')

    def click_pb_add_chat_objects(self):
        chat_object = self.le_chat_object.text().strip()
        chat_object_type = self.cb_chat_object_type.currentIndex()
        chat_object_type_name = self.cb_chat_object_type.currentText()

        if chat_object == '':
            self.showMessageBox('请输入聊天对象')
            return

        if chat_object_type == 0:
            self.showMessageBox('请选择对象类型')
            return

        chat_object = f'({chat_object_type_name}){chat_object}'
        current_chat_objects = list(filter(None, self.te_chat_objects.toPlainText().split('\n')))
        if chat_object in current_chat_objects:
            self.showMessageBox('该聊天对象已存在')
            return

        self.te_chat_objects.append(chat_object)

    def click_pb_clear_chat_objects(self):
        self.te_chat_objects.setText('')

    def click_pb_add_msg_contents(self):
        msg_content = self.le_msg_content.text().strip()
        if msg_content == '':
            self.showMessageBox('请输入消息内容')
            return

        current_msg_contents = list(filter(None, self.te_msg_contents.toPlainText().split('\n')))
        if msg_content in current_msg_contents:
            self.showMessageBox('该消息内容已存在')
            return

        self.te_msg_contents.append(msg_content)

    def click_pb_clear_msg_contents(self):
        self.te_msg_contents.setText('')

    def click_pb_add_tactic0(self):
        if self.check_if_already_start():
            return

        if self.le_concern_num.text().strip().isdigit():
            concern_num = int(self.le_concern_num.text().strip())
            if concern_num <= 0:
                self.showMessageBox('关注数必须为大于1的整数')
                return
        else:
            self.showMessageBox('关注数必须为整数')
            return

        current_official_accounts = list(filter(None, self.te_official_accounts.toPlainText().split('\n')))
        if not current_official_accounts:
            self.showMessageBox('请至少添加一个公众号')
            return

        if self.check_interval(0,self.le_concern_interval_1.text(),self.le_concern_interval_2.text()):
            concern_interval_1 = int(self.le_concern_interval_1.text())
            concern_interval_2 = int(self.le_concern_interval_2.text())
        else:
            return

        if self.check_interval(1,self.le_tactic0_interval.text()):
            tactic0_interval = int(self.le_tactic0_interval.text())
        else:
            return

        self.tactics.append(
            {
                'type': 0,
                'name': '关注公众号',
                'concern_num': concern_num,
                'official_accounts': current_official_accounts,
                'concern_interval': (concern_interval_1,concern_interval_2),
                'tactic_interval': tactic0_interval
            }
        )

        self.bind_te_current_tactics()

    def click_pb_add_tactic1(self):
        if self.check_if_already_start():
            return

        if self.le_article_read_num.text().strip().isdigit():
            article_read_num = int(self.le_article_read_num.text().strip())
            if article_read_num <= 0:
                self.showMessageBox('阅读文章数必须为大于1的整数')
                return
        else:
            self.showMessageBox('阅读文章数必须为整数')
            return

        if self.check_interval(0, self.le_read_share_interval_1.text(), self.le_read_share_interval_2.text()):
            read_share_interval_1 = int(self.le_read_share_interval_1.text())
            read_share_interval_2 = int(self.le_read_share_interval_2.text())
        else:
            return

        if self.check_interval(1, self.le_tactic1_interval.text()):
            tactic1_interval = int(self.le_tactic1_interval.text())
        else:
            return

        if_share = self.cb_if_share.isChecked()

        self.tactics.append(
            {
                'type': 1,
                'name': '文章阅读转发',
                'article_read_num': article_read_num,
                'if_share': if_share,
                'read_share_interval': (read_share_interval_1,read_share_interval_2),
                'tactic_interval':tactic1_interval
            }
        )

        self.bind_te_current_tactics()

    def click_pb_add_tactic2(self):
        if self.check_if_already_start():
            return

        if self.le_moments_swipe_num.text().strip().isdigit():
            moments_swipe_num = int(self.le_moments_swipe_num.text().strip())
            if moments_swipe_num <= 0:
                self.showMessageBox('滑动次数必须为大于1的整数')
                return
        else:
            self.showMessageBox('滑动次数必须为整数')
            return

        if self.le_moments_thumbup_ratio.text().strip().isdigit():
            moments_thumbup_ratio = int(self.le_moments_thumbup_ratio.text().strip())
            if moments_thumbup_ratio < 0 or moments_thumbup_ratio > 100:
                self.showMessageBox('点赞概率必须为0-100的整数')
                return
        else:
            self.showMessageBox('点赞概率必须为整数')
            return

        if self.check_interval(0, self.le_thumbup_interval_1.text(), self.le_thumbup_interval_2.text()):
            thumbup_interval_1 = int(self.le_thumbup_interval_1.text())
            thumbup_interval_2 = int(self.le_thumbup_interval_2.text())
        else:
            return

        if self.check_interval(1, self.le_tactic2_interval.text()):
            tactic2_interval = int(self.le_tactic2_interval.text())
        else:
            return

        self.tactics.append(
            {
                'type': 2,
                'name': '朋友圈点赞',
                'moments_swipe_num': moments_swipe_num,
                'moments_thumbup_ratio':moments_thumbup_ratio,
                'thumbup_interval': (thumbup_interval_1,thumbup_interval_2),
                'tactic_interval':tactic2_interval
            }
        )

        self.bind_te_current_tactics()

    def click_pb_add_tactic3(self):
        if self.check_if_already_start():
            return

        current_chat_objects = self.get_current_chat_objects()
        if not current_chat_objects:
            self.showMessageBox('请至少添加一个聊天对象')
            return

        current_msg_contents = list(filter(None, self.te_msg_contents.toPlainText().split('\n')))
        if not current_msg_contents:
            self.showMessageBox('请至少添加一条消息内容')
            return

        if self.check_interval(0, self.le_send_msg_interval_1.text(), self.le_send_msg_interval_2.text()):
            send_msg_interval_1 = int(self.le_send_msg_interval_1.text())
            send_msg_interval_2 = int(self.le_send_msg_interval_2.text())
        else:
            return

        if self.check_interval(1, self.le_tactic3_interval.text()):
            tactic3_interval = int(self.le_tactic3_interval.text())
        else:
            return

        self.tactics.append(
            {
                'type': 3,
                'name': '聊天消息',
                'chat_objects': current_chat_objects,
                'msg_contents': current_msg_contents,
                'send_msg_interval': (send_msg_interval_1,send_msg_interval_2),
                'tactic_interval':tactic3_interval
            }
        )

        self.bind_te_current_tactics()

    def click_pb_import_tactics(self):
        if self.check_if_already_start():
            return

        reply = self.showMessageBox('导入策略会清空当前已维护策略,是否继续?',type='question')
        if reply != QMessageBox.Yes:
            return
        try:
            filename, _ = QFileDialog.getOpenFileName(self, "选取文件", "", "Json Files (*.json)")
            if filename:
                self.tactics = json.load(open(filename,'r'))
                self.bind_te_current_tactics()
        except:
            self.showMessageBox('导入失败,请检查文件内容是否正确')

    def click_pb_export_tactics(self):
        if not self.tactics:
            self.showMessageBox('当前无策略,不需要导出')
            return

        filename, _ = QFileDialog.getSaveFileName(self, "文件保存", "", "Json Files (*.json)")
        if filename:
            json.dump(self.tactics,open(filename,'w'))

    def click_pb_clear_tactics(self):
        if self.check_if_already_start():
            return

        self.tactics = []
        self.bind_te_current_tactics()

    def click_pb_start(self):
        if self.check_if_already_start():
            return

        if not self.tactics:
            self.showMessageBox('请至少添加一个策略')
            return

        self.init_table_info()
        self.save_default_tactics()

        self.start_flag = 1

        screen_off = self.cb_screen_off.isChecked()
        switch_accounts = self.cb_switch_accounts.isChecked()

        backend = Backend(self.tactics,self.TableDataSignal,screen_off,switch_accounts,self)
        backend.finish_signal.connect(self.update_flag)
        backend.start()

        self.pb_start.setDisabled(True)

    # endregion

    def init_table_info(self):
        '''
        初始化列表信息
        :return:
        '''
        for row in range(1,self.model.rowCount()):
            for column in range(2,self.model.columnCount()):
                if column == 2:
                    self.update_item(row,column,'未开始')
                elif column == 7:
                    self.update_item(row, column, '')
                else:
                    self.update_item(row,column,'0')

    def save_default_tactics(self):
        '''
        保存此次策略,下次程序初始化时使用
        :return:
        '''
        json.dump(self.tactics,open(self.default_tactics_filename,'w'))

    def update_flag(self,text):
        self.start_flag = 0
        self.pb_start.setDisabled(False)

    def update_item(self, row, column, data):
        new_item = MyQStandardItem(data)
        if column == HEADERS_INDEX_DICT['状态']:
            if data in GREEN_STATE:
                new_item.setForeground(QBrush(QColor(*CORLOR_GREEN)))

            elif data in BLUE_STATE:
                new_item.setForeground(QBrush(QColor(*CORLOR_BLUE)))

            elif data in ORANGE_STATE:
                new_item.setForeground(QBrush(QColor(*CORLOR_ORANGE)))

            elif data in RED_STATE:
                new_item.setForeground(QBrush(QColor(*CORLOR_RED)))


        self.model.setItem(row, column, new_item)

    # region 辅助方法

    def reconnect_device(self,device):
        try:
            # device_in_libusb = usb.core.find(serial_number=device)
            device_in_libusb = None
            if device_in_libusb is not None:
                device_in_libusb.reset()
                time.sleep(3)

                devices = self.get_devices()
                if device in devices:
                    logging.info(f'Reconnect Succeed:{device}')
                    return True

                else:
                    logging.warning(f'Reconnect Failed:device({device}) lost connection')

            else:
                logging.warning(f'Reconnect Failed:device({device}) not exist in libusb')

        except Exception as e:
            logging.warning(e)

    def check_interval(self,type,*args):
        if type == 0:
            interval1,interval2 = args
            if interval1.isdigit() and interval2.isdigit():
                interval1,interval2 = int(interval1),int(interval2)
                if interval1 <= interval2:
                    return True

                else:
                    self.showMessageBox('最小间隔必须小于等于最大间隔')
            else:
                self.showMessageBox('间隔必须为整数')

        elif type == 1:
            interval = args[0]
            if interval.isdigit():
                return True
            else:
                self.showMessageBox('策略间隔必须为整数')

    def get_current_chat_objects(self):
        current_chat_objects = []
        objects_in_te = list(filter(None, self.te_chat_objects.toPlainText().split('\n')))
        for obj in objects_in_te:
            if obj.startswith('(好友)'):
                current_chat_objects.append({'name':obj[4:],'type':1})

            elif obj.startswith('(群聊)'):
                current_chat_objects.append({'name': obj[4:], 'type': 2})

        return current_chat_objects

    def check_if_already_start(self):
        if self.start_flag != 0:
            self.showMessageBox('当前有策略正在运行')
            return True
        else:
            return False

    def bind_te_current_tactics(self):
        self.te_current_tactics.setText('')

        for i, tactic in enumerate(self.tactics):
            type = tactic['type']
            name = tactic['name']

            info = ''
            if type == 0:
                concern_num = tactic['concern_num']
                official_accounts = tactic['official_accounts']
                concern_interval = tactic['concern_interval']
                tactic0_interval = tactic['tactic_interval']
                info = f'策略号:{i+1} \n 策略类型:{name} \n 关注数:{concern_num} \n 公众号:{official_accounts} \n 间隔:{concern_interval}秒 \n 策略间隔:{tactic0_interval}分钟 \n '

            elif type == 1:
                article_read_num = tactic['article_read_num']
                if_share = '是' if tactic['if_share'] else '否'
                read_share_interval = tactic['read_share_interval']
                tactic1_interval = tactic['tactic_interval']
                info = f'策略号:{i+1} \n 策略类型:{name} \n 阅读文章数:{article_read_num} \n 是否转发:{if_share} \n 间隔:{read_share_interval}秒 \n 策略间隔:{tactic1_interval}分钟 \n '

            elif type == 2:
                moments_swipe_num = tactic['moments_swipe_num']
                moments_thumbup_ratio = tactic['moments_thumbup_ratio']
                thumbup_interval = tactic['thumbup_interval']
                tactic2_interval = tactic['tactic_interval']
                info = f'策略号:{i+1} \n 策略类型:{name} \n 滑动次数:{moments_swipe_num} \n 点赞概率:{moments_thumbup_ratio} \n 间隔:{thumbup_interval}秒 \n 策略间隔:{tactic2_interval}分钟 \n '

            elif type == 3:
                chat_objects = tactic['chat_objects']
                msg_contents = tactic['msg_contents']
                send_msg_interval = tactic['send_msg_interval']
                tactic3_interval = tactic['tactic_interval']
                info = f'策略号:{i+1} \n 策略类型:{name} \n 聊天对象:{chat_objects} \n 消息内容:{msg_contents} \n 间隔:{send_msg_interval}秒 \n 策略间隔:{tactic3_interval}分钟 \n '

            self.te_current_tactics.append(info)

    def showMessageBox(self, msg, title='提示', type='information'):
        if type == 'information':
            QMessageBox.information(self, title, msg)
        elif type == 'question':
            reply = QMessageBox.question(self, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return reply

    # endregion


class Backend(QThread):
    finish_signal = pyqtSignal(str)

    def __init__(self,tactics,table_data_signal,screen_off,switch_accounts,parent=None):
        super(Backend, self).__init__(parent)
        self.tactics = tactics
        self.table_data_signal = table_data_signal
        self.screen_off = screen_off
        self.switch_accounts = switch_accounts

    def run(self):
        auto_obj = WRAAutoToolMulti(self.tactics,qt_signal=self.table_data_signal,screen_off=self.screen_off,switch_accounts=self.switch_accounts)
        auto_obj.init_settings()
        auto_obj.run()

        self.finish_signal.emit('Done')


class MyQStandardItem(QStandardItem):
    def __init__(self,data,align=Qt.AlignCenter):
        super().__init__(data)
        self.setTextAlignment(align)


if __name__ == '__main__':
    auth = oauth.if_auth()
    if auth:
        try:
            app = QApplication(sys.argv)
            window = WRAQt()
            window.show()
            sys.exit(app.exec())
        except Exception as e:
            logging.error(e)



