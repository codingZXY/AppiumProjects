# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qqaf_auto_tool_ui.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(642, 572)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(20, 20, 601, 221))
        self.groupBox.setStyleSheet("#groupBox{border:1px solid}")
        self.groupBox.setObjectName("groupBox")
        self.pb_import_data_source = QtWidgets.QPushButton(self.groupBox)
        self.pb_import_data_source.setGeometry(QtCore.QRect(99, 27, 75, 23))
        self.pb_import_data_source.setObjectName("pb_import_data_source")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(23, 33, 48, 16))
        self.label.setObjectName("label")
        self.lb_data_source_info = QtWidgets.QLabel(self.groupBox)
        self.lb_data_source_info.setGeometry(QtCore.QRect(180, 33, 401, 16))
        self.lb_data_source_info.setText("")
        self.lb_data_source_info.setObjectName("lb_data_source_info")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(21, 70, 54, 12))
        self.label_3.setObjectName("label_3")
        self.te_verify_msg = QtWidgets.QTextEdit(self.groupBox)
        self.te_verify_msg.setGeometry(QtCore.QRect(100, 70, 411, 71))
        self.te_verify_msg.setObjectName("te_verify_msg")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(20, 160, 54, 12))
        self.label_4.setObjectName("label_4")
        self.le_add_interval_2 = QtWidgets.QLineEdit(self.groupBox)
        self.le_add_interval_2.setGeometry(QtCore.QRect(168, 157, 61, 20))
        self.le_add_interval_2.setObjectName("le_add_interval_2")
        self.le_add_interval_1 = QtWidgets.QLineEdit(self.groupBox)
        self.le_add_interval_1.setGeometry(QtCore.QRect(98, 157, 61, 20))
        self.le_add_interval_1.setObjectName("le_add_interval_1")
        self.label_13 = QtWidgets.QLabel(self.groupBox)
        self.label_13.setGeometry(QtCore.QRect(160, 160, 21, 16))
        self.label_13.setObjectName("label_13")
        self.pb_start = QtWidgets.QPushButton(self.groupBox)
        self.pb_start.setGeometry(QtCore.QRect(520, 190, 75, 23))
        self.pb_start.setObjectName("pb_start")
        self.pb_import_verify_msg = QtWidgets.QPushButton(self.groupBox)
        self.pb_import_verify_msg.setGeometry(QtCore.QRect(520, 70, 41, 23))
        self.pb_import_verify_msg.setObjectName("pb_import_verify_msg")
        self.pb_export_verify_msg = QtWidgets.QPushButton(self.groupBox)
        self.pb_export_verify_msg.setGeometry(QtCore.QRect(520, 118, 41, 23))
        self.pb_export_verify_msg.setObjectName("pb_export_verify_msg")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 260, 601, 281))
        self.groupBox_2.setStyleSheet("#groupBox_2{border:1px solid}")
        self.groupBox_2.setObjectName("groupBox_2")
        self.tableView = QtWidgets.QTableView(self.groupBox_2)
        self.tableView.setGeometry(QtCore.QRect(10, 20, 581, 251))
        self.tableView.setObjectName("tableView")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(20, 240, 601, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "QQ加好友"))
        self.groupBox.setTitle(_translate("MainWindow", "配置信息"))
        self.pb_import_data_source.setText(_translate("MainWindow", "导入"))
        self.label.setText(_translate("MainWindow", "数据来源"))
        self.label_3.setText(_translate("MainWindow", "验证消息"))
        self.te_verify_msg.setPlaceholderText(_translate("MainWindow", "每行一句,随机抽取"))
        self.label_4.setText(_translate("MainWindow", "间隔（秒）"))
        self.label_13.setText(_translate("MainWindow", "-"))
        self.pb_start.setText(_translate("MainWindow", "开始"))
        self.pb_import_verify_msg.setText(_translate("MainWindow", "导入"))
        self.pb_export_verify_msg.setText(_translate("MainWindow", "导出"))
        self.groupBox_2.setTitle(_translate("MainWindow", "设备信息"))


