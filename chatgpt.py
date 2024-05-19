import requests
import json
from loguru import logger
from config import chatgpt_config

chat_endpoint = chatgpt_config.chat_endpoint
draw_endpoint = chatgpt_config.draw_endpoint
token = chatgpt_config.token
chat_model = chatgpt_config.chat_model
draw_model = chatgpt_config.draw_model
max_tokens = chatgpt_config.max_tokens
timeout = chatgpt_config.timeout


def chat(message, history):
    messages = history
    messages.append({"role": "user", "content": message})
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    data = {
        "model": chat_model,
        "max_tokens": max_tokens,
        "messages": messages
    }
    status = -1  # -1: undefined, 0: ok, 1: response json error, 2: HTTP status error, 3: timeout
    try:
        logger.debug(data)
        response = requests.post(chat_endpoint, headers=headers, data=json.dumps(data), timeout=(30, int(timeout)))
        if response.status_code == 200:
            result = response.json()
            try:
                answer = result["choices"][0]["message"]["content"]
                history = messages
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


def chat_with_image(message, images, history):
    messages = history
    content = [{"type": "text", "text": message}]
    for image in images:
        content.append({"type": "image_url", "image_url": {"url": image}})
    messages.append({"role": "user", "content": content})
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    data = {
        "model": chat_model,
        "max_tokens": max_tokens,
        "messages": messages
    }
    status = -1  # -1: undefined, 0: ok, 1: response json error, 2: HTTP status error, 3: timeout
    try:
        response = requests.post(chat_endpoint, headers=headers, data=json.dumps(data), timeout=(30, int(timeout)))
        if response.status_code == 200:
            result = response.json()
            try:
                answer = result["choices"][0]["message"]["content"]
                history = messages
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
    logger.info(_answer)
