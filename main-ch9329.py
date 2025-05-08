from machine import Pin, UART
import uos
import time

# 🔧 Step 1: 断开 UART0 与 REPL 的绑定（允许收发数据）
uos.dupterm(None, 1)

# 🔧 Step 2: 初始化 UART0，波特率设为 9600（匹配 CH9329 默认设置）
uart = UART(0, baudrate=9600)

btn_a = Pin(4, Pin.IN, Pin.PULL_UP)  # D2 -> GPIO4
btn_b = Pin(5, Pin.IN, Pin.PULL_UP)  # D1 -> GPIO5
btn_shift = Pin(14, Pin.IN, Pin.PULL_UP)  # 新增按钮 3（D0）

# 🔧 Step 4: 设置 LED 引脚（假设使用 D0 作为 LED 输出）
led = Pin(2, Pin.OUT)  # D4 -> GPIO2（默认高电平熄灭）

# 🔄 辅助函数：LED 闪烁 N 次（周期 0.2s）
def blink_led(times):
    for _ in range(times):
        led.value(0)  # 点亮（低电平有效）
        time.sleep(0.3)
        led.value(1)  # 熄灭
        time.sleep(0.3)

blink_led(5)  # 初始提示
# 📤 发送 ASCII 字符函数（带 LED 反馈）
def send_ascii(text):
    uart.write(text)
    blink_led(2)  # 每次发送后快速闪烁 2 次

# 🔄 主循环：检测按键并发送相应文本
while True:

    # 🟢 单独按键事件（无 Shift）
    if btn_a.value() == 0 and btn_shift.value() == 1:  # Btn1 被按下，Shift 未按
        send_ascii("HELLO\r\n")
        print("Sent: HELLO")
        time.sleep(0.5)  # 防抖

    if btn_b.value() == 0 and btn_shift.value() == 1:  # Btn2 被按下，Shift 未按
        send_ascii("WORLD\r\n" \
        "456" \
        "46555")
        print('''123
              hjk ioio
              123''')
        time.sleep(0.5)

    # 🔴 组合按键事件（Shift + 其他键）
    if btn_shift.value() == 0:  # Shift 被按下
        if btn_a.value() == 0:  # Shift + Btn1
            send_ascii("APPLE\r\n")
            time.sleep(0.5)
        elif btn_b.value() == 0:  # Shift + Btn2
            send_ascii("BANANA\r\n")
            time.sleep(0.5)