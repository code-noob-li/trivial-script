from dashscope import Generation
from dashscope.api_entities.dashscope_response import Role

messages=[]
n=0
while True:
    print(f'{n}轮对话')
    message=input("请输入您的问题：")
    messages.append({'role':Role.USER,'content':message})
    whole_message=''
    responses=Generation.call(model='qwen-max',
                             messages=messages,
                             stream=True,
                             result_format='message',
                             incremental=True)
    print('system',end='')
    for response in responses:
        whole_message += response.output.choices[0]['message']['content']
        print(response.output.choices[0]['message']['content'],end='')
    print()
    messages.append({'role':'assistant','content':whole_message})
    n+=1
