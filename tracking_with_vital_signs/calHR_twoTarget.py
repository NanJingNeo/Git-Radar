# -*-coding:utf-8 -*-
from __future__ import print_function
import json
import time
from time import sleep
import matlab.engine
eng = matlab.engine.start_matlab()
eng.addpath('./ml')
print('Matlab start.')
from pylab import *
import threading
mpl.rcParams['font.sans-serif'] = ['SimHei']

tmp_hr1=0
tmp_hr2=0
load_hr=[]

while 1:
    time.sleep(0.1)
    try:
        with open("result.json", 'r') as load_f:
            load_hr = json.load(load_f)
        load_f.close()
    except:
        print('load wrong')

    if load_hr:
        tops1_list = load_hr['tops1_list']

        peaks1_list = load_hr['peaks1_list']
        tops2_list = load_hr['tops2_list']
        peaks2_list = load_hr['peaks2_list']

        hr_l1 = []
        hr_l2 = []
        lasthr1 = -1
        lasthr2 = -1
        # print(23)

        for i in range(len(peaks1_list)):
            if len(peaks1_list[i]) > 20:
                # print(len(peaks1_list[i]))
                tmp_tops1_list=matlab.double(tops1_list[i])
                tmp_peaks1_list=matlab.double(peaks1_list[i])
                tmp_tops2_list= matlab.double(tops2_list[i])
                tmp_peaks2_list=matlab.double(peaks2_list[i])

                br1, hr1 = eng.respiration_multi2_vncmd_2(tmp_tops1_list, tmp_peaks1_list, nargout=2)
                br2, hr2 = eng.respiration_multi2_vncmd_2(tmp_tops2_list, tmp_peaks2_list, nargout=2)
                if hr1>0 and hr2>0:
                    if lasthr1 == -1:
                        lasthr1 = hr1
                        lasthr2 = hr2
                        if hr1>50 and hr1<120:
                            hr_l1.append(hr1)
                        if hr2 > 50 and hr2 < 120:
                            hr_l2.append(hr2)

                    else:
                        abs1 = abs(hr1 - lasthr1)
                        abs2 = abs(hr1 - lasthr2)
                        abs3 = abs(hr2 - lasthr1)
                        abs4 = abs(hr2 - lasthr2)
                        minabs = min(abs1, abs2, abs3, abs4)
                        if (minabs == abs1 or minabs == abs4):
                            if hr1 > 50 and hr1 < 120:
                                hr_l1.append(hr1)
                            if hr2 > 50 and hr2 < 120:
                                hr_l2.append(hr2)
                        else:
                            if hr1 > 50 and hr1 < 120:
                                hr_l1.append(hr2)
                            if hr2 > 50 and hr2 < 120:
                                hr_l2.append(hr1)

                    if hr_l1:
                        tmp_hr1 = int(np.mean(hr_l1))
                    if hr_l2:
                        tmp_hr2 = int(np.mean(hr_l2))
                    print(tmp_hr1, tmp_hr2)

                    names = {"1":int(tmp_hr1),"2":int(tmp_hr2)}

                    filename='hrResult.json'
                    with open(filename,'w') as file_obj:
                        json.dump(names,file_obj)
                else:
                    print(hr1,hr2)

        load_hr = []
