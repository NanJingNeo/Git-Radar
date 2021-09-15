# -*-coding:utf-8 -*-
from __future__ import print_function
import json
import time
from time import sleep
import matlab.engine
eng = matlab.engine.start_matlab()
eng.addpath('./ml')
from pylab import *
mpl.rcParams['font.sans-serif'] = ['SimHei']

tmp_hr1=0
tmp_hr2=0
load_hr=[]

hr_l1 = []
while 1:
    time.sleep(0.1)
    try:
        with open("result_one_target.json", 'r') as load_f:
            load_hr = json.load(load_f)
        load_f.close()
    except:
        print('load wrong')

    if load_hr:
        topList = load_hr['topList']

        peakList = load_hr['peakList']

        lasthr1 = -1

        tmp_tops1_list=matlab.double(topList)
        tmp_peaks1_list=matlab.double(peakList)
        br1, hr1 = eng.respiration_multi2_vncmd_1(tmp_tops1_list, tmp_peaks1_list, nargout=2)

        if len(hr_l1)>3:
            hr_l1.pop()
        hr_l1.append(hr1)
        tmp_hr1 = int(np.mean(hr_l1))
        print(hr1)

        f1 = open('oxi1_data_matlab.txt', 'r')
        oxiread1 = f1.read()
        oxi1 = oxiread1.split(' ')
        oxi1 = oxi1[1]
        f1.close()

        print('radar:{},oximeter:{}'.format(str(tmp_hr1),str(oxi1)))


        # names = {"1":int(tmp_hr1),"2":int(tmp_hr2)}
        #
        # filename='hrResult.json'
        # with open(filename,'w') as file_obj:
        #     json.dump(names,file_obj)

        load_hr = []
