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

def gj(puredata,rawdata,M,L,ls1,ls2):
    plt.ion()
    frame_gen = sio.loadmat('frame_gen.mat')['frame_gen']
    c = puredata.shape  # 数组维度
    # print(c)
    peaks1_list = []
    peaks2_list = []
    tops1_list=[]#近
    tops2_list=[]#远
    s1 = ls1  # 目标1的当前距离
    s2 = ls2  # 目标2的当前距离
    km_rg1 = Kalman(s1, 0)  # Kalman滤波后的目标1距离值
    km_rg2 = Kalman(s2, 0)  # Kalman滤波后的目标2距离值
    rdata=rawdata[M-1:-1, L-1:-1]
    leiji = np.zeros((10, c[1]))
    peaks1=[]
    peaks2=[]
    tops1 = []
    tops2 = []
    adj = 0  # 两个轨迹粘连的次数
    index=[]
    resultIndex1=[]
    resultIndex2=[]
    resultPeaks1=[]
    resultPeaks2=[]
    htList=[]
    for i in range(0, c[0]):


        tmp = rdata[i,:]

        xx = leiji[0:-2, :]
        leiji[1:-1, ] = xx
        leiji[0, :] = tmp
        if i >= 10:
            if i == 10:
                 print('innit')
            else:
                # print(1)
                meandata = np.mean(leiji, axis=0)
                dedata = leiji[0, :] - meandata
                # dedata[0:50] = np.zeros(50)
                signal = dedata
                # print(1)
                [cmap, dmap, n, ht] = clean(signal, frame_gen, 1e-3)
                # print(1)
                ss = ht[0:-25]
                ht[0:25] = np.zeros(25)
                ht[25:] = ss
                for j in range(len(ht)):
                    if (ht[j]) > 0:
                        htList.append(j)
                        index.append(i)

                # KNN + Kalman
                km_rg1, km_rg2, s1, s2 = knn_kalman(ht, km_rg1, km_rg2, s1, s2)
                if (s1 > s2):
                    ttmmpp = s1
                    s1 = s2
                    s2 = ttmmpp
                if s2 > 4.6:
                    s2 = 4.6
                if s1 > 4.6:
                    s1 = 4.6
                tp1=puredata[i,int((s1-0.5)*156)]
                tp2=puredata[i,int((s2-0.5)*156)]

                if (abs(s1 - s2) < 0.06):
                    adj = adj + 1
                    ########################
                # print ("ppppppppppppppppppppppppppppppppppp")
                # print(adj)

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
                        if (s1 > s2):
                            ttmmpp = s1
                            s1 = s2
                            s2 = ttmmpp
                        if s2 > 4.6:
                            s2 = 4.6
                        if s1 > 4.6:
                            s1 = 4.6
                        tp1 = puredata[i, int((s1 - 0.5) * 156)]
                        tp2 = puredata[i, int((s2 - 0.5) * 156)]
                        adj = 0

                # print(1)


                ##判断两个人是否离得太近,若两个人距离大于0.6米则可以
                if (abs(s1 - s2) > 0.2):
                    peaks1.append(round((s1-0.5)*156))
                    peaks2.append(round((s2-0.5)*156))
                    tops1.append(tp1)
                    tops2.append(tp2)
                    resultIndex1.append(i)
                    resultIndex2.append(i)
                    resultPeaks1.append(round((s1-0.5)*156+0.5))
                    resultPeaks2.append(round((s2-0.5)*156+0.5))


                else:
                    # print("************************************************************************************************")
                    peaks1_list.append(peaks1)
                    peaks2_list.append(peaks2)
                    peaks1=[]
                    peaks2=[]
                    # print(len(peaks1))
                    # print(peaks1)
                    tops1_list.append(tops1)
                    tops2_list.append(tops2)
                    tops1=[]
                    tops2=[]

                estimate1 = s1
                estimate2 = s2
                # plt.scatter(i, estimate1, color='b')
                # plt.scatter(i, estimate2, color='b')
                # # 设置坐标轴范围
                # plt.xlim(0, 990)
                # plt.ylim(0, 4.5)

    tops1_list.append(tops1)
    tops2_list.append(tops2)
    peaks1_list.append(peaks1)
    peaks2_list.append(peaks2)
    plt.clf()

    plt.scatter(index, htList, color='b')
    plt.scatter(resultIndex1, resultPeaks1, color='r')
    plt.scatter(resultIndex2, resultPeaks2, color='r')
    # plt.axis([0, 200, 0, 5])
    plt.pause(0.2)
    plt.show()
    # print(tops1_list)
    return peaks1_list,peaks2_list,tops1_list,tops2_list,s1,s2