功能:双人追踪+心率

主要文件说明：
twoclient_socktest1.py（双人追踪client1,运行在树莓派上）
twoclient_socktest2.py（双人追踪client2,运行在树莓派上）
twoclient_socktest3.py（双人追踪client3,运行在树莓派上）
twoclient_socktest4.py（双人追踪client4,运行在电脑上，出动目标心率的轨迹也从这里出）
twoserver_test2(final).py（双人追踪server，运行在树莓派上）
calHR_twoTarget.py（调matlab出心率，运行在电脑上）
pltVSandTracking.py（画图，连血氧仪，运行在电脑上）
树莓派上运行的文件以树莓派为准，本地只是备份，不要用本地的去覆盖树莓派！！！！
每次改完及时备份，搞不好哪次用完树莓派就坏了！！！

运行的时候需要检查：
1、运行前树莓派需要联网同步下时钟，确保时间和电脑时间一致（不一致心率不更新）
1、先开server再开其他的client，先开画图程序再用手机连血氧仪
2、每次demo七个文件都要运行，确保全部运行成功（应该都会有实时更新的数据打印，没有说明没成功）
3、检查ip设置对不对，运行时所有设备连同一个局域网，相应设备ip更新到ip.txt（所有设备的ip.txt都要更新），血氧仪app内输入pc的ip地址
4、确保三个树莓派位置正确，client1在左下角，client2在中间，client3在右下角，client4在左下角
5、确保com口设置正确，树莓派usb统一插左上那个，换usb端口需要改代码
6、血氧仪app使用oximeter1 和 oximeter2，并且两人轨迹不能交叉，不然心率会乱
(血氧仪接口数据带有的tag，这里不懂可以打印接口数据看下或看下血氧仪代码)
7、调matlab能不能成功
8、client123采样频率5，client4采样频率20
9、如果上面问题都没有的话且运行不起来，就debug（一定仔细检查前面的问题，可以解决95%的问题）

如果结果不准可能需要调的地方
1、重要！！！！！！调之前一定要备份！！！！这个demo很脆弱！！！！！！
2、调所有地方一定在理解代码/算法的基础上，把每个参数的含义搞清楚再调，不然很可能demo整个崩坏
3、调的时候一定控制变量，确保有效再改，不然会出现很离谱的问题
4、先把轨迹调准先把轨迹调准先把轨迹调准

轨迹不准（按照优先级排列）：
1、clean函数阈值
2、server文件处理距离较远or距离较近or边界的阈值（文件里有注释）
3、所有client文件KNN相关阈值（文件里有注释，主要辅助优化clean，基本调clean就能解决，最好不要动）
4、kalman相关参数（这个非必要不要动，如果慢速走轨迹有明显滞后或抖动可以稍微调下）
5、自己发挥

心率不准（按照优先级排列）：
1、重要！！！先输出client4得到的距离看能不能得到准确轨迹（轨迹在result.json），不准先按照上面的把轨迹调准
2、result.json看下有效数据够不够长（就是有值的列表，不够长是因为交叉点太多，按轨迹不准调）
3、调核心函数respiration_multi2_vncmd_2（调之前备份）：
bw（一个带宽，不是雷达的带宽），
Fs1（采样频率检查对不对），
其他自由发挥

更新速度慢可能的问题：
轨迹更新慢：
1、看下设备时钟有没有对齐
2、采样频率设置对不对（追踪5心率20）
3、kalman设置对不对
4、按照轨迹不准调
心率更新慢：
1、看下轨迹准不准
2、看下每次心率计算时间，如果太长加一个vncmd超时跳出（应该有的，具体哪里加请看代码）
3、按照心率不准调
血氧仪更新慢：大概率没连上

其他可能的问题：
读写文件可能有冲突，会有极低概率系统报错，这里需要优化下
其他报错就靠自己吧，加油








