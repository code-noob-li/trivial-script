#!/bin/bash
current_ip=`ifconfig |grep 109|awk '{print $2}'`
old_ip=$(cat ip.txt) 
temp=$(cat /sys/class/thermal/thermal_zone0/temp)

# 转换为摄氏度
celsius=$(($temp / 1000))

# 判断是否超过阈值
if [ $celsius -ge 65 ] && [ $celsius -lt 75 ]; then
  play /home/ubuntu/aralmtask/hightemp.mp3

elif [ $celsius -ge 75 ]; then
  play /home/ubuntu/aralmtask/limittemp.mp3

fi

sleep 3


echo $current_ip
echo $old_ip

if [ "$current_ip" = "$old_ip" ]; then
  exit
fi

if [ "$current_ip" != "192.168.1.109" ]; then
  play /home/ubuntu/aralmtask/link_down.mp3
  echo $current_ip > ip.txt
else
  play /home/ubuntu/aralmtask/link_up.mp3
  echo $current_ip > ip.txt  
fi
