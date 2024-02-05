import openai
from config.config import OPENAI_API_KEY
from .Security_LLM_Prompt import security_prompt
openai_api_key = OPENAI_API_KEY

def Security_LLM(input):
    gpt_prompt = security_prompt(input)
    message = [{"role": "user", "content": gpt_prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=message,
        temperature=0,
        max_tokens=2000,
        frequency_penalty=0.0
    )

    secured_prompt = response['choices'][0]['message']['content']
    print("GPT출력값: ", secured_prompt,"\n")

    return secured_prompt