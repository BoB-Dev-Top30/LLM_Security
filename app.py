
import requests
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify, send_from_directory
# from flask.helpers import send_from_directory

from config.config import *
import time


#############
from buffer.buffer import *
#######


load_dotenv()

app = Flask(__name__, static_folder='static')
port = os.getenv('PORT', 5000)

openai_api_key = OPENAI_API_KEY
print(openai_api_key)


MAX_HISTORY_LENGTH=10

conversation_history = []
conversation_seq=0

@app.route('/api/chat', methods=['POST'])
def chat():
    global conversation_seq
    user_input = request.json['userInput']
    start = time.time() * 1000 # 요청 시간을 기록
    print(f' => 사용자 요청: {user_input}')

    # 이전 대화 내용 추가
    conversation_history.append({'role':'user','content':user_input})
    # conversation_history = buffer_manage(conversation_history)
    conversation_seq +=1

    chatgpt_response = get_chat_gpt_response(conversation_history)
    print(f' <= chatGPT 응답 :{chatgpt_response}')
    end = time.time() * 1000
    print(f'==요청응답시간:{end - start}ms')

    conversation_history.append({'role':'assistant', 'content': chatgpt_response})
    conversation_seq += 1

    while(len(conversation_history) > MAX_HISTORY_LENGTH):
        conversation_history.pop(0)


    print(conversation_history)
    # conversation_history = buffer_manage(conversation_history)
    return jsonify({'GPTResponse': chatgpt_response})

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

def get_chat_gpt_response(conversation_history):
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            json = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'system', 'content': 'You are a helpful assistent'},
                    #{'role': 'user', 'content': user_input},
                    *conversation_history
                ]
            },
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {openai_api_key}',
            }
        )

        return response.json()['choices'][0]['message']['content']
    except Exception as error:
        print('ChatGPT API 호출 중 오류 발생: ', str(error))
        return '오류 발생'

def chat_with_user():
    user_input = '안녕 챗봇!'
    gpt_response = get_chat_gpt_response(user_input)
    print('챗봇 응답: ', gpt_response)

if __name__ == '__main__':
    app.run(port=port, debug=True)
