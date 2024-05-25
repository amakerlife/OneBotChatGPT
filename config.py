import yaml
from loguru import logger

config_path = "config.yml"


class OnebotConfig:
    def __init__(self, http_url, access_token):
        self.http_url = http_url
        self.access_token = access_token


class ChatgptConfig:
    def __init__(self, chat_endpoint, draw_endpoint, token, chat_model, draw_model, max_tokens, system_prompt, timeout):
        self.chat_endpoint = chat_endpoint
        self.draw_endpoint = draw_endpoint
        self.token = token
        self.chat_model = chat_model
        self.draw_model = draw_model
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        self.timeout = timeout


class MessageConfig:
    def __init__(self, chat_prefix, draw_prefix, reply_quote: bool, reply_mention: bool, allowed_groups):
        self.chat_prefix = chat_prefix
        self.draw_prefix = draw_prefix
        self.reply_quote = reply_quote
        self.reply_mention = reply_mention
        self.allowed_groups = allowed_groups


with open(config_path, "r", encoding="utf-8") as f:
    config_data = yaml.safe_load(f)

try:
    onebot_config = OnebotConfig(**config_data.get("onebot", {}))
    chatgpt_config = ChatgptConfig(**config_data.get("chatgpt", {}))
    message_config = MessageConfig(**config_data.get("message", {}))
    logger.success("Config loaded successfully")
except Exception as e:
    logger.error(f"Failed to load config: {e}")
