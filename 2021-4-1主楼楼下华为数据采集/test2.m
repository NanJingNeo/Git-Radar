clear;clc;close all;
load('./Data/None.mat')
data=data(:,1:end-3);
M=10; %前面去掉的行数
L=50; %前面去掉的列数
K=1; %后面去掉的列数
rx_num=2;
pg=1;

enresult=[];
indexresult=[];
count=0;
for i=1:25 %5s一个窗口，1s滑动一次
    rawData=data((i-1)*20+1:(i-1)*20+100,:);
    pureData=pca_filter_x4(data((i-1)*20+1:(i-1)*20+100,:),rx_num,pg,M,L,K);
%     pureData=rawData-mean(rawData);
%     mesh(pureData)    
    %%这里写处理代码
    % 最大列
%     pureEn=sum(pureData.^2,1);
%     [maxEn,index]=max(pureEn);
%     if maxEn>4e-07
%         count=count+1;
%     end

    %总能量
    pureEn=sum(sum(pureData.^2));
%     [maxEn,index]=max(pureEn);
    if pureEn>4e-05
        count=count+1;
    end
    
    enresult=[enresult pureEn];
%     indexresult=[indexresult index];
end

max(enresult)
% mean(indexresult/156+0.5)
count



