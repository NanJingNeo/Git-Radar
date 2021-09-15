clear;
clc;
data=importdata('../dyclose_maxEnergyAndPosition.mat');
peaks=data.resultPeaks;
tops=data.resultTops;
for i=1:size(peaks,1)
    [br_v,hr_v]=respiration_multi2_vncmd_2(tops(i,:),peaks(i,:));   %%% VNCMD
    hr_v
    hr(i)=hr_v;
end
%             figure
%             plot(br(j,:))
%             figure
%             plot(hr(j,:))
save('dyclose_matlab.mat','hr')