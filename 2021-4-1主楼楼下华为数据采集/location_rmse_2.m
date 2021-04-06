%%%%每次脉冲返回一行数据，每行数据个数与探测距离相关
clear;clc;close all;

M=10; %前面去掉的行数
L=40; %前面去掉的列数
K=1; %后面去掉的列数
rx_num=2;
pg=1;

count=0;%读取的时间片段个数
rmse=[];%均方误差
names=[];

for t=[0.5,1,2,3]%共三种距离
% for t=[3.0]%共三种距离   
    %提取以距离命名的文件夹内的.mat文件列表
    char_t=num2str(t);
    fileFolder=fullfile(['./Data/',char_t]);
    dirOutput=dir(fullfile(fileFolder,'*.mat'));
    fileNames={dirOutput.name}';
    
    %挨个预处理每个.mat文件，循环次数是文件个数
    for k = 1:length(fileNames)%fileNames的类型是cell
        enresult=[];%存放能量数据
        indexresult=[];%
        load([fileFolder,'/',cell2mat(fileNames(k))])
        names=[names {cell2mat(fileNames(k))}];
        data=data(:,1:end-3);
        
        %滑动提取.mat文件的信息
        for i=1:25 %5s一个窗口，1s滑动一次
            rawData=data((i-1)*20+1:(i-1)*20+100,:);
            pureData=pca_filter_x4(data((i-1)*20+1:(i-1)*20+100,:),rx_num,pg,M,L,K);
%             pureData=rawData-mean(rawData);%mean()对矩阵每列求平均
            mesh(pureData)
            %%这里写处理代码
            % 最大列
            pureEn=sum(pureData.^2,1);
            [maxEn,index]=max(pureEn);%返回最大值及其位置
            if maxEn>4e-07
                count=count+1;
            end
            indexresult=[indexresult index];
        end
        %单次测量的均方误差rmse
%         rmseresult=sqrt(mean(indexresult/156+0.5)-t);
        rmseresult=sqrt((sum((indexresult/156+0.44-t).^2))/length(indexresult));
        rmse=[rmse {rmseresult}];
    end
end
rmse=['scenes',names;'rmse',rmse]';
s = xlswrite('rmse.xls', rmse);  
count



