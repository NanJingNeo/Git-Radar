clear;
clc;
close all;
i = 0;
M=10;L=50;K=50;%K=1,M=2
pg=1;rx_num=2;
scale=200;
T=round((6000-scale)/100+1);

radar=importdata('D:\lab\demo\tracking_with_vital_signs\dataprocessing\Data\dy_inroom_closemove.mat');
radar=radar(27:5980,1:747);
T=floor((size(radar,1)-scale)/100+1);
% PureData=pca_filter_x4(radar,rx_num,pg,M,L,K);
for i=1:T
    PureData=pca_filter_x4(radar((i-1)*100+1:(i-1)*100+210,:),rx_num,pg,M,L,K);
%     tmp=PureData((i-1)*100+1:(i-1)*100+200,:);
% ²âÊÔº¯Êý
    T=size(PureData,1);
    peaks=zeros(1,T);tops=zeros(1,T);
    for pp=1:size(PureData,1)
        [vv,tmp]=max(abs(PureData(pp,:)));
        peaks(pp)=tmp;  %% position
        tops(pp)=vv;  %% amplitude
    end
    [br_v,hr_v]=respiration_multi2_vncmd_2(tops,peaks);   %%% VNCMD
%     [br_v,hr_v]=respiration_multi2_vncmd(PureData);   %%% VNCMD
    hr_v
    hr(i)=hr_v;
end
%             figure
%             plot(br(j,:))
%             figure
%             plot(hr(j,:))
save('dyclose_matlab.mat','hr')