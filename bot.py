import os
import discord
from dotenv import load_dotenv

CHANNELS_LIST = []
PATTERNS_LIST = []

load_dotenv()
ENV_TOKEN = os.getenv('TOKEN')

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        print(f'Observing channels {CHANNELS_LIST}')

    async def on_message(self, message):
        if message.channel.id in CHANNELS_LIST:
            print(f'Received message from server {message.guild}')
            for pattern in PATTERNS_LIST:
                if pattern in message.content:
                    print(message.content)
                    break
        if message.author.id == self.user.id:
            return

client = MyClient()
client.run(ENV_TOKEN)
