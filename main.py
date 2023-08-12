from flask import Flask, request
import asyncio
from aiogram import Bot, Dispatcher, types
from db import database as db

from config import TOKEN, INFO_CHAT_ID

app = Flask(__name__)
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)
database = db()
loop = asyncio.get_event_loop()  # Получаем цикл событий asyncio

@app.route('/', methods=['GET'])
def info():
    #data = request.get_json()
    sub_id_10 = request.args.get('sub_id_10')
    sub_id_11 = request.args.get('sub_id_11')
    sub_id_12 = request.args.get('sub_id_12')
    sub_id_13 = request.args.get('sub_id_13')
    sub_id_14 = request.args.get('sub_id_14')
    sub_id_15 = request.args.get('sub_id_15')
    subid = request.args.get('subid')
    status = request.args.get("status")
    revenue = request.args.get("revenue")
    for id in INFO_CHAT_ID:
        if id:
            database.create_request(sub_id_10,
                        sub_id_11,
                        sub_id_12,
                        sub_id_13,
                        sub_id_14,
                        sub_id_15,
                        subid,
                        status,
                        revenue)
            async def send():
                await bot.send_message(id, f"""<b>Пользователь</b> : {sub_id_10}
    <b>ID конверсии</b> : {subid}
    <b>ID оффера</b> : {sub_id_11}
    <b>ID страны</b> : {sub_id_12}
    <b>Пиксель</b> : {sub_id_13}
    <b>Креатив</b> : {sub_id_14}
    <b>Рекламный кабинет</b> : {sub_id_15}
    <b>Статус конверсии</b> : {status}
    <b>Профит</b> : {revenue}""")

            loop.run_until_complete(send())  # Используем цикл событий для выполнения асинхронной функции
            return 'Message sent successfully'
        else:
            return 'Invalid request data'
    
@app.route('/send_message', methods=['GET'])
def send_message():
    #data = request.get_json()
    text = request.args.get('text')
    chat_id = "687899499"

    if chat_id and text:
        async def send():
            await bot.send_message("687899499", text)

        loop.run_until_complete(send())  # Используем цикл событий для выполнения асинхронной функции
        return 'Message sent successfully'
    else:
        return 'Invalid request data'

if __name__ == '__main__':
    app.run()#host='213.166.71.72', port=5000)
