%%%%ÿ�����巵��һ�����ݣ�ÿ�����ݸ�����̽��������
clear;clc;close all;

M=10; %ǰ��ȥ��������
L=40; %ǰ��ȥ��������
K=1; %����ȥ��������
rx_num=2;
pg=1;

count=0;%��ȡ��ʱ��Ƭ�θ���
% rmse=[];%�������
indexresult_sum=[];
names=[];

for t=[4]%��һ�־���
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
        pureData=pca_filter_x4(data,rx_num,pg,M,L,K);
        %������ȡ.mat�ļ�����Ϣ
        for i=1:190
            %%����д�������
            % �����
            dataw=pureData(i,:).^2;
%             pureEn=sum(pureData.^2,1);
            [maxEn,index]=max(dataw);%�������ֵ����λ��
            indexresult=[indexresult index];
        end
        indexresult_sum=[indexresult_sum;indexresult/156+0.44];
    end
end

indexresult_sum=num2cell(indexresult_sum);

ori=[names;indexresult_sum']';
s = xlswrite('walk.xls', ori);  
count



