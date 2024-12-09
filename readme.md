#### openwrt路由器的管理脚本
- wifi-reboot.sh 有些路由器有断流的情况，这个脚本用来检测系统日志然后自动重启WIFI服务的，实际上好像作用不大
- signal-change.sh 晚上周围用WIFI的多有点卡，自动在晚上增强WIFI信号
- traffic_network.sh 通过crontab定时记录路由器WAN的流量
---
#### 下面是树莓派用的
- network-detetive.sh探测在线、离线，语音提示
- monitor_temp是检测树莓派的CPU温度,已经添加到network-detetive.sh去了
- aralm.sh 通过微软的tts整点报时，配合crontab使用
- at_aralm_sugar.py 建立一个api可以通过手机访问来设置2小时后定时播报提醒闹钟
---
- mp3文件可以用TTS文本转语音自己生成哦
- /mnt/sda1是我路由器u盘的路径，你需要自己改哦
---
#### 下面是ESP8266用的
- main.py esp8266的micropython固件代码
---
#### 语言模型调用API
- llm-api-stream.py 流式调用
- llm-api.py 普通调用
---
#### 下面是安卓手机用的，配合termux
- raspi_ipv6_login.sh 登录树莓派SSH，通过2个参数填入IP段
- tty.py 手机调用edge-tts配合termux-api进行语音播报



