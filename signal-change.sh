#!/bin/sh
cur_time=`date|awk {'print $4'}|awk -F: '{print $1}'`
cd /etc/config
cur_signal=`grep "txpower" wireless| awk 'NR==2'|awk '{print $3}'`
cur_signal=${cur_signal:1:2}
echo "-------------------" >> /mnt/sda1/signal.log
if [ $cur_time -ge '19' ] && [ $cur_time -lt '23' ]; then
    echo ${cur_signal} >> /mnt/sda1/signal.log
    if [ $cur_signal -eq '16' ]; then
        echo "Setting cur_signal to 19" >> /mnt/sda1/signal.log
        sed -i "s/option txpower \'16\'/option txpower \'19\'/g" wireless
        /etc/init.d/network restart
    else 
        echo  "Do nothing" >> /mnt/sda1/signal.log
    fi
else 
    if [ $cur_signal != '16' ]; then
        cd /etc/config 
        echo "Setting cur_signal to 16" >> /mnt/sda1/signal.log
        sed -i "s/option txpower \'19\'/option txpower \'16\'/g" wireless
        /etc/init.d/network restart
    fi
fi