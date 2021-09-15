#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
# sys.path.append("F:/radar/ModuleConnector/ModuleConnector-win32_win64-1.4.2/python36-win64/duoleida")
# sys.path.append("C:/Users/zxy/Desktop")
sys.path.append("/home/pi/ModuleConnector/ModuleConnector-rpi-1.5.3/python35-arm-linux-gnueabihf/duoleida")
import threading
# import numpy as np
from numpy import *
import pymoduleconnector
from pymoduleconnector import ModuleConnector
from pymoduleconnector.ids import *
import time
from time import sleep
from pymoduleconnector import create_mc
import scipy.io as sio
import pca_filter
# import random
from kalman import *
import serial
from socket import *
import os
from clean import *
from kcluster import *
from sklearn.cluster import KMeans
import logging
import argparse
import json

def radar(com):
    global leiji
    with create_mc(com) as mc:
        xep = mc.get_xep()

        # inti x4driver
        xep.x4driver_init()

        # Set enable pin
        xep.x4driver_set_enable(1)

        # Set iterations
        xep.x4driver_set_iterations(64)
        # Set pulses per step
        xep.x4driver_set_pulses_per_step(5)
        # Set dac step
        xep.x4driver_set_dac_step(1)
        # Set dac min
        xep.x4driver_set_dac_min(949)
        # Set dac max
        xep.x4driver_set_dac_max(1100)
        # Set TX power
        xep.x4driver_set_tx_power(2)

        # Enable downconversion
        xep.x4driver_set_downconversion(0)

        # Set frame area offset
        xep.x4driver_set_frame_area_offset(0.18)
        offset = xep.x4driver_get_frame_area_offset()

        # Set frame area
        xep.x4driver_set_frame_area(0.2, 5)
        frame_area = xep.x4driver_get_frame_area()

        # Set TX center freq
        xep.x4driver_set_tx_center_frequency(3)

        # Set PRFdiv
        xep.x4driver_set_prf_div(16)
        prf_div = xep.x4driver_get_prf_div()

        # Start streaming
        xep.x4driver_set_fps(5)
        fps = xep.x4driver_get_fps()
        # Stop streaming
        print("wait radar")

        # -----------------------------------读取数据与处理-------------------------------------#
        def read_frame():
            """Gets frame data from module"""
            d = xep.read_message_data_float()
            frame = np.array(d.data)
            # Convert the resulting frame to a complex array if downconversion is enabled
            return frame

        def get_data():
            save = np.ones((1, 751))

            for jj in range(1):
                frame2 = read_frame()

                save[jj, 0:750] = frame2
                ll2 = time.asctime(time.localtime(time.time()))

                ll21 = ll2[11:13]
                ll22 = ll2[14:16]
                ll23 = ll2[17:19]

                lll = int(ll21) * 10000 + int(ll22) * 100 + int(ll23)
                save[jj, -1] = lll

            return save


        while 1:
            save = get_data()
            leiji = np.vstack((leiji, save))
            sleep(0.005)

    xep.module_reset()

if __name__=="__main__":

    #############################################log#################################
    logger = logging.getLogger('pi2')
    logger.setLevel(logging.INFO)
    rf_handler = logging.StreamHandler(sys.stderr)  # 默认是sys.stderr
    rf_handler.setLevel(logging.DEBUG)
    rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(message)s"))
    logger.addHandler(rf_handler)

    #################################ip######################################
    [server,pi1,pi2,pi3,winip]=['','','','','']
    with open('ip.txt') as f:
        lines = f.readlines()
        for line in lines:
            tmp = line.strip('\n').split(':')
            if tmp[0] == 'server':
                server = tmp[1]
            elif tmp[0] == 'pi1':
                pi1 = tmp[1]
            elif tmp[0] == 'pi2':
                pi2 = tmp[1]
            elif tmp[0] == 'pi3':
                pi3 = tmp[1]
            elif tmp[0] == 'win':
                winip = tmp[1]
        if server=='' or pi1=='' or pi2=='' or pi3=='' or winip=='':
            logging.INFO('wrong ip')
    f.close()

    ##############################consoler###################################
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", type=str, default=server, help="server ip")
    parser.add_argument("--pi1", type=str, default=pi1, help="pi1 ip")
    parser.add_argument("--pi2", type=str, default=pi2, help="pi2 ip")
    parser.add_argument("--pi3", type=str, default=pi3, help="pi3 ip")
    parser.add_argument("--winip", type=str, default=winip, help="PC ip")
    parser.add_argument("--com", type=str, default='/dev/device0', help="com")
    args = parser.parse_args()

    HOST = args.server
    PORT = 10000
    BUFSIZ = 16
    ADDR = (HOST,PORT)

    ser = serial.Serial(args.com, 9600)
    com = ser.name

    frame_gen = sio.loadmat('frame_gen.mat')['frame_gen']

    ycl = 0
    ijjj = 0
    leiji = np.zeros((1, 751))
    M = 0
    L = 50
    flag = 1
    adj = 0
    save1=[]
    save2=[]
    state1='--'
    state2='--'
    s1 = 0.95  # 目标1的当前距离
    s2 = 4.26  # 目标2的当前距离


    def l_m(Pure, M, L):
        pnum = float(156)
        c = Pure.shape
        valueplace = zeros(c[0])
        for i in range(c[0]):
            valueplace[i] = np.argmax(Pure[i, :]) + L
        return valueplace


    tcpCliSock = socket(AF_INET, SOCK_STREAM)
    tcpCliSock.connect(ADDR)
    msg = tcpCliSock.recv(16).decode()
    if msg == "start":
        t=threading.Thread(target=radar,args=(com,))
        t.start()

    while 1:
        start=time.time()
        if leiji.shape[0]>20:
            end3=time.time()
            leiji=leiji[-20:,:].copy()  # 前4s的数据
            nowTime = leiji[-1, -1]  # 最新的数据的时间戳
            # rawdata=leiji[-20:,49:-12].copy()
            rawdata = leiji[-20:, 49:-32].copy() #测到4.8
            meandata = np.mean(rawdata, axis=0)
            dedata = rawdata[-1, :] - meandata
            # dedata[0:50] = np.zeros(50)
            signal = dedata
            [cmap, dmap, n, ht] = clean(signal, frame_gen, 1e-3)
            ss = ht[0:-25]
            ht[0:25] = np.zeros(25)
            ht[25:] = ss

            # KNN + Kalman
            s1, s2 = kcluster(ht, s1, s2)

            if abs(s1 - s2) < 0.05:
                adj = adj + 1
            logger.info(adj)
            if adj > 5:
                a3_list2 = []
                for j in range(len(ht)):
                    if (ht[j]) > 0:
                        a3_list2.append(j / 156 + 0.5)

                if len(a3_list2) >= 2:
                    estimator = KMeans(n_clusters=2)  # 构造聚类器
                    a3_ = np.array(a3_list2)
                    a3_ = np.reshape(a3_, (-1, 1))

                    estimator.fit(a3_)  # 聚类
                    label_pred = estimator.cluster_centers_
                    s1 = label_pred[0].tolist()
                    s2 = label_pred[1].tolist()
                    s1 = s1[0]
                    s2 = s2[0]
                    logger.info("pppppppppppppppppppppppppppp")
                    logger.info(s1)
                    logger.info(s2)
                    # adj = 0
                    if abs(s1 - s2) > 0.5:
                        adj = 0
                    else:
                        adj = adj
            logger.info("s1={:.2f}  s2={:.2f}".format(float(s1), float(s2)))
            logger.info("-------------------------------------------------")
            jg1 = s1
            jg2 = s2

            result={
                '1': jg1,
                '2': jg2,
                'time':nowTime
            }
            # str_jg = str(jg1)+ ',' + str(jg2)+'|'

            tcpCliSock.send(json.dumps(result).encode())
            tcpCliSock.recv(16).decode()
            end4=time.time()
            logger.info(ycl)
            logger.info(str(end4-start))
            ycl = ycl + 1
        else:
            None
        sleep(0.1)
