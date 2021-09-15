% 改文件名
% 改起始分割位置
%手动保存hrlabel

% timestamp=char(timestamp);
% timestamp=str2num([timestamp(:,1:2),timestamp(:,4:5),timestamp(:,7:8)]);
% hrtrain = [];
% hrtest = [];
% radar = radar1.radar1(11:end,:);
if ~exist('i','var')
    i=1;
end
if i == 1
    hrlabel = [];
end
Rstart =51;  % 起始点 根据具体数据设置
Rstop = Rstart;
RT = radar1(:,end);  % 时间戳
Len = length(RT);
fps = 20;

% PureData = newfilter(  radar1.radar1  );

while Rstop+fps*10-1<Len
    % 切分
    Rstop = Rstart+fps*10-1;  % 10s一段
    slice = radar1(Rstart:Rstop,:);
    
%     PureData = newfilter(  slice  );
%     PureData = PureData(:,1:50);
    
    
    for Tflag = Rstart+5*fps-10:Rstart+5*fps+9  % 找下一段的起始点
        if RT(Tflag+1)>RT(Tflag)
            Rstart = Tflag+1;
            break;
        end
    end
%     save(['D:\lab\AIgame\AIgame2020\20201201_zxy_zuowei\slices\C1' num2str(i,'%03d') '.mat'], 'slice')
%     disp(['D:\lab\AIgame\AIgame2020\20201201_zxy_zuowei\slices\C1' num2str(i,'%03d') '.mat'])
    i = i+1;
    
    % 求血氧仪记录的平均心率
    T=slice(:,end);
    dur1= T(1);
    durE = T(end-1);
    start=0;
    stop=0;
    for j=1:length(timestamp)
        if timestamp(j)>=dur1
            start = j;
            break;
        end
    end
    for j=start:length(timestamp)
        if timestamp(j)>durE
            stop = j;
            break;
        end
    end
    
%     if isnan(mean(bpm(start:stop)))
%         continue;
%     end
%     for k= start:stop
%         if bpm(k)==0
%             bpm(k)=[];
%         end
%     end
        
    hrlabel = [hrlabel, mean(bpm(start:stop))];
    mean(bpm(start:stop));
end


% while Rstop+200-1<12200
%    Rstop = Rstart+200-1;
%    slice = radar1.radar1(Rstart:Rstop,:); 
%    save(['./test2/TEST' num2str(i,'%03d') '.mat'], 'slice')
%    disp(['./test2/TEST' num2str(i,'%03d') '.mat'])
%    i = i+1;
%    for Tflag = Rstart+5*20-10:Rstart+5*20+9
%        if RT(Tflag+1)>RT(Tflag)
%            Rstart = Tflag+1;
%            break;
%        end
%    end
%     T=slice(:,end);
%     dur1= T(1);
%     durE = T(end-1);
%     start=0;
%     stop=0;
%     for j=1:length(timestamp)
%         if timestamp(j)>=dur1
%             start = j;
%             break;
%         end
%     end
%     for j=start:length(timestamp)
%         if timestamp(j)>durE
%             stop = j-1;
%             break;
%         end
%     end
%     hrtest= [hrtest, mean(bpm(start:stop))];
% end