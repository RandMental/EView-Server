# ** Copyright © Shenzhen Eview GPS Technology Co., Ltd.
# ** All Rights Reserved.
# @Time    : 2022-09-02
# @Author  : zhangyong
# @File    : dev_server.py
# @Software: Server Demo python3

from e_proto_com import ePacketCmd
from e_proto_com import ePacketKey
import time

class ePacketCfgCmd(ePacketCmd):
    def __init__(self):
        ePacketCmd.__init__(self, 0x02)

    def decode(cmdId, data):
        g_key_decode_dict = {
            0x03:keyCfgDevId.decode,
            0x06:keyCfgSettingTime.decode,
            0x30:keyCfgAuthNumber.decode,
            0x52:keyCfgMotionAlert.decode,
            0x00:keyCfgDef.decode
        }
        cmd = ePacketCfgCmd();
        offset = 0;
        while offset < len(data):
            length = data[offset+0];
            keyId = data[offset+1];
            print(f"keyId={keyId}");
            if(offset + length + 1 > len(data)):
                print(f"invalid key length {length}!");
                break;
            key_method_func = g_key_decode_dict.get(keyId, keyCfgDef.decode)
            cmd.keys.append(key_method_func(keyId, data[offset+2:offset+2+length-1]));
            offset += 1 + length;
        return cmd;
    def ack(self):
        return (0, None);

class keyCfgDef(ePacketKey):
    def __init__(self, keyId):
        ePacketKey.__init__(self, keyId);

    def decode(keyId, data):
        return keyCfgDef(keyId);

class keyCfgReadAll(ePacketKey):
    def __init__(self):
        ePacketKey.__init__(self, 0xF0);
        self.readKeys = [];

    def appendKeyList(self, keys):
        self.readKeys = self.readKeys + keys;

    def serialize(self):
        data = []
        data.append(1+len(self.readKeys));
        data.append(self.keyId);
        for i in range(len(self.readKeys)):
            data.append(self.readKeys[i]);
        return data;

class keyCfgDevId(ePacketKey):
    def __init__(self):
        ePacketKey.__init__(self, 0x03);

    def __str__(self):
        result_s = "";
        result_s += f'"imei":{self.devId}'
        return result_s

    def decode(keyId, data):
        key=keyCfgDevId();
        key.devId = data.decode();
        return key;

    def serialize(self):
        data = []
        data.append(0x10)
        data.append(self.keyId)
        for i in range(len(self.devId)):
            data.append(ord(self.devId[i]))
        return data;

class keyCfgSettingTime(ePacketKey):
    def __init__(self, utc_time):
        ePacketKey.__init__(self, 0x06)
        self.utc_time = utc_time;

    def __str__(self):
        result_s = "";
        result_s += f'"timestamp":{self.utc_time}'
        return result_s

    def decode(keyId, data):
        key=keyCfgSettingTime(0);
        key.utc_time = data[0+3]&0xFF;
        key.utc_time <<= 8;
        key.utc_time |= data[0+2]&0xFF;
        key.utc_time <<= 8;
        key.utc_time |= data[0+1]&0xFF;
        key.utc_time <<= 8;
        key.utc_time |= data[0+0]&0xFF;
        return key;
        
    def serialize(self):
        data = []
        data.append(0x05)
        data.append(self.keyId)
        data.append((self.utc_time >> 0) & 0xFF)
        data.append((self.utc_time >> 8) & 0xFF)
        data.append((self.utc_time >> 16) & 0xFF)
        data.append((self.utc_time >> 24) & 0xFF)
        return data;

class keyCfgAuthNumber(ePacketKey):
    def __init__(self):
        ePacketKey.__init__(self, 0x30);

    def __str__(self):
        result_s = "";
        enable = True;
        if((self.flag&(1<<7))==0):
            enable = False;
        sms = True;
        if((self.flag&(1<<6))==0):
            sms = False;
        call = True;
        if((self.flag&(1<<5))==0):
            call = False;
        result_s += f'"Auth number index":{self.flag&0x0F},"enable":{enable}\n';
        result_s += f'"sms":{sms},"call":{call},';
        result_s += f'"number":{self.number}';
        return result_s;

    def setAuth(self, enable, sms, call, index, number):
        self.flag = 0;
        if(enable != 0):
            self.flag |= (1<<7);
        else:
            self.flag &= ~(1<<7);
        if(sms != 0):
            self.flag |= (1<<6);
        else:
            self.flag &= ~(1<<6);
        if(call != 0):
            self.flag |= (1<<5);
        else:
            self.flag &= ~(1<<5);
        self.flag &= ~(1<<4); #No SIM Dialing
        self.flag &= ~((0xF)<<0);
        self.flag |= ((index&0xF)<<0);
        self.number = number;

    def decode(keyId, data):
        key=keyCfgAuthNumber();
        key.flag = data[0]&0xFF;
        key.number = data[1:].decode();
        return key;

    def serialize(self):
        data = []
        data.append((len(self.number)+2)&0xFF);
        data.append(self.keyId);
        data.append(self.flag & 0xFF);
        for i in range(len(self.number)):
            data.append(ord(self.number[i]))
        return data;

class keyCfgMotionAlert(ePacketKey):
    def __init__(self):
        ePacketKey.__init__(self, 0x52)

    def __str__(self):
        result_s = "";
        result_s += f'"Motion Alert"\n';
        result_s += f'"enable":{self.isEnable()},';
        result_s += f'"dial":{self.isDial()},';
        result_s += f'"active":{self.getActive()},';
        result_s += f'"cooldown":{self.getCooldown()},';
        return result_s;

    def setStatus(self, enable, dial, cooldown, active):
        self.status = 0;
        if(enable != 0):
            self.status |= (1<<31);
        else:
            self.status &= ~(1<<31);
        if(enable != 0):
            self.status |= (1<<30);
        else:
            self.status &= ~(1<<30);
        self.status &= ~((0x3FFF)<<16);
        self.status |= ((active&0x3FFF)<<16);
        self.status &= ~((0xFFFF)<<0);
        self.status |= ((cooldown&0xFFFF)<<0);

    def isEnable(self):
        enable = True;
        if((self.status&(1<<31))==0):
            enable = False;
        return enable;

    def isDial(self):
        dial = True;
        if((self.status&(1<<30))==0):
            dial = False;
        return dial;

    def getActive(self):
        return ((self.status>>16)&0x3FFF);

    def getCooldown(self):
        return (self.status&0xFFFF);

    def serialize(self):
        data = []
        data.append(0x05);
        data.append(self.keyId);
        data.append((self.status >> 0) & 0xFF)
        data.append((self.status >> 8) & 0xFF)
        data.append((self.status >> 16) & 0xFF)
        data.append((self.status >> 24) & 0xFF)
        return data;

    def decode(keyId, data):
        key = keyCfgMotionAlert();
        key.status = data[0+3]&0xFF;
        key.status <<= 8;
        key.status |= data[0+2]&0xFF;
        key.status <<= 8;
        key.status |= data[0+1]&0xFF;
        key.status <<= 8;
        key.status |= data[0+0]&0xFF;
        return key;
