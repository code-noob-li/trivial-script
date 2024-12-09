import subprocess



text="这是一个测试，程序正在运行123"
print(text)
voice="zh-CN-XiaoxiaoNeural"
output='aralm.mp3'



import subprocess
result0=subprocess.run(['termux-volume','music','15'],capture_output=True,text=True)
result1=subprocess.run(['edge-tts', '--voice',voice,'--text',text,'--write-media',output],capture_out>


if result1.returncode == 0:
    print('out',result1.stdout)
    else:
        print('error',result1.stderr)
        
        result2=subprocess.run(['mpv',output],capture_output=True,text=True)
        result3=subprocess.run(['termux-volume','music','4'],capture_output=True,text=True))