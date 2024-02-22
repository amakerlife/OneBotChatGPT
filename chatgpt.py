import requests
import json
import configparser

config = configparser.ConfigParser()
config.read("config.cfg")

endpoint = config.get("chatgpt", "endpoint")
token = config.get("chatgpt", "token")
model = config.get("chatgpt", "model")
timeout = config.get("chatgpt", "timeout")


def chat(message, history):
    history.append({"role": "user", "content": message})
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    data = {
        "model": model,
        "messages": history
    }
    status = -1  # -1: undefined, 0: ok, 1: response json error, 2: HTTP status error, 3: timeout
    try:
        response = requests.post(endpoint, headers=headers, data=json.dumps(data), timeout=(20, int(timeout)))
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


if __name__ == "__main__":
    _private_chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
    _answer, _private_chat_history, _status = chat("Hello", _private_chat_history)
    print(_answer)
