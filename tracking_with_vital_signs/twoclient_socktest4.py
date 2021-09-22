# -*-coding:utf-8 -*-
from __future__ import print_function
from pymoduleconnector import create_mc
import pca_filter
import numpy as np
# import matlab.engine
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

# def receive(tcpCliSock):
#     ##这里改成非阻塞
#     global data
#     while True:
#         buf = tcpCliSock.recv(1024).decode()
#         tcpCliSock.send('ok'.encode())
#         data = json.loads(buf)
#         sleep(0.01)

def receive(r_inputs, w_inputs, e_inputs):
    global data,refineDistance
    while 1:
        r_list, w_list, e_list = select.select(r_inputs, w_inputs, e_inputs, 0.005)
        for event in r_list:
            buf = event.recv(1024).decode()
            # logger.info(buf)
            event.send('ok'.encode())
            data = json.loads(buf)
            with open('trkResult.json', 'w') as f:
                json.dump(data, f)
            f.close()
            s1 = ((data['1'][0]+2.1) ** 2 + data['1'][1] ** 2) ** 0.5
            s2 = ((data['2'][0]+2.1) ** 2 + data['2'][1] ** 2) ** 0.5
            refineDistance = np.vstack((refineDistance, np.array([s1, s2, data['time']])))
            data = dict()

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
            save = np.ones((1, 748))

            for jj in range(1):
                frame2 = read_frame()

                save[jj, 0:747] = frame2 #新雷达数据格式：747+1
                ll2 = time.asctime(time.localtime(time.time()))

                ll21 = ll2[11:13]
                ll22 = ll2[14:16]
                ll23 = ll2[17:19]

                lll = int(ll21) * 10000 + int(ll22) * 100 + int(ll23)
                save[jj, -1] = lll

            return save


        while 1:
            save = get_data()
            # print(save.shape)
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
    #################################ip######################################
    [server, pi1, pi2, pi3, winip] = ['', '', '', '', '']
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
        if server == '' or pi1 == '' or pi2 == '' or pi3 == '' or winip == '':
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
    ADDR = (HOST, PORT)

    # frame_gen = sio.loadmat('frame_gen.mat')['frame_gen']
    # eng = matlab.engine.start_matlab()
    # mpl.rcParams['font.sans-serif'] = ['SimHei']
    # eng.addpath('./ml')
    # plt.ion()
    com = 'COM3'

    leiji = np.zeros((1, 748))#新雷达数据格式：747+1
    M = 10
    L = 50
    data=dict()
    flag=1
    ycl=1

    #这里需要修改
    # ls1 = 4.26 #13
    # ls2 = 0.95 #37

    #socket连接
    tcpCliSock = socket(AF_INET, SOCK_STREAM)
    tcpCliSock.connect(ADDR)
    tcpCliSock.setblocking(False)
    r_inputs = set()
    r_inputs.add(tcpCliSock)
    w_inputs = set()
    w_inputs.add(tcpCliSock)
    e_inputs = set()
    e_inputs.add(tcpCliSock)

    t1 = threading.Thread(target=radar, args=(com,))
    t2 = threading.Thread(target=receive, args=(r_inputs, w_inputs, e_inputs))

    while 1:
        msg=''
        r_list, w_list, e_list = select.select(r_inputs, w_inputs, e_inputs, 0.1)
        for event in r_list:
            msg = event.recv(16).decode()
            if msg == "start":
                t1.start()
                t2.start()
        if msg == "start":
            break
        sleep(0.05)


    # ##用追踪时间戳对雷达，大概9s算一次
    # while 1:
    #     begin=time.time()
    #     sleep(0.01)
    #     ##这里改成对数据
    #     if flag:
    #         if data:
    #             flag=0
    #             begin = time.time()
    #             s1=(data['1'][0]**2+data['1'][1]**2)**0.5
    #             s2 = (data['2'][0] ** 2 + data['2'][1] ** 2) ** 0.5
    #             timestamps=leiji[:,-1].copy()
    #             index=np.where(timestamps.reshape(-1)==data['time'])
    #             print(index)
    #             if index:
    #                 index=index[0].tolist()
    #                 sliceindex=index[0]
    #                 data=dict()
    #                 # print(index)
    #                 leiji=leiji[sliceindex:,:]
    #     else:
    #         if leiji.shape[0] >200:
    #             flag=1
    #             RawData1 = leiji[1:201, 0:-1].copy()
    #             ###行前截10，列后截50，前截100
    #             # 590,600
    #             PureData1 = pca_filter.p_f(RawData1, M, L)
    #
    #             # 双人
    #             peaks1_list, peaks2_list, tops1_list, tops2_list, s1, s2 = gj(PureData1, RawData1, M, L, s1, s2)
    #             # peaks1_list, peaks2_list, tops1_list, tops2_list= gj(PureData1, RawData1, M, L)
    #
    #             result={'peaks1_list':peaks1_list,
    #                     'peaks2_list': peaks2_list,
    #                     'tops1_list': tops1_list,
    #                     'tops2_list': tops2_list,
    #                     }
    #             with open('result.json','w') as f:
    #                 json.dump(result,f)
    #             f.close()
    #             # sio.savemat(result,{'result':result})
    #             logger.info(ycl)
    #             ycl+=1
    #             end=time.time()
    #             logger.info(str(end-begin))

    ##用雷达时间戳对追踪
    refineDistance=np.zeros([1,3])
    while 1:
        begin = time.time()
        sleep(0.01)
        ##这里改成对数据
        # if flag:
        if leiji.shape[0] >210:
            flag=0
            RawData1 = leiji[-200:, :].copy()
            radarTime=int(RawData1[0,-1])
            # print(radarTime)
            # else:
            timestamps = refineDistance[:, -1]
            index = np.where(timestamps.reshape(-1) == radarTime)
            if index[0]!=np.array([]):
                flag=1
                print(index)
                index = index[0].tolist()
                sliceindex=refineDistance[index[0], 0:2].copy()
                [s1,s2] =sliceindex.tolist()
                print(s1,s2)
                refineDistance=refineDistance[index[0]:,:]
                ###行前截10，列后截50，前截100
                # 590,600
                PureData1 = pca_filter.p_f(RawData1[:,0:-1].copy(), M, L)

                # 双人
                peaks1_list, peaks2_list, tops1_list, tops2_list, s1, s2 = gj(PureData1, RawData1[:,0:-1], M, L, s1, s2)
                # peaks1_list, peaks2_list, tops1_list, tops2_list= gj(PureData1, RawData1, M, L)

                result={'peaks1_list':peaks1_list,
                        'peaks2_list': peaks2_list,
                        'tops1_list': tops1_list,
                        'tops2_list': tops2_list,
                        }
                with open('result.json','w') as f:
                    json.dump(result,f)
                f.close()
                # sio.savemat(result,{'result':result})
                logger.info(ycl)
                ycl+=1
                end=time.time()
                logger.info(str(end-begin))