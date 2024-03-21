from aiogram import Router
from aiogram.types import Message

# from filters.filters import UserOnDB
# from keyboards.inline_keyboard_menu.start_menu import start_menu
from lexicon.lexicon import LEXICON

router: Router = Router()


@router.message()
async def send_default_message(message: Message, ):
    await message.answer(LEXICON['no command'][0])


@router.message()
async def send_default_message(message: Message):
    await message.answer(text=LEXICON['no command'][1])
