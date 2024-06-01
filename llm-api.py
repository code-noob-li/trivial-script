from dashscope import Generation

def get_response(messages):
    response = Generation.call(model="qwen-long",
                               messages=messages,
                               # 将输出设置为"message"格式
                               result_format='message')
    return response

def write_history(text1,text2):
    with open('history.txt', 'a') as f:
        f.write('User:'+text1+'\n')
        f.write('AI:'+text2+'\n\n')


messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}]
n=1

# 您可以自定义设置对话轮数，当前为3
for i in range(10):
    print(f'第{n}轮对话\n')
    user_input = input("请输入：")
    messages.append({'role': 'user', 'content': user_input})
    assistant_output = get_response(messages).output.choices[0]['message']['content']
    messages.append({'role': 'assistant', 'content': assistant_output})
    #print(f'用户输入：{user_input}')
    print(f'模型输出：{assistant_output}')
    write_history(user_input,assistant_output)
    print('\n')
    n+=1