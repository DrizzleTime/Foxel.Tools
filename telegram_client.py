from telethon import TelegramClient
from telethon.sessions import StringSession

class TelegramClientManager:
    def __init__(self, api_id, api_hash):
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = TelegramClient(StringSession(), self.api_id, self.api_hash)

    def get_client(self):
        return self.client
