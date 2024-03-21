from aiogram import Router, Bot, types
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from lexicon.lexicon import LEXICON
from aiogram.utils.deep_linking import create_start_link, decode_payload

router: Router = Router()



@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        f'{LEXICON["/start"][0]}<b>{message.from_user.first_name}</b>'
        f'{LEXICON["/start"][3]}{LEXICON["/start"][4]}',
        reply_markup=start_menu)


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON[message.text])


@router.message(Command(commands='instruction'), UserOnDB())
async def process_instruction_command(message: Message):
    await message.answer(LEXICON[message.text], reply_markup=instruction_menu)


@router.message(Command(commands='invite'))
async def process_invite_command(message: Message, bot: Bot):
    link = await create_start_link(bot, str(message.from_user.id), encode=True)
    await message.answer(text=f'{LEXICON["invite"]}<code>{link}</code>')


@router.message(Command(commands='balance'), UserOnDB())
async def process_balance_command(message: Message, bot: Bot):
    await check_balance(message.from_user.id, bot)


@router.message(Command(commands='device'), UserOnDB())
async def process_device_command(message: Message):
    button = await create_inline_kb(message.from_user.id)
    await message.answer(LEXICON['menu_device'], reply_markup=button)


#  Выдаёт меню пополнения оплаты
@router.message(Command(commands='topup'), UserOnDB())
async def process_to_pup_command(message: types.Message):
    user = await select_user(message.from_user.id)
    balance = user.balance
    await message.answer(text=f"{LEXICON['pay'][0]}{balance}{LEXICON['pay'][1]}", reply_markup=pay_menu)
