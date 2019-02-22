# -*- coding: utf-8 -*-

from pytransform import pyarmor_runtime
from qqaf_auto_tool_ui import Ui_MainWindow
import oauth
from settings import *
from qqaf_auto_tool_multi import QQAFAutoToolMulti
from qt_table_view import DevicesTableView
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json
import os
import re
import logging
import time
import subprocess
import pandas as pd
from oxls import export_from_mongoDB

class QQAFQt(QtWidgets.QMainWindow, Ui_MainWindow):
    # 表格数据信号,用于接收信号来改变表格内容
    TableDataSignal = pyqtSignal(str, str, str)

    def __init__(self):
        '''
        Qt窗口对象初始化
        '''
        self.add_qq_list = []
        self.start_flag = 0
        self.default_verify_msg_filename = 'default_verify_msg.json'

        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.initUi()

    def initUi(self):
        '''
        界面初始化
        :return:
        '''
        # 事件绑定
        self.pb_import_data_source.clicked.connect(self.click_pb_import_data_source)
        self.pb_import_verify_msg.clicked.connect(self.click_pb_import_verify_msg)
        self.pb_export_verify_msg.clicked.connect(self.click_pb_export_verify_msg)
        self.pb_start.clicked.connect(self.click_pb_start)

        # 设置默认值
        self.le_add_interval_1.setText('10')
        self.le_add_interval_2.setText('20')

        # 初始化默认验证消息
        if os.path.exists(self.default_verify_msg_filename):
            try:
                verify_msg_list = json.load(open(self.default_verify_msg_filename, 'r'))
                self.te_verify_msg.setText('\n'.join(verify_msg_list))
            except:
                logging.info('Verify Msg Json File Not Correct.')

        # 初始化设备列表
        self.device_table_view = DevicesTableView(self.tableView, self.TableDataSignal)
        self.device_table_view.list_bind(init=True)

        # 启动设备检测定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.device_table_view.list_bind)
        self.timer.start(10000)

    def click_pb_import_data_source(self):
        '''
        点击导入数据来源
        :return:
        '''
        if self.check_if_already_start():
            return

        fileName_choose, _ = QFileDialog.getOpenFileName(self, "选取文件", "", "All Files (*);;Excel Files (*.xlsx);;Excel Files (*.xls);;Csv Files (*.csv)")
        if fileName_choose == "":
            return

        self.parse_data_source(fileName_choose)

    def parse_data_source(self,filename):
        '''
        解析数据来源
        :param filename: 文件名
        :return:
        '''
        try:
            if '.xls' in filename or '.xlsx' in filename:
                df = pd.read_excel(filename)
            elif '.csv' in filename:
                df = pd.read_csv(filename)
            else:
                self.showMessageBox('文件格式不正确，请检查文件后缀是否为.xls/.xlsx/.csv')
                return

            data = df.values.tolist()
            self.add_qq_list = [{'name':i[0].strip(),'qq':str(i[1]).strip()} for i in data]
            self.lb_data_source_info.setText(f'QQ号总数：{len(self.add_qq_list)}')

        except Exception as e:
            self.showMessageBox(f'导入失败:{e}')

    def click_pb_import_verify_msg(self):
        if self.check_if_already_start():
            return

        fileName_choose, _ = QFileDialog.getOpenFileName(self, "选取文件", "", "Json Files (*.json)")
        if fileName_choose == "":
            return

        try:
            verify_msg_list = json.load(open(fileName_choose, 'r'))
            self.te_verify_msg.setText('\n'.join(verify_msg_list))

        except Exception as e:
            self.showMessageBox(f'导入失败:{e}')

    def click_pb_export_verify_msg(self):
        fileName_choose, _ = QFileDialog.getSaveFileName(self, "文件保存", "", "Json Files (*.json)")
        if fileName_choose == "":
            return

        verify_msg_list = self.te_verify_msg.toPlainText().split('\n')
        json.dump(verify_msg_list, open(fileName_choose, 'w'))

    def click_pb_start(self):
        if self.check_data() == False:
            return

        self.device_table_view.init_table_info()
        self.save_default_verify_msg()

        self.start_flag = 1

        verify_msg_list = self.te_verify_msg.toPlainText().split('\n')
        add_friends_interval = (int(self.le_add_interval_1.text()), int(self.le_add_interval_2.text()))

        backend = Backend(self.add_qq_list, verify_msg_list, add_friends_interval, self.TableDataSignal, self)
        backend.finish_signal.connect(self.update_flag)
        backend.start()

        self.pb_start.setDisabled(True)

    def save_default_verify_msg(self):
        '''
        保存此次验证消息，下次初始化时使用
        :return:
        '''
        verify_msg_list = self.te_verify_msg.toPlainText().split('\n')
        json.dump(verify_msg_list, open(self.default_verify_msg_filename, 'w'))

    def update_flag(self,text):
        self.start_flag = 0
        self.pb_start.setDisabled(False)

    def check_data(self):
        if_ok = True
        if len(self.add_qq_list) <= 0:
            self.showMessageBox('QQ号个数必须大于0')
            if_ok = False

        if self.te_verify_msg.toPlainText() == "":
            self.showMessageBox('验证消息不能为空')
            if_ok = False

        interval1,interval2 = self.le_add_interval_1.text(),self.le_add_interval_2.text()
        if interval1.isdigit() and interval2.isdigit():
            interval1, interval2 = int(interval1), int(interval2)
            if interval1 > interval2:
                self.showMessageBox('最小间隔必须小于等于最大间隔')
                if_ok = False
        else:
            self.showMessageBox('间隔必须为整数')
            if_ok = False

        return if_ok

    def check_if_already_start(self):
        if self.start_flag != 0:
            self.showMessageBox('正在添加好友,无法进行该操作')
            return True
        else:
            return False

    def click_pb_export_result(self):
        fileName_choose, _ = QFileDialog.getSaveFileName(self, "文件保存", "", "Excel Files (*.xlsx)")
        if fileName_choose == "":
            return

        field_mapping = {}


    def showMessageBox(self, msg, title='提示', type='i'):
        if type == 'i':
            QMessageBox.information(self, title, msg)
        elif type == 'q':
            reply = QMessageBox.question(self, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return reply


class Backend(QThread):
    finish_signal = pyqtSignal(str)

    def __init__(self,add_qq_list,verify_msg_list,add_friends_interval,table_data_signal,parent=None):
        super(Backend, self).__init__(parent)
        self.add_qq_list = add_qq_list
        self.verify_msg_list = verify_msg_list
        self.add_friends_interval = add_friends_interval
        self.table_data_signal = table_data_signal

    def run(self):
        auto_obj = QQAFAutoToolMulti(self.add_qq_list, self.verify_msg_list, self.add_friends_interval, qt_signal=self.table_data_signal)
        auto_obj.init_settings()
        auto_obj.run()

        self.finish_signal.emit('Done')


if __name__ == '__main__':
    # auth = oauth.if_auth()
    # if auth:
    try:
        app = QApplication(sys.argv)
        window = QQAFQt()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error(e)