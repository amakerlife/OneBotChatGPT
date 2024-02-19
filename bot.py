from chatgpt import chat
from msg import send_private_message, send_group_message
from flask import Flask, request
import configparser

app = Flask(__name__)

private_chat_history = {}
group_chat_history = {}

config = configparser.ConfigParser()
config.read("config.cfg")

prefix = config.get("message", "prefix")
allowed_groups = config.get("message", "allowed_groups").split(", ")


@app.route("/", methods=["POST"])
def handle_request():
    global private_chat_history

    request_data = request.get_json()
    # print(request_data)

    if not request_data.get("message"):
        return '', 204

    self_id = request_data.get("self_id", "")
    sender_id = request_data.get("sender", {}).get("user_id", "")
    sender_nickname = request_data.get("sender", {}).get("nickname", "")
    message_type = request_data.get("message_type", "")
    message = request_data.get("message", [])[0].get("data", {}).get("text", "")

    if message_type == "private":
        sender_history = private_chat_history.get(sender_id, [])
        if ((not message.startswith(prefix)) and prefix != "") or message.startswith("[AI]"):
            print(f"Private: {sender_id}({sender_nickname}) -> Unknown User: {message} (PASSED)")
            return '', 204

        if sender_id != self_id:
            print(f"Private: {sender_id}({sender_nickname}) -> {self_id}: {message}")
        else:
            print(f"Private: {sender_id}({sender_nickname}) -> Unknown User: {message}")

        prefix_len = len(prefix)
        if prefix != "":
            prefix_len += 1
        message = message[prefix_len:]
        if message.startswith("cls"):
            private_chat_history[sender_id] = []
            print("Chat history cleared")
            send_private_message(sender_id, "[AI] Chat history cleared")
            return '', 204
        print(f"Processing message: {message}")
        answer, sender_history = chat(message, sender_history)
        private_chat_history[sender_id] = sender_history
        print(f"Answer from GPT: {answer}")
        send_private_message(sender_id, "[AI] " + answer)
        return '', 204

    elif message_type == "group":
        group_id = request_data.get("group_id", "")
        group_history = group_chat_history.get(group_id, [])
        if str(group_id) not in allowed_groups:
            print(f"Group: {sender_id}({sender_nickname}) -> {group_id}: {message} (PASSED)")
            return '', 204
        if ((not message.startswith(prefix)) and prefix != "") or message.startswith("[AI]"):
            print(f"Group: {sender_id}({sender_nickname}) -> {group_id}: {message} (PASSED)")
            return '', 204

        print(f"Group: {sender_id}({sender_nickname}) -> {group_id}: {message}")
        prefix_len = len(prefix)
        if prefix != "":
            prefix_len += 1
        message = message[prefix_len:]
        if message.startswith("cls"):
            group_chat_history[group_id] = []
            print("Chat history cleared")
            send_group_message(group_id, sender_id, "[AI] Chat history cleared")
            return '', 204
        print(f"Processing message: {message}")
        answer, group_history = chat(message, group_history)
        group_chat_history[group_id] = group_history
        print(f"Answer from GPT: {answer}")
        send_group_message(group_id, sender_id, "[AI] " + answer)
        return '', 204

    else:
        return '', 204


if __name__ == "__main__":
    # print(f"正在使用配置：\n消息触发前缀：{prefix}\n")
    app.run(host="127.0.0.1", port=5000)
