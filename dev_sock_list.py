# ** Copyright © Shenzhen Eview GPS Technology Co., Ltd.
# ** All Rights Reserved.
# @Time    : 2022-09-02
# @Author  : zhangyong
# @File    : dev_server.py
# @Software: Server Demo python3
import threading;

class deviceToSocketDict:
    def __init__(self):
        self.g_devices_dict = {
        };
        self.g_devices_dict_r = {
        };
        self.threadLock = threading.Lock();

    def __str__(self):
        result_s = "";
        result_s += str(self.g_devices_dict_r.values())+"\n";
        result_s += str(self.g_devices_dict.keys());
        return  result_s;

    def online(self, devId, sock):
        self.threadLock.acquire();
        if(devId in self.g_devices_dict):
            self.threadLock.release();
            print(f"[online] {devId}, failed!");
            return 0;
        if(sock in self.g_devices_dict_r):
            self.threadLock.release();
            print(f"[online] {devId}, failed!");
            return 0;
        self.g_devices_dict.update({devId:sock});
        self.g_devices_dict_r.update({sock:devId});
        self.threadLock.release();
        print(f"[online] {devId}");
        print(f"{self}");
        return 1;

    def offline(self, sock):
        self.threadLock.acquire();
        if(sock in self.g_devices_dict_r):
            devId = self.g_devices_dict_r[sock];
            del self.g_devices_dict_r[sock];
            if(devId in self.g_devices_dict):
                del self.g_devices_dict[devId];
            print(f"[offline] {devId}");
        self.threadLock.release();
        print(f"{self}");

    def find(self, devId):
        self.threadLock.acquire();
        sock = self.g_devices_dict.get(devId);
        self.threadLock.release();
        return sock;

    def getAllSocks(self):
        return self.g_devices_dict.values();
