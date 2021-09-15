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



if __name__=="__main__":
    #############################################log#################################
    logger = logging.getLogger('pi4')
    logger.setLevel(logging.INFO)
    rf_handler = logging.StreamHandler(sys.stderr)  # 默认是sys.stderr
    rf_handler.setLevel(logging.DEBUG)
    rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(message)s"))
    logger.addHandler(rf_handler)


    frame_gen = sio.loadmat('frame_gen.mat')['frame_gen']
    eng = matlab.engine.start_matlab()
    mpl.rcParams['font.sans-serif'] = ['SimHei']
    eng.addpath('./ml')
    plt.ion()
    com = 'COM16'

    leiji = np.zeros((1, 751))
    M = 10
    L = 50
    data=dict()
    flag=1
    ycl=1

    data = sio.loadmat('./Data/dy_farmove_zxy_closemove.mat')['data']
    data = data[50:-16, :]
    result = []
    s1=1
    s2=3
    RawData1 = data.copy()
    PureData1 = pca_filter.p_f(RawData1[:, 0:-1].copy(), M, L)

    peaks1_list, peaks2_list, tops1_list, tops2_list, s1, s2 = gj(PureData1, RawData1[:, 0:-1], M, L, s1, s2)
    for i in range(int(floor((PureData1.shape[0] - 200) / 100 + 1))):
        tmp_tops1_list = matlab.double(tops1_list[0][i*100:i*100+200])
        tmp_peaks1_list = matlab.double(peaks1_list[0][i*100:i*100+200])
        tmp_tops2_list = matlab.double(tops2_list[0][i*100:i*100+200])
        tmp_peaks2_list = matlab.double(peaks2_list[0][i*100:i*100+200])

        br1, hr1 = eng.respiration_multi2_vncmd_2(tmp_tops1_list, tmp_peaks1_list, nargout=2)
        br2, hr2 = eng.respiration_multi2_vncmd_2(tmp_tops2_list, tmp_peaks2_list, nargout=2)

        print(i,hr1,hr2)
        result.append([hr1, hr2])
    result = np.array(result)
    result.reshape((int((data.shape[0] - 200) / 100 + 1), -1))
    # sio.savemat('zxyclosedyfar_demoresult.mat', {'result': result, })