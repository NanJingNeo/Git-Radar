load('./20210331_jxk_static_locate_0_3.0.mat')
data=data(:,1:end-3);
M=10; %ǰ��ȥ��������
L=0; %ǰ��ȥ��������
K=50; %����ȥ��������
rx_num=2;
pg=1;
pureData=pca_filter_x4(data,rx_num,pg,M,L,K);
mesh(pureData)

