import json
import requests
import configparser

config = configparser.ConfigParser()
config.read("config.cfg")

http_url = config.get("onebot", "http_url")


def send_message(user_id, content):
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
        if result["status"] == 0:
            print(f"Successfully sent message: {content}")
            return True
        else:
            print(f"Failed to send message, response: {str(result)}")
            return False
    else:
        print(f"Failed to send message, status code: {str(response.status_code)}")
        return False
