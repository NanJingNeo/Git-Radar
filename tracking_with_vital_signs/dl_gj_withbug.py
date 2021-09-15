#-*-coding:utf-8 -*-
from sklearn.cluster import KMeans
from numpy import *
from time import sleep
import scipy.io as sio
from kalman import *
import os
from clean import *
from knn_kalman import knn_kalman
import matplotlib.pyplot as plt
#输出的是一个包含peaks1和peaks2的list，因为遇到了交叉点的时候需要跳过
#输出peaks1_list和peaks2_list

def gj(puredata,rawdata,M,L):
    plt.ion()
    frame_gen = sio.loadmat('frame_gen.mat')['frame_gen']
    c = puredata.shape  # puredata数组维度
    # print(c)
    peaks1_list = []
    peaks2_list = []
    tops1_list = []#近
    tops2_list = []#远
    s1=0
    s2=0
    km_rg1 = Kalman(s1, 0)  # Kalman滤波后的目标1距离值，是一个类，见karman.py
    km_rg2 = Kalman(s2, 0)  # Kalman滤波后的目标2距离值
    rdata=rawdata[M-1:-1, L-1:-1]       #rdata为rawdata的前10行&前50列&最后一行&最后一列不取
    leiji = np.zeros((10, c[1]))        #10行，用于存放puredata数据
    peaks1=[]
    peaks2=[]
    tops1 = []
    tops2 = []
    adj = 0     #两个轨迹粘连的次数
    index=[]
    resultIndex1=[]
    resultIndex2=[]
    resultPeaks1=[]
    resultPeaks2=[]
    htList=[]
    flag=1
    
    for i in range(0, c[0]):    #循环次数和puredata的行数一样

        leiji[1:-1, ] = leiji[0:-2, :]
        leiji[0, :] = rdata[i,:]        #10次循环后(不一定够十次)，leiji的最后一行不变，其他行均已被替换为rdata
        if i >= 10:
            if i == 10:
                 print('innit')
            else:

                meandata = np.mean(leiji, axis=0)   #得到一行数据
                signal = leiji[0, :] - meandata     #滑动？得到一行数据
                [cmap, dmap, n, ht] = clean(signal, frame_gen, 1e-3)    #输入一行信号，模板信号，一个阈值；返回一行ht。
                ss = ht[0:-25]
                ht[0:25] = np.zeros(25)
                ht[25:] = ss            #将ht后移25行，前25行置零
                a3_list=[]              #暂存
                for j in range(len(ht)):
                    if (ht[j]) > 0:
                        htList.append(j / 156.0 + 0.5)
                        index.append(i)
                        a3_list.append(j / 156.0 + 0.5)

                if flag:
                    estimator = KMeans(n_clusters=2)  # 构造聚类器
                    a3_ = np.array(a3_list)
                    a3_ = np.reshape(a3_, (-1, 1))  #铺成一行
                    if (len(a3_) > 1):
                        estimator.fit(a3_)  # 聚类
                        label_pred = estimator.cluster_centers_
                        if (label_pred[0] < label_pred[1]):
                            s1 = label_pred[1].tolist()
                            s2 = label_pred[0].tolist()
                        else:
                            s1 = label_pred[0].tolist()
                            s2 = label_pred[1].tolist()
                        s1 = s1[0]      #s1存大的那个
                        s2 = s2[0]
                        if abs(s1 - s2) > 0.2:#s1和s2的值被分离后，则不再使用聚类，且这时才开始统计s1和s2的数值。s1和s2的值作为初始值，用于KNN + karman
                            flag=0
                            if (s1 > s2):   #s1和s2相差超过0.2，则调换
                                ttmmpp = s1
                                s1 = s2
                                s2 = ttmmpp
                            if s2>4.4:
                                s2=4.4
                else:
                    # KNN + Kalman
                    km_rg1, km_rg2, s1, s2 = knn_kalman(ht, km_rg1, km_rg2, s1, s2)     #输入s1 s2不一定为0
                    tp1=puredata[i,int((s1-0.5)*156)]   #还原了s1在puredata中的位置
                    tp2=puredata[i,int((s2-0.5)*156)]

                    if (s1 > s2):
                        ttmmpp = s1
                        s1 = s2
                        s2 = ttmmpp

                    if (abs(s1 - s2) < 0.06):       #判断粘合次数
                        adj = adj + 1

                    if (adj > 10):
                        a3_list2 = []

                        for j in range(c[1]):
                            if (ht[j]) > 0:
                                a3_list2.append(j / 156.0 + 0.5)

                        estimator = KMeans(n_clusters=2)  # 构造聚类器
                        a3_ = np.array(a3_list2)
                        a3_ = np.reshape(a3_, (-1, 1))
                        if(len(a3_)>1):
                            estimator.fit(a3_)  # 聚类
                            label_pred = estimator.cluster_centers_
                            if(label_pred[0]<label_pred[1]):
                                s1 = label_pred[1].tolist()
                                s2 = label_pred[0].tolist()
                            else:
                                s1 = label_pred[0].tolist()
                                s2 = label_pred[1].tolist()
                            s1=s1[0]
                            s2=s2[0]
                            tp1 = puredata[i, int((s1 - 0.5) * 156)]
                            tp2 = puredata[i, int((s2 - 0.5) * 156)]
                            adj = 0

                    ##最后再判断两个人是否离得太近,若两个人距离大于0.6米则可以
                    if (abs(s1 - s2) > 0.2):
                        peaks1.append(s1)
                        peaks2.append(s2)
                        tops1.append(tp1)
                        tops2.append(tp2)
                        resultIndex1.append(i)
                        resultIndex2.append(i)
                        resultPeaks1.append(s1)
                        resultPeaks2.append(s2)

                    else:
                        peaks1_list.append(peaks1)
                        peaks2_list.append(peaks2)
                        peaks1=[]   #距离太小就清空peaks数组和tops数组，重新统计
                        peaks2=[]
                        tops1_list.append(tops1)
                        tops2_list.append(tops2)
                        tops1=[]
                        tops2=[]

            tops1_list.append(tops1)
            tops2_list.append(tops2)    #tops为puredata中原始数值
            peaks1_list.append(peaks1)
            peaks2_list.append(peaks2)

    plt.clf()       #清除图像窗口
    print('length:{},{}'.format(len(resultIndex1),len(resultPeaks1)))
    plt.scatter(index, htList, color='b')
    plt.scatter(resultIndex1, resultPeaks1, color='r')
    plt.scatter(resultIndex2, resultPeaks2, color='r')
    plt.axis([0, 200, 0, 5])
    plt.pause(0.2)
    plt.show()
    return peaks1_list,peaks2_list,tops1_list,tops2_list