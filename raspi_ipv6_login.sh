#!/bin/bash

# 检查是否提供了两个参数
if [ $# -ne 2 ]; then
  echo "Usage: $0 <middle_address_part1> <middle_address_part2>"
    exit 1
    fi

    # 定义固定的前缀和后缀
    PREFIX="fe80:"
    SUFFIX="::1"

    # 获取两个参数作为中间地址的部分
    MIDDLE_PART1="$1"
    MIDDLE_PART2="$2"

    # 构建完整的IPv6地址
    FULL_IPV6="${PREFIX}${MIDDLE_PART1}:${MIDDLE_PART2}${SUFFIX}"

    # SSH端口号
    SSH_PORT=5566

    # 打印出正在尝试连接的完整IPv6地址
    echo "Attempting to connect to $FULL_IPV6 on port $SSH_PORT..."

    # 使用ssh命令连接到指定的IPv6地址和端口
    ssh -6 -p $SSH_PORT ubuntu@$FULL_IPV6