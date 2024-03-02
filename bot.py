from chatgpt import chat, draw
from msg import send_private_message, send_group_message, send_private_img, send_group_img
from flask import Flask, request
from loguru import logger
from config import message_config

app = Flask(__name__)

private_chat_history = {}
group_chat_history = {}

chat_prefix = message_config.chat_prefix
draw_prefix = message_config.draw_prefix
allowed_groups = message_config.allowed_groups


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

    if message.startswith("[AI]"):
        logger.info(f"Private: {sender_id}({sender_nickname}) -> Unknown User: {message} (IGNORED)")

    elif message_type == "private":  # 私聊消息
        if message.startswith("cls"):
            logger.info(f"Private: {sender_id}({sender_nickname}) -> Unknown User: {message}")
            private_chat_history[sender_id] = []
            logger.success("Chat history cleared")
            send_private_message(sender_id, "[AI] Chat history cleared")

        elif message.startswith(chat_prefix):  # 私聊 Text to Text
            logger.info(f"Private: {sender_id}({sender_nickname}) -> {self_id}: {message} (Text to Text)")
            sender_history = private_chat_history.get(sender_id, [])
            chat_prefix_len = len(chat_prefix)
            if chat_prefix != "":
                chat_prefix_len += 1
            message = message[chat_prefix_len:]
            logger.info(f"Processing chat prompt: {message}")
            answer, sender_history, status = chat(message, sender_history)
            if status != 0:
                logger.error(answer)
                send_private_message(sender_id, f"[AI] An error occurred(Code {status}): {answer}")
                return '', 204
            private_chat_history[sender_id] = sender_history
            logger.info(f"Response from GPT: {answer}")
            send_private_message(sender_id, f"[AI] {answer}")

        elif message.startswith(draw_prefix):  # 私聊 Text to Image
            logger.info(f"Private: {sender_id}({sender_nickname}) -> {self_id}: {message} (Text to Image)")
            if draw_prefix == "":
                logger.warning("Draw prefix not set, ignored")
                send_private_message(sender_id, "[AI] The feature is not enabled")
                return '', 204
            draw_prefix_len = len(draw_prefix) + 1
            message = message[draw_prefix_len:]
            logger.info(f"Processing draw prompt: {message}")
            url, status = draw(message)
            if status != 0:
                logger.error(url)
                send_private_message(sender_id, f"[AI] An error occurred(Code {status}): {url}")
                return '', 204
            logger.info(f"Response from GPT: {url}")
            send_private_img(sender_id, url)

        else:
            logger.info(f"Private: {sender_id}({sender_nickname}) -> {self_id}: {message} (IGNORED)")

        return '', 204

    elif message_type == "group":  # 群聊消息
        group_id = request_data.get("group_id", "")
        group_history = group_chat_history.get(group_id, [])
        if str(group_id) not in allowed_groups:
            logger.info(f"Group: {sender_id}({sender_nickname}) -> {group_id}: {message} (IGNORED)")

        elif message.startswith("cls"):
            logger.info(f"Group: {sender_id}({sender_nickname}) -> {group_id}: {message}")
            group_chat_history[group_id] = []
            logger.success("Chat history cleared")
            send_group_message(group_id, sender_id, "[AI] Chat history cleared")

        elif message.startswith(chat_prefix):  # 群聊 Text to Text
            logger.info(f"Group: {sender_id}({sender_nickname}) -> {group_id}: {message} (Text to Text)")
            chat_prefix_len = len(chat_prefix)
            if chat_prefix != "":
                chat_prefix_len += 1
            message = message[chat_prefix_len:]
            logger.info(f"Processing chat prompt: {message}")
            answer, group_history, status = chat(message, group_history)
            if status != 0:
                logger.error(answer)
                send_group_message(group_id, sender_id, f"[AI] An error occurred(Code {status}): {answer}")
                return '', 204
            group_chat_history[group_id] = group_history
            logger.info(f"Response from GPT: {answer}")
            send_group_message(group_id, sender_id, f"[AI] {answer}")

        elif message.startswith(draw_prefix):  # 群聊 Text to Image
            logger.info(f"Group: {sender_id}({sender_nickname}) -> {group_id}: {message} (Text to Image)")
            if draw_prefix == "":
                logger.warning("Draw prefix not set, ignored")
                send_group_message(group_id, sender_id, "[AI] The feature is not enabled")
                return '', 204
            draw_prefix_len = len(draw_prefix) + 1
            message = message[draw_prefix_len:]
            logger.info(f"Processing draw prompt: {message}")
            url, status = draw(message)
            if status != 0:
                logger.error(url)
                send_group_message(group_id, sender_id, f"[AI] An error occurred(Code {status}): {url}")
                return '', 204
            logger.info(f"Response from GPT: {url}")
            send_group_img(group_id, sender_id, url)

        else:
            logger.info(f"Group: {sender_id}({sender_nickname}) -> {group_id}: {message} (IGNORED)")
    return '', 204


if __name__ == "__main__":
    # logger.info(f"正在使用配置：\n消息触发前缀：{prefix}\n")
    app.run(host="127.0.0.1", port=5000)
