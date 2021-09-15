# -*-coding:utf-8 -*-
import scipy.io as sio
import numpy as np


# from numpy import *
def p_f(RawData, M, L):
    c = RawData.shape  # 数组维度
    FrameStitchnum = int(c[-1] / 156)
    # SpeedOfLight = 3 * 10 ^ 8
    # Resolution = 0.006430041
    # Fs = SpeedOfLight / (Resolution * 2)
    #########带通滤波器##################
    load_bf = sio.loadmat('./BandFilter_3.mat')
    BanFilter = load_bf['bandfilter']
    BanFilter2 = np.array(BanFilter)
    BanFilter3 = np.reshape(BanFilter2, [-1])

    #########带通滤波器##################
    batches = c[0]
    BandpassData = np.zeros((c[0], c[1]))
    ClutterData = np.zeros((c[0], c[1]))
    PureData = np.zeros((c[0], c[1]))
    pnum = 76  # 帧长
    firnum = 50
    alpha = 0.5
    ####################################预处理######################################
    for row in range(batches):
        for framenum in range(FrameStitchnum):
            blockdata = RawData[row, framenum * pnum + 1:min((framenum + 1) * pnum, c[1])]
            blockmean = np.mean(blockdata)
            # aa=blockdata.shape

            DCmean = np.ones((1, blockdata.shape[0])) * blockmean
            RawData[row, framenum * pnum + 1:min((framenum + 1) * pnum, c[1])] = blockdata - DCmean

        convres = np.convolve(RawData[row, :], BanFilter3)

        BandpassData[row, :] = convres[firnum // 2:firnum // 2 + c[1]]
        if row == 0:
            ClutterData[row, :] = (1 - alpha) * BandpassData[row, :]
            PureData[row, :] = BandpassData[row, :] - ClutterData[row, :]
        if row > 0:
            ClutterData[row, :] = alpha * ClutterData[row - 1, :] + (1 - alpha) * BandpassData[row, :]
            PureData[row, :] = BandpassData[row, :] - ClutterData[row, :]
    PureData = PureData[M:c[0], L:c[1]]

    return PureData
