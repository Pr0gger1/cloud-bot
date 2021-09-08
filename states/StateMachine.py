from aiogram.dispatcher.filters.state import StatesGroup, State


class Form(StatesGroup):
    Link = State()
    Title = State()
    Tags = State()
    Data_question = State()
    Search_data_name = State()
    Search_data_tags = State()
