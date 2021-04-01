import socket
import sys
import matplotlib.pyplot as plt
import numpy
from socket import *
from time import *
import logging
import argparse

#############################################log#################################
logger = logging.getLogger('win')
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
with open('D:/lab/raspberry/ip.txt') as f:
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
###########################################################################

plt.ion() #可打开多图对比
# xl = numpy.arange(-2.1, 2.1, 0.6)
# yl = np.arange(0, 4.2, 0.6)

HOST = args.server
PORT = 10000
BUFSIZ = 1024
ADDR = (HOST,PORT)
tcpCliSock = socket(AF_INET,SOCK_STREAM)
tcpCliSock.connect(ADDR)
logger.info("wait")

num=1
buf=''
while True:
	buf = tcpCliSock.recv(1024).decode()
	try:
		# tcpCliSock.send('ok'.encode())
		begin=time()
		a=buf.split('|')[0]
		# buf=buf[len(a)+1:]
		x=float(a.split(',')[0])
		y=float(a.split(',')[1])
		logger.info(num)
		# print(x)
		# print("----------------")
		plt.clf()
		# plt.scatter(x,y,s=200)
		for ii in range(7):
			for iii in range(7):
				plt.text(iii * 0.6 - 1.8, 3.5 - 0.25 - ii * 0.6, str(ii * 7 + iii + 1), fontdict={'size': 15})

		xnum=[-2.1,2.1,0]
		ynum=[0,0,3.6]
		xl = numpy.arange(-2.1, 2.1, 0.6)
		yl = numpy.arange(-0.6, 3.6, 0.6)
		plt.xticks(xl)
		plt.yticks(yl)
		plt.grid(True)

		plt.axis([-2.1, 2.1, -0.6, 3.6])
		begin=time()
		plt.plot(x,y,color='red',marker='o',markersize=20)
		plt.scatter(xnum,ynum,s=300,c='blue',marker='o',label='radar')
		plt.pause(0.0005)
		plt.show()
		end=time()
		logger.info(num)
		logger.info(buf)
		num+=1
		#end=time()
		logger.info("delay:"+str(end-begin))
	except:
		None
