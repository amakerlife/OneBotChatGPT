import json
import requests
from loguru import logger
from config import onebot_config

http_url = onebot_config.http_url
access_token = onebot_config.access_token


def send_private_message(user_id, content, origin_message_id=None):
    url = f"{http_url}/send_private_msg"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    request_message = []
    if origin_message_id:
        request_message.append({
            "type": "reply",
            "data": {"id": origin_message_id}
        })
    request_message.append({
        "type": "text",
        "data": {"text": content}
    })
    data = {
        "user_id": user_id,
        "message": request_message
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "ok":
            logger.info(f"Successfully sent message: {content}")
            return True
        else:
            logger.warning(f"Failed to send message, response: {str(result)}")
            return False
    else:
        logger.error(f"Failed to send message, status code: {str(response.status_code)}")
        return False


def send_group_message(group_id, sender_id, content, origin_message_id=None, at_sender=False):
    url = f"{http_url}/send_group_msg"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    request_message = []
    if origin_message_id:
        request_message.append({
            "type": "reply",
            "data": {"id": origin_message_id}
        })
    if at_sender:
        request_message.append({
            "type": "at",
            "data": {"qq": sender_id}
        })
    request_message.append({
        "type": "text",
        "data": {"text": f"{' ' if at_sender else ''}{content}"}
    })
    data = {
        "group_id": group_id,
        "message": request_message
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "ok":
            logger.info(f"Successfully sent message: {content}")
            return True
        else:
            logger.warning(f"Failed to send message, response: {str(result)}")
            return False
    else:
        logger.error(f"Failed to send message, status code: {str(response.status_code)}")
        return False


def send_private_img(user_id, content, origin_message_id=None):
    url = f"{http_url}/send_private_msg"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    request_message = []
    if origin_message_id:
        request_message.append({
            "type": "reply",
            "data": {"id": origin_message_id}
        })
    request_message.append({
        "type": "image",
        "data": {"file": content}
    })
    data = {
        "user_id": user_id,
        "message": request_message
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "ok":
            logger.info(f"Successfully sent image: {content}")
            return True
        else:
            logger.warning(f"Failed to send image, response: {str(result)}")
            return False
    else:
        logger.error(f"Failed to send image, status code: {str(response.status_code)}")
        return False


def send_group_img(group_id, sender_id, content, origin_message_id=None, at_sender=False):
    url = f"{http_url}/send_group_msg"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    request_message = []
    if origin_message_id:
        request_message.append({
            "type": "reply",
            "data": {"id": origin_message_id}
        })
    if at_sender:
        request_message.append({
            "type": "at",
            "data": {"qq": sender_id}
        })
    request_message.append({
        "type": "image",
        "data": {"file": content}
    })
    data = {
        "group_id": group_id,
        "message": request_message
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "ok":
            logger.info(f"Successfully sent message: {content}")
            return True
        else:
            logger.warning(f"Failed to send message, response: {str(result)}")
            return False
    else:
        logger.error(f"Failed to send message, status code: {str(response.status_code)}")
        return False


def get_image(image_url):
    url = f"{http_url}/get_image"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    data = {
        "file": image_url
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "ok":
            logger.info(f"Successfully get image: {image_url}")
            return result["data"]["file"]
        else:
            logger.warning(f"Failed to get image, response: {str(result)}")
            return None
    else:
        logger.error(f"Failed to get image, status code: {str(response.status_code)}")
        return None
