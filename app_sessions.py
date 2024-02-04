
import requests
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify, send_from_directory
# from flask.helpers import send_from_directory

from config.config import *
import time
import openai
import sqlite3

import json


load_dotenv()

app = Flask(__name__, static_folder='static')
port = os.getenv('PORT', 5000)

# openai_api_key = OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

#DB설정(멀티쓰레드 용이 아님)
conn = sqlite3.connect('history.db', check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# DB테이블 생성
cursor.execute("CREATE TABLE IF NOT EXISTS conversation (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, role TEXT, content TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS session (id INTEGER PRIMARY KEY AUTOINCREMENT, start_time DATETIME DEFAULT CURRENT_TIMESTAMP)")
conn.commit()

MAX_HISTORY_LENGTH=10

#conversation_history = []
#conversation_seq=0

def get_recent_conversation():
    cursor.execute("SELECT * FROM conversation ORDER By id DESC LIMIT 10")
    rows = cursor.fetchall()
    formatted_rows = [{'role' : row['role'], 'content':row['content']} for row in rows]
    return formatted_rows[::-1]

@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.json['userInput']
    print(f' => 사용자 요청: {user_input}')

    # 이전 대화 내용 추가
    # conversation_history.append({'role':'user','content':user_input})
    cursor.execute("INSERT INTO conversation (role, content) VALUES (?, ?)", ('user', user_input))
    # conversation_history = buffer_manage(conversation_history)

    conversation_history = get_recent_conversation()
    print(f'=> 실제 프롬프트 요청:{conversation_history}')

    chatgpt_response = get_chat_gpt_response(conversation_history)
    print(f'<= 챗지피티 응답:{chatgpt_response}')

    cursor.execute("INSERT INTO conversation (role, content) VALUES (?, ?)", ('assistant', chatgpt_response))

    return jsonify({'GPTResponse': chatgpt_response})

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/history')
def get_history():
    conversation_history = get_recent_conversation()
    return json.dumps(conversation_history, ensure_ascii=False)

@app.route('/api/current-sesssion', methods=["GET"])
def current_session():
    current_session = get_current_session()
    conversation_history = get_recent_conversation_by_session(current_session['id'])
    return jsonify({'History': conversation_history, 'id':current_session['id'], 'start_rtime':current_session['start_time']})

def get_current_session():
    cursor.execute('SELECT id, start_time FROM session ORDER By start_time DESC LIMIT 1')
    current_session = cursor.fetchone()

    if not current_session:
        cursor.execute("INSERT INTO session DEFAULT VALUES")
        conn.commit()
        cursor.execute("SELECT id, start_time FROM session ORDER By start_time DESC LIMIT 1")
        current_session = cursor.fetchone()

    result = {'id':current_session['id'], 'start_time':current_session['start_time']}
    print(result)
    return result

def get_recent_conversation_by_session(session_id):
    cursor.execute("SELECT * FROM conversation WHERE session_id = ? ORDER BY id DESC", (session_id,))
    conversation_history = cursor.fetchall()

    result = {'role':conversation_history['role'], 'content':conversation_history['content']}
    print(result)
    return result
def get_chat_gpt_response(conversation_history):
    input_messages=[
        {'role': 'system', 'content': 'You are a helpful assistent'},
        *conversation_history
    ]
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = input_messages
    )
    return response['choices'][0]['message']['content']

def chat_with_user():
    user_input = '안녕 챗봇!'
    gpt_response = get_chat_gpt_response(user_input)
    print('챗봇 응답: ', gpt_response)

if __name__ == '__main__':
    app.run(port=port, debug=True)
