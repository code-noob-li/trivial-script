#!/bin/sh

str1=`logread | tail -n 25 |grep "AP-STA-DISCONNECTED"`

flagstr="AP-STA-DISCONNECTED"
flagstr1="deauthenticated due to inactivity"

echo $str1
#echo flagstr


n=0

for i in $str1
do
    #echo $i
    if [[ "$i" == "$flagstr" || "$i" == "$flagstr1" ]] 
    then
        n=`expr  $n + 1`
    fi
done
if [[ $n -gt 2 ]]
then
    time=`date`
    echo $time >> /mnt/sda1/wifi.log
    echo $n >> /mnt/sda1/wifi.log
    echo "reboot"
    wifi_reboot=`wifi down && wifi up`
    echo $wifi_reboot
else
    echo $n
    echo "canel"
fi

