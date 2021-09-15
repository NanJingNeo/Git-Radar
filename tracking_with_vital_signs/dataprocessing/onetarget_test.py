# -*-coding:utf-8 -*-
from __future__ import print_function
from pymoduleconnector import create_mc
import pca_filter
import numpy as np
import matlab.engine
from dl_gj import *
from pylab import *
from kalman_test import *
import logging
import scipy.io as sio

def maxEnergyAndPosition(puredata):
    data = puredata.copy()
    dataEnergy=abs(data)
    topList=[]
    peakList=[]
    for i in range(dataEnergy.shape[0]):
        topList.append(max(dataEnergy[i,:]))
        peakList.append(np.argmax(dataEnergy[i,:])/156+0.5)
    return topList,peakList

def findWithKalman(puredata):
    global d_k
    data = puredata.copy()
    dataEnergy=abs(data)
    topList=[]
    peakList=[]
    for i in range(dataEnergy.shape[0]):
        distance=np.argmax(dataEnergy[i,:])/156+0.5
        if i==0:
            if abs(distance-d_k.xx)>1:
                distance=d_k.xx
        else:
            if abs(distance-peakList[i-1])>1:
                distance=peakList[i-1]
        d_k.z = np.array([distance])
        d_k.kf_update()
        lcs = d_k.x[0, 0]
        if lcs>2.5 or lcs<0.5:
            lcs=distance
        peakList.append(lcs)
        topList.append(data[i,int((lcs-0.5)*156)])
    return topList,peakList

def maxEnergyAndIndex(puredata):
    data = puredata.copy()
    dataEnergy = abs(data)
    topList = []
    peakList = []
    for i in range(dataEnergy.shape[0]):
        topList.append(max(dataEnergy[i, :]))
        peakList.append(np.argmax(dataEnergy[i, :]))
    return topList, peakList

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
    M = 10
    L = 50
    flag=1
    ycl=1

    eng = matlab.engine.start_matlab()
    eng.addpath('./ml')
    from pylab import *

    mpl.rcParams['font.sans-serif'] = ['SimHei']

    data=sio.loadmat('./Data/dy_inroom_farmove.mat')['data']
    # data=data[26:-20,:] #dycolse
    data = data[35:-11, :] #dyfar
    result=[]
    d_k = Kalman(2, 0)  # 规定初始位置
    for i in range(int(floor((data.shape[0] - 200) / 100 + 1))):
        RawData1 = data[i * 100:i * 100 + 200, :].copy()
        PureData1 = pca_filter.p_f(RawData1[:, 0:-3].copy(), M, L)

        # topList, peakList = findWithKalman(PureData1)

        # index = list(range(1, 191))

        # plt.clf()
        #
        # plt.scatter(index, peakList, color='r')
        # plt.axis([0, 191, 0, 5])
        # plt.pause(0.5)
        # plt.show()

        # topList,peakList=maxEnergyAndPosition(PureData1)

        topList, peakList = maxEnergyAndIndex(PureData1) #效果较好

        tmp_tops1_list = matlab.double(topList)
        tmp_peaks1_list = matlab.double(peakList)
        br1, hr1 = eng.respiration_multi2_vncmd_2(tmp_tops1_list, tmp_peaks1_list, nargout=2)
        result.append([br1, hr1])
        print(i,br1,hr1)

    result= np.array(result)
    result.reshape((int((data.shape[0] - 200) / 100 + 1), -1))
    sio.savemat('./result/dyfar_sampFreq20Fs120bw1.2_result.mat', {'result': result,})

    # RawData1 = data.copy()
    # PureData1 = pca_filter.p_f(RawData1[:,0:-3].copy(), M, L)
    #
    # # topList, peakList=maxEnergyAndPosition(PureData1)
    # topList, peakList=findPeaksAndTops(PureData1)
    #
    # index = list(range(1, RawData1.shape[0]-M+1))
    #
    #
    # plt.clf()
    #
    # plt.scatter(index, peakList, color='r')
    # plt.axis([0, 5991, 0, 5])
    # plt.pause(10)
    # plt.show()



