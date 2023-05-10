#!/bin/sh
dat=`date`
net_stat=`ifconfig|grep -A8 pppoe|grep "RX by"`
upti=`uptime`
echo "$dat" >> /mnt/sda1/pocket-statistics
echo "$upti" >> /mnt/sda1/pocket-statistics
echo "$net_stat" >> /mnt/sda1/pocket-statistics
