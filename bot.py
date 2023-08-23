from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.types.input_file import InputFile
import sqlite3 as sql
import random

from config import TOKEN, ADMIN_ID, BOT_NAME
from db import database

admin_kb = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Добавить айди", callback_data="add_id"),
    InlineKeyboardButton("Изменить баланс", callback_data="change_balance"),
    InlineKeyboardButton("Посмотреть баланс", callback_data="view_balance"),
    InlineKeyboardButton("Просмотреть реферелов", callback_data="ref_view")
)

class photo_do_state(StatesGroup):
    user = State()
    time_delta = State()

class ref_view(StatesGroup):
    user_id = State()

class view_balance(StatesGroup):
    chat_id = State()

class add_user(StatesGroup):
    user_id = State()
    name = State()

class change_balance(StatesGroup):
    sub_id_10 = State()
    new_balance = State()

class out_cash(StatesGroup):
    typpe = State()
    amount = State()
    usdt_wallet = State()

#Модель бота и клас диспетчер
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())
db = database()
data = {}
data_2 = {}

def extract_chat_id_from_link(text): #Ну типа достаёт чат айди реферала из старт ссылки (Я спиздил этот код на стек офер флоу, если не рабоатет не ебу)
    return text.split()[1] if len(text.split()) > 1 else None

@dp.message_handler(commands=["start", "старт"], state="*")
async def start_command(message : types.Message):
    global data
    up_ref_id = extract_chat_id_from_link(message.text)
    if up_ref_id:
        await message.delete()
        print(db.update_ref_balance(message.from_user.id, up_ref_id))
        db_request = db.select_user(message.from_user.id)
        if db_request["status"]:
            data[message.chat.id] = {}
            balance = db.select_balance(message.chat.id)
            data[message.chat.id]["user"] = db_request["name"]
            kb = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("Сутки", callback_data="1"),
                InlineKeyboardButton("7 дней", callback_data="7"),
                InlineKeyboardButton("30 дней", callback_data="30"),
                InlineKeyboardButton("Вывод средств", callback_data="cash_out"),
                InlineKeyboardButton("Реферальная ссылка", callback_data="ref_link")
            )
            await bot.send_message(message.chat.id, f"""Твой баланс: {balance['data']}
Твой реферальный баланс: {balance['ref_balance']}

Выбери время для просмотра статистики: """, reply_markup=kb)
            await photo_do_state.time_delta.set()
        else: await bot.send_message(message.from_user.id, db_request['text'])
    else:
        await message.delete()
        db_request = db.select_user(message.from_user.id)
        if db_request["status"]:
            data[message.chat.id] = {}
            balance = db.select_balance(message.chat.id)
            data[message.chat.id]["user"] = db_request["name"]
            kb = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("Сутки", callback_data="1"),
                InlineKeyboardButton("7 дней", callback_data="7"),
                InlineKeyboardButton("30 дней", callback_data="30"),
                InlineKeyboardButton("Вывод средств", callback_data="cash_out"),
                InlineKeyboardButton("Реферальная ссылка", callback_data="ref_link")
            )
            await bot.send_message(message.chat.id, f"""Твой баланс: {balance['data']}$
Твой реферальный баланс: {balance['ref_balance']}$

Выбери время для просмотра статистики: """, reply_markup=kb)
            await photo_do_state.time_delta.set()
        else: await bot.send_message(message.from_user.id, db_request['text'])
    
@dp.message_handler(commands=["id"])
async def id_command(message : types.Message):
    await message.reply(message.from_user.id)

@dp.message_handler(commands=["admin"], state="*")
async def id_command(message : types.Message, state : FSMContext):
    for id in ADMIN_ID:
        if str(message.from_user.id) == id:
            print(id, " | ", message.from_user.id, "✅")
            await state.finish()
            await bot.send_message(message.from_user.id, "Привет, выбери функции ниже", reply_markup=admin_kb)
        else: print(id, " | ", message.from_user.id, "⛔️")
    
@dp.message_handler(state=photo_do_state.user)
async def start_command(message : types.Message):
    global data
    data[message.chat.id] = {}
    data[message.chat.id]["user"] = message.text
    kb = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("Сутки", callback_data="1"),
            InlineKeyboardButton("7 дней", callback_data="7"),
            InlineKeyboardButton("30 дней", callback_data="30"),
            InlineKeyboardButton("Вывод средств", callback_data="cash_out")
    )
    await bot.send_message(message.chat.id, "Выбери время для просмотра статистики: ", reply_markup=kb)
    await photo_do_state.time_delta.set()
    
@dp.callback_query_handler(state=photo_do_state.time_delta)
async def process_buy_command(callback_query: types.CallbackQuery, state : FSMContext):
    if callback_query.data != "cash_out" and callback_query.data != "ref_link":
        kb = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("Сутки", callback_data="1"),
                InlineKeyboardButton("7 дней", callback_data="7"),
                InlineKeyboardButton("30 дней", callback_data="30"),
                InlineKeyboardButton("Вывод средств", callback_data="cash_out")
        )
        global data
        data[callback_query.from_user.id]["time_delta"] = callback_query.data
        db_request = db.select_request(data[callback_query.from_user.id]["user"], int(data[callback_query.from_user.id]["time_delta"]))
        try:
            await callback_query.message.edit_text(db_request['text'], reply_markup=kb)
        except:
            await bot.send_message(callback_query.from_user.id, db_request['text'], reply_markup=kb)
    if callback_query.data == "cash_out":
        db_ansver = db.select_balance(callback_query.from_user.id)
        if db_ansver['status']:
            await bot.send_message(callback_query.from_user.id, "Введите сумму для вывода, не больше чем есть у вас на балансе")
            await bot.send_message(callback_query.from_user.id, f"На вашем балансе {db_ansver['data']}, на вашем реферальном балансе {db_ansver['ref_balance']}")
            await out_cash.amount.set()
        else: 
            await bot.send_message(callback_query.from_user.id, db_ansver['text'])
            await bot.send_message(callback_query.from_user.id, "Напишите /start")
            await state.finish()
    elif callback_query.data == "ref_link":
        kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Меню", callback_data="m"))
        await state.finish()
        await bot.send_message(callback_query.from_user.id, f"Твоя реферальная ссылка: http://t.me/{BOT_NAME}?start={callback_query.from_user.id}", reply_markup=kb)

amount_data = {}

@dp.message_handler(state=out_cash.amount)
async def start_command(message : types.Message, state : FSMContext):
    global amount_data
    db_ansver = db.select_balance(message.from_user.id)
    if db_ansver['status']:
        try:
            if int(db_ansver['data']) >= int(message.text):
                amount_data[message.from_user.id] = message.text
                await bot.send_message(message.from_user.id, "Введите совой usdt адресс:")
                await out_cash.usdt_wallet.set()
            else:
                await bot.send_message(message.from_user.id, "Введите сумму которая есть у вас на балансе!")
                await bot.send_message(message.from_user.id, f"На вашем балансе {db_ansver['data']}")
        except TypeError:
            await bot.send_message(message.from_user.id, "Введите значение числом")
    else: 
        await bot.send_message(message.from_user.id, "Произошла ошибка, повторите попытку позже!")
        await state.finish()

@dp.message_handler(state=out_cash.usdt_wallet)
async def start_command(message : types.Message, state : FSMContext):
    global amount_data
    await bot.send_message(message.from_user.id, "Запрос на вывод успешно отправлен!")
    for chat_id in ADMIN_ID:
        try:
            await bot.send_message(chat_id, f"""Запрос на вывод средств
                                
sub_id_10 = {db.select_user(message.from_user.id)['name']}

кошелёк = {message.text}

сумма = {amount_data[message.from_user.id]}""")
        except: pass
        
    db_request = db.select_user(message.from_user.id)
    if db_request["status"]:
        global data
        data[message.from_user.id] = {}
        data[message.from_user.id]["user"] = db_request["name"]
        kb = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("Сутки", callback_data="1"),
            InlineKeyboardButton("7 дней", callback_data="7"),
            InlineKeyboardButton("30 дней", callback_data="30"),
            InlineKeyboardButton("Вывод средств", callback_data="cash_out")
        )
        await bot.send_message(message.from_user.id, "Выбери время для просмотра статистики: ", reply_markup=kb)
        await photo_do_state.time_delta.set()


@dp.message_handler(commands=["admin"])
async def start_command(message : types.Message):
    for id in ADMIN_ID:
        if str(message.from_user.id) == id:
            print(id, " | ", message.from_user.id, "✅")
            await bot.send_message(message.from_user.id, "Привет, выбери функции ниже", reply_markup=admin_kb)
        else: print(id, " | ", message.from_user.id, "⛔️")

sub_id_10_for_out = ""

@dp.callback_query_handler(text="change_balance")
async def process_buy_command(callback_query: types.CallbackQuery): 
    await bot.send_message(callback_query.from_user.id, "Отправьте sub_id_10: ")
    await change_balance.sub_id_10.set()

@dp.message_handler(state=change_balance.sub_id_10)
async def start_command(message : types.Message):
    global sub_id_10_for_out
    sub_id_10_for_out = message.text
    await bot.send_message(message.from_user.id, "Введите новый баланс пользователя цифрой: ")
    await change_balance.new_balance.set()

@dp.message_handler(state=change_balance.new_balance)
async def start_command(message : types.Message, state : FSMContext):
    global sub_id_10_for_out

    db_ansver = db.update_revenue(message.text, sub_id_10_for_out)
    if db_ansver['status']: await bot.send_message(message.from_user.id, "Баланс успешно изменён")
    else: await bot.send_message(message.from_user.id, db_ansver['text'])
    await state.finish()

@dp.callback_query_handler(text="add_id")
async def process_buy_command(callback_query: types.CallbackQuery): 
    await bot.send_message(callback_query.from_user.id, "Введи тг айди пользователя, например 687899499")
    await add_user.user_id.set()
    
@dp.message_handler(state=add_user.user_id)
async def start_command(message : types.Message):
    global data
    data[message.chat.id] = {}
    data[message.chat.id]["user_id"] = message.text
    await bot.send_message(message.chat.id, "Введи имя пользователя в конверсии")
    await add_user.name.set()

@dp.message_handler(state=add_user.name)
async def start_command(message : types.Message, state : FSMContext):
    await state.finish()
    if db.create_user(data[message.chat.id]["user_id"], message.text)['status']:
        await bot.send_message(message.chat.id, "Данные приняты!")
    
@dp.callback_query_handler(text="view_balance")
async def process_buy_command(callback_query: types.CallbackQuery): 
    await bot.send_message(callback_query.from_user.id, "Введите тг айди того, чей баланс хотите посмотреть")
    await view_balance.chat_id.set()

@dp.message_handler(state=view_balance.chat_id)
async def start_command(message : types.Message, state : FSMContext):
    db_ansver = db.select_balance(message.text)
    if db_ansver['status']: await message.reply(f"На балансе: {db_ansver['data']}", reply_markup=admin_kb)
    else: await message.reply(db_ansver['text'], reply_markup=admin_kb)
    await state.finish()

@dp.callback_query_handler(text="ref_view")
async def process_buy_command(callback_query: types.CallbackQuery): 
    await bot.send_message(callback_query.from_user.id, "Введите тг айди того, чей реферал хотите посмотреть")
    await ref_view.user_id.set()

@dp.message_handler(state=ref_view.user_id)
async def start_command(message : types.Message, state : FSMContext):
    ansv = db.select_refs(message.text)
    if len(ansv['data']) > 0:
        await bot.send_message(message.from_user.id, f"""Рефералы {message.text}: {ansv['data']}""", reply_markup=admin_kb)
    else: await bot.send_message(message.from_user.id, f"""Рефералы {message.text} отсутствуют""", reply_markup=admin_kb)
    await state.finish()

@dp.callback_query_handler()
async def process_buy_command(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    db_request = db.select_user(callback_query.message.from_user.id)
    if db_request["status"]:
        global data
        data[callback_query.message.chat.id] = {}
        data[callback_query.message.chat.id]["user"] = db_request["name"]
        kb = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("Сутки", callback_data="1"),
            InlineKeyboardButton("7 дней", callback_data="7"),
            InlineKeyboardButton("30 дней", callback_data="30")
        )
        await bot.send_message(callback_query.message.chat.id, "Выбери время для просмотра статистики: ", reply_markup=kb)
        await photo_do_state.time_delta.set()
    else: await bot.send_message(callback_query.message.from_user.id, db_request['text'])
#Функция которая запускается со стартом бота
async def on_startup(_):
    print('bot online')
#Пулинг бота
executor.start_polling(dp,skip_updates=True, on_startup=on_startup) #Пуллинг бота

#Вывод уведомления про отключение бота
print("Bot offline")
#                               