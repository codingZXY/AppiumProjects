import os
import sys
import re
import time
# import usb.core



def get_devices():
    devices = []
    ret = os.popen('adb devices -l')
    devices_info = [i for i in ret.readlines() if 'model' in i]
    ret.close()
    for info in devices_info:
        serial = str(re.search(r'(.*?)device', info).group(1).strip())
        devices.append(serial)

    return devices

def get_window_size(device):
    ret = os.popen(f'adb -s {device} shell wm size')
    result = ret.read()
    ret.close()

    if result:
        clear_btn_loc = re.search(r'Physical size: (\d+)x(\d+)', result)
        x = int(clear_btn_loc.group(1))
        y = int(clear_btn_loc.group(2))

        return x,y

def device_check():
    ret = os.popen('adb devices -l')
    devices_info = [i for i in ret.readlines() if 'model' in i]
    ret.close()
    print(f'设备数量:{len(devices_info)}\n')
    print('详细信息:')
    device_serials = []
    for i, info in enumerate(devices_info):
        serial = str(re.search(r'(.*?)device', info).group(1).strip())
        deviceName = re.search(r'model:(.*?) device', info).group(1).strip()
        device_serials.append(serial)
        print(f'序列号:{serial} 		机型:{deviceName}')

    print('')
    return device_serials

def clear_cache():
    devices = get_devices()
    for device in devices:
        ret = os.popen(f'adb -s {device} shell input keyevent 3')
        ret.close()

        ret = os.popen(f'adb -s {device} shell input keyevent 82')
        ret.close()

        x,y = get_window_size(device)
        x *= 0.5
        y *= 0.9

        ret = os.popen(f'adb -s {device} shell input tap {x} {y}')
        ret.close()
        print(f'设备 {device} 操作成功')


# 唤醒并解锁屏幕
def awake_and_unlock_screen():
    devices = get_devices()
    for device in devices:
        ret1 = os.popen(f'adb -s {device} shell "dumpsys window policy|grep isStatusBarKeyguard"')
        result1 = ret1.read()
        ret1.close()

        ret2 = os.popen(f'adb -s {device} shell "dumpsys window policy|grep mShowingLockscreen"')
        result2 = ret2.read()
        ret2.close()

        ret3 = os.popen(f'adb -s {device} shell "dumpsys window policy|grep mScreenOnEarly"')
        result3 = ret3.read()
        ret3.close()

        if 'isStatusBarKeyguard=true' in result1 or 'mShowingLockscreen=true' in result2:
            x, y = get_window_size(device)
            x1, y1, x2, y2 = 1 / 2 * x, 9 / 10 * y, 1 / 2 * x, 1 / 10 * y

            if 'mScreenOnEarly=false' in result3:
                ret = os.popen(f'adb -s {device} shell input keyevent 26')
                ret.close()

            ret = os.popen(f'adb -s {device} shell input swipe {x1} {y1} {x2} {y2}')
            ret.close()

        print(f'设备 {device} 操作成功')

def click_by_keycode(keycode):
    devices = get_devices()
    for device in devices:
        ret = os.popen(f'adb -s {device} shell input keyevent {keycode}')
        ret.close()

        print(f'设备 {device} 操作成功')

def install_app(device,filename):
    ret = os.popen(f'adb -s {device} install -r {filename}')

    x,y = get_window_size(device)
    x*=0.25
    y*=0.91

    time.sleep(10)

    tap_install = os.popen(f'adb -s {device} shell input tap {x} {y}')
    tap_install.close()

    result = ret.read()
    ret.close()
    if result.strip() == 'Success':
        print(f'设备 {device} 安装成功')

def update_version(app_filename,package_name,update_version):
    devices = get_devices()

    # filename = (os.path.dirname(__file__) + '/' + app_filename).replace('\\', '/')
    filename = (os.path.dirname(os.path.realpath(sys.argv[0])) + '/' + app_filename).replace('\\', '/')
    print(filename)
    if not os.path.exists(filename):
        print('apk文件不存在,请将apk文件与该程序放在同一目录下\n')
        return

    for device in devices:
        ret = os.popen(f'adb -s {device} shell pm dump {package_name} | findstr "versionName"')
        result = ret.read()
        ret.close()

        version = re.search(r'versionName=(.*)',result)
        if version:
            version = version.group(1).strip()
            if version != update_version:
                print(f'设备 {device} 的版本为{version},需更新为 {update_version},正在卸载旧版本...')
                ret = os.popen(f'adb -s {device} shell pm uninstall {package_name}')
                result = ret.read()
                ret.close()

                if result.strip() == 'Success':
                    print(f'设备 {device} 卸载旧版本成功,正在安装...')
                    install_app(device,filename)

            else:
                print(f'设备 {device} 的app版本正确,无需更新')

        else:
            print(f'设备 {device} 未安装该app,正在安装...')
            install_app(device, filename)

def reset_keyboard():
    devices = get_devices()
    for device in devices:
        ret = os.popen(f'adb -s {device} shell ime set com.sohu.inputmethod.sogou.xiaomi/.SogouIME')
        ret.close()
        print(f'设备 {device} 操作成功')

# def reconnect_device():
#     cnt = 0
#     try:
#         devs = list(usb.core.find(find_all=1))
#         for dev in devs:
#             print(f'正在重连设备 {dev.serial_number} ')
#             dev.reset()
#             cnt += 1
#
#
#         print(f'重连设备数:{cnt}')
#
#     except Exception as e:
#         print(f'重连失败:{e}')

print('命令:\n0:设备检测\n1:点击菜单\n2:点击HOME\n3:清除缓存\n4:唤醒并解锁\n5:重置输入法\n6:按下电源键\n7:按下拨号键\n'
      '11:更新抖音版本\n12:更新小红书版本\n13:更新微信版本\n14:更新QQ版本\n98:设备重连\n99:退出\n')
while True:
    command = input('\n请输入命令进行相应操作:')

    try:
        command = int(command)
        if command == 0:
            device_check()
        elif command == 1:
            click_by_keycode(82)
        elif command == 2:
            click_by_keycode(3)
        elif command == 3:
            clear_cache()
        elif command == 4:
            awake_and_unlock_screen()
        elif command == 5:
            reset_keyboard()
        elif command == 6:
            click_by_keycode(26)
        elif command == 7:
            click_by_keycode(5)
        elif command == 11:
            update_version('com.ss.android.ugc.aweme_380.apk', 'com.ss.android.ugc.aweme', '3.8.0')
        elif command == 12:
            update_version('com.xingin.xhs_5.35.1_5351001.apk', 'com.xingin.xhs', '5.35.1')
        elif command == 13:
            update_version('com.tencent.mm_7.0.0_1380.apk', 'com.tencent.mm', '7.0.0')
        elif command == 14:
            update_version('com.tencent.mobileqq_7.9.8_999.apk', 'com.tencent.mobileqq', '7.9.8')

        # elif command == 98:
        #     reconnect_device()

        elif command == 99:
            break
        else:
            print('未知命令,请重新输入\n')

    except Exception as e:
        print('未知命令,请重新输入\n')
        print('错误:',e)
