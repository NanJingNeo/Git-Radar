# -*-coding:utf-8 -*-
from __future__ import print_function
import pca_filter
from pylab import *
import logging
import scipy.io as sio
from kalman_test import *

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
    dataEnergy=data*data
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

    M = 10
    L = 50

    leiji=sio.loadmat('./Data/dy_inroom_closemove.mat')['data']
    leiji=leiji[26:-20]
    resultPeaks=[]
    resultTops=[]

    flag=0

    d_k = Kalman(2, 0) #规定初始位置

    for i in range(int((leiji.shape[0]-210)/100+1)):
        RawData1 = leiji[i*100:i*100+210, :].copy()
        PureData1 = pca_filter.p_f(RawData1[:,0:-3].copy(), M, L)

        # topList, peakList=maxEnergyAndPosition(PureData1)
        # topList, peakList=findWithKalman(PureData1)
        topList, peakList = maxEnergyAndIndex(PureData1)

        # index = list(range(1, 191))


        # plt.clf()
        #
        # plt.scatter(index, peakList, color='r')
        # plt.axis([0, 191, 0, 5])
        # plt.pause(0.5)
        # plt.show()

        resultPeaks.append(peakList)
        resultTops.append(topList)

    resultPeaks=np.array(resultPeaks)
    resultTops=np.array(resultTops)
    resultPeaks.reshape((int((leiji.shape[0]-210)/100+1),-1))
    resultTops.reshape((int((leiji.shape[0] - 210) / 100 + 1), -1))
    sio.savemat('dyclose_maxEnergyAndIndex.mat',{'resultTops':resultTops,
                                                  'resultPeaks':resultPeaks})

    # RawData1 = leiji.copy()
    # PureData1 = pca_filter.p_f(RawData1[:,0:-3].copy(), M, L)
    #
    # # topList, peakList=maxEnergyAndPosition(PureData1)
    # topList, peakList=findPeaksAndTops(PureData1)
    #
    # index = list(range(1, 5991))
    #
    #
    # plt.clf()
    #
    # plt.scatter(index, peakList, color='r')
    # plt.axis([0, 5991, 0, 5])
    # plt.pause(10)
    # plt.show()
    #
    # resultPeaks.append(peakList)
    # resultTops.append(topList)