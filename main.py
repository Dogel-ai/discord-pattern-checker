import config
import discord
import logging
import datetime

from discord import SyncWebhook
from colorlog import ColoredFormatter

formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        "DEBUG": "white",
        "INFO": "cyan",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white"
    },
    secondary_log_colors={},
    style="%"
)

stream = logging.StreamHandler()
stream.setFormatter(formatter)
logging.root.addHandler(stream)
logging.root.setLevel(config.log_level())

logger = logging.getLogger("observer")


class MyClient(discord.Client):
    async def on_ready(self):
        logger.info(f"Logged in as {client.user}")
        logger.debug(f"Observing channels {config.observer_channels()}")
        if not config.webhook_active():
            logger.warning("Webhook is not active. Matching messages will be sent to console")

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
        match_message = message.content
        for pattern in config.observer_patterns():
            if not config.observer_case_sensitive():
                pattern = pattern.lower()
                match_message = match_message.lower()

            if pattern in match_message:
                match_found = True
                break

        if not match_found:
            logger.debug(f"Ignoring message (pattern not found): {message.id}")
            return

        if not config.webhook_active():
            logger.info(f"{message.author.name}: {message.content}")
            return

        webhook = SyncWebhook.from_url(config.webhook_url())

        webhook_name = message.author.name
        if config.webhook_name():
            webhook_name = config.webhook_name()

        webhook_avatar_url = message.author.avatar
        if config.webhook_avatar_url():
            webhook_avatar_url = config.webhook_avatar_url()

        if config.webhook_embed_active():
            config_embed = config.webhook_embed()
            config_embed_colour = None

            if config.webhook_embed_colour():
                config_embed_colour = discord.Colour.from_str(config_embed.colour)

            e = discord.Embed(title=config_embed.title,
                              description=config_embed.description,
                              colour=config_embed_colour,
                              url=config_embed.url,
                              timestamp=message.created_at)

            e.set_author(name=config_embed.author.name,
                         url=config_embed.author.url,
                         icon_url=config_embed.author.icon_url)

            e.set_thumbnail(url=config_embed.thumbnail_url)
            e.set_footer(text=config_embed.footer.text,
                         icon_url=config_embed.footer.icon_url)

            for fields in config_embed.fields:
                e.add_field(name=config_embed.fields[fields]["name"],
                            value=config_embed.fields[fields]["value"],
                            inline=config_embed.fields[fields]["inline"])

            webhook.send(username=webhook_name,
                         avatar_url=webhook_avatar_url,
                         embed=e)
        else:
            webhook.send(content=message.content,
                         username=webhook_name,
                         avatar_url=webhook_avatar_url)

        logger.info(f"Webhook for message {message.id} sent")


client = MyClient()

if __name__ == "__main__":
    client.run(config.bot_token(), log_handler=stream, log_level=logging.INFO)
