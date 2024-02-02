from flask import Flask, jsonify
import subprocess


app = Flask(__name__)

@app.route('/', methods=['GET'])
def handle_request():
    # 成功接收请求并返回消息
    response_message = "成功定时"
    # 使用at命令设置定时任务并添加2小时作为定时时间
    command = f'echo "play /home/user/alarm.mp3" | at now + 2 hours'
    subprocess.run(command, shell=True, check=True)
    return jsonify({"message": response_message})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6666)