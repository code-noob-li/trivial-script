import ntptime
import uasyncio as asyncio
import machine
import time
import network

from machine import I2C, Pin
from ssd1306 import SSD1306_I2C
i2c=I2C(scl=Pin(5), sda=Pin(4))
print('addresses: ',i2c.scan())

#get ip address
wlan = network.WLAN(network.STA_IF)
time.sleep(5)
if wlan.active() and wlan.isconnected():
    ip_address = wlan.ifconfig()[0]

# 创建OLED对象
oled=SSD1306_I2C(128, 64, i2c,addr=60)

def oled_show(*texts):
    oled.fill(0)
    init_y = 0
    for word in texts:
        oled.text(str(word), 0,init_y)
        init_y+=11
    oled.show()
#开机显示OLED
def init_oled():
    oled.fill(1)
    oled.show()
    time.sleep(0.5)
    
    oled.fill(0)
    oled.show()
    time.sleep(0.5)
    
    oled.rect(0, 0, 128, 64, 1)
    oled.show()
    time.sleep(0.5)

    oled.hline(0, 8, 128, 1)
    oled.show()
    time.sleep(0.5)
    
    oled.rect(32, 16, 64, 32, 1)
    oled.show()
    time.sleep(0.5)

    oled.vline(20, 8, 64, 1)
    oled.show()
    time.sleep(0.5)
    
    oled.text('--IOT DEVICE--', 1, 35)
    oled.invert(True)
    oled.show()
    time.sleep(1)
    oled.invert(False)
    oled.contrast(1)
    
    

# 设置LED引脚
led = machine.Pin(14, machine.Pin.OUT)


# 设置RTC
ntptime.host = "ntp7.aliyun.com"
ntptime.settime()

# 显示时间
def show_time():
    #cur_time=RTC().datetime()
    cur_time=time.localtime(time.time()+28800)
    beijing_time = f'{cur_time[0]}-{cur_time[1]:02d}-{cur_time[2]:02d} {cur_time[3]:02d}:{cur_time[4]:02d}'
    return beijing_time



async def handle_request(reader, writer):
    request_line = await reader.readline()
    client_addr = writer.get_extra_info('peername')

    while await reader.readline() != b"\r\n":
        pass
    # 解析请求路径
    path = request_line.decode().split()[1]

    if path == '/led':
        state = led.value()
        if state == 1:
            led.off()            
            response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nLED is Off '
            oled_show('LED is Off','relay status:','0','from ip:',client_addr[0],f'port:{client_addr[1]}')
        else:
            led.on()
            response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nLED is On '
            oled_show('LED is On','relay status:','1','from ip:',client_addr[0],f'port:{client_addr[1]}')
    elif path == '/reset':
        response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nRebooting.'
        oled_show('Rebooting...','please wait...',client_addr[0])

    else:
        response = f'HTTP/1.1 404 NOT FOUND\r\nContent-Type: text/html\r\n\r\nNot Found'


    writer.write(response)
    await writer.drain()
    await writer.wait_closed()
    print('Client Disconnected')


async def oled_show_loop():
    while True:
        beijing_time = show_time()
        oled_show('Listening on',ip_address,f'led status:{led.value()}',beijing_time,'   init done','      ^__^')
        print("oled_show_loop")
        await asyncio.sleep(50)
# 设置ESP8266作为服务器

async def main():
    # 获取IP地址并设置监听
    print('Setting up server')
    server = asyncio.start_server(handle_request, '0.0.0.0', 80)
    asyncio.create_task(server)
    asyncio.create_task(oled_show_loop())


#init oled
init_oled()
print('Listening on')






loop = asyncio.get_event_loop()
loop.create_task(main())


try:
    # Run the event loop indefinitely
    loop.run_forever()
except Exception as e:
    print('Error occured: ', e)
except KeyboardInterrupt:
    print('Program Interrupted by the user')

