load('./20210331_jxk_static_locate_0_3.0.mat')
data=data(:,1:end-3);
M=10; %前面去掉的行数
L=0; %前面去掉的列数
K=50; %后面去掉的列数
rx_num=2;
pg=1;
pureData=pca_filter_x4(data,rx_num,pg,M,L,K);
mesh(pureData)

