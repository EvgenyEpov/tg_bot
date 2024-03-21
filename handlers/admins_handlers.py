from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message

from config_data.config import ConfigFile, load_config_file
from database.file.file_commands import count_file, select_file, file_del, \
    select_all_files_on_server, select_file_free_all
from filters.filters import IsAdmin
from database.quick_commands import count_users, select_all_users, update_balance, select_user, \
    select_user_with_no_referral, select_user_more_15, select_user_less_15
from keyboards.inline_keyboard_menu.phone_or_pc import add_device_pc, add_device_phone
from keyboards.inline_keyboard_menu.sale_menu import sale_menu, promo_less_42, promo_more_42, change_wg, change_xray
from mailing.mailing import mailing

from ssh.ssh import count_clients, run_loop, del_all, run_client, del_file_with_del, info_xray, info_wg, \
    copy_config_to_bot, \
    clean_server, info_del, search_key_for_del

file_path: ConfigFile = load_config_file()

router = Router()


@router.message(IsAdmin(), Command(commands='ban'))
async def process_update_db(message: Message):
    await message.answer('ты ещё это не написал')


@router.message(IsAdmin(), Command(commands='db'))
async def process_update_db(message: Message):
    # users_dict = {}
    count_user = await count_users()
    # users = await select_all_users()
    # for user in users:
    #     users_dict[user.user_id] = {'Баланс пользователя ': user.balance, 'id конфигов пользователя ': user.file_id}
    try:
        file_all = await count_file()
        file_busy_xray = await select_file_free_all('xray', 'busy')
        file_busy_wg = await select_file_free_all('wg0', 'busy')
        file_free_xray = await select_file_free_all('xray', 'free')
        file_free_wg = await select_file_free_all('wg0', 'free')
        file_del_xray = await select_file_free_all('xray', 'del')
        file_del_wg = await select_file_free_all('wg0', 'del')
        await message.answer(f'Общее количество людей в базе данных: {count_user}\n'
                             f'Количество свободных конфигов wg: {len(file_free_wg)}\n'
                             f'Количество свободных конфигов xray: {len(file_free_xray)}\n'
                             f'Количество занятых конфигов wg: {len(file_busy_wg)}\n'
                             f'Количество занятых конфигов xray: {len(file_busy_xray)}\n'
                             f'Количество конфигов для удаления wg: {len(file_del_wg)}\n'
                             f'Количество конфигов для удаления xray: {len(file_del_xray)}\n'
                             f'Количество всего конфигов: {file_all}\n')
    except Exception as err:
        print(err)


# Выдавет количество конфигов на каждом сервере
@router.message(IsAdmin(), Command(commands='count'))
async def process_new(message: Message):
    try:
        count_client_ssh = await count_clients()
        for client in count_client_ssh:
            await message.answer(f'Kоличество конфигов на сервере {client[0]}: {client[1]}')
    except Exception as err:
        print(err)


@router.message(IsAdmin(), Command(commands='info_xray_server'))
async def info_xray_server(message: Message):
    try:
        counts_xray = await info_xray()
        for count in counts_xray:
            await message.answer(f'info: b,f,d,all: {count[0]}: {count[1]}')
    except Exception as err:
        print(err)


@router.message(IsAdmin(), Command(commands='info_wg_server'))
async def info_wg_server(message: Message):
    try:
        counts_wg = await info_wg()
        for count in counts_wg:
            await message.answer(f'info: b,f,d,all: {count[0]}: {count[1]}')
    except Exception as err:
        print(err)


@router.message(IsAdmin(), Command(commands='info_del_server'))
async def info_wg_server(message: Message):
    try:
        counts_del = await info_del()
        for count in counts_del:
            await message.answer(f'info: b,f,d,all: {count[0]}: {count[1]}')
    except Exception as err:
        print(err)


@router.message(IsAdmin(), Command(commands='load_all'))
async def process_update_db(message: Message):
    await run_loop()


@router.message(IsAdmin(), Command(commands='download_config'))
async def download_config(message: Message):
    await copy_config_to_bot()


# Удаляет все конфиги со всех серверов
# @router.message(IsAdmin(), Command(commands='del_all'))
# async def process_update_db(message: Message):
#     await del_all()


# Очищает базу данных файлов от удаленных
@router.message(IsAdmin(), Command(commands='clear'))
async def process_clear_db(message: Message):
    users = await select_all_users()
    for user in users:
        user_list = []
        for file_id in user.file_id:
            try:
                file = await select_file(file_id)
                if file.status == 'busy':
                    user_list.append(file.file_id)
            except:
                continue
        await user.update(file_id=user_list).apply()


# изменяет баланс пользователя
@router.message(IsAdmin(), F.text.startswith('user'))
async def process_update_balance(message: Message):
    try:
        user = message.text.split()
        await update_balance(int(user[1]), int(user[2]))
    except Exception as err:
        print(err)


# Удаляет пользователя вместе с его файлами из бд, новые файлы не содаёт
@router.message(IsAdmin(), F.text.startswith('del'))
async def process_del_user_balance(message: Message):
    try:
        id = int(message.text.split()[1])
        user = await select_user(id)
        for file_id in user.file_id:
            file = await select_file(file_id)
            await run_client(file.server, f'./revokeClient.sh {file.file_id}')
            await file_del(file_path.file_pach.media_pach, file.name)
            await file.delete()
        await user.delete()
    except Exception as err:
        print(err)


@router.message(IsAdmin(), F.text.startswith('status_to_del'))
async def process_status_to_del(message: Message):
    try:
        ip = str(message.text.split()[1])
        files = await select_all_files_on_server(ip)
        for file in files:
            if file.status == 'busy':
                await file.update(status='del').apply()
    except Exception as err:
        print(err)


@router.message(IsAdmin(), F.text.startswith('clean_server'))
async def process_del_user_balance(message: Message):
    ip = str(message.text.split()[1])
    password = str(message.text.split()[2])
    try:
        files = await select_all_files_on_server(ip)
        for file in files:
            try:
                if file.status == 'del':
                    await clean_server(ip, password, file.file_id)
                    await file_del(file_path.file_pach.media_pach, file.name)
                    await file.delete()
            except Exception as err:
                print(err)
    except Exception as err:
        print(err)


@router.message(IsAdmin(), Command(commands='del_file_with_del'))
async def process_del_file_with_del(message: Message):
    try:
        await del_file_with_del()
    except Exception as err:
        print(err)


# Рассылка рекламы все пользователям
@router.message(IsAdmin(), F.text.startswith('mailing') | F.photo[-1].as_('photo_id') | F.video | F.animation)
async def process_mailing(message: Message, bot: Bot):
    await mailing(message, bot)


# Рассылка повторного предложения зарегестрироваться

# Собирает и присылает статистику
@router.message(IsAdmin(), Command(commands='statistic'))
async def process_statistic(message: Message, bot: Bot):
    users1 = await select_user_with_no_referral()
    users2 = await select_user_more_15()
    users3 = await select_user_less_15()
    count_users2 = 0
    count_users3 = 0
    for user in users2:
        if not user.file_id:
            count_users2 += 1
    for user in users3:
        if not user.file_id:
            count_users3 += 1
    await bot.send_message(chat_id=message.chat.id, text=f'Количество пользователей рефералов: {len(users1)}\n'
                                                         f'Количество пользователей с балансом больше 15: {count_users2}\n'
                                                         f'Количество пользователей с балансом меньше 15: {count_users3}')


@router.message(IsAdmin(), Command(commands='sale'))
async def process_statistic(message: Message, bot: Bot):
    users = await select_user_less_15()
    count_users1 = 0
    count_users2 = 0
    for user in users:
        if not user.file_id:
            try:
                await bot.send_message(chat_id=user.user_id, text='Только для вас скидка 50%', reply_markup=sale_menu)
                count_users1 += 1
            except Exception as err:
                count_users2 += 1
    await bot.send_message(chat_id=message.chat.id, text=f'Попытка рассылки: {len(users)}\n'
                                                         f'Пользователей получило: {count_users1}\n'
                                                         f'Пользователей заблокировало: {count_users2}')


@router.message(IsAdmin(), Command(commands='promo'))
async def process_statistic(message: Message, bot: Bot):
    users = await select_user_less_15()
    count_users1 = 0
    count_users2 = 0
    for user in users:
        if not user.file_id:
            try:
                await bot.send_message(chat_id=user.user_id, text=f'<b>Друзья! Добрый день!</b> 👋\n\n'
                                                                  f'У нас для вас 2 новости:\n\n'
                                                                  f'1. За друга, приглашенного по реферальной ссылке, теперь начисляется <b>100₽</b>.\n\n'
                                                                  f'2. Если вы пропустили, у нас <b>новый VPN</b>, две недели <b>бесплатного</b> теста.\n',
                                       reply_markup=promo_less_42)
                count_users1 += 1
                await user.update(promo='get').apply()
            except Exception as err:
                await user.update(promo='blocked').apply()
                count_users2 += 1
    await bot.send_message(chat_id=message.chat.id, text=f'Попытка рассылки: {len(users)}\n'
                                                         f'Пользователей получило: {count_users1}\n'
                                                         f'Пользователей заблокировало: {count_users2}')


@router.message(IsAdmin(), Command(commands='search_key_for_del'))
async def process_search_key_for_del(message: Message, bot: Bot):
    wg_key_for_del, xray_key_for_del = await search_key_for_del()
    wg_text = ', '.join(map(str, wg_key_for_del))
    xray_text = ', '.join(map(str, xray_key_for_del))
    users = await select_all_users()
    i = 0
    for user in users:
        for key in user.file_id:
            if key in wg_key_for_del:
                i += 1
                await bot.send_message(chat_id=message.chat.id,
                                       text=f'Добрый день,{user.name} {user.user_id} wg: {key} , будет удален.\n'
                                            f'Если вам нужен новый ключ, добавьте его:',
                                       reply_markup=change_wg)
            if key in xray_key_for_del:
                i += 1
                await bot.send_message(chat_id=message.chat.id, text=f'{user.user_id} xray: {key} , будет удален.\n'
                                                                     f'Если вам нужен новый ключ, добавьте его:',
                                       reply_markup=change_xray)
        if i > 20:
            break


#   await bot.send_message(chat_id=message.chat.id, text=f'Количество ключей для удаления wg: {len(wg_key_for_del)}\n'
#                                                      f'Количество ключей для удаления xray: {len(xray_key_for_del)}\n')
#                                                      f'Список ключей: {xray_text}')
#                                                      f'Список ключей: {wg_text}\n')


@router.message(IsAdmin(), Command(commands='user_clean_key'))
async def process_user_clean_key(message: Message, bot: Bot):
    wg_key_for_del, xray_key_for_del = await search_key_for_del()
    users = await select_all_users()
    user_get = 0
    user_block = 0
    for user in users:
        try:
            for key in user.file_id:
                if key in wg_key_for_del:
                    if user.promo == 'change':
                        await bot.send_message(chat_id=user.user_id,
                                               text=f'14 февраля ключ c id <b>{key}</b> перестанет работать, пожалуйста замените его:',
                                               reply_markup=add_device_pc)
                    else:
                        user_get += 1
                        await bot.send_message(chat_id=user.user_id,
                                               text=f'{user.name}, добрый день! 👋\n'
                                                    f'Мы переходим на новые, более быстрые, сервера, а от старых будем отказываться.\n'
                                                    f'14 февраля ключ c id <b>{key}</b> перестанет работать, пожалуйста замените его:',
                                               reply_markup=add_device_pc)
                        await user.update(promo='change').apply()
                if key in xray_key_for_del:
                    if user.promo == 'change':
                        await bot.send_message(chat_id=user.user_id,
                                               text=f'14 февраля ключ c id <b>{key}</b> перестанет работать, пожалуйста замените его:',
                                               reply_markup=add_device_phone)
                    else:
                        user_get += 1
                        await bot.send_message(chat_id=user.user_id,
                                               text=f'{user.name}, добрый день! 👋\n'
                                                    f'Мы переходим на новые, более быстрые, сервера, а от старых будем отказываться.\n'
                                                    f'14 февраля ключ c id <b>{key}</b> перестанет работать, пожалуйста замените его:',
                                               reply_markup=add_device_phone)
                        await user.update(promo='change').apply()
        except Exception as err:
            user_block += 1
            await user.update(promo='blocked_clean').apply()
    await bot.send_message(chat_id=message.chat.id, text=f'Пользователей получило: {user_get}\n'
                                                         f'Пользователей заблокировало: {user_block}')


@router.message(IsAdmin(), Command(commands='info_del'))
async def process_user_clean_key(message: Message, bot: Bot):
    wg_key_for_del, xray_key_for_del = await search_key_for_del()
    await bot.send_message(chat_id=message.chat.id, text=f'Количество ключей для удаления wg: {len(wg_key_for_del)}\n'
                                                         f'Количество ключей для удаления xray: {len(xray_key_for_del)}\n')


# Проверка количества ключей и пользовталелей и общего значения
@router.message(IsAdmin(), Command(commands='number_of_keys_users_have'))
async def process_number_of_keys_users_have(message: Message, bot: Bot):
    number_of_keys_users_have = []
    users = await select_all_users()
    for user in users:
        if user.file_id:
            for file_id in user.file_id:
                number_of_keys_users_have.append(file_id)
    print(len(number_of_keys_users_have))

