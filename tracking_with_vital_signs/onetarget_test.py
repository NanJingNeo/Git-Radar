# -*-coding:utf-8 -*-
from __future__ import print_function
from pymoduleconnector import create_mc
import pca_filter
import numpy as np
import matlab.engine
from dl_gj import *
from pylab import *
import threading
import argparse
import json
from socket import *
import select
import time
from time import sleep
import logging
import scipy.io as sio

def maxEnergyAndPosition(puredata):
    data = puredata.copy()
    dataEnergy=data*data
    topList=[]
    peakList=[]
    for i in range(dataEnergy.shape[0]):
        topList.append(max(dataEnergy[i,:]))
        peakList.append(np.argmax(dataEnergy[i,:])/156+0.5)
    return topList,peakList

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
        xep.x4driver_set_fps(20)
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
    logger = logging.getLogger('pi4')
    logger.setLevel(logging.INFO)
    rf_handler = logging.StreamHandler(sys.stderr)  # 默认是sys.stderr
    rf_handler.setLevel(logging.DEBUG)
    rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(message)s"))
    logger.addHandler(rf_handler)
    plt.ion()
    com = 'COM16'

    leiji = np.zeros((1, 751))
    M = 20
    L = 50
    data=dict()
    flag=1
    ycl=1

    ##用雷达时间戳对追踪
    t=threading.Thread(target=radar,args=(com,))
    t.start()
    while 1:
        sleep(0.01)
        if leiji.shape[0] >230:
            leiji = leiji[-220:, :].copy()
            RawData1=leiji[-220:, :].copy()
            PureData1 = pca_filter.p_f(RawData1[:,0:-3].copy(), M, L)
            topList,peakList=maxEnergyAndPosition(PureData1)

            index=list(range(1,201))

            plt.clf()

            plt.scatter(index, peakList, color='r')
            plt.axis([0, 200, 0, 5])
            plt.pause(0.005)
            plt.show()

            result={'topList':topList,
                    'peakList': peakList,
                    }
            with open('result_one_target.json','w') as f:
                json.dump(result,f)
            f.close()