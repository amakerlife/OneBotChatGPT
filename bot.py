from chatgpt import chat
from msg import send_message
from flask import Flask, request

app = Flask(__name__)

chat_history = {}


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
        if not message.startswith("ask"):
            print(f"{sender_id}({sender_nickname}) -> {self_id} : {message} (PASSED)")
            return '', 204

        message = message[4:]
        print(f"{sender_id}({sender_nickname}) -> {self_id} : {message}")
        print(f"Processing message: {message}")
        answer, sender_history = chat(message, sender_history)
        chat_history[sender_id] = sender_history
        print(f"Answer from chat: {answer}")
        send_message(sender_id, "[AI] " + answer)
        return '', 204

    else:
        return '', 204


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
