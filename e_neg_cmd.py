# ** Copyright © Shenzhen Eview GPS Technology Co., Ltd.
# ** All Rights Reserved.
# @Time    : 2022-02-12
# @Author  : zhangyong
# @File    : dev_server.py
# @Software: Server Demo python3
from e_proto_com import ePacketCmd
from e_proto_com import ePacketKey

class ePacketNegCmd(ePacketCmd):
    def __init__(self):
        ePacketCmd.__init__(self, 0x7F)

    def decode(cmdId, data):
        g_key_decode_dict = {
            0x00:keyNegRsp.decode
        }
        cmd = ePacketNegCmd()
        length = data[0];
        keyId = data[1];
        #print(f"keyId={keyId}")
        key_method_func = g_key_decode_dict.get(keyId, keyNegRsp.decode)
        cmd.keys.append(key_method_func(keyId, data[2:2+length-1]))
        return cmd;

class keyNegRsp(ePacketKey):
    def __init__(self, keyId):
        ePacketKey.__init__(self, keyId)

    def decode(keyId, data):
        return keyNegRsp(keyId)
