radardata=load('/Users/yuyibo/Desktop/data/����켣/radar3_3.mat');
radar=radardata.radar3;
rx_num=2;  %%�״�����
pg=1;      %%��������Ƶ�� --- X4
pg2=1;
M=60;L=50;K=51;
%ǰȥM�У�ǰȥL�У���ȥK��
%��������peaks����������ö��˵�׷�ٷ�����
T=size(Pure,1);
peaks=zeros(1,T)
[PureData]=pca_filter_x4(radar,rx_num,pg,M,L,K);
[br_v,hr_v]=respiration_multi2_vncmd_1(PureData);
