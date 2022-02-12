# ** Copyright © Shenzhen Eview GPS Technology Co., Ltd.
# ** All Rights Reserved.
# @Time    : 2022-02-12
# @Author  : zhangyong
# @File    : dev_server.py
# @Software: Server Demo python3
import socket
import threading
import time
from datetime import datetime
from threading import Timer
from e_packet import ePacket
from e_proto_com import *

DEFAULT_ADDR = "127.0.0.1";
DEFAULT_PORT = 8889;
RX_TIME_OUT = 300;
g_seqId_req = 1;
def client_close(sock):
    timestr = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S");
    print(f"{timestr} [socket]close start...")
    try:
        sock.shutdown(socket.SHUT_RDWR);
        #sock.close();
    except Exception as e:
        print(f"[socket]Execption1: {str(e)}")
    try:
        sock.close();
    except Exception as e:
        print(f"[socket]Execption2: {str(e)}")

def client_send(sock, pkt):
    timestr = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S");
    try:
        print(f"{timestr} [send]{pkt.toHexStr()}");
        sock.send(bytes(pkt.serialize()));
        #print(f"[socket]send end")
        #client.close()
    except ConnectionResetError as e:
        print(f"[socket] {str(e)}")
    except ConnectionRefusedError as e:
        print(f"[socket] {str(e)}")
    except Exception as e:
        print(f"[socket]Execption: {str(e)}")

def rx_data_proc(sock, rx_queue, data):
	all_data = rx_queue + data;
	offset = 0;
	while(offset < len(all_data)):
	    rpkt = ePacket()
	    result = rpkt.decode(all_data, offset);
	    print(f'[parse]{result}');
	    offset = result[1];
	    if(result[0] > 0):
	    	break;
	    if(result[0] <0):
	    	continue;
	    print(f'[recv]{str(rpkt)}');
	    apkt = rpkt.ack();
	    print(f'[ack]{str(apkt[0])}');
	    if(apkt[0] > 0):
	    	print(f'[send]{str(apkt[1])}');
	    	client_send(sock, apkt[1]);
	return all_data[offset:];

def genSingleLocReqData():
    global g_seqId_req;
    pkt = ePacket();
    pkt.setHeader(1, g_seqId_req)
    cmd1 = ePacketCmd(0x01)
    genKey = ePacketKey(0x12);
    cmd1.addKey(genKey);
    pkt.addCmd(cmd1)
    return pkt;

def demo_cmd_to_dev(sock):
	global g_seqId_req;
	client_send(sock, genSingleLocReqData());
	g_seqId_req +=1;

def demo_cmd_to_dev_start_timer(sock):
    t = Timer(1800, demo_cmd_to_dev, args=(sock,));
    t.start();
    return t;
def demo_cmd_to_dev_stop_timer(t):
	t.cancel();

def rx_work_timeout(sock):
	client_close(sock);

def rx_work_start_timer(sock):
    t = Timer(RX_TIME_OUT, rx_work_timeout, args=(sock,));
    t.start();
    return t;

def rx_work_reset_timer(t, sock):
	t.cancel();
	t = Timer(RX_TIME_OUT, rx_work_timeout, args=(sock,));
	t.start();
	return t;

def rx_work_stop_timer(t):
	t.cancel();

def receive_handle(sock, addr):
    print(f"[socket]{str(addr)} rx start")
    #demo_timer = demo_cmd_to_dev_start_timer(sock);#for test demo
    work_timer = rx_work_start_timer(sock);
    rx_queue=bytes([]);
    try:
        while True:
            data = sock.recv(1024)
            if(data == b''):
                break;
            else:
                timestr = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S");
                print(f'{timestr} [recv]{ePacket.bytesToHexStr(data)}')
                rx_queue = rx_data_proc(sock, rx_queue, data);
                work_timer = rx_work_reset_timer(work_timer, sock);
    except ConnectionResetError as e:
        print(f"[socket] {str(e)}")
    except ConnectionRefusedError as e:
        print(f"[socket] {str(e)}")
    except Exception as e:
        print(f"[socket] {str(e)}")
    client_close(sock);
    rx_work_stop_timer(work_timer);
    #demo_cmd_to_dev_stop_timer(demo_timer);
    print(f"[socket]{str(addr)} rx exit!")

def server_init():
	global DEFAULT_PORT;
	print(f"[socket]server port {DEFAULT_PORT}");

def server_start():
	global DEFAULT_PORT;
	global DEFAULT_ADDR;
	serversocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM);
	host = socket.gethostname();
	serversocket.bind((host, DEFAULT_PORT));
	serversocket.listen(5);
	while True:
		clientsocket,addr = serversocket.accept();
		print(f"[socket]accept client {str(addr)}");
		receive_thread = threading.Thread(target=receive_handle, args=(clientsocket,addr,));
		receive_thread.start();

def main():
    server_init();
    time.sleep(1);
    try:
    	server_start();
    except ConnectionRefusedError as e:
        print(f"[socket] {str(e)}")
    except Exception as e:
        print(f"[socket] {str(e)}")

if __name__ == '__main__':
    main()
