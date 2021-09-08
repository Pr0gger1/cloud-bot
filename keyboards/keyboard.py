from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

keyboard_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

search_for_tags_btn = KeyboardButton('По тегам 🔗')
search_for_name = KeyboardButton('По заголовку 🏷')

keyboard_markup.add(search_for_tags_btn, search_for_name)