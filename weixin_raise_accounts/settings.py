# -*- coding: utf-8 -*-



class DeviceInfo():
    device_serial = ''
    device_state = 0
    current_tactic = '未开始'
    concern_num = 0
    read_num = 0
    moments_swipe_num = 0
    send_num = 0
    current_account = ''

DEVICE_HEADERS = ['设备','状态','策略号','关注数','阅读数','滑动数','消息数','当前账号']


HEADERS_INDEX_DICT = {
    '设备':0,
    '状态':1,
    '策略号':2,
    '关注数':3,
    '阅读数':4,
    '滑动数':5,
    '消息数':6,
    '当前账号':7,
}

DEVICE_STATE_DICT = {
    0:'连接成功',
    1:'正在启动',
    2:'启动成功',
    3:'启动失败',
    4:'运行中',
    5:'运行完成',
    6:'运行异常',
    7:'连接中断',
    8:'断线重连',
    9:'重连成功',
}

DEVICE_STATE_NAME_DICT = {
    '连接成功':0,
    '正在启动':1,
    '启动成功':2,
    '启动失败':3,
    '运行中':4,
    '运行完成':5,
    '运行异常':6,
    '连接中断':7,
    '断线重连':8,
    '重连成功':9,
}

GREEN_STATE = ['连接成功','重连成功','运行完成']
BLUE_STATE = ['正在启动','启动成功','运行中']
RED_STATE = ['启动失败','运行异常','连接中断']
ORANGE_STATE = ['断线重连']

CORLOR_GREEN = (50,205,50)
CORLOR_BLUE = (0,0,255)
CORLOR_RED = (255,0,0)
CORLOR_ORANGE = (255,165,0)

# 微信密码,用于切换账号
WECHAT_PASSWORD = 'ss123123'