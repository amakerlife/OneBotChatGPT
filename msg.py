import json
import requests
import configparser

config = configparser.ConfigParser()
config.read("config.cfg")

http_url = config.get("onebot", "http_url")


def send_private_message(user_id, content):
    url = f"{http_url}/send_private_msg"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "user_id": user_id,
        "message": [
            {
                "type": "text",
                "data": {"text": content}
            }
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "ok":
            print(f"Successfully sent message: {content}")
            return True
        else:
            print(f"Failed to send message, response: {str(result)}")
            return False
    else:
        print(f"Failed to send message, status code: {str(response.status_code)}")
        return False


def send_group_message(group_id, sender_id, content):
    url = f"{http_url}/send_group_msg"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "group_id": group_id,
        "message": [
            {
                "type": "at",
                "data": {"qq": sender_id}
            },
            {
                "type": "text",
                "data": {"text": " " + content}
            }
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "ok":
            print(f"Successfully sent message: {content}")
            return True
        else:
            print(f"Failed to send message, response: {str(result)}")
            return False
    else:
        print(f"Failed to send message, status code: {str(response.status_code)}")
        return False


def send_private_img(user_id, content):
    url = f"{http_url}/send_private_msg"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "user_id": user_id,
        "message": [
            {
                "type": "image",
                "data": {"file": content}
            }
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "ok":
            print(f"Successfully sent image: {content}")
            return True
        else:
            print(f"Failed to send image, response: {str(result)}")
            return False
    else:
        print(f"Failed to send image, status code: {str(response.status_code)}")
        return False


def send_group_img(group_id, sender_id, content):
    url = f"{http_url}/send_group_msg"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "group_id": group_id,
        "message": [
            {
                "type": "at",
                "data": {"qq": sender_id}
            },
            {
                "type": "image",
                "data": {"file": content}
            }
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "ok":
            print(f"Successfully sent message: {content}")
            return True
        else:
            print(f"Failed to send message, response: {str(result)}")
            return False
    else:
        print(f"Failed to send message, status code: {str(response.status_code)}")
        return False
