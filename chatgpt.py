import requests
import json
import configparser
from loguru import logger

config = configparser.ConfigParser()
config.read("config.cfg")

chat_endpoint = config.get("chatgpt", "chat_endpoint")
draw_endpoint = config.get("chatgpt", "draw_endpoint")
token = config.get("chatgpt", "token")
chat_model = config.get("chatgpt", "chat_model")
draw_model = config.get("chatgpt", "draw_model")
timeout = config.get("chatgpt", "timeout")


def chat(message, history):
    history.append({"role": "user", "content": message})
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    data = {
        "model": chat_model,
        "messages": history
    }
    status = -1  # -1: undefined, 0: ok, 1: response json error, 2: HTTP status error, 3: timeout
    try:
        response = requests.post(chat_endpoint, headers=headers, data=json.dumps(data), timeout=(30, int(timeout)))
        if response.status_code == 200:
            result = response.json()
            try:
                answer = result["choices"][0]["message"]["content"]
                history.append({"role": "assistant", "content": answer})
                status = 0
            except KeyError:
                answer = f"Error: {response.text}"
                status = 1
        else:
            answer = f"Error: {response.text}"
            status = 2
    except requests.exceptions.Timeout:
        answer = "Error: Timeout"
        status = 3
    return answer, history, status


def draw(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    data = {
        "model": draw_model,
        "prompt": prompt
    }
    status = -1  # -1: undefined, 0: ok, 1: response json error, 2: HTTP status error, 3: timeout
    try:
        response = requests.post(draw_endpoint, headers=headers, data=json.dumps(data), timeout=(20, int(timeout)))
        if response.status_code == 200:
            result = response.json()
            try:
                answer = result["data"][0]["url"]
                status = 0
            except KeyError:
                answer = f"Error: {response.text}"
                status = 1
        else:
            answer = f"Error: {response.text}"
            status = 2
    except requests.exceptions.Timeout:
        answer = "Error: Timeout"
        status = 3
    return answer, status


if __name__ == "__main__":
    _private_chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
    _answer, _private_chat_history, _status = chat("Hello", _private_chat_history)
    print(_answer)
