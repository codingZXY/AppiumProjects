# -*- coding: utf-8 -*-
import uuid
from hashlib import sha224
import pickle
import ctypes
import subprocess
import re

AUTH_FILE = 'auth.config'

class AuthError(Exception):
    pass

def get_encrypted_mac(mac):
    mac = mac.replace('-','').lower()
    encrypt_mac = sha224(mac.encode())

    return encrypt_mac.hexdigest()

def create_allowed_macs(allow_macs):
    allow_macs = list(map(get_encrypted_mac,allow_macs))
    with open(AUTH_FILE,'wb') as f:
        pickle.dump(allow_macs,f)

def get_current_encrypted_mac():
    node = uuid.getnode()
    mac = uuid.UUID(int=node).hex[-12:]
    encrypt_mac = sha224(mac.encode())

    return encrypt_mac.hexdigest()

def get_current_encrypted_mac_yt():
    try:
        p = subprocess.Popen("ipconfig /all", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             shell=True)
        ipconfig_info = p.stdout.read().decode('gbk')

        patterns = [
            '以太网适配器 以太网:.*?物理地址.*?: (.{17})',
            '以太网适配器 本地连接:.*?物理地址.*?: (.{17})'
        ]

        m = None
        for pattern in patterns:
            m = re.search(pattern,ipconfig_info,re.S)
            if m != None:
                break

        mac = m.group(1).replace('-','').lower()
        # print(ipconfig_info)
        # print(mac)

        encrypt_mac = sha224(mac.encode())
        return encrypt_mac.hexdigest()

    except Exception as e:
        raise AuthError('Get Mac Failed: %s ' % e)

def get_allowed_macs():
    with open(AUTH_FILE,'rb') as f:
        allow_macs = pickle.load(f)
        return allow_macs

def if_auth():
    try:
        allowed = get_allowed_macs()
        current = get_current_encrypted_mac_yt()
        if current in allowed:
            return True
        else:
            ctypes.windll.user32.MessageBoxW(0, '您的计算机无权限对该程序进行操作！', '提示', 0)
            return False

    except Exception as e:
        ctypes.windll.user32.MessageBoxW(0, f'{e}', '错误', 0)
        return False




if __name__ == '__main__':
    allow_macs = ['B0-FC-36-78-C7-52','94-DE-80-3C-7B-94','00-E0-4C-06-6C-BC',
                  '1C-6F-65-BB-BA-4C','30-9C-23-C6-5F-38','08-00-27-20-4D-C0']
    create_allowed_macs(allow_macs)

    # get_current_encrypted_mac_yt()

