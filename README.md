# trivial-script

一个个人工具脚本集合，包含路由器（OpenWrt）、树莓派、ESP8266/ESP32、安卓(termux) 以及若干桌面/辅助脚本。脚本以实用为主，便于快速部署与二次修改。

## 目录（按设备/用途分组）
- OpenWrt / 路由器
  - wifi-reboot.sh — 检查系统日志中的断流/断开信息，满足条件时重启 WiFi（注意：实际效果视路由器与驱动而定）
  - signal-change.sh — 晚间自动增强 WiFi 信号（晚上/白天信号策略切换）
  - traffic_network.sh — 通过 crontab 定时记录 WAN 流量到本地存储

- 树莓派 (Raspberry Pi)
  - network-detetive.sh — 探测在线/离线并语音提示（整合了监控与提示）
  - monitor_temp — 检测树莓派 CPU 温度（已集成至 network-detetive.sh）
  - aralm.sh — 使用 edge-tts 或其它 TTS 实现整点或定时语音报时（配合 crontab 使用）
  - at_aralm_sugar.py — 提供一个 HTTP API，可通过手机设置 2 小时后播报提醒（示例服务端脚本）
  - raspi_ipv6_login.sh — 通过 IP 段批量登录树莓派 SSH 的脚本（配合参数使用）

- ESP8266 / ESP32 (MicroPython / Arduino)
  - main.py — ESP 的 MicroPython 灯光控制示例（OLED 初始化��按钮处理等）
  - main-hum.py — MicroPython 用于加湿器控制的示例
  - main-ch9329.py — MicroPython + CH9329（USB 键盘芯片）相关的示例（如键盘控制）
  - main-ch9329.py、main.py 等为 MicroPython 示例，可直接上传到设备
  - ir.ino — ESP8266/Arduino 的红外遥控实现（包含 raw / NEC 命令表与执行函数）
  - esp_bluetooth_keyboard.ino — ESP32 蓝牙键盘 / 媒体键扩展示例

- 安卓 / Termux
  - tty.py — 在手机上调用 edge-tts 并配合 termux-api 进行语音播报的示例
  - raspi_ipv6_login.sh（也可在 termux 中配合使用）

- LLM / AI 接口
  - llm-api.py — 简单的模型 API 调用（普通/非流式）
  - llm-api-stream.py — 流式调用示例（演示如何接收增量响应并打印）

- 桌面工具 / PDF
  - pdf_generator_qt.py — 基于 PyQt 的图片转 PDF GUI（支持拖拽排序、预览、进度显示）
  - create-pdf.py — 命令行/脚本方式将多张图片打包为 PDF

- 通用/其他
  - at_aralm_sugar.py — （见上）提供远程设置闹钟的 API 示例
  - 其它脚本、示例文件及资源（mp3、配置片段等）

## 使用说明与注意事项
- 权限：除 Python 脚本外，Shell / .sh 脚本需 `chmod +x` 并在支持的环境下运行（比如 OpenWrt shell、Linux、termux 等）。
- 路径：多个脚本将日志或文件写到 `/mnt/sda1`，请根据你的环境修改为实际挂载点或路径（例如路由器的 U 盘路径）。
- Crontab：若要定时运行脚本，请使用 crontab（路由器或树莓派）：
  - traffic_network.sh 示例（每 5 分钟）：
    */5 * * * * /path/to/traffic_network.sh
  - aralm.sh 示例（整点报时，小时触发）：
    0 * * * * /path/to/aralm.sh
- 树莓派语音依赖：aralm.sh / tty.py / network-detetive.sh 等可能依赖 edge-tts、mpg123/play 或本地 TTS 工具，运行前请安装相应依赖（如 pip 包或系统软件）。
- MicroPython：ESP 的 `.py` 文件为 MicroPython 示例，上传至设备前请根据板子引脚与外设调整 GPIO 编号与初始化代码。
- Arduino：`.ino` 文件适配 ESP8266/ESP32 的 Arduino 环境，编译前请在 Arduino IDE / PlatformIO 中选择对应板子与核心库。
- LLM 接口：llm-api-stream.py 显示了怎样进行流式调用。请替换为你自己的 API key / 模型名称与 SDK 初始化参数。

## 快速示例
- 运行 pdf GUI（需要 PyQt5/PyQt6、Pillow、reportlab 等）：
  python3 pdf_generator_qt.py
- 在树莓派上进行整点语音（示例，需安装 edge-tts 或其他 tts）：
  bash aralm.sh

## 项目结构（摘要）
- wifi-reboot.sh
- signal-change.sh
- traffic_network.sh
- network-detetive.sh
- monitor_temp
- aralm.sh
- at_aralm_sugar.py
- main.py
- main-hum.py
- main-ch9329.py
- ir.ino
- esp_bluetooth_keyboard.ino
- llm-api.py
- llm-api-stream.py
- pdf_generator_qt.py
- create-pdf.py
- raspi_ipv6_login.sh
- tty.py
- 其它资源文件（mp3、配置示例等）

## 贡献 & 许可证
- 本仓库多数脚本以实用为主，欢迎 issue/PR 指出问题或补充说明。
- 若无其他声明，建议以 MIT 许可证发布（pdf_generator_qt.py 中也提到 MIT）。