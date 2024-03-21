import logging

from aiogram import Bot
from config.config import Config_tg, load_tg_config

admins: Config_tg = load_tg_config()


async def on_startup_notify(bot: Bot):
    for admin in admins.tg_bot.admin_ids:
        try:
            text = 'Бот запущен'
            await bot.send_message(chat_id=admin, text=text)
        except Exception as err:
            logging.exception(err)
