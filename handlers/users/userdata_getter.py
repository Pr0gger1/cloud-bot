from typing import Text
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from loader import dp
from aiogram.utils import markdown as mkn
from data.database import Database
from states.StateMachine import Form
from keyboards.keyboard import keyboard_markup
import validators
import json



db = Database('database.db')

#Обработчик команды /start -- приветсвенное сообщение
@dp.message_handler(commands='start')
async def welcome_msg(message: types.Message):
    await message.answer("Привет, меня зовут Марти))\nЯ твой личный помощник по коллекционированию полезных статей из Телеграмма." 
    + "\nДля сохранения понравившейся статьи, введи команду /add")

#Обработчик отмены команды
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    
    await state.finish()
    await message.answer('Да, хозяин, выхожу из команды', reply_markup=types.ReplyKeyboardRemove())

#Обработчик команды /add -- механизм сохранения ссылок
@dp.message_handler(commands='add', state=None)
async def enter_link(message: types.Message):
    await message.answer("Отправьте мне ссылку на статью...")
    await Form.Link.set()

#Сохранение пользовательского ресурса в машину состояний
@dp.message_handler(state=Form.Link)
async def get_link(message: types.Message, state: FSMContext):
    user_link = message.text

    if validators.url(user_link) or validators.domain(user_link):
        await state.update_data(link = user_link)

        #Переход кследующей машине состояинй
        await message.answer("Задайте заголовок для записи")
        await Form.Title.set()
    else:
        await message.answer("Это не url-адрес!")

#Сохранение заголовка ресурса в машину состояний
@dp.message_handler(state=Form.Title)
async def get_title(message: types.Message, state: FSMContext):
    user_title = message.text

    await state.update_data(title = user_title)
    await message.answer('Окей, а теперь задайте теги для записи')

    await Form.Tags.set()

#Сохранение тегов ресурса в машину состояний, сохранение всей информации о ресурсе в базу данных
@dp.message_handler(state=Form.Tags)
async def get_tags(message: types.Message, state: FSMContext):
    user_tags = message.text.lower()
    await state.update_data(tags = user_tags)

    data = await state.get_data()

    link = data.get('link')
    title = data.get('title')
    tags = json.dumps(data.get('tags').replace(" ", "").split(','))

    user_id = message.from_user.id

    try:
        db.add_user_data(user_id, title, link, tags)
        await message.answer('Данные о ресурсе успешно сохранены')

    except Exception as e:
        await message.answer(f"Такая ссылка уже есть в базе данных\n{e}")

    await Form.Link.set()

#Обработчик команды /search_data
@dp.message_handler(commands='search_data', state=None)
async def get_data_cmd(message: types.Message):
    await message.answer('По каким данным вы хотите искать ресурс', reply_markup=keyboard_markup)
    await Form.Data_question.set()

@dp.message_handler(state=Form.Data_question)
async def get_data_q(message: types.Message):
    answer = message.text

    if answer == 'По тегам 🔗':
        await message.answer('Напишите через запятую теги ресурса')
        await Form.Search_data_tags.set()

    elif answer == 'По заголовку 🏷':
        await message.answer('Напишите заголовок ресурса')
        await Form.Search_data_name.set()
    else:
        await message.reply('Извините, но я не понимаю этой команды')

#Механизм поиска ресурса по тегам
@dp.message_handler(state=Form.Search_data_tags)
async def get_data_for_tags(message: types.Message, state: FSMContext):
    tags = message.text.replace(' ', '').split(',')
    user_id = message.from_user.id

    query = db.search_link_for_tags(user_id)
    for data in query:
        title, link, db_tags = data[0], data[1], json.loads(data[-1])

        for tag in tags:
            if tag in json.loads(data[-1]):
                await message.answer(
                    mkn.text(
                        mkn.text('🔗' + mkn.hbold('Ресурс: '), link),
                        mkn.text('🏷' + mkn.hbold('Заголовок: '), title),
                        mkn.text('📌' + mkn.hbold('Теги: '), db_tags),
                        sep='\n'
            )
                )#f"Заголовок: {data[0]}\nРесурс: {data[1]}")
    await Form.Search_data_tags.set()

#Механизм поиска ресурса по заголовку
@dp.message_handler(state=Form.Search_data_name)
async def get_data_for_name(message: types.Message, state: FSMContext):
    name = message.text
    result = db.search_link_for_name(user_id=message.from_user.id, name=name)
    for data in result:
        link, title, tags = data[0], data[1], json.loads(data[-1])

        await message.answer('Вот что я смог найти')
        await message.answer(
            mkn.text(
                mkn.text('🔗' + mkn.hbold('Ресурс: '), link),
                mkn.text('🏷' + mkn.hbold('Заголовок: '), title),
                mkn.text('📌' + mkn.hbold('Теги: '), tags),
                sep='\n'
            )
        )
    await Form.Search_data_name.set()

#Тестовая функция
@dp.message_handler(commands='alldata')
async def get_all_data(message: types.Message):
    user_id = message.from_user.id
    query = db.user_query(f"SELECT * FROM '{user_id}'")

    for el in query:
        result = [el[0],el[1], json.loads(el[-1])]
        await message.answer(result)


