# ** Copyright © Shenzhen Eview GPS Technology Co., Ltd.
# ** All Rights Reserved.
# @Time    : 2022-02-12
# @Author  : zhangyong
# @File    : dev_server.py
# @Software: Server Demo python3
from e_proto_com import *
import time

class ePacketDataCmd(ePacketCmd):
    def __init__(self):
        ePacketCmd.__init__(self, 0x01)

    def decode(cmdId, data):
        g_key_decode_dict = {
            0x24:keyGeneralData.decode,
            0x20:keyLocateGps.decode,
            0x01:keyDeviceId.decode
        }
        cmd = ePacketDataCmd();
        offset = 0;
        while offset < len(data):
            length = data[offset+0];
            keyId = data[offset+1];
            if(offset + length + 1 > len(data)):
                print(f"invalid key length {length}!");
                break;
            key_method_func = g_key_decode_dict.get(keyId, ePacketKeyUndef.decode)
            cmd.keys.append(key_method_func(keyId, data[offset+2:offset+2+length-1]));
            offset += 1 + length;
        return cmd;

class keyDeviceId(ePacketKey):
    def __init__(self, imei):
        ePacketKey.__init__(self, 0x01)
        self.devId = imei

    def __str__(self):
        result_s = "";
        result_s += f'"imei":{self.devId}'
        return result_s

    def serialize(self):
        data = []
        data.append(0x10)
        data.append(self.keyId)
        for i in range(len(self.devId)):
            data.append(ord(self.devId[i]))
        return data;

    def decode(keyId, data):
        key=keyDeviceId("");
        key.devId = data.decode();
        return key;

class keyGeneralData(ePacketKey):
    def __init__(self, utc_time):
        ePacketKey.__init__(self, 0x24)
        if(utc_time == 0):
            utc_time = int(time.time());
        #print(f"{utc_time}")
        self.utc_time = utc_time
        self.status = 0

    def __str__(self):
        result_s = "";
        result_s += f'"gps":{self.isGps()}\n';
        result_s += f'"utc_time":{self.utc_time}';
        return result_s

    def setGps(self, en):
        if(en != 0):
            self.status |= (1<<0);
        else:
            self.status &= ~(1<<0);
    def isGps(self):
        gp = True;
        if((self.status&(1<<0))==0):
            gp = False;
        return gp;

    def setWorkMode(self, mode):
        self.status &= ~((7)<<16);
        self.status |= ((mode&7)<<16);

    def setMobileStrength(self, level):
        self.status &= ~((0x1F)<<19);
        self.status |= ((level&0x1F)<<19);

    def setBatteryLevel(self, level):
        self.status &= ~((0xFF)<<24);
        self.status |= ((level&0xFF)<<24);

    def serialize(self):
        data = []
        data.append(0x09)
        data.append(self.keyId)
        data.append((self.utc_time >> 0) & 0xFF)
        data.append((self.utc_time >> 8) & 0xFF)
        data.append((self.utc_time >> 16) & 0xFF)
        data.append((self.utc_time >> 24) & 0xFF)
        data.append((self.status >> 0) & 0xFF)
        data.append((self.status >> 8) & 0xFF)
        data.append((self.status >> 16) & 0xFF)
        data.append((self.status >> 24) & 0xFF)
        return data;

    def decode(keyId, data):
        key=keyGeneralData(0);
        key.utc_time = data[0+3]&0xFF;
        key.utc_time <<= 8;
        key.utc_time |= data[0+2]&0xFF;
        key.utc_time <<= 8;
        key.utc_time |= data[0+1]&0xFF;
        key.utc_time <<= 8;
        key.utc_time |= data[0+0]&0xFF;

        key.status = data[4+3]&0xFF;
        key.status <<= 8;
        key.status |= data[4+2]&0xFF;
        key.status <<= 8;
        key.status |= data[4+1]&0xFF;
        key.status <<= 8;
        key.status |= data[4+0]&0xFF;
        return key;


class keyLocateGps(ePacketKey):
    def __init__(self, lat, lng, speed, direction, alt, acc, mil, sat_n):
        ePacketKey.__init__(self, 0x20)
        self.lat = lat
        self.lng = lng
        self.speed = speed
        self.direction = direction
        self.acc = acc
        self.alt = alt
        self.mil = mil
        self.sat_n = sat_n

    def __str__(self):
        result_s = "";
        result_s += f'"lat":{self.lat}\n';
        result_s += f'"lng":{self.lng}\n';
        result_s += f'"speed":{self.speed}\n';
        result_s += f'"direction":{self.direction}\n';
        result_s += f'"alt":{self.alt}\n';
        result_s += f'"acc":{self.acc}\n';
        result_s += f'"mil":{self.mil}\n';
        result_s += f'"sat_n":{self.sat_n}';
        return result_s

    def serialize(self):
        data = []
        data.append(0x16)
        data.append(self.keyId)
        data.append((self.lat >> 0) & 0xFF)
        data.append((self.lat >> 8) & 0xFF)
        data.append((self.lat >> 16) & 0xFF)
        data.append((self.lat >> 24) & 0xFF)
        data.append((self.lng >> 0) & 0xFF)
        data.append((self.lng >> 8) & 0xFF)
        data.append((self.lng >> 16) & 0xFF)
        data.append((self.lng >> 24) & 0xFF)
        data.append((self.speed >> 0) & 0xFF)
        data.append((self.speed >> 8) & 0xFF)
        data.append((self.direction >> 0) & 0xFF)
        data.append((self.direction >> 8) & 0xFF)
        data.append((self.alt >> 0) & 0xFF)
        data.append((self.alt >> 8) & 0xFF)
        data.append((self.acc >> 0) & 0xFF)
        data.append((self.acc >> 8) & 0xFF)
        data.append((self.mil >> 0) & 0xFF)
        data.append((self.mil >> 8) & 0xFF)
        data.append((self.mil >> 16) & 0xFF)
        data.append((self.mil >> 24) & 0xFF)
        data.append(self.sat_n)
        return data

    def decode(keyId, data):
        offset=0;
        lat = data[offset+3];
        lat <<= 8;
        lat |= data[offset+2]&0xFF;
        lat <<= 8;
        lat |= data[offset+1]&0xFF;
        lat <<= 8;
        lat |= data[offset+0]&0xFF;

        offset += 4;
        lng = data[offset+3];
        lng <<= 8;
        lng |= data[offset+2]&0xFF;
        lng <<= 8;
        lng |= data[offset+1]&0xFF;
        lng <<= 8;
        lng |= data[offset+0]&0xFF;

        offset += 4;
        speed = data[offset+1]&0xFF;
        speed <<= 8;
        speed |= data[offset+0]&0xFF;

        offset += 2;
        direction = data[offset+1]&0xFF;
        direction <<= 8;
        direction |= data[offset+0]&0xFF;

        offset += 2;
        alt = data[offset+1];
        alt <<= 8;
        alt |= data[offset+0]&0xFF;

        offset += 2;
        acc = data[offset+1]&0xFF;
        acc <<= 8;
        acc |= data[offset+0]&0xFF;

        offset += 2;
        mil = data[offset+3]&0xFF;
        mil <<= 8;
        mil |= data[offset+2]&0xFF;
        mil <<= 8;
        mil |= data[offset+1]&0xFF;
        mil <<= 8;
        mil |= data[offset+0]&0xFF;

        offset += 4;
        sat_n = data[offset+0]&0xFF;
        return keyLocateGps(lat, lng, speed, direction, alt, acc, mil, sat_n);