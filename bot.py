from chatgpt import chat
from msg import send_message
from flask import Flask, request
import configparser

app = Flask(__name__)

chat_history = {}

config = configparser.ConfigParser()
config.read("config.cfg")

prefix = config.get("message", "prefix")


@app.route('/', methods=['POST'])
def handle_request():
    global chat_history

    request_data = request.get_json()
    # print(request_data)

    if not request_data.get('message'):
        return '', 204

    self_id = request_data.get('self_id', '')
    sender_id = request_data.get('sender', {}).get('user_id', None)
    sender_nickname = request_data.get('sender', {}).get('nickname', None)
    message_type = request_data.get('message_type', '')
    message = request_data.get('message', [])[0].get('data', {}).get('text', '')
    sender_history = chat_history.get(sender_id, [])

    if message_type != 'group':
        if message.startswith("cls"):
            chat_history[sender_id] = []
            print("Chat history cleared")
            send_message(sender_id, "[AI] Chat history cleared")
            return '', 204
        if ((not message.startswith(prefix)) and prefix != "") or message.startswith("[AI]") or sender_id != self_id:
            print(f"{sender_id}({sender_nickname}) -> Unknown User: {message} (PASSED)")
            return '', 204

        prefix_len = len(prefix)
        if prefix != "":
            prefix_len += 1
        message = message[prefix_len:]
        if sender_id != self_id:
            print(f"{sender_id}({sender_nickname}) -> {self_id}: {message}")
        else:
            print(f"{sender_id}({sender_nickname}) -> Unknown User: {message}")
        print(f"Processing message: {message}")
        answer, sender_history = chat(message, sender_history)
        chat_history[sender_id] = sender_history
        print(f"Answer from chat: {answer}")
        send_message(sender_id, "[AI] " + answer)
        return '', 204

    else:
        return '', 204


if __name__ == "__main__":
    print(f"正在使用配置：\n消息触发前缀：{prefix}\n")
    app.run(host='127.0.0.1', port=5000)
