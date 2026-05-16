import config
import discord
import logging

from discord import SyncWebhook
from colorlog import ColoredFormatter

formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'white',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white'
    },
    secondary_log_colors={},
    style='%'
)

stream = logging.StreamHandler()
stream.setFormatter(formatter)
logging.root.addHandler(stream)
logging.root.setLevel(config.log_level())

logger = logging.getLogger("observer")


class MyClient(discord.Client):
    async def on_ready(self):
        logger.info(f'Logged in as {client.user}')
        logger.debug(f'Observing channels {config.observer_channels()}')
        if not config.webhook_active():
            logger.warning(f"Webhook is not active. Matching messages will be sent to console")

    async def on_message(self, message):
        if message.author.id == self.user.id:
            logger.debug(f"Ignoring self message: {message.id}")
            return

        if message.author.bot and config.observer_bot_ignore():
            logger.debug(f"Ignoring bot message: {message.id}")
            return

        if message.channel.id not in config.observer_channels():
            logger.debug(f"Ignoring mesage (channel not observed): {message.id}")
            return

        match_found = False
        for pattern in config.observer_patterns():
            if pattern in message.content:
                match_found = True
                break

        if not match_found:
            logger.debug(f"Ignoring message (pattern not found): {message.id}")
            return

        if not config.webhook_active():
            logger.info(f"{message.author.name}: {message.content}")
            return

        logger.info(f"Processing message from user {message.author.name} with pattern {pattern}: {message.id}")

        webhook = SyncWebhook.from_url(config.webhook_url())
        webhook.send(content=message.content,
                     username=message.author.name,
                     avatar_url=message.author.avatar)


client = MyClient()

if __name__ == '__main__':
    client.run(config.bot_token(), log_handler=stream, log_level=logging.INFO)
