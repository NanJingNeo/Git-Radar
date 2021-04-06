%%%%每次脉冲返回一行数据，每行数据个数与探测距离相关
clear;clc;close all;

M=10; %前面去掉的行数
L=50; %前面去掉的列数
K=1; %后面去掉的列数
rx_num=2;
pg=1;

count=0;%读取的时间片段个数
rmse=[];%均方误差
names=[];

for t=[0.5,1,2,3]
    char_t=num2str(t);
    fileFolder=fullfile(['./Data/',char_t]);
    dirOutput=dir(fullfile(fileFolder,'*.mat'));
    fileNames={dirOutput.name}';
    for k = 1:length(fileNames)
        enresult=[];%存放能量数据
        indexresult=[];%
        load([fileFolder,'/',cell2mat(fileNames(k))])
        names=[names {cell2mat(fileNames(k))}];
        data=data(:,1:end-3);
        for i=1:25 %5s一个窗口，1s滑动一次
            rawData=data((i-1)*20+1:(i-1)*20+100,:);
            pureData=pca_filter_x4(data((i-1)*20+1:(i-1)*20+100,:),rx_num,pg,M,L,K);
            pureData=rawData-mean(rawData);%mean()对矩阵每列求平均
            
            %%这里写处理代码
            % 最大列
            pureEn=sum(pureData.^2,1);
            [maxEn,index]=max(pureEn);
            if maxEn>4e-07
                count=count+1;
            end
            indexresult=[indexresult index];
        end
        %单次测量的均方误差
        rmseresult=abs(mean(indexresult/156+0.5)-t);        
        rmse=[rmse {rmseresult}];
    end
end
rmse=[names;rmse];
rmse=rmse';
s = xlswrite('rmse.xls', rmse);  
% result=sum(rmse)/length(rmse);
count



