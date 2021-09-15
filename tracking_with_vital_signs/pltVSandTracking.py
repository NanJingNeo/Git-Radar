# -*- coding: utf-8 -*-
import threading
from numpy import *
import time
import numpy as np
from socket import *
import logging
import matplotlib.pyplot as plt
import json
import warnings# import globaldefine
import select
import sys
warnings.filterwarnings('ignore')

plt.ion()


def oximeter(port_oximeter):
    global result
    tcpCliSock3= socket(AF_INET,SOCK_STREAM)
    tcpCliSock3.setblocking(False)
    tcpCliSock3.bind(('', port_oximeter))
    tcpCliSock3.listen()
    logger.info('oximeter is ready.')
    inputs = [tcpCliSock3, ]
    while 1:
        r_list, w_list, e_list = select.select(inputs, [], [],0.005)
        for event in r_list:
            if event == tcpCliSock3:
                new_sock, addr = event.accept()
                inputs=[tcpCliSock3,new_sock,]
            else:
                data = event.recv(1024)
                # logger.info(data)
                if data!=b'' and data!=b'socket connected':
                    # logger.info(data)
                    oximeter_result=data.split()
                    try:
                        oximeter_tag_num=bytes.decode(oximeter_result[-1])[-1]
                        # if oximeter_list[oximeter_tag_num - 1] in result.keys():
                        result[oximeter_tag_num]['oximeter'] = int(oximeter_result[-2])
                    except:
                        logger.info('oximeter id wrong')


if __name__=='__main__':
    #############################################log#################################
    global logger
    logger = logging.getLogger('driver_vital_signs')
    logger.setLevel(logging.INFO)
    rf_handler = logging.StreamHandler(sys.stderr)  # 默认是sys.stderr
    rf_handler.setLevel(logging.DEBUG)
    rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(message)s"))
    logger.addHandler(rf_handler)

    port_oximeter=10001

    result = {
        '1': {'oximeter':80,
              },
        '2': {'oximeter': 80,
              }
    }
    slide_window=[]
    #######################


    t3 = threading.Thread(name="oximeter", target=oximeter,args=(port_oximeter,))
    t3.start()

    #画图

    Radarbox1 = [0, 0, 0, 0, 0, 0]
    brbox2 = [0, 0, 0, 0, 0, 0]
    Oxi1box = [0, 0, 0, 0, 0, 0]

    timebox = [0, 0, 0, 0, 0, 0]

    xxx = [1, 2, 3, 4, 5, 6]

    while 1:
        try:
            with open("hrResult.json", 'r') as load_f:
                load_hr = json.load(load_f)
            load_f.close()

            with open("trkResult.json", 'r') as load_f:
                load_trk = json.load(load_f)
            load_f.close()

            logger.info(load_trk)
        except:
            print('load wrong')
        # print(load_hr["1"])
        # print(load_trk["1"])
        # print(load_trk["1"][0])

        start = time.perf_counter()
        plt.figure(12, figsize=(10, 4))
        plt.clf()
        plt.subplot(121)

        for ii in range(7):
            for iii in range(7):
                plt.text(iii * 0.6 - 1.9, 3.5 - 0.3 - ii * 0.6, str(ii * 7 + iii + 1), fontdict={'size': 10})

        xnum = [-2.1, 2.1, 0]
        ynum = [0, 0, 3.6]
        xl = np.arange(-2.1, 2.1, 0.6)
        yl = np.arange(-0.6, 3.6, 0.6)
        # xnum = [-2.1, 2.1, 0]
        # ynum = [0.6, 0.6, 4.2]
        # xl = np.arange(-2.1, 2.1, 0.6)
        # yl = np.arange(-0.6, 3.6, 0.6)
        plt.xticks(xl)
        plt.yticks(yl)
        plt.grid(True)
        plt.axis([-2.1, 2.1, -0.6, 3.6])

        x1 = np.arange(-2.1, -1.5, 0.01)
        y11 = 3.6 - x1 * 0
        y12 = 3 - x1 * 0
        plt.fill_between(x1, y11, y12, facecolor='grey')

        x2 = np.arange(1.5, 2.1, 0.01)
        y21 = 3.6 - x2 * 0
        y22 = 3 - x2 * 0
        plt.fill_between(x2, y21, y22, facecolor='grey')

        x3 = np.arange(-1.5, 1.5, 0.01)
        y31 = 3 - x3 * 0
        y32 = 0 - x3 * 0
        plt.fill_between(x3, y31, y32, facecolor='pink')

        plt.plot(load_trk["1"][0], load_trk["1"][1], color='red', marker='o', markersize=50)
        plt.plot(load_trk["2"][0], load_trk["2"][1], color='red', marker='o', markersize=50)

        plt.scatter(xnum, ynum, s=1000, c='blue', marker='o', label='radar')

        plt.subplot(122)

        xl = np.arange(0, 3, 1)
        yl = np.arange(0, 2, 1)
        plt.xticks([])
        plt.yticks([])
        plt.grid(True)

        plt.text(0.1, 0.3, 'oximeter', fontdict={'size': 20})
        plt.text(1.1, 0.3, result['1']['oximeter'], fontdict={'size': 30})
        plt.text(2.1, 0.3, result['2']['oximeter'], fontdict={'size': 30})

        plt.text(0.1, 1.3, 'radar', fontdict={'size': 20})
        plt.text(1.1, 1.3, str(int(load_hr["1"])), fontdict={'size': 30})
        plt.text(2.1, 1.3, str(int(load_hr["2"])), fontdict={'size': 30})

        plt.text(0.8, 2.5, 'heartbeats1', fontdict={'size': 20})
        plt.text(1.1, 2.2, '(bpm)', fontdict={'size': 20})
        plt.text(1.8, 2.5, 'heartbeats2', fontdict={'size': 20})
        plt.text(2.1, 2.2, '(bpm)', fontdict={'size': 20})
        plt.axis([0, 3, 0, 3])

        end = time.perf_counter()
        logger.info(str(end - start) + 'lalala')
        plt.show()
        plt.pause(0.005)
        time.sleep(0.35)