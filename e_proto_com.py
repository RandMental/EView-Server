# ** Copyright © Shenzhen Eview GPS Technology Co., Ltd.
# ** All Rights Reserved.
# @Time    : 2022-02-12
# @Author  : zhangyong
# @File    : dev_server.py
# @Software: Server Demo python3
class ePacketCmd:
    def __init__(self, cmdId):
        self.cmdId = cmdId
        self.keys = []
    def __str__(self):
        result_s = "";
        result_s += f'"cmdId":%02X\n'%self.cmdId;
        for i in range(len(self.keys)):
            result_s += str(self.keys[i])+"\n";
        return result_s;
    def addKey(self, key):
        self.keys.append(key)
    def serialize(self):
        data=[]
        data.append(self.cmdId)
        for i in range(len(self.keys)):
            data += self.keys[i].serialize()
        return data
    def decode(cmdId, data):
        print(f"Undefined cmdId={cmdId} decode!");
        cmd = ePacketCmd(cmdId);
        offset = 0;
        while offset < len(data):
            length = data[offset+0];
            keyId = data[offset+1];
            print(f"keyId={keyId}");
            if(offset + length + 1 > len(data)):
                print(f"invalid key length {length}!");
                break;
            key_method_func = ePacketKeyUndef.decode;
            cmd.keys.append(key_method_func(keyId, data[offset+2:offset+2+length-1]));
            offset += 1 + length;
        return cmd;
    def getCmdId(self):
        return self.cmdId;
    def ack(self):
        return (0, None);
        
    def findDeviceId(self):
        return None;

class ePacketKey:
    def __init__(self, keyId):
        self.keyId = keyId;
    def __str__(self):
        result_s = "";
        result_s += f'"keyId-undef":%02X'%self.keyId;
        return result_s;
    def serialize(self):
        data = []
        data.append(1)
        data.append(self.keyId)
        return data
    def decode(keyId, data):
        print(f"Undefined keyId={keyId} decode!")
        return ePacketKey(keyId)
    def getKeyId(self):
        return self.keyId;

class ePacketKeyUndef(ePacketKey):
    def __init__(self, keyId, data):
        ePacketKey.__init__(self, keyId);
        self.data = data;
        
    def __str__(self):
        result_s = "";
        result_s += f'"keyId-undef":%02X,%02X,'%(self.keyId,len(self.data));
        for i in range(len(self.data)):
            result_s += f"%02X"%self.data[i]
        return result_s;
    def serialize(self):
        data = []
        data.append(1)
        data.append(self.keyId)
        return data
    def decode(keyId, data):
        #print(f"Undefined keyId={keyId} decode!")
        return ePacketKeyUndef(keyId, data)
    def getKeyId(self):
        return self.keyId;

def firstByteToIntSigned(val):
    if(val > 127):
        return (~0xFF) | val;
    return val;
