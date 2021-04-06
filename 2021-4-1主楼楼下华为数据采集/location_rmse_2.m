%%%%ÿ�����巵��һ�����ݣ�ÿ�����ݸ�����̽��������
clear;clc;close all;

M=10; %ǰ��ȥ��������
L=40; %ǰ��ȥ��������
K=1; %����ȥ��������
rx_num=2;
pg=1;

count=0;%��ȡ��ʱ��Ƭ�θ���
rmse=[];%�������
names=[];

for t=[0.5,1,2,3]%�����־���
% for t=[3.0]%�����־���   
    %��ȡ�Ծ����������ļ����ڵ�.mat�ļ��б�
    char_t=num2str(t);
    fileFolder=fullfile(['./Data/',char_t]);
    dirOutput=dir(fullfile(fileFolder,'*.mat'));
    fileNames={dirOutput.name}';
    
    %����Ԥ����ÿ��.mat�ļ���ѭ���������ļ�����
    for k = 1:length(fileNames)%fileNames��������cell
        enresult=[];%�����������
        indexresult=[];%
        load([fileFolder,'/',cell2mat(fileNames(k))])
        names=[names {cell2mat(fileNames(k))}];
        data=data(:,1:end-3);
        
        %������ȡ.mat�ļ�����Ϣ
        for i=1:25 %5sһ�����ڣ�1s����һ��
            rawData=data((i-1)*20+1:(i-1)*20+100,:);
            pureData=pca_filter_x4(data((i-1)*20+1:(i-1)*20+100,:),rx_num,pg,M,L,K);
%             pureData=rawData-mean(rawData);%mean()�Ծ���ÿ����ƽ��
            mesh(pureData)
            %%����д�������
            % �����
            pureEn=sum(pureData.^2,1);
            [maxEn,index]=max(pureEn);%�������ֵ����λ��
            if maxEn>4e-07
                count=count+1;
            end
            indexresult=[indexresult index];
        end
        %���β����ľ������rmse
%         rmseresult=sqrt(mean(indexresult/156+0.5)-t);
        rmseresult=sqrt((sum((indexresult/156+0.44-t).^2))/length(indexresult));
        rmse=[rmse {rmseresult}];
    end
end
rmse=['scenes',names;'rmse',rmse]';
s = xlswrite('rmse.xls', rmse);  
count



