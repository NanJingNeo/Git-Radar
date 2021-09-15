# -*-coding:utf-8 -*-
from __future__ import print_function
from pymoduleconnector import create_mc
import pca_filter
import numpy
import matlab.engine
from dl_gj_withbug import *
from pylab import *
import threading

########radar()函数只是为了获取数据，并没有更多功能########
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
            save = np.ones((1, 750))

            for jj in range(1):
                frame2 = read_frame()

                save[jj, :] = frame2
            return save

        ################################数据处理##################################

        while 1:
            save = get_data()
            leiji = np.vstack((leiji, save))
            sleep(0.005)

    xep.module_reset()


if __name__=="__main__":
    #############################################log#################################
    global logger
    logger = logging.getLogger('two_walkers_heartrate')
    logger.setLevel(logging.INFO)
    rf_handler = logging.StreamHandler(sys.stderr)  # 默认是sys.stderr
    rf_handler.setLevel(logging.DEBUG)
    rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(message)s"))
    logger.addHandler(rf_handler)
    ##################################################################################
    eng = matlab.engine.start_matlab()
    mpl.rcParams['font.sans-serif'] = ['SimHei']
    eng.addpath('./ml')
    plt.ion()
    com = 'COM16'

    leiji = np.zeros((1, 750))      #leiji为全局变量
    M = 10      #行前截10
    L = 50      #列后截50
    hr_list1 = []
    tmp_hr1 = 0
    tmp_hr2 = 0

    t=threading.Thread(name='UWB',target=radar,args=(com,))
    t.start()

    while 1:
        sleep(0.01)
        if leiji.shape[0] >= 220:
            RawData1 = leiji[-201:-1, 0:-1].copy()
            ###行前截10，列后截50，前截100
            # 590,600
            PureData1 = pca_filter.p_f(RawData1, M, L)

            # 双人
            peaks1_list, peaks2_list, tops1_list, tops2_list= gj(PureData1, RawData1, M, L)

            hr_l1 = []
            hr_l2 = []
            lasthr1 = -1
            lasthr2 = -1

            for i in range(len(peaks1_list)):   #len()为二维数组的行数
                if len(peaks1_list[i]) > 20:

                    peaks1_tmp = peaks1_list[i] #每次取一行数据
                    peaks2_tmp = peaks2_list[i]
                    tops1_tmp = tops1_list[i]
                    tops2_tmp = tops2_list[i]

                    tops1_tmp = matlab.double(tops1_tmp)
                    peaks1_tmp = matlab.double(peaks1_tmp)
                    tops2_tmp = matlab.double(tops2_tmp)
                    peaks2_tmp = matlab.double(peaks2_tmp)
                    br1, hr1 = eng.respiration_multi2_vncmd_1(tops1_tmp, peaks1_tmp, nargout=2)     #调用的matlab函数，在.ml文件夹里，输入一行数据，返回的应该是一个数值
                    br2, hr2 = eng.respiration_multi2_vncmd_1(tops2_tmp, peaks2_tmp, nargout=2)

                    if lasthr1 == -1:
                        lasthr1 = hr1
                        lasthr2 = hr2
                        hr_l1.append(hr1)
                        hr_l2.append(hr2)

                    else:

                        abs1 = abs(hr1 - lasthr1)
                        abs2 = abs(hr1 - lasthr2)
                        abs3 = abs(hr2 - lasthr1)
                        abs4 = abs(hr2 - lasthr2)
                        minabs = min(abs1, abs2, abs3, abs4)
                        if (minabs == abs1 or minabs == abs4):
                            hr_l1.append(hr1)
                            hr_l2.append(hr2)
                        else:
                            hr_l1.append(hr2)
                            hr_l2.append(hr1)

            # 防止出现心率0值
            if hr_l1:
                tmp_hr1 = int(np.mean(hr_l1))
                tmp_hr2 = int(np.mean(hr_l2))
            print(tmp_hr1,tmp_hr2)

            # #绘制表格
            # f1 = open('oxi1_data_matlab.txt', 'r')
            # oxiread1 = f1.read()
            # oxi1 = oxiread1.split(' ')
            # oxi1 = oxi1[1]
            # f1.close()
            #
            # f2 = open('oxi2_data_matlab.txt', 'r')
            # oxiread2 = f2.read()
            # oxi2 = oxiread2.split(' ')
            # oxi2 = oxi2[1]
            # f2.close()
            #
            # plt.clf()
            # print(hr_l1)
            # print(hr_l2)
            # xl = numpy.arange(0, 3, 1)
            # yl = numpy.arange(0, 2, 1)
            # plt.xticks([])
            # plt.yticks([])
            # plt.grid(True)
            #
            # plt.text(0.2, 0.3, 'oximeter', fontdict={'size': 15})
            # plt.text(1.2, 0.3, oxi1, fontdict={'size': 35})
            # plt.text(2.2, 0.3, oxi2, fontdict={'size': 35})
            #
            # plt.text(0.2, 1.3, 'radar', fontdict={'size': 15})
            # plt.text(1.2, 1.3, str(tmp_hr1), fontdict={'size': 35})
            # plt.text(2.2, 1.3, str(tmp_hr2), fontdict={'size': 35})
            #
            # plt.text(1.1, 2.6, 'heartbeats1', fontdict={'size': 15})
            # plt.text(1.1, 2.3, '(bpm)', fontdict={'size': 15})
            # plt.text(2.1, 2.6, 'heartbeats2', fontdict={'size': 15})
            # plt.text(2.1, 2.3, '(bpm)', fontdict={'size': 15})
            #
            # plt.axis([0, 3, 0, 3])
            # plt.pause(0.01)
            # plt.draw()


