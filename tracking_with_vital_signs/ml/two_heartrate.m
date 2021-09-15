radardata=load('/Users/yuyibo/Desktop/data/交叉轨迹/radar3_3.mat');
radar=radardata.radar3;
rx_num=2;  %%雷达类型
pg=1;      %%发射脉冲频段 --- X4
pg2=1;
M=60;L=50;K=51;
%前去M行，前去L列，后去K列
%生成两个peaks（这里可以用多人的追踪方法）
T=size(Pure,1);
peaks=zeros(1,T)
[PureData]=pca_filter_x4(radar,rx_num,pg,M,L,K);
[br_v,hr_v]=respiration_multi2_vncmd_1(PureData);
