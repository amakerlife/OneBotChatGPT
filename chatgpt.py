import requests
import json
import configparser

config = configparser.ConfigParser()
config.read("config.cfg")

endpoint = config.get("chatgpt", "endpoint")
token = config.get("chatgpt", "token")
model = config.get("chatgpt", "model")


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
    response = requests.post(endpoint, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        history.append({"role": "assistant", "content": answer})
    else:
        answer = "Error: " + response.text
    return answer, history


if __name__ == "__main__":
    private_chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
    answer, private_chat_history = chat("Hello", private_chat_history)
    print(answer)
