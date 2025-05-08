import ntptime
import uasyncio as asyncio
import urequests 
import machine
import time
import network





#get ip address
wlan = network.WLAN(network.STA_IF)
time.sleep(5)
if wlan.active() and wlan.isconnected():
    ip_address = wlan.ifconfig()[0]


    
    

# 设置引脚
device_toggle = machine.Pin(13, machine.Pin.OUT)
device_state=0

# 点击一次
def click_once():
    device_toggle.value(1)
    time.sleep(0.5)
    device_toggle.value(0)
def click_twice():
    device_toggle.value(1)
    time.sleep(0.5)
    device_toggle.value(0)
    time.sleep(0.5)
    device_toggle.value(1)
    time.sleep(0.5)
    device_toggle.value(0)

#长摁5秒
def long_press():
    device_toggle.value(1)
    time.sleep(4)
    device_toggle.value(0)
# 定时功能函数
async def timed_device_state_change():
    global device_state
        # 等待1分钟
    if device_state == 0:
        click_once()
    elif device_state == 2:
        click_twice()
    device_state = 1

    await asyncio.sleep(3600)  # 再等待1分钟
    click_twice()
    device_state = 0
    print(device_state)
    try:
        resp = urequests.get(f'http://192.168.1.109:8083/device_timed_close')
        resp.close()
    except Exception as e:
        print(f'Failed to send GET request: {e}')


# 设置RTC
ntptime.host = "ntp7.aliyun.com"
ntptime.settime()




# 处理客户端请求

async def handle_request(reader, writer):
    global device_state
    request_line = await reader.readline()
    #client_addr = writer.get_extra_info('peername')

    while await reader.readline() != b"\r\n":
        pass
    # 解析请求路径
    path = request_line.decode().split()[1]

    if path == '/open_normal':    
        if device_state == 0:
            click_once()
        elif device_state == 2:
            click_twice()
        else:
            pass
        device_state=1
        response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nDevice is running '
        
        #这里需要添加一个GET请求主动访问192.168.1.109:80/led
        try:
            resp = urequests.get(f'http://192.168.1.109:8083/device_on')
            #print(f'Response from 192.168.1.109: {resp.status_code}')
            resp.close()
        except Exception as e:
            print(f'Failed to send GET request: {e}')

    elif path == '/open_interval':
        if device_state == 0:
            click_twice()
        elif device_state == 1:
            click_once()
        else:
            pass
        device_state=2
        response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nDevice is running interval '
        try:
            resp = urequests.get(f'http://192.168.1.109:8083/device_on2')
            resp.close()
        except Exception as e:
            print(f'Failed to send GET request: {e}')
    elif path == '/close' :
        if device_state == 0:
            pass
        elif device_state == 1:
            click_twice()
        elif device_state == 2:
            click_once()
        device_state=0
        response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nDevice is Off '
        try:
            resp = urequests.get(f'http://192.168.1.109:8083/device_off')
            resp.close()
        except Exception as e:
            print(f'Failed to send GET request: {e}')
    elif path == '/led_press' :
        long_press()
        response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nDevice led '
        try:
            resp= urequests.get(f'http://192.168.1.109:8083/device_led')
            resp.close()
        except Exception as e:
            print(f'Failed to send GET request: {e}')
    elif path == '/timed' :
        asyncio.create_task(timed_device_state_change())
        response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nDevice timed '
        try:
            resp = urequests.get(f'http://192.168.1.109:8083/device_timed')
            resp.close()
        except Exception as e:
            print(f'Failed to send GET request: {e}')

    else:
        response = f'HTTP/1.1 404 NOT FOUND\r\nContent-Type: text/html\r\n\r\nNot Found'


    writer.write(response)
    await writer.drain()
    await writer.wait_closed()
    print('Client Disconnected')



async def check_wifi_status():
    while True:
        global wlan
        if not wlan.active() or not wlan.isconnected():

            print("WiFi connection lost. Reconnecting...")
            wlan.connect()
            await asyncio.sleep(60)
        else:
            print("WiFi connection established.")
            await asyncio.sleep(300)

async def check_ntp_sync():
    while True:
        global wlan
        if wlan.isconnected():
            try:
                ntptime.settime()
                print("NTP time synchronization successful.")
                await asyncio.sleep(3600)
            except Exception as e:
                print("NTP time synchronization failed:", e)
                await asyncio.sleep(600)
        else:
            await asyncio.sleep(600)
            print('network disconnected,ntp sync skipped')
# 设置ESP8266作为服务器

async def main():
    # 获取IP地址并设置监听
    print('Setting up server')
    server = asyncio.start_server(handle_request, '0.0.0.0', 80)
    asyncio.create_task(server)
    asyncio.create_task(check_wifi_status())
    asyncio.create_task(check_ntp_sync())



#init oled

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

