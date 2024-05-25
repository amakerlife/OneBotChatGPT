from chatgpt import chat, chat_with_image, draw
from msg import send_private_message, send_group_message, send_private_img, send_group_img, get_image
from flask import Flask, request
from loguru import logger
from config import message_config
import base64

app = Flask(__name__)

private_chat_history = {}
group_chat_history = {}

chat_prefix = message_config.chat_prefix
draw_prefix = message_config.draw_prefix
allowed_groups = message_config.allowed_groups


def image_to_base64(image_url):
    image = get_image(image_url)
    with open(image, "rb") as f:
        return f"data:image/;base64,{base64.b64encode(f.read()).decode()}"


@app.route("/", methods=["POST"])
def handle_request():
    request_data = request.get_json()

    if not request_data.get("message"):
        return '', 204

    process_message(request_data)
    return '', 204


def process_message(request_data):
    origin_messages_list = request_data.get("message", [])
    message_list = []
    for message in origin_messages_list:
        if message.get("type") == "text":
            message_list.append(("text", message.get("data", {}).get("text", "")))
        elif message.get("type") == "image":
            message_list.append(("image", message.get("data", {}).get("file", "")))
    if len(message_list) == 1 and message_list[0][0] == "text":  # 只有一个文本消息
        text_message(message_list[0][1], request_data)
        return
    flag = False
    for message in message_list:
        if message[0] != "text" and message[0] != "image":
            flag = True
            break
    if not flag:
        image_list = [message[1] for message in message_list if message[0] == "image"]
        text = "".join([message[1] for message in message_list if message[0] == "text"])
        mixed_message(text, image_list, request_data)
        return
    else:
        logger.warning(f"Unsupported message type: {str(message_list)}")
        send_private_message(request_data.get("sender", {}).get("user_id", ""), "[AI] Unsupported message type")
        return


def text_message(message, request_data):
    global private_chat_history, group_chat_history

    self_id = request_data.get("self_id", "")
    sender_id = request_data.get("sender", {}).get("user_id", "")
    sender_nickname = request_data.get("sender", {}).get("nickname", "")
    message_type = request_data.get("message_type", "")

    if message.startswith("[AI]"):
        logger.info(f"Private: {sender_id}({sender_nickname}) -> Unknown User: {message} (IGNORED)")

    elif message_type == "private":  # 私聊消息
        if message.startswith("cls"):
            logger.info(f"Private: {sender_id}({sender_nickname}) -> {self_id}: {message}")
            private_chat_history[sender_id] = []
            send_private_message(sender_id, "[AI] Chat history cleared")

        elif message.startswith(chat_prefix):  # 私聊 Text to Text
            logger.info(f"Private: {sender_id}({sender_nickname}) -> {self_id}: {message} (Text to Text)")
            sender_history = private_chat_history.get(sender_id, [])
            message = message[len(chat_prefix):]
            logger.info(f"Processing chat prompt: {message}")
            answer, sender_history, status = chat(message, sender_history)
            if status != 0:
                logger.error(answer)
                send_private_message(sender_id, f"[AI] An error occurred(Code {status}): {answer}")
                return
            private_chat_history[sender_id] = sender_history
            logger.info(f"Response from GPT: {answer}")
            send_private_message(sender_id, f"[AI] {answer}")

        elif message.startswith(draw_prefix):  # 私聊 Text to Image
            logger.info(f"Private: {sender_id}({sender_nickname}) -> {self_id}: {message} (Text to Image)")
            if draw_prefix == "":
                logger.warning("Draw prefix not set, ignored")
                send_private_message(sender_id, "[AI] The feature is not enabled")
            message = message[len(draw_prefix):]
            logger.info(f"Processing draw prompt: {message}")
            url, status = draw(message)
            if status != 0:
                logger.error(url)
                send_private_message(sender_id, f"[AI] An error occurred(Code {status}): {url}")
                return
            logger.info(f"Response from GPT: {url}")
            send_private_img(sender_id, url)

        else:
            logger.info(f"Private: {sender_id}({sender_nickname}) -> {self_id}: {message} (IGNORED)")

    elif message_type == "group":  # 群聊消息
        group_id = request_data.get("group_id", "")
        group_history = group_chat_history.get(group_id, [])
        if group_id not in allowed_groups:
            logger.info(f"Group: {sender_id}({sender_nickname}) -> {group_id}: {message} (IGNORED)")

        elif message.startswith("cls"):
            logger.info(f"Group: {sender_id}({sender_nickname}) -> {group_id}: {message}")
            group_chat_history[group_id] = []
            send_group_message(group_id, sender_id, "[AI] Chat history cleared")

        elif message.startswith(chat_prefix):  # 群聊 Text to Text
            logger.info(f"Group: {sender_id}({sender_nickname}) -> {group_id}: {message} (Text to Text)")
            message = message[len(chat_prefix):]
            logger.info(f"Processing chat prompt: {message}")
            answer, group_history, status = chat(message, group_history)
            if status != 0:
                logger.error(answer)
                send_group_message(group_id, sender_id, f"[AI] An error occurred(Code {status}): {answer}")
                return
            group_chat_history[group_id] = group_history
            logger.info(f"Response from GPT: {answer}")
            send_group_message(group_id, sender_id, f"[AI] {answer}")

        elif message.startswith(draw_prefix):  # 群聊 Text to Image
            logger.info(f"Group: {sender_id}({sender_nickname}) -> {group_id}: {message} (Text to Image)")
            if draw_prefix == "":
                logger.warning("Draw prefix not set, ignored")
                send_group_message(group_id, sender_id, "[AI] The feature is not enabled")
            message = message[len(draw_prefix):]
            logger.info(f"Processing draw prompt: {message}")
            url, status = draw(message)
            if status != 0:
                logger.error(url)
                send_group_message(group_id, sender_id, f"[AI] An error occurred(Code {status}): {url}")
                return
            logger.info(f"Response from GPT: {url}")
            send_group_img(group_id, sender_id, url)

        else:
            logger.info(f"Group: {sender_id}({sender_nickname}) -> {group_id}: {message} (IGNORED)")


def mixed_message(text, image_list, request_data):
    global private_chat_history, group_chat_history

    self_id = request_data.get("self_id", "")
    sender_id = request_data.get("sender", {}).get("user_id", "")
    sender_nickname = request_data.get("sender", {}).get("nickname", "")
    message_type = request_data.get("message_type", "")
    if text.startswith("[AI]"):
        logger.info(f"Private: {sender_id}({sender_nickname}) -> Unknown User: {text} (IGNORED)")

    elif message_type == "private":
        if text.startswith(chat_prefix):
            logger.info(f"Private: {sender_id}({sender_nickname}) -> {self_id}: {text} (Text with Image to Text)")
            sender_history = private_chat_history.get(sender_id, [])
            text = text[len(chat_prefix):]
            for i in range(len(image_list)):
                image_list[i] = image_to_base64(image_list[i])
            logger.info(f"Processing chat prompt: {text} with image(s)")
            answer, sender_history, status = chat_with_image(text, image_list, sender_history)
            if status != 0:
                logger.error(answer)
                send_private_message(sender_id, f"[AI] An error occurred(Code {status}): {answer}")
                return
            private_chat_history[sender_id] = sender_history
            logger.info(f"Response from GPT: {answer}")
            send_private_message(sender_id, f"[AI] {answer}")

    elif message_type == "group":
        group_id = request_data.get("group_id", "")
        group_history = group_chat_history.get(group_id, [])
        if group_id not in allowed_groups:
            logger.info(f"Group: {sender_id}({sender_nickname}) -> {group_id}: {text} (IGNORED)")

        elif text.startswith("cls"):
            logger.info(f"Group: {sender_id}({sender_nickname}) -> {group_id}: {text}")
            group_chat_history[group_id] = []
            send_group_message(group_id, sender_id, "[AI] Chat history cleared")

        elif text.startswith(chat_prefix):  # 群聊 Text to Text
            logger.info(f"Group: {sender_id}({sender_nickname}) -> {group_id}: {text} (Text with Image to Text)")
            text = text[len(chat_prefix):]
            for i in range(len(image_list)):
                image_list[i] = image_to_base64(image_list[i])
            logger.info(f"Processing chat prompt: {text} with image(s)")
            answer, group_history, status = chat_with_image(text, image_list, group_history)
            if status != 0:
                logger.error(answer)
                send_group_message(group_id, sender_id, f"[AI] An error occurred(Code {status}): {answer}")
                return
            group_chat_history[group_id] = group_history
            logger.info(f"Response from GPT: {answer}")
            send_group_message(group_id, sender_id, f"[AI] {answer}")


if __name__ == "__main__":
    # logger.info(f"正在使用配置：\n消息触发前缀：{prefix}\n")
    app.run(host="127.0.0.1", port=5000)
