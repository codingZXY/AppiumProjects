
# 数据库信息
MONGO_CLIENT = 'localhost'
MONGO_DB = 'QQ'
MONGO_COLLECTION = 'AddRecord'

# 设备信息列表字段
DEVICE_HEADERS = ['设备','状态','当前账号','待添加']

# 设备信息类
class DeviceInfo():
    device_serial = ''
    device_state = 0
    current_account = ''
    wait_to_add = ''

# 设备状态字典
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

# 设备状态名称字典
DEVICE_STATE_NAME_DICT = {v:k for k,v in DEVICE_STATE_DICT.items()}


# 列头索引字典
HEADERS_INDEX_DICT = {
    '设备':0,
    '状态':1,
    '当前账号':2,
    '待添加':3,
}


# 设备状态颜色归类
GREEN_STATE = ['连接成功','重连成功','运行完成']
BLUE_STATE = ['正在启动','启动成功','运行中']
RED_STATE = ['启动失败','运行异常','连接中断']
ORANGE_STATE = ['断线重连']

# 颜色RGB设置
CORLOR_GREEN = (50,205,50)
CORLOR_BLUE = (0,0,255)
CORLOR_RED = (255,0,0)
CORLOR_ORANGE = (255,165,0)