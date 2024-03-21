from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InputMediaVideo
from aiogram import Router, F, types
from aiogram import Bot

from keyboards.inline_keyboard_menu.instruction_menu import instruction_menu_windows, instruction_menu_macos
from keyboards.inline_keyboard_menu.instruction_menu_2 import instruction_menu
from keyboards.inline_keyboard_menu.menu_device import create_inline_kb
from keyboards.inline_keyboard_menu.pay_menu import pay_menu
from keyboards.inline_keyboard_menu.phone_or_pc import choice_device
from lexicon.lexicon import LEXICON, LEXICON_PAY
from database.quick_commands import select_user, add_user, update_balance, add_new_device, check_count_busy, \
    add_new_device_xray
from keyboards.inline_keyboard_menu.start_menu_device import start_menu_device
from media.send_media.send_media import send_media2, send_key2, send_key, send_media
from aiogram.utils.deep_linking import create_start_link
from config_data.config import ConfigFile, load_config_file, ConfigPAY, load_config_pay

from services.check_balance import check_balance
from state.referral import FSMReferral

router = Router()

path: ConfigFile = load_config_file()

pay_token: ConfigPAY = load_config_pay()


@router.callback_query(F.data == 'Registration')
async def process_callback_query_command(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    try:
        user = await select_user(callback.from_user.id)
        if user.status == 'active':
            button = await create_inline_kb(callback.from_user.id)
            await callback.message.edit_text(
                text=f"{LEXICON['Registration'][1]}{callback.from_user.first_name}"
                     f"{LEXICON['Registration'][2]}{user.balance}{LEXICON['Registration'][3]}", reply_markup=button)
        elif user.status == 'baned':
            await callback.message.edit_text(text=LEXICON['Registration'][4])
    except Exception:
        data = await state.get_data()
        if data:
            try:
                referral_id = data['referral_id']
                await update_balance(referral_id, 100)
                user = await select_user(referral_id)
                await bot.send_message(chat_id=referral_id, text=f'{LEXICON["referral"]}{user.balance}₽')
            except Exception:
                referral_id = 0
        else:
            await state.set_state(FSMReferral.referral_id)
            referral_id = 0
            await state.update_data(referral_id=int(referral_id))
        # file = await select_file_active('free')
        await add_user(user_id=callback.from_user.id,
                       name=callback.from_user.full_name,
                       balance=50,
                       referral_id=referral_id,
                       file_id=[],
                       status='active')
        await callback.message.edit_text(text=f"{LEXICON['Registration'][0]}\n\n{LEXICON['/instruction']}",
                                         reply_markup=instruction_menu)
        # await send_media(file.file_id, callback, bot)
        # await file.update(status='busy').apply()


#  выдаёт инструкции по настройки
@router.callback_query(F.data == 'iPhone')
async def process_callback_query_command(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    video_bytes = FSInputFile(f'{path.file_pach.media_pach}send_media/XRay_Iphone_v2.mp4')
    try:
        await bot.edit_message_media(chat_id=callback.message.chat.id,
                                     message_id=(callback.message.message_id + 1),
                                     media=InputMediaVideo(
                                         media=video_bytes,
                                         caption=f'{LEXICON["XRAY"]["iPhone_v2"]}'),
                                     reply_markup=start_menu_device)
    except Exception as err:
        await bot.send_video(chat_id=callback.message.chat.id, video=video_bytes,
                             caption=f'{LEXICON["XRAY"]["iPhone_v2"]}', reply_markup=start_menu_device)
        user = await select_user(callback.from_user.id)
        if not user.file_id and user.balance >= 3:
            file = await add_new_device_xray(user.user_id)
            await send_key2(file.file_id, callback, bot)
            # await add_new_device(user.user_id)
            # user = await select_user(callback.from_user.id)
            # await send_media2(user.file_id[0], callback, bot)


#  выдаёт инструкции по настройки
@router.callback_query(F.data == 'Android')
async def process_callback_query_command(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    video_bytes = FSInputFile(f'{path.file_pach.media_pach}send_media/XRay_Android.mp4')
    # await callback.message.edit_caption(caption="- это ваш ключ файл")
    try:
        await bot.edit_message_media(chat_id=callback.message.chat.id,
                                     message_id=(callback.message.message_id + 1),
                                     media=InputMediaVideo(
                                         media=video_bytes,
                                         caption=f'{LEXICON["XRAY"]["Android"]}'),
                                     reply_markup=start_menu_device)
    except Exception as err:
        await bot.send_video(chat_id=callback.message.chat.id, video=video_bytes,
                             caption=f'{LEXICON["XRAY"]["Android"]}', reply_markup=start_menu_device)
        user = await select_user(callback.from_user.id)
        if not user.file_id and user.balance >= 3:
            file = await add_new_device_xray(user.user_id)
            await send_key2(file.file_id, callback, bot)
            # await add_new_device(user.user_id)
            # user = await select_user(callback.from_user.id)
            # await send_media2(user.file_id[0], callback, bot)


@router.callback_query(F.data == 'wg_iPhone')
async def process_callback_query_command(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    video_bytes = FSInputFile(f'{path.file_pach.media_pach}send_media/iPhone.mp4')
    try:
        await bot.edit_message_media(chat_id=callback.message.chat.id,
                                     message_id=(callback.message.message_id + 1),
                                     media=InputMediaVideo(
                                         media=video_bytes,
                                         caption=f'{LEXICON["OS"]["iPhone"]}'))
    except Exception as err:
        await bot.send_video(chat_id=callback.message.chat.id, video=video_bytes,
                             caption=f'{LEXICON["OS"]["iPhone"]}')


@router.callback_query(F.data == 'wg_Android')
async def process_callback_query_command(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    video_bytes = FSInputFile(f'{path.file_pach.media_pach}send_media/Android.mp4')
    try:
        await bot.edit_message_media(chat_id=callback.message.chat.id,
                                     message_id=(callback.message.message_id + 1),
                                     media=InputMediaVideo(
                                         media=video_bytes,
                                         caption=f'{LEXICON["OS"]["Android"]}'))
    except Exception as err:
        await bot.send_video(chat_id=callback.message.chat.id, video=video_bytes,
                             caption=f'{LEXICON["OS"]["Android"]}')


#  выдаёт инструкции по настройки
@router.callback_query(F.data == 'Windows')
async def process_callback_query_command(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    user = await select_user(callback.from_user.id)
    if not user.file_id and user.balance >= 3:
        file = await add_new_device(user.user_id)
        user = await select_user(callback.from_user.id)
        await send_media2(file.file_id, callback, bot)
    await bot.send_message(chat_id=callback.message.chat.id, text='Ссылка на инструкцию:',
                           reply_markup=instruction_menu_windows)


#  выдаёт инструкции по настройки
@router.callback_query(F.data == 'macOS')
async def process_callback_query_command(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    user = await select_user(callback.from_user.id)
    if not user.file_id and user.balance >= 3:
        file = await add_new_device(user.user_id)
        user = await select_user(callback.from_user.id)
        await send_media2(file.file_id, callback, bot)
    await bot.send_message(chat_id=callback.message.chat.id, text='Ссылка на инструкцию:',
                           reply_markup=instruction_menu_macos)


# Создание реферальной ссылки
@router.callback_query(F.data == 'invite')
async def process_referral_command(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    link = await create_start_link(bot, str(callback.from_user.id), encode=True)
    await callback.message.delete()
    await callback.message.answer(text=f'{LEXICON["invite"]}<code>{link}</code>')


# Добавление устройства
@router.callback_query(F.data == 'device')
async def process_device_command(callback: CallbackQuery):
    await callback.answer()
    button = await create_inline_kb(callback.from_user.id)
    await callback.message.delete()
    await callback.message.answer(LEXICON['menu_device'], reply_markup=button)


@router.callback_query(F.data == 'choice_device')
async def process_choice_device_command(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(LEXICON['choice_device'], reply_markup=choice_device)


@router.callback_query(F.data == 'add_device_phone')
async def process_add_device_command(callback: CallbackQuery, bot: Bot):
    # await callback.message.delete()
    count_file = await check_count_busy(callback.from_user.id)
    user = await select_user(callback.from_user.id)
    if (count_file[0] + 1) * 3 > user.balance:
        await callback.answer(text=LEXICON['add_device'][0], show_alert=True)
    elif count_file[0] == 5:
        await callback.answer(text=LEXICON['add_device'][1], show_alert=True)
    else:
        try:
            file = await add_new_device_xray(callback.from_user.id)
            button = await create_inline_kb(callback.from_user.id)
            if callback.message.caption:
                await callback.message.edit_caption(caption=callback.message.caption, reply_markup=button)
                await send_key(file.file_id, callback, bot)
            else:
                await callback.message.edit_text(LEXICON['menu_device'], reply_markup=button)
                await send_key(file.file_id, callback, bot)
        except AttributeError as err:
            await callback.answer(text=LEXICON['add_device'][2], show_alert=True)


@router.callback_query(F.data == 'add_device_pc')
async def process_add_device_command(callback: CallbackQuery, bot: Bot):
    # await callback.message.delete()
    count_file = await check_count_busy(callback.from_user.id)
    user = await select_user(callback.from_user.id)
    if (count_file[0] + 1) * 3 > user.balance:
        await callback.answer(text=LEXICON['add_device'][0], show_alert=True)
    elif count_file[0] == 5:
        await callback.answer(text=LEXICON['add_device'][1], show_alert=True)
    else:
        try:
            file = await add_new_device(callback.from_user.id)
            button = await create_inline_kb(callback.from_user.id)
            if callback.message.caption:
                await callback.message.edit_caption(caption=callback.message.caption, reply_markup=button)
                await send_media(file.file_id, callback, bot)
            else:
                await callback.message.edit_text(LEXICON['menu_device'], reply_markup=button)
                await send_media(file.file_id, callback, bot)
        except AttributeError as err:
            await callback.answer(text=LEXICON['add_device'][2], show_alert=True)


#  Выдаёт меню пополнения баланса
@router.callback_query(F.data == 'topup')
async def process_topup_command(callback: CallbackQuery):
    await callback.answer()
    user = await select_user(callback.from_user.id)
    balance = user.balance
    await callback.message.answer(text=f"{LEXICON['pay'][0]}{balance}{LEXICON['pay'][1]}", reply_markup=pay_menu)


@router.callback_query(F.data.startswith('PAYMENT'))
async def process_to_pup_command(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    balance = int(callback.data[8:])
    await callback.message.delete()
    await bot.send_invoice(
        callback.message.chat.id,
        title=LEXICON_PAY['tm_title'],
        description=LEXICON_PAY['tm_description'],
        provider_token=pay_token.pay_bot.provider_token,
        currency='rub',
        photo_url=None,
        photo_height=None,  # !=0/None, иначе изображение не покажется
        photo_width=None,
        photo_size=None,
        is_flexible=False,  # True если конечная цена зависит от способа доставки
        prices=[types.LabeledPrice(label=f'{balance} рублей', amount=balance * 100)],
        start_parameter='one-month-subscription',
        payload='some-invoice-payload-for-our-internal-use')


@router.callback_query(F.data.startswith('SALE'))
async def process_sale_command(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    balance = int(callback.data[5:])
    await callback.message.delete()
    await bot.send_invoice(
        callback.message.chat.id,
        title=LEXICON_PAY['tm_title'],
        description=LEXICON_PAY['tm_description'],
        provider_token=pay_token.pay_bot.provider_token,
        currency='rub',
        photo_url=None,
        photo_height=None,  # !=0/None, иначе изображение не покажется
        photo_width=None,
        photo_size=None,
        is_flexible=False,  # True если конечная цена зависит от способа доставки
        prices=[types.LabeledPrice(label=f'{balance} рублей', amount=balance * 100)],
        start_parameter='one-month-subscription',
        payload='some-invoice-payload-for-our-internal-use')


# pre checkout  (must be answered in 10 seconds)
@router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@router.message(lambda message: message.content_type in {types.ContentType.SUCCESSFUL_PAYMENT})
async def successful_payment(message: types.Message, bot: Bot):
    payment_balance = message.successful_payment.total_amount / 100
    if payment_balance == 300:
        pay = 330
        user = await select_user(message.from_user.id)
        if user.promo == 'promo_less':
            await user.update(promo='less_300').apply()
        if user.promo == 'promo_more':
            await user.update(promo='more_300').apply()
    elif payment_balance == 500:
        pay = 600
        user = await select_user(message.from_user.id)
        if user.promo == 'promo_less':
            await user.update(promo='less_500').apply()
        if user.promo == 'promo_more':
            await user.update(promo='more_500').apply()
    elif payment_balance == 900:
        pay = 1200
        user = await select_user(message.from_user.id)
        if user.promo == 'promo_less':
            await user.update(promo='less_900').apply()
        if user.promo == 'promo_more':
            await user.update(promo='more_900').apply()
    elif payment_balance == 99:
        pay = 150
        user = await select_user(message.from_user.id)
        await user.update(promo='less_99').apply()
    elif payment_balance == 199:
        pay = 300
        user = await select_user(message.from_user.id)
        await user.update(promo='less_199').apply()
    else:
        pay = payment_balance
        user = await select_user(message.from_user.id)
        if user.promo == 'promo_less':
            await user.update(promo='less_100').apply()
        if user.promo == 'promo_more':
            await user.update(promo='more_100').apply()
    await update_balance(message.from_user.id, pay)
    await check_balance(message.from_user.id, bot)
