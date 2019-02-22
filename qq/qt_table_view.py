# -*- coding: utf-8 -*-

from settings import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import re
import subprocess


class DevicesTableView():
    def __init__(self,tableView,TableDataSignal):
        self.devices = []
        self.tableView = tableView
        self.TableDataSignal = TableDataSignal
        self.TableDataSignal.connect(self.update_device)

        # 列表初始化
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(DEVICE_HEADERS)
        self.tableView.setModel(self.model)

        # 水平方向标签拓展剩下的窗口部分，填满表格
        self.tableView.horizontalHeader().setStretchLastSection(True)
        # 水平方向，表格大小拓展到适当的尺寸
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 禁止单元格编辑
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def list_bind(self, init=False):
        '''
        绑定列表
        :param init: 是否初始化，默认为False；传入init为True时用于列表初始化，不执行update_devices方法
        :return:
        '''
        current_devices = self.get_devices()

        # 添加原无现有的设备至设备列表
        self.append_devices(current_devices)

        # 将原有现无,且原状态不为连接中断的设备,更新为连接中断；将原有现有,且原状态为连接中断的设备,更新为重连成功
        if not init:
            self.update_devices(current_devices)

    def get_devices(self):
        '''
        获取当前连接的设备信息
        :return: 当前连接的设备序列号列表
        '''
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

    def append_devices(self,current_devices):
        '''
        添加设备至设备列表
        :param current_devices: 当前连接设备
        :return:
        '''
        for device in current_devices:
            if device not in self.devices:
                device_model = DeviceInfo()
                device_model.device_serial = device

                state_item = MyQStandardItem(DEVICE_STATE_DICT[device_model.device_state])
                state_item.setForeground(QBrush(QColor(*CORLOR_GREEN)))

                self.model.appendRow([
                    MyQStandardItem(device_model.device_serial,align=Qt.AlignLeft|Qt.AlignVCenter),
                    state_item,
                ])

                self.devices.append(device)

    def update_devices(self,current_devices):
        '''
        将当前连接设备与原连接设备对比，更新设备列表
        :param current_devices:
        :return:
        '''
        for device in self.devices:
            item = self.model.findItems(device, Qt.MatchExactly, column=HEADERS_INDEX_DICT['设备'])
            row = item[0].row()
            column = HEADERS_INDEX_DICT['状态']
            state = DEVICE_STATE_NAME_DICT[str(self.model.data(self.model.index(row, column)))]

            '''
            检测原设备是否存在当前连接的设备中,
            不存在代表该设备失去连接，需要将状态改为连接中断;
            存在但设备状态为连接中断的,代表设备曾经断过,需要将状态改为重连成功
            '''
            if device not in current_devices:
                self.TableDataSignal.emit(device, '状态', DEVICE_STATE_DICT[7])
                QApplication.processEvents()
            else:
                if state == 7:
                    self.TableDataSignal.emit(device, '状态', DEVICE_STATE_DICT[9])

    def update_device(self, serial, field_name, data):
        '''
        更新设备信息
        :param serial: 要更新的设备的序列号
        :param field_name: 要更新的字段名
        :param data: 更新的数据内容
        :return:
        '''
        item = self.model.findItems(serial, Qt.MatchExactly, column=HEADERS_INDEX_DICT['设备'])
        row = item[0].row()
        column = HEADERS_INDEX_DICT[field_name]

        self.update_item(row, column, data)

    def update_item(self, row, column, data):
        '''
        根据行列坐标更新列表数据，若更新的字段为状态，则根据状态更新为自定义的颜色
        :param row: 行号
        :param column: 列号
        :param data: 更新的数据内容
        :return:
        '''
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

    def init_table_info(self):
        '''
        初始化列表信息
        :return:
        '''
        for row in range(0,self.model.rowCount()):
            for column in range(2,self.model.columnCount()):
                self.update_item(row, column, '')



class MyQStandardItem(QStandardItem):
    def __init__(self,data,align=Qt.AlignCenter):
        super().__init__(data)
        self.setTextAlignment(align)
