clear;clc;close all;
load('./Data/None.mat')
data=data(:,1:end-3);
M=10; %ǰ��ȥ��������
L=50; %ǰ��ȥ��������
K=1; %����ȥ��������
rx_num=2;
pg=1;

enresult=[];
indexresult=[];
count=0;
for i=1:25 %5sһ�����ڣ�1s����һ��
    rawData=data((i-1)*20+1:(i-1)*20+100,:);
    pureData=pca_filter_x4(data((i-1)*20+1:(i-1)*20+100,:),rx_num,pg,M,L,K);
%     pureData=rawData-mean(rawData);
%     mesh(pureData)    
    %%����д�������
    % �����
%     pureEn=sum(pureData.^2,1);
%     [maxEn,index]=max(pureEn);
%     if maxEn>4e-07
%         count=count+1;
%     end

    %������
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



