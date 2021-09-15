% 读取对应时间段内的血氧仪的心率值及时间戳
[date,time,value_nPR,device] ...
= textread('D:\lab\demo\tracking_with_vital_signs\dataprocessing\Data\zxy\2020-12-11 103837.688myfile.txt', '%s %s %f %s');

time=char(time);
time=str2num([time(:,1:2),time(:,4:5),time(:,7:8)]);

radar1 = load('D:\lab\demo\tracking_with_vital_signs\dataprocessing\Data\dy_farmove_zxy_closemove.mat');
radar1=radar1.data;

% radar1=radar1(1:24000,:);


T=radar1(:,end);  % 雷达时间戳

dur1= T(1);
durE = T(end-1);
start=0;
stop=0;
for j=1:length(time)
    if time(j)>=dur1
        start = j;
        break;
    end
end
for j=start:length(time)
    if time(j)>durE
        stop = j-1;
        break;
    end
end
bpm = value_nPR(start:stop);  % 血氧仪对应时间的心率
timestamp = time(start:stop);
lingzhi=find(bpm==0);
bpm(lingzhi)=[];
timestamp(lingzhi)=[];
for j=1:2000

    if timestamp(j+1) > timestamp(j)+1 
        if mod(timestamp(j)+1,100) == 60
           cache =  timestamp(j)+41;
        else
            cache = timestamp(j)+1;
        end
        timestamp = [ timestamp(  1 : j); cache; timestamp(  j+1 : end ,:)];
        bpm = [ bpm(  1 : j ); bpm(j); bpm(  j+1 : end )];
    end
    if timestamp(j+1) == timestamp(j)
        timestamp = [timestamp(  1 : j);timestamp(  j+2 : end ,:)];
        bpm = [ bpm(  1 : j ); bpm(  j+2 : end )];
    end
    if length(timestamp)<=j+1
        break;
    end
    
end
        