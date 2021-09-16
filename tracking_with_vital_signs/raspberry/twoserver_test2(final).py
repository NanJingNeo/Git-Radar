# coding=utf-8
from socket import *
import sys
import threading
from time import sleep
import time
import cmath
import numpy
import matplotlib.pyplot as plt
import scipy.io as sio
import os
from kalman import *
import logging
import argparse
import json

def response(sock, addr):
    global buf
    while True:
        sleep(0.01)
        data = sock.recv(1024).decode()
        sock.sendto('ok'.encode(),addr)
        if data:
            buf[str(addr[0])]=json.loads(data)


class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        time.sleep(0.3)
        self.result = self.func(*self.args)

    def get_result(self):
        # threading.Thread.join(self) # 等待线程执行完毕
        try:
            return self.result
        except Exception:
            return None


#############################################log#################################
logger = logging.getLogger('oneserver')
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
        logger.info('wrong ip')
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

HOST = ''
PORT = 10000
BUFSIZ = 1024
ADDR = (HOST, PORT)
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)
threads = []
socks = []
address = []
receive = []  # 初始化地址储存
resultaddr = []  # 单步探测地址储存
winsock=''
winaddr=''

msg = "start"
buf = dict()

print("wait for connect...")

while 1:
    sleep(0.1)
    sock, addr = tcpSerSock.accept()
    print(str(addr[0]) + ":response received")
    if addr[0] == args.winip:
        winsock = sock
        winaddr = addr
    else:
        t = MyThread(response, (sock, addr))
        threads.append(t)
        address.append(addr)
        socks.append(sock)

    if len(threads) == 3 and winaddr:
        for i in range(0, 3):
            threads[i].start()
            socks[i].sendto(msg.encode('utf-8'), address[i])
            buf[str(address[i][0])] = ''
        winsock.sendto(msg.encode('utf-8'), winaddr)
        break
    else:
        None

check = 0
num = 1

result = numpy.ones((248, 2))
# 每个网格点到雷达的距离
d2r=sio.loadmat('./d2r')['d2r']
d1=d2r[:,:,0]
d2 = d2r[:,:,1]
d3 = d2r[:,:,2]

x1_p = -1.2
y1_p = 0.3
x2_p = 1.2
y2_p = 2.7
km_x1 = Kalman(x1_p, 0)
km_y1 = Kalman(y1_p, 0)
km_x2 = Kalman(x2_p, 0)
km_y2 = Kalman(y2_p, 0)

while 1:
    for value in buf.values():
        if value:
            check += 1
    if check == 3:
        begin=time.time()
        jg = [buf[args.pi1]['1'],buf[args.pi1]['2']]
        jg2 = [buf[args.pi2]['1'], buf[args.pi2]['2']]
        jg3 = [buf[args.pi3]['1'], buf[args.pi3]['2']]
        nowtime=buf[args.pi1]['time'] ##这里取雷达1的时间
        buf = dict()
        logger.info(num)
        logger.info("***************")

        MLmatrix = numpy.zeros((420, 420, 8))
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    mlmtrx = (jg[i] - d1) ** 2 + (jg2[j] - d2) ** 2 + (jg3[k] - d3) ** 2
                    MLmatrix[:, :, (i - 1) * 4 + (j - 1) * 2 + k] = mlmtrx

        # 找最小均方误差的坐标组合
        Emin = []
        target_estimate = []
        for i in range(8):  # 计算每个距离组合中误差最小的坐标
            matrixI = numpy.array(MLmatrix[:, :, i])
            # print(matrixI)
            mm = numpy.min(matrixI)
            Emin.append(mm)
            # print('Emin:'+str(Emin))
            index = numpy.argmin(matrixI)
            # print('index:'+str(index))
            x = int(index // 420) * 0.01 - 2.1
            y = int(index % 420) * 0.01 - 0.6
            # print(str(x)+','+str(y))
            target_estimate.append([x, y])
        idx = numpy.argsort(Emin)  # 计算误差最小的距离组合
        # print(idx)
        x1_e = target_estimate[idx[0]][0]
        y1_e = target_estimate[idx[0]][1]
        x2_e = target_estimate[idx[1]][0]
        y2_e = target_estimate[idx[1]][1]
        de = (x1_e - x2_e) ** 2 + (y1_e - y2_e) ** 2

        # kalman滤波
        xep11 = x1_e - x1_p  # 当前时刻估计值与上一时刻预测值的差
        yep11 = y1_e - y1_p
        xep22 = x2_e - x2_p
        yep22 = y2_e - y2_p
        xep12 = x1_e - x2_p
        yep12 = y1_e - y2_p
        xep21 = x2_e - x1_p
        yep21 = y2_e - y1_p

        previous = [x1_p, y1_p, x2_p, y2_p]
        d11 = xep11 ** 2 + yep11 ** 2
        d22 = xep22 ** 2 + yep22 ** 2
        d12 = xep12 ** 2 + yep12 ** 2
        d21 = xep21 ** 2 + yep21 ** 2
        dmin = min(d11, d22, d12, d21)

        # [x1_p, y1_p, x2_p, y2_p]=[x1_e,y1_e,y2_e,y2_e]

        # 两估计点距离较远
        if de >= 0.36:  # 两估计点距离不低于0.6m时
            thrs = 6.25  # 当前估计点与上一时刻预测点的距离阈值(2.5m)，即新估计值与原轨迹的允许偏差范围
            # thrs = 2.25
            if dmin < thrs:
                if dmin == d11:
                    km_x1.z = np.array([x1_e])
                    km_x1.kf_update()
                    x1_p = km_x1.x[0, 0]
                    km_y1.z = np.array([y1_e])
                    km_y1.kf_update()
                    y1_p = km_y1.x[0, 0]
                    if x1_p<-2.1 or x1_p>2.1:
                        x1_p=x1_e
                    if y1_p<-0.6 or y1_p>3.6:
                        y1_p=y1_e
                    if d22 < thrs:
                        km_x2.z = np.array([x2_e])
                        km_x2.kf_update()
                        x2_p = km_x2.x[0, 0]
                        km_y2.z = np.array([y2_e])
                        km_y2.kf_update()
                        y2_p = km_y2.x[0, 0]
                        if x2_p < -2.1 or x2_p > 2.1:
                            x2_p =x2_e
                        if y2_p < -0.6 or y2_p > 3.6:
                            y2_p = y2_e
                    else:  # 当前估计点与上一时刻预测点的距离较远，此时认为实际位置已经偏离预测的轨迹，重新初始化该条轨迹的Kalman
                        # km_x2 = Kalman(x2_e, 0)
                        # km_y2 = Kalman(y2_e, 0)
                        # y2_p = y2_e
                        # x2_p = x2_e
                        logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                        # x2_ = np.dot(km_x2.A, km_x2.x)
                        # y2_ = np.dot(km_y2.A, km_y2.x)
                        # km_x2.z = np.array([x2_[0, 0]])
                        # km_x2.kf_update()
                        # x2_p = km_x2.x[0, 0]
                        # km_y2.z = np.array([y2_[0, 0]])
                        # km_y2.kf_update()
                        # y2_p = km_y2.x[0, 0]
                        # logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                        # if x2_p < -2.1 or x2_p > 2.1:
                        #     x2_p = previous[2]
                        # if y2_p < -0.6 or y2_p > 3.6:
                        #     y2_p = previous[3]
                elif dmin == d22:
                    km_x2.z = np.array([x2_e])
                    km_x2.kf_update()
                    x2_p = km_x2.x[0, 0]
                    km_y2.z = np.array([y2_e])
                    km_y2.kf_update()
                    y2_p = km_y2.x[0, 0]
                    if x2_p < -2.1 or x2_p > 2.1:
                        x2_p = x2_e
                    if y2_p < -0.6 or y2_p > 3.6:
                        y2_p = y2_e
                    if d11 < thrs:
                        km_x1.z = np.array([x1_e])
                        km_x1.kf_update()
                        x1_p = km_x1.x[0, 0]
                        km_y1.z = np.array([y1_e])
                        km_y1.kf_update()
                        y1_p = km_y1.x[0, 0]
                        if x1_p < -2.1 or x1_p > 2.1:
                            x1_p = x1_e
                        if y1_p < -0.6 or y1_p > 3.6:
                            y1_p = y1_e
                    else:
                        # km_x1 = Kalman(x1_e, 0)
                        # km_y1 = Kalman(y1_e, 0)
                        logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                        # x1_p = x1_e
                        # y1_p = y1_e
                        # x1_ = np.dot(km_x1.A, km_x1.x)
                        # y1_ = np.dot(km_y1.A, km_y1.x)
                        # km_x1.z = np.array([x1_[0, 0]])
                        # km_x1.kf_update()
                        # x1_p = km_x1.x[0, 0]
                        # km_y1.z = np.array([y1_[0, 0]])
                        # km_y1.kf_update()
                        # y1_p = km_y1.x[0, 0]
                        # logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                        # if x1_p < -2.1 or x1_p > 2.1:
                        #     x1_p = previous[0]
                        # if y1_p < -0.6 or y1_p > 3.6:
                        #     y1_p = previous[1]
                elif dmin == d12:
                    km_x2.z = np.array([x1_e])
                    km_x2.kf_update()
                    x2_p = km_x2.x[0, 0]
                    km_y2.z = np.array([y1_e])
                    km_y2.kf_update()
                    y2_p = km_y2.x[0, 0]
                    if x2_p < -2.1 or x2_p > 2.1:
                        x2_p = x2_e
                    if y2_p < -0.6 or y2_p > 3.6:
                        y2_p = y2_e
                    if d21 < thrs:
                        km_x1.z = np.array([x2_e])
                        km_x1.kf_update()
                        x1_p = km_x1.x[0, 0]
                        km_y1.z = np.array([y2_e])
                        km_y1.kf_update()
                        y1_p = km_y1.x[0, 0]
                        if x1_p < -2.1 or x1_p > 2.1:
                            x1_p = x1_e
                        if y1_p < -0.6 or y1_p > 3.6:
                            y1_p = y1_e
                    else:
                        # km_x1 = Kalman(x1_e, 0)
                        # km_y1 = Kalman(y1_e, 0)
                        logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                        # x1_p = x1_e
                        # y1_p = y1_e
                        # x1_ = np.dot(km_x1.A, km_x1.x)
                        # y1_ = np.dot(km_y1.A, km_y1.x)
                        # km_x1.z = np.array([x1_[0, 0]])
                        # km_x1.kf_update()
                        # x1_p = km_x1.x[0, 0]
                        # km_y1.z = np.array([y1_[0, 0]])
                        # km_y1.kf_update()
                        # y1_p = km_y1.x[0, 0]
                        # logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                        # if x1_p < -2.1 or x1_p > 2.1:
                        #     x1_p = previous[0]
                        # if y1_p < -0.6 or y1_p > 3.6:
                        #     y1_p = previous[1]
                else:
                    km_x1.z = np.array([x2_e])
                    km_x1.kf_update()
                    x1_p = km_x1.x[0, 0]
                    km_y1.z = np.array([y2_e])
                    km_y1.kf_update()
                    y1_p = km_y1.x[0, 0]
                    if x1_p < -2.1 or x1_p > 2.1:
                        x1_p = x1_e
                    if y1_p < -0.6 or y1_p > 3.6:
                        y1_p = y1_e
                    if d12 < thrs:
                        km_x2.z = np.array([x1_e])
                        km_x2.kf_update()
                        x2_p = km_x2.x[0, 0]
                        km_y2.z = np.array([y1_e])
                        km_y2.kf_update()
                        y2_p = km_y2.x[0, 0]
                        if x2_p < -2.1 or x2_p > 2.1:
                            x2_p = x2_e
                        if y2_p < -0.6 or y2_p > 3.6:
                            y2_p = y2_e
                    else:
                        # km_x2 = Kalman(x2_e, 0)
                        # km_y2 = Kalman(y2_e, 0)
                        # y2_p = y2_e
                        # x2_p = x2_e
                        logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                        # x2_ = np.dot(km_x2.A, km_x2.x)
                        # y2_ = np.dot(km_y2.A, km_y2.x)
                        # km_x2.z = np.array([x2_[0, 0]])
                        # km_x2.kf_update()
                        # x2_p = km_x2.x[0, 0]
                        # km_y2.z = np.array([y2_[0, 0]])
                        # km_y2.kf_update()
                        # y2_p = km_y2.x[0, 0]
                        # logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                        # if x2_p < -2.1 or x2_p > 2.1:
                        #     x2_p = previous[2]
                        # if y2_p < -0.6 or y2_p > 3.6:
                        #     y2_p = previous[3]
            else:
                # km_x2 = Kalman(x2_e, 0)
                # km_y2 = Kalman(y2_e, 0)
                # y2_p = y2_e
                # x2_p = x2_e
                logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                # km_x1 = Kalman(x1_e, 0)
                # km_y1 = Kalman(y1_e, 0)
                # logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                # x1_p = x1_e
                # y1_p = y1_e
                # x2_ = np.dot(km_x2.A, km_x2.x)
                # y2_ = np.dot(km_y2.A, km_y2.x)
                # km_x2.z = np.array([x2_[0, 0]])
                # km_x2.kf_update()
                # x2_p = km_x2.x[0, 0]
                # km_y2.z = np.array([y2_[0, 0]])
                # km_y2.kf_update()
                # y2_p = km_y2.x[0, 0]
                # x1_ = np.dot(km_x1.A, km_x1.x)
                # y1_ = np.dot(km_y1.A, km_y1.x)
                # km_x1.z = np.array([x1_[0, 0]])
                # km_x1.kf_update()
                # x1_p = km_x1.x[0, 0]
                # km_y1.z = np.array([y1_[0, 0]])
                # km_y1.kf_update()
                # y1_p = km_y1.x[0, 0]
                # logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                # if x1_p < -2.1 or x1_p > 2.1:
                #     x1_p = previous[0]
                # if y1_p < -0.6 or y1_p > 3.6:
                #     y1_p = previous[1]
                # if x2_p < -2.1 or x2_p > 2.1:
                #     x2_p = previous[2]
                # if y2_p < -0.6 or y2_p > 3.6:
                #     y2_p = previous[3]

        # 两估计点距离较近
        else:  # 两估计点距离小于0.6m时
            thrs = 1  # 当前估计点与上一时刻预测点的距离阈值(1m)
            if dmin < thrs:
                if dmin == d11:
                    km_x1.z = np.array([x1_e])
                    km_x1.kf_update()
                    x1_p = km_x1.x[0, 0]
                    km_y1.z = np.array([y1_e])
                    km_y1.kf_update()
                    y1_p = km_y1.x[0, 0]
                    if x1_p < -2.1 or x1_p > 2.1:
                        x1_p = x1_e
                    if y1_p < -0.6 or y1_p > 3.6:
                        y1_p = y1_e
                    if d22 < thrs:
                        km_x2.z = np.array([x2_e])
                        km_x2.kf_update()
                        x2_p = km_x2.x[0, 0]
                        km_y2.z = np.array([y2_e])
                        km_y2.kf_update()
                        y2_p = km_y2.x[0, 0]
                        if x2_p < -2.1 or x2_p > 2.1: #边界限制
                            x2_p = x2_e
                        if y2_p < -0.6 or y2_p > 3.6:
                            y2_p = y2_e
                    else:
                        # km_x2 = Kalman(x2_e, 0)
                        # km_y2 = Kalman(y2_e, 0)
                        # y2_p = y2_e
                        # x2_p = x2_e
                        # logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                        x2_ = np.dot(km_x2.A, km_x2.x)
                        y2_ = np.dot(km_y2.A, km_y2.x)
                        km_x2.z = np.array([x2_[0, 0]])
                        km_x2.kf_update()
                        x2_p = km_x2.x[0, 0]
                        km_y2.z = np.array([y2_[0, 0]])
                        km_y2.kf_update()
                        y2_p = km_y2.x[0, 0]
                        logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                        if x2_p < -2.1 or x2_p > 2.1:
                            x2_p = x2_e
                        if y2_p < -0.6 or y2_p > 3.6:
                            y2_p = y2_e
                elif dmin == d22:
                    km_x2.z = np.array([x2_e])
                    km_x2.kf_update()
                    x2_p = km_x2.x[0, 0]
                    km_y2.z = np.array([y2_e])
                    km_y2.kf_update()
                    y2_p = km_y2.x[0, 0]
                    if x2_p < -2.1 or x2_p > 2.1:
                        x2_p = x2_e
                    if y2_p < -0.6 or y2_p > 3.6:
                        y2_p = y2_e
                    if d11 < thrs:
                        km_x1.z = np.array([x1_e])
                        km_x1.kf_update()
                        x1_p = km_x1.x[0, 0]
                        km_y1.z = np.array([y1_e])
                        km_y1.kf_update()
                        y1_p = km_y1.x[0, 0]
                        if x1_p < -2.1 or x1_p > 2.1:
                            x1_p = x1_e
                        if y1_p < -0.6 or y1_p > 3.6:
                            y1_p = y1_e
                    else:
                        # km_x1 = Kalman(x1_e, 0)
                        # km_y1 = Kalman(y1_e, 0)
                        # logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                        # x1_p = x1_e
                        # y1_p = y1_e
                        x1_ = np.dot(km_x1.A, km_x1.x)
                        y1_ = np.dot(km_y1.A, km_y1.x)
                        km_x1.z = np.array([x1_[0, 0]])
                        km_x1.kf_update()
                        x1_p = km_x1.x[0, 0]
                        km_y1.z = np.array([y1_[0, 0]])
                        km_y1.kf_update()
                        y1_p = km_y1.x[0, 0]
                        logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                        if x1_p < -2.1 or x1_p > 2.1:
                            x1_p = x1_e
                        if y1_p < -0.6 or y1_p > 3.6:
                            y1_p = y1_e
                elif dmin == d12:
                    km_x2.z = np.array([x1_e])
                    km_x2.kf_update()
                    x2_p = km_x2.x[0, 0]
                    km_y2.z = np.array([y1_e])
                    km_y2.kf_update()
                    y2_p = km_y2.x[0, 0]
                    if x2_p < -2.1 or x2_p > 2.1:
                        x2_p = x2_e
                    if y2_p < -0.6 or y2_p > 3.6:
                        y2_p = y2_e
                    if d21 < thrs:
                        km_x1.z = np.array([x2_e])
                        km_x1.kf_update()
                        x1_p = km_x1.x[0, 0]
                        km_y1.z = np.array([y2_e])
                        km_y1.kf_update()
                        y1_p = km_y1.x[0, 0]
                        if x1_p < -2.1 or x1_p > 2.1:
                            x1_p = x1_e
                        if y1_p < -0.6 or y1_p > 3.6:
                            y1_p = y1_e
                    else:
                        # km_x1 = Kalman(x1_e, 0)
                        # km_y1 = Kalman(y1_e, 0)
                        # logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                        # x1_p = x1_e
                        # y1_p = y1_e
                        x1_ = np.dot(km_x1.A, km_x1.x)
                        y1_ = np.dot(km_y1.A, km_y1.x)
                        km_x1.z = np.array([x1_[0, 0]])
                        km_x1.kf_update()
                        x1_p = km_x1.x[0, 0]
                        km_y1.z = np.array([y1_[0, 0]])
                        km_y1.kf_update()
                        y1_p = km_y1.x[0, 0]
                        logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                        if x1_p < -2.1 or x1_p > 2.1:
                            x1_p = x1_e
                        if y1_p < -0.6 or y1_p > 3.6:
                            y1_p = y1_e
                else:
                    km_x1.z = np.array([x2_e])
                    km_x1.kf_update()
                    x1_p = km_x1.x[0, 0]
                    km_y1.z = np.array([y2_e])
                    km_y1.kf_update()
                    y1_p = km_y1.x[0, 0]
                    if x1_p < -2.1 or x1_p > 2.1:
                        x1_p = x1_e
                    if y1_p < -0.6 or y1_p > 3.6:
                        y1_p = y1_e
                    if d12 < thrs:
                        km_x2.z = np.array([x1_e])
                        km_x2.kf_update()
                        x2_p = km_x2.x[0, 0]
                        km_y2.z = np.array([y1_e])
                        km_y2.kf_update()
                        y2_p = km_y2.x[0, 0]
                        if x2_p < -2.1 or x2_p > 2.1:
                            x2_p = x2_e
                        if y2_p < -0.6 or y2_p > 3.6:
                            y2_p = y2_e
                    else:
                        # km_x2 = Kalman(x2_e, 0)
                        # km_y2 = Kalman(y2_e, 0)
                        # y2_p = y2_e
                        # x2_p = x2_e
                        # logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                        x2_ = np.dot(km_x2.A, km_x2.x)
                        y2_ = np.dot(km_y2.A, km_y2.x)
                        km_x2.z = np.array([x2_[0, 0]])
                        km_x2.kf_update()
                        x2_p = km_x2.x[0, 0]
                        km_y2.z = np.array([y2_[0, 0]])
                        km_y2.kf_update()
                        y2_p = km_y2.x[0, 0]
                        logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                        if x2_p < -2.1 or x2_p > 2.1:
                            x2_p = x2_e
                        if y2_p < -0.6 or y2_p > 3.6:
                            y2_p = y2_e
            else:
                # km_x1 = Kalman(x1_e, 0)
                # km_y1 = Kalman(y1_e, 0)
                # logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                # x1_p=x1_e
                # y1_p=y1_e
                # km_x2 = Kalman(x2_e, 0)
                # km_y2 = Kalman(y2_e, 0)
                # y2_p=y2_e
                # x2_p = x2_e
                logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                # x2_ = np.dot(km_x2.A, km_x2.x)
                # y2_ = np.dot(km_y2.A, km_y2.x)
                # km_x2.z = np.array([x2_[0, 0]])
                # km_x2.kf_update()
                # x2_p = km_x2.x[0, 0]
                # km_y2.z = np.array([y2_[0, 0]])
                # km_y2.kf_update()
                # y2_p = km_y2.x[0, 0]
                # x1_ = np.dot(km_x1.A, km_x1.x)
                # y1_ = np.dot(km_y1.A, km_y1.x)
                # km_x1.z = np.array([x1_[0, 0]])
                # km_x1.kf_update()
                # x1_p = km_x1.x[0, 0]
                # km_y1.z = np.array([y1_[0, 0]])
                # km_y1.kf_update()
                # y1_p = km_y1.x[0, 0]
                # logger.info('aaaaaaaaaaaaaaaaaaaaaa')
                # if x1_p < -2.1 or x1_p > 2.1:
                #     x1_p = previous[0]
                # if y1_p < -0.6 or y1_p > 3.6:
                #     y1_p = previous[1]
                # if x2_p < -2.1 or x2_p > 2.1:
                #     x2_p = previous[2]
                # if y2_p < -0.6 or y2_p > 3.6:
                #     y2_p = previous[3]



        end=time.time()
        # logger.info(str(end-begin))
        result={
            '1':[x1_p,y1_p],
            '2':[x2_p,y2_p],
            'time':int(nowtime)
        }
        logger.info(result)
        winsock.sendto(json.dumps(result).encode(), winaddr)
        winsock.recv(1024)

        # winsock.sendto((str(x1_p) + '+'+str(y1_p) + '+'+str(x2_p) +'+'+ str(y2_p)+ '|').encode('utf-8'), winaddr)

        num += 1
    check = 0
    sleep(0.005)
    # except:
    # 	None

