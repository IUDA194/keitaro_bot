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

from config import TOKEN, ADMIN_ID
from db import database

admin_kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Добавить айди", callback_data="add_id"))

class photo_do_state(StatesGroup):
    user = State()
    time_delta = State()


class add_user(StatesGroup):
    user_id = State()
    name = State()

#Модель бота и клас диспетчер
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())
db = database()
data = {}
data_2 = {}

@dp.message_handler(commands=["start", "старт"])
async def start_command(message : types.Message):
    await message.delete()
    db_request = db.select_user(message.from_user.id)
    if db_request["status"]:
        global data
        data[message.chat.id] = {}
        data[message.chat.id]["user"] = db_request["name"]
        kb = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("Сутки", callback_data="1"),
            InlineKeyboardButton("7 дней", callback_data="7"),
            InlineKeyboardButton("30 дней", callback_data="30")
        )
        await bot.send_message(message.chat.id, "Выбери время для просмотра статистики: ", reply_markup=kb)
        await photo_do_state.time_delta.set()
    else: await bot.send_message(message.from_user.id, db_request['text'])
    
@dp.message_handler(commands=["id"])
async def id_command(message : types.Message):
    await message.reply(message.from_user.id)
    
@dp.message_handler(state=photo_do_state.user)
async def start_command(message : types.Message):
    global data
    data[message.chat.id] = {}
    data[message.chat.id]["user"] = message.text
    kb = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("Сутки", callback_data="1"),
        InlineKeyboardButton("7 дней", callback_data="7"),
        InlineKeyboardButton("30 дней", callback_data="30")
    )
    await bot.send_message(message.chat.id, "Выбери время для просмотра статистики: ", reply_markup=kb)
    await photo_do_state.time_delta.set()
    
@dp.callback_query_handler(state=photo_do_state.time_delta)
async def process_buy_command(callback_query: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("Обновить за сутки", callback_data="1"),
        InlineKeyboardButton("Обновить за 7 дней", callback_data="7"),
        InlineKeyboardButton("Обновить за 30 дней", callback_data="30")
    )
    global data
    data[callback_query.from_user.id]["time_delta"] = callback_query.data
    db_request = db.select_request(data[callback_query.from_user.id]["user"], int(data[callback_query.from_user.id]["time_delta"]))
    try:
        await callback_query.message.edit_text(db_request['text'], reply_markup=kb)
    except:
        await bot.send_message(callback_query.from_user.id, db_request['text'], reply_markup=kb)

@dp.message_handler(commands=["admin"])
async def start_command(message : types.Message):
    for id in ADMIN_ID:
        if str(message.from_user.id) == id:
            print(id, " | ", message.from_user.id, "✅")
            await bot.send_message(message.from_user.id, "Привет, выбери функции ниже", reply_markup=admin_kb)
        else: print(id, " | ", message.from_user.id, "⛔️")

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