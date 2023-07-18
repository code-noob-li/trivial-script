import asyncio
import edge_tts
import os
import time

cur_time=os.popen('''date|awk '{print $4}' ''').read()
cur_time=cur_time.replace('\n', '').split(':')
print(cur_time)
beijing_hour=int(cur_time[0])
cur_status=''
if beijing_hour>=6 and beijing_hour<12:
    cur_status='早上'
elif beijing_hour >=12 and beijing_hour<14 :
    cur_status='中午'
elif beijing_hour >=14 and beijing_hour<18:
    cur_status='下午'
else:
    cur_status='晚上'

is_online=os.popen(''' ifconfig |grep '192.168.1.109'|awk '{print $2}' ''').read()
is_online=is_online.replace('\n', '')
text='''  
现在时间,北京时间{}{}点{}分{}秒
'''.format(cur_status,cur_time[0],cur_time[1],cur_time[2])
print(text)
voice="zh-CN-XiaoxiaoNeural"
output='aralm.mp3'

async def _main() -> None:
    communicate=edge_tts.Communicate(text,voice)
    await communicate.save(output)
    os.popen('play /home/ubuntu/aralmtask/aralm1.mp3').read()
    await asyncio.sleep(3)
    cmd=os.popen('play aralm.mp3').read()
    #print(cmd)
if is_online=='192.168.1.109':
    #print('true')


    asyncio.run(_main())
else:
    #print('flase')
    os.popen('play /home/ubuntu/aralmtask/aralm1.mp3').read()
    #print('done')
