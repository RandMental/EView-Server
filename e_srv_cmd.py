# ** Copyright © Shenzhen Eview GPS Technology Co., Ltd.
# ** All Rights Reserved.
# @Time    : 2022-02-12
# @Author  : zhangyong
# @File    : dev_server.py
# @Software: Server Demo python3
from e_proto_com import ePacketCmd
from e_proto_com import ePacketKey
import time

class ePacketSrvCmd(ePacketCmd):
    def __init__(self):
        ePacketCmd.__init__(self, 0x03)

    def decode(cmdId, data):
        g_key_decode_dict = {
            0x01:keySrvDevId.decode,
            0x12:keySrvTimestamp.decode,
            0x10:keySrvHeartBeat.decode,
            0x00:keySrvDef.decode
        }
        cmd = ePacketSrvCmd();
        offset = 0;
        while offset < len(data):
            length = data[offset+0];
            keyId = data[offset+1];
            print(f"keyId={keyId}");
            if(offset + length + 1 > len(data)):
                print(f"invalid key length {length}!");
                break;
            key_method_func = g_key_decode_dict.get(keyId, keySrvDef.decode)
            cmd.keys.append(key_method_func(keyId, data[offset+2:offset+2+length-1]));
            offset += 1 + length;
        return cmd;
    def ack(self):
        apkt = ePacketSrvCmd();
        for i in range(len(self.keys)):
            keyId = self.keys[i].getKeyId();
            if(keyId == 0x12):
                apkt.addKey(keySrvTimestamp(int(time.time())));
                return (1, apkt);
            if(keyId == 0x10):
                return (0, None); #Return default
            if(keyId == 0x11):
                #Need you implements
                return(0, None); 
            if(keyId == 0x21):
                #Need you implements
                return(0, None); 
            if(keyId == 0x22):
                #Need you implements
                return(0, None); 
        return (0, None);
    def findDeviceId(self):
        for key in self.keys:
            if(key.getKeyId() == 0x01):
                return key.devId;
        return None; 

class keySrvDevId(ePacketKey):
    def __init__(self):
        ePacketKey.__init__(self, 0x01);

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
        key=keySrvDevId();
        key.devId = data.decode();
        return key;

class keySrvTimestamp(ePacketKey):
    def __init__(self, utc_time):
        ePacketKey.__init__(self, 0x12)
        self.utc_time = utc_time;

    def __str__(self):
        result_s = "";
        result_s += f'"timestamp":{self.utc_time}'
        return result_s

    def decode(keyId, data):
        key=keySrvTimestamp(0);
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

class keySrvDef(ePacketKey):
    def __init__(self, keyId):
        ePacketKey.__init__(self, keyId)

    def decode(keyId, data):
        return keySrvDef(keyId)

class keySrvHeartBeat(ePacketKey):
    def __init__(self):
        ePacketKey.__init__(self, 0x10)

    def __str__(self):
        result_s = "";
        result_s += f'"heartbeat"'
        return result_s

    def decode(keyId, data):
        return keySrvHeartBeat();
