第一次去青岛演示室内运动目标心率及状态（走站）
但是很慢（还没解决）-19.12.2

two_heartrate_on为主函数

Alheartbeat是实时的心率的代码（可在电脑上，也可在树莓派上）

testtime是用来检测two_heartrate_on在调用matlab时的各部分时延情况

demo_matlab_oxi.py是电脑端用来连接血氧仪

其余的py程序是双人室内运动目标心率（two_heartrate_on）的调用函数

20201207
试图将追踪频率提高到20，并用电脑替换掉一个追踪节点，用MMT-HEAR优化轨迹，同步处理心率
问题：电脑在进行位置计算时，计算速度不能满足20HZ的要求
todo：
分批计算位置