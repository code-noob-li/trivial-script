#!/bin/bash

# 获取CPU温度
temp=$(cat /sys/class/thermal/thermal_zone0/temp)

# 转换为摄氏度
celsius=$(($temp / 1000))

# 判断是否超过阈值
if [ $celsius -ge 65 ] && [ $celsius -lt 75 ]; then
  play ./hightemp.mp3

elif [ $celsius -ge 75 ]; then  
  play ./limittemp.mp3

fi
