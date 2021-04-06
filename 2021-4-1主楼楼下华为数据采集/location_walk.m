%%%%每次脉冲返回一行数据，每行数据个数与探测距离相关
clear;clc;close all;

M=10; %前面去掉的行数
L=40; %前面去掉的列数
K=1; %后面去掉的列数
rx_num=2;
pg=1;

count=0;%读取的时间片段个数
% rmse=[];%均方误差
indexresult_sum=[];
names=[];

for t=[4]%共一种距离
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
        pureData=pca_filter_x4(data,rx_num,pg,M,L,K);
        %滑动提取.mat文件的信息
        for i=1:190
            %%这里写处理代码
            % 最大列
            dataw=pureData(i,:).^2;
%             pureEn=sum(pureData.^2,1);
            [maxEn,index]=max(dataw);%返回最大值及其位置
            indexresult=[indexresult index];
        end
        indexresult_sum=[indexresult_sum;indexresult/156+0.44];
    end
end

indexresult_sum=num2cell(indexresult_sum);

ori=[names;indexresult_sum']';
s = xlswrite('walk.xls', ori);  
count



