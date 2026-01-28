#!/bin/bash

# 加载 zram 模块
modprobe zram

# 动态添加一个 zram 设备 (返回设备ID，通常是0)
# 这里我们直接操作，不依赖 hot_add 的返回值解析
echo 1 > /sys/class/zram-control/hot_add 2>/dev/null || true

# 设置 zram0 的参数 (假设新设备是 zram0)
# 1. 设置压缩算法为 lz4
echo lz4 > /sys/block/zram0/comp_algorithm

# 2. 设置大小为 512MB (536870912 字节)
echo 536870912 > /sys/block/zram0/disksize

# 3. 格式化为 swap 并启用
mkswap /dev/zram0
swapon /dev/zram0

# 4. 设置 swappiness
sysctl vm.swappiness=90
