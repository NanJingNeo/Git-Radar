#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
# sys.path.append("F:/radar/ModuleConnector/ModuleConnector-win32_win64-1.4.2/python36-win64/duoleida")
# sys.path.append("C:/Users/zxy/Desktop")
sys.path.append("/home/pi/ModuleConnector/ModuleConnector-rpi-1.5.3/python35-arm-linux-gnueabihf/duoleida")
import threading
import numpy as np
from numpy import *
import pymoduleconnector
from pymoduleconnector import ModuleConnector
from pymoduleconnector.ids import *
import time
from time import sleep
from pymoduleconnector import create_mc
import scipy.io as sio
import pca_filter
import random
from kalman import *
import serial
from socket import *
import os
import logging
import argparse


#############################################log#################################
logger = logging.getLogger('pi1')
logger.setLevel(logging.INFO)
rf_handler = logging.StreamHandler(sys.stderr)  # 默认是sys.stderr
rf_handler.setLevel(logging.DEBUG)
rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(message)s"))
logger.addHandler(rf_handler)

# print ("wait for connect...")

# f_handler = logging.FileHandler('error.log')
# f_handler.setLevel(logging.ERROR)
# f_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s"))
# logger.addHandler(f_handler)

#################################ip######################################
[server,pi1,pi2,pi3,winip]=['','','','','']
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
	if server=='' or pi1=='' or pi2=='' or pi3=='' or winip=='':
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
BUFSIZ = 1024
ADDR = (HOST,PORT)


ser = serial.Serial(args.com, 9600)
com = ser.name
#######################初始化##############################
with create_mc(com) as mc:
	xep = mc.get_xep()

	# inti x4driver
	xep.x4driver_init()

	# Set enable pin
	xep.x4driver_set_enable(1);

	# Set iterations
	xep.x4driver_set_iterations(64);
	# Set pulses per step
	xep.x4driver_set_pulses_per_step(20);
	# Set dac step
	xep.x4driver_set_dac_step(1);
	# Set dac min
	xep.x4driver_set_dac_min(949);
	# Set dac max
	xep.x4driver_set_dac_max(1100);
	# Set TX power
	xep.x4driver_set_tx_power(2);

	# Enable downconversion
	xep.x4driver_set_downconversion(0);

	# Set frame area offset
	xep.x4driver_set_frame_area_offset(0.18)
	offset = xep.x4driver_get_frame_area_offset()


	# Set frame area
	xep.x4driver_set_frame_area(0.2, 5)
	frame_area = xep.x4driver_get_frame_area()

	# Set TX center freq
	xep.x4driver_set_tx_center_frequency(3);

	# Set PRFdiv
	xep.x4driver_set_prf_div(16)
	prf_div = xep.x4driver_get_prf_div()


	# Start streaming
	xep.x4driver_set_fps(0.1)
	fps = xep.x4driver_get_fps()
	# Stop streaming
	logger.info("wait")

	#-----------------------------------读取数据与处理-------------------------------------#
	tmp=[]
	tmp=np.array(tmp)
	tcpCliSock = socket(AF_INET,SOCK_STREAM)
	tcpCliSock.connect(ADDR)
	def read_frame(): 
		"""Gets frame data from module"""
		d = xep.read_message_data_float()
		frame = np.array(d.data) 
		# Convert the resulting frame to a complex array if downconversion is enabled
		return frame

	def get_data():
		save = np.ones((1, 751))

		for jj in range(1):

			frame2 = read_frame()

			save[jj, 0:750] = frame2
			#ll2=time.clock()-start
			start=1
			ll2=time.time()-start
			save[jj, -1] = ll2
		return save

	################################数据处理##################################

	ycl=1
	ijjj=1
	leji=np.zeros((1,750))
	M = 0
	L = 50
	flag=1

	def l_m(Pure,M,L):
		pnum=float(156)
		c=Pure.shape
		valueplace = zeros(c[0])
		for i in range(c[0]):
			valueplace[i]=np.argmax(Pure[i,:])+L
		return valueplace

	while(True):
		msg=tcpCliSock.recv(1024).decode()
		if msg=="start":
			xep.x4driver_set_fps(20)
			break
		else:
			None
		sleep(0.1)

	#----------------------------初始化一百次获得环境数据--------------------------#
	# data = sio.loadmat('./save/2019-01-15-20-35/2019-01-15-20-35rawdata3.mat')["pcradar3"];
	# data = np.ones((35000, 751))
	leji = sio.loadmat('./leji.mat')["leji"];
	while 1:
	# for i in range(0,35000):
		#print(ycl)	
		#initialbegin=time.time()
		save=get_data()
		# data[i,:]=save
		tmp = save[:, 0:750]
		if ijjj==4:
			ijjj=1
			# RawData = np.reshape(data[i, 0:750],[1,750])
			# tmp=np.reshape(tmp,[1,650])
			leji = np.vstack((leji, tmp))
			if ycl==1:
				logger.info('innit')
				tcpCliSock.send("innit".encode())
			else:
				None
			while True:
				msg2=tcpCliSock.recv(1024).decode()
				if msg2=="detectionbegin":
					break
				else:
					None
			leji = leji[1:101, :]
			PureData = pca_filter.p_f(leji, M, L)
			p = PureData[99, :]
			PD = np.reshape(p, [1, -1])
			v = l_m(PD, M, L)/156
			tcpCliSock.send(str(v[0])[:6].encode())
			logger.info(str(v[0])[:6])
			sleep(0.005)
			logger.info(ycl)
			ycl=ycl+1
		else:
			ijjj+=1
		tmp = []


now = int(round(time.time()*1000))
now02 = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(now/1000))[:-3]
path="./save/"+now02+'/'
if not os.path.exists(path):
	os.makedirs(path)
sio.savemat(path+now02+'rawdata1', {'pcradar1': data})

xep.module_reset()


