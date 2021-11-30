from pyrogram import Client
import config

plugins = dict(
    root="plugins"
)
app = Client(
    "kitchen",
    api_id=config.api_id,
    api_hash=config.api_hash,
    bot_token=config.TOKEN,
    plugins=plugins,
    parse_mode="html"
)

app.run()