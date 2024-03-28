# ** Copyright © Shenzhen Eview GPS Technology Co., Ltd.
# ** All Rights Reserved.
# @Time    : 2022-02-12
# @Author  : zhangyong
# @File    : dev_server.py
# @Software: Server Demo python3


import re
import socket
import threading
from datetime import datetime, timedelta, timezone
from threading import Timer
from e_packet import ePacket
from e_proto_com import *
from e_cfg_cmd import *
from dev_sock_list import *

DEFAULT_ADDR = ''
DEFAULT_PORT = 6060
RX_TIME_OUT = 300
g_seqId_req = 1
g_device_sock_list = deviceToSocketDict();

import webbrowser
import time



# Define a function to decode the string
# Define a function to decode the string
def decode_gps_data(packet_str):
    # Define regular expressions for extracting data
    utc_time_pattern = r'"utc_time":(\d+)'
    lat_pattern = r'"lat ":(-?\d+)'
    lng_pattern = r'"long":(-?\d+)'
    speed_pattern = r'"speed":(\d+)'
    gps_status_pattern = r'"gps":(True|False)'

    # Search for patterns and extract data
    utc_time_match = re.search(utc_time_pattern, packet_str)
    lat_match = re.search(lat_pattern, packet_str)
    lng_match = re.search(lng_pattern, packet_str)
    speed_match = re.search(speed_pattern, packet_str)
    gps_status_match = re.search(gps_status_pattern, packet_str)

    # Extract values, converting them to appropriate types
    utc_time = int(utc_time_match.group(1)) if utc_time_match else None
    lat = int(lat_match.group(1)) if lat_match else None
    lng = int(lng_match.group(1)) if lng_match else None
    speed = int(speed_match.group(1)) if speed_match else None
    gps_status = gps_status_match.group(1) == 'True' if gps_status_match else None

    # Convert UTC time to timezone-aware datetime object and adjust for timezone (+2 hours)
    utc_datetime = datetime.fromtimestamp(utc_time, timezone.utc)
    local_timezone = timezone(timedelta(hours=2))
    local_datetime = utc_datetime.astimezone(local_timezone).strftime('%d/%m/%Y %H:%M:%S')

    return local_datetime, utc_time, lat, lng, speed, gps_status

def plot_on_google_maps(utc_time, lat, lng, speed):
    # Convert timestamp to readable format (unused in URL but useful for reference)
    readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(utc_time))

    # Correcting the latitude and longitude values
    corrected_lat = lat / 10000000
    corrected_lng = lng / 10000000

    # Create the Google Maps URL
    # Create the Google Maps URL for a place (which adds a marker)
    google_maps_url = f"https://www.google.com/maps/place/{corrected_lat},{corrected_lng}/@{corrected_lat},{corrected_lng},15z"

    # Print the converted time and coordinates for reference
    print(f"UTC Time: {readable_time}")
    print(f"Latitude: {corrected_lat}, Longitude: {corrected_lng}")
    print(f"Speed: {speed} units")
    print(f"Opening Google Maps at the specified location...")

    # Open the URL in the default web browser
    webbrowser.open(google_maps_url)



def client_close(sock):
    g_device_sock_list.offline(sock);
    timestr = datetime.now().strftime("%Y-%m-%d %H:%M:%S");
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
    timestr = datetime.now().strftime("%Y-%m-%d %H:%M:%S");
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
    global g_device_sock_list;
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

        # Decode the string and assign variables
        local_datetime, utc_time, lat, lng, speed, gps_status = decode_gps_data(str(rpkt))

        # Print extracted variables for verification
        print('===========================================================')
        print(f"GPS Status: {gps_status}")
        if gps_status:
            print(f"UTC Time: {utc_time}")
            print(f"Local Time: {local_datetime}")

            print(f"Latitude: {lat}")
            print(f"Longitude: {lng}")
            print(f"Speed: {speed} km/h\n\n")

            plot_on_google_maps(utc_time, lat, lng, speed)

        apkt = rpkt.ack();
        print(f'[ack]{str(apkt[0])}');
        if(apkt[0] > 0):
            print(f'[send]{str(apkt[1])}');
            client_send(sock, apkt[1]);
        devId = rpkt.findDeviceId();
        if(devId):
            old_sock = g_device_sock_list.find(devId);
            if(old_sock != sock):
                if(old_sock):
                    print(f"[socket]tick out old {devId}");
                    client_close(old_sock);
                g_device_sock_list.online(devId, sock);

    return all_data[offset:]

def genSingleLocReqData():
    global g_seqId_req;
    pkt = ePacket();
    pkt.setHeader(1, g_seqId_req)
    cmd1 = ePacketCmd(0x01)
    genKey = ePacketKey(0x12);
    cmd1.addKey(genKey);
    pkt.addCmd(cmd1)
    return pkt;

def genReadAllCfgData():
    global g_seqId_req;
    pkt = ePacket();
    pkt.setHeader(1, g_seqId_req);
    cmd1 = ePacketCmd(0x02);
    readAllK = keyCfgReadAll();
    readAllK.appendKeyList([0x03,0x06,0x30,0x52]);
    cmd1.addKey(readAllK);
    pkt.addCmd(cmd1);
    return pkt;

def genMotionAlertCfgData():
    global g_seqId_req;
    pkt = ePacket();
    pkt.setHeader(1, g_seqId_req);
    cmd1 = ePacketCmd(0x02);
    k = keyCfgMotionAlert();
    k.setStatus(True, True, 1800, 500);
    cmd1.addKey(k);
    pkt.addCmd(cmd1);
    return pkt;

def genAuthNumberCfgData():
    global g_seqId_req;
    pkt = ePacket();
    pkt.setHeader(1, g_seqId_req);
    cmd1 = ePacketCmd(0x02);
    k = keyCfgAuthNumber();
    k.setAuth(True, True, True, 0, "17512091283");
    cmd1.addKey(k);
    pkt.addCmd(cmd1);
    return pkt;

def demo_cmd_to_all():
    global g_seqId_req;
    global g_device_sock_list;
    socks = g_device_sock_list.getAllSocks();
    for sock in socks:
        if(sock):
            client_send(sock, genReadAllCfgData());

def demo_cmd_to_dev():
    global g_seqId_req;
    global g_device_sock_list;
    #client_send(sock, genSingleLocReqData());
    #sock = g_device_sock_list.find("862212112333301");
    #if(sock):
    #    client_send(sock, genMotionAlertCfgData());
    #sock = g_device_sock_list.find("861629050028632");
    #if(sock):
    #    client_send(sock, genAuthNumberCfgData());
    #g_seqId_req +=1;
    demo_cmd_to_all();
    g_seqId_req +=1;
    demo_cmd_to_dev_start_timer();

def demo_cmd_to_dev_start_timer():
    t = Timer(60, demo_cmd_to_dev, args=());
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
    work_timer = rx_work_start_timer(sock);
    rx_queue=bytes([]);
    try:
        while True:
            data = sock.recv(1024)
            if(data == b''):
                break;
            else:
                timestr = datetime.now().strftime("%Y-%m-%d %H:%M:%S");
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
    print(f"[socket]{str(addr)} rx exit!")

def server_init():
    global DEFAULT_PORT;
    global DEFAULT_ADDR;
    print(f"[socket]server {DEFAULT_ADDR}:{DEFAULT_PORT}");

def server_start():
    global DEFAULT_PORT;
    global DEFAULT_ADDR;
    #demo_cmd_to_dev_start_timer();#for test demo
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    #host = socket.gethostname();
    serversocket.bind((DEFAULT_ADDR, DEFAULT_PORT));
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


    #plot_on_google_maps(utc_time,lat,long,speed)


if __name__ == '__main__':
    main()
