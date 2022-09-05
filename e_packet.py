# ** Copyright © Shenzhen Eview GPS Technology Co., Ltd.
# ** All Rights Reserved.
# @Time    : 2022-02-12
# @Author  : zhangyong
# @File    : dev_server.py
# @Software: Server Demo python3
from e_proto_com import *
from e_neg_cmd import *
from e_srv_cmd import *
from e_dat_cmd import *
from e_cfg_cmd import *

class ePacket:
    CRC_OFFSET = 4
    LEN_OFFSET = 2
    def __init__(self):
        self.cmds = []
        self.prop = 0
        self.seqId = 0

    def __str__(self):
        result_s = "";
        ack = True;
        if((self.prop&0x10)==0):
            ack = False;
        result_s += f'"ack":{ack}\n';
        result_s += f'"seqId":{self.seqId}\n';
        for i in range(len(self.cmds)):
            result_s += str(self.cmds[i]) + "\n";
        return result_s;

    def toHexStr(self):
        data = self.serialize()
        result_s = "";
        for i in range(len(data)):
            result_s += f"%02X"%data[i]
        return result_s

    def isAck(self):
        ack = True;
        if((self.prop&0x10)==0):
            ack = False;
        return ack;

    def setHeader(self, ack, seqId):
        prop=0
        if(ack == 1):
            prop |= 0x10
        self.prop = prop
        self.seqId = seqId

    def decode(self, data, offset):
        if(data[offset+0] != 0xAB):
            return (-1, offset + 1);
        self.prop = data[offset+1];
        len_body = data[offset+self.LEN_OFFSET+1]
        len_body <<= 8
        len_body |= data[offset+self.LEN_OFFSET]
        if(offset + 8 + len_body > len(data)):
            return (1, offset + 0);
        crc16 = data[offset+self.CRC_OFFSET+1];
        crc16 <<= 8
        crc16 |= data[offset+self.CRC_OFFSET]
        seqId = data[offset+7]
        seqId <<= 8
        seqId |= data[offset+6]
        #print(f"seqId={seqId}, crc16={crc16}, len={len_body}")
        self.seqId = seqId;
        calc_crc16_result = 0
        for i in range(offset+8, offset + 8 + len_body):
            calc_crc16_result = ePacket.crc16_calc(calc_crc16_result, data[i])
        if(calc_crc16_result != crc16):
            print(f"crc={calc_crc16_result} != {crc16}")
            return (-2, offset + 1);

        cmd_data = data[(offset+8) : (offset + 8 + len_body)]
        cmdId = cmd_data[0];
        g_cmdId_decode_dict = {
            0x7F:ePacketNegCmd.decode,
            0x03:ePacketSrvCmd.decode,
            0x01:ePacketDataCmd.decode,
            0x02:ePacketCfgCmd.decode,
            0x00:ePacketCmd.decode
        }
        print(f"cmdId={cmdId}")
        cmd_method_func = g_cmdId_decode_dict.get(cmdId, ePacketCmd.decode)
        #print(f"cmdId={cmd_method_func}")
        self.cmds.append(cmd_method_func(cmdId, cmd_data[1:len_body]))
        return (0, offset + 8 + len_body)

    def findDeviceId(self):
        for cmd in self.cmds:
            devId = cmd.findDeviceId();
            if(devId):
                return devId;
        return None;

    def bytesToHexStr(data):
        result_s = "";
        for i in range(len(data)):
            result_s += f"%02X"%data[i]
        return result_s

    def crc16_calc(crc16, value):
        CRC_TABLE =[0x0000, 0x1021, 0x2042, 0x3063,
            0x4084, 0x50a5, 0x60c6, 0x70e7, 0x8108, 0x9129, 0xa14a, 0xb16b,
            0xc18c, 0xd1ad, 0xe1ce, 0xf1ef, 0x1231, 0x0210, 0x3273, 0x2252,
            0x52b5, 0x4294, 0x72f7, 0x62d6, 0x9339, 0x8318, 0xb37b, 0xa35a,
            0xd3bd, 0xc39c, 0xf3ff, 0xe3de, 0x2462, 0x3443, 0x0420, 0x1401,
            0x64e6, 0x74c7, 0x44a4, 0x5485, 0xa56a, 0xb54b, 0x8528, 0x9509,
            0xe5ee, 0xf5cf, 0xc5ac, 0xd58d, 0x3653, 0x2672, 0x1611, 0x0630,
            0x76d7, 0x66f6, 0x5695, 0x46b4, 0xb75b, 0xa77a, 0x9719, 0x8738,
            0xf7df, 0xe7fe, 0xd79d, 0xc7bc, 0x48c4, 0x58e5, 0x6886, 0x78a7,
            0x0840, 0x1861, 0x2802, 0x3823, 0xc9cc, 0xd9ed, 0xe98e, 0xf9af,
            0x8948, 0x9969, 0xa90a, 0xb92b, 0x5af5, 0x4ad4, 0x7ab7, 0x6a96,
            0x1a71, 0x0a50, 0x3a33, 0x2a12, 0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e,
            0x9b79, 0x8b58, 0xbb3b, 0xab1a, 0x6ca6, 0x7c87, 0x4ce4, 0x5cc5,
            0x2c22, 0x3c03, 0x0c60, 0x1c41, 0xedae, 0xfd8f, 0xcdec, 0xddcd,
            0xad2a, 0xbd0b, 0x8d68, 0x9d49, 0x7e97, 0x6eb6, 0x5ed5, 0x4ef4,
            0x3e13, 0x2e32, 0x1e51, 0x0e70, 0xff9f, 0xefbe, 0xdfdd, 0xcffc,
            0xbf1b, 0xaf3a, 0x9f59, 0x8f78, 0x9188, 0x81a9, 0xb1ca, 0xa1eb,
            0xd10c, 0xc12d, 0xf14e, 0xe16f, 0x1080, 0x00a1, 0x30c2, 0x20e3,
            0x5004, 0x4025, 0x7046, 0x6067, 0x83b9, 0x9398, 0xa3fb, 0xb3da,
            0xc33d, 0xd31c, 0xe37f, 0xf35e, 0x02b1, 0x1290, 0x22f3, 0x32d2,
            0x4235, 0x5214, 0x6277, 0x7256, 0xb5ea, 0xa5cb, 0x95a8, 0x8589,
            0xf56e, 0xe54f, 0xd52c, 0xc50d, 0x34e2, 0x24c3, 0x14a0, 0x0481,
            0x7466, 0x6447, 0x5424, 0x4405, 0xa7db, 0xb7fa, 0x8799, 0x97b8,
            0xe75f, 0xf77e, 0xc71d, 0xd73c, 0x26d3, 0x36f2, 0x0691, 0x16b0,
            0x6657, 0x7676, 0x4615, 0x5634, 0xd94c, 0xc96d, 0xf90e, 0xe92f,
            0x99c8, 0x89e9, 0xb98a, 0xa9ab, 0x5844, 0x4865, 0x7806, 0x6827,
            0x18c0, 0x08e1, 0x3882, 0x28a3, 0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e,
            0x8bf9, 0x9bd8, 0xabbb, 0xbb9a, 0x4a75, 0x5a54, 0x6a37, 0x7a16,
            0x0af1, 0x1ad0, 0x2ab3, 0x3a92, 0xfd2e, 0xed0f, 0xdd6c, 0xcd4d,
            0xbdaa, 0xad8b, 0x9de8, 0x8dc9, 0x7c26, 0x6c07, 0x5c64, 0x4c45,
            0x3ca2, 0x2c83, 0x1ce0, 0x0cc1, 0xef1f, 0xff3e, 0xcf5d, 0xdf7c,
            0xaf9b, 0xbfba, 0x8fd9, 0x9ff8, 0x6e17, 0x7e36, 0x4e55, 0x5e74,
            0x2e93, 0x3eb2, 0x0ed1, 0x1ef0]
        crc16 = CRC_TABLE[(((crc16 >> 8) & 0xff) ^ value) & 0xFF] ^ (crc16 << 8);
        return crc16 & 0xFFFF;

    def addCmd(self, cmd):
        self.cmds.append(cmd)

    def serialize(self):
        head = []
        head.append(0xAB) 
        head.append(self.prop)
        head.append(0)
        head.append(0)
        head.append(0)
        head.append(0)
        head.append(self.seqId & 0xFF)
        head.append((self.seqId >> 8) & 0xFF)
        body = []
        for i in range(len(self.cmds)):
            body += self.cmds[i].serialize()
        crc16 = 0
        for i in range(len(body)):
            crc16 = ePacket.crc16_calc(crc16, body[i])

        len_body = len(body);
        head[self.LEN_OFFSET]=(len_body & 0xFF)
        head[self.LEN_OFFSET+1]=((len_body >> 8) & 0xFF)
        head[self.CRC_OFFSET]=(crc16 & 0xFF)
        head[self.CRC_OFFSET+1]=((crc16 >> 8) & 0xFF)
        return head + body;
    def ack(self):
        if(self.isAck()==False):
            return (0, None);
        cmd_n = len(self.cmds);
        apkt = ePacket();
        apkt.setHeader(0, self.seqId); 
        if(cmd_n == 0):
            negCmd=ePacketNegCmd();
            negCmd.addKey(keyNegRsp(0x15));
            apkt.addCmd(negCmd);
            return (1, apkt);
        results = self.cmds[0].ack();
        if(results[1] == None):
            negCmd=ePacketNegCmd();
            negCmd.addKey(keyNegRsp(0));
            apkt.addCmd(negCmd);
            return (1, apkt);
        apkt.addCmd(results[1]);
        return (results[0], apkt);


