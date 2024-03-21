import asyncio
import logging

from aiogram.fsm.storage.memory import MemoryStorage
from keyboards.main_menu import set_main_menu
from handlers import other_handlers, user_handlers, callback_handlers, admins_handlers

from aiogram import Bot, Dispatcher

from config.config import Config_tg, load_tg_config

from utils.notify_admins import on_startup_notify

logger = logging.getLogger(__name__)

CALLBACK_TYPES = ('show_snackbar', 'open_link', 'open_app')


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    config_tg: Config_tg = load_tg_config()

    bot: Bot = Bot(token=config_tg.tg_bot.token)
    storage = MemoryStorage()
    dp: Dispatcher = Dispatcher(storage=storage)

    await set_main_menu(bot)

    dp.include_router(admins_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(callback_handlers.router)
    dp.include_router(other_handlers.router)

    await on_startup_notify(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
