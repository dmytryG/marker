import logging

import aiomysql
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

import database
from loader import dp, database_con, loop
from states.test import BotState

## await state.reset_state()

@dp.message_handler(Command("help"))
async def show_help(message: types.Message):
    await message.answer("Привет! \n\n"
                         "Это бот-дневник, в нем ты сможешь отмечать как прошел твой день "
                         "или насколько продуктивно ты сегодня учился, а потом смотреть свою статистику "
                         "и делиться ей с дригими! Не переживай, что пропустишь день, вечером я напомню "
                         "о себе! \n"
                         "Что бы начать использовать бот, добавь метрику коммандой /add\n"
                         "Ты можешь удалить метрику командой /delete\n"
                         "Или можешь посмотреть свою статистику /show")

@dp.message_handler(Command("start"), state=None)
async def say_hello(message: types.Message):

    try:
        await database.add_user(message.from_user.id, message.from_user.username, loop)
        await show_help(message)
    except aiomysql.Error:
        await message.answer("Привет! \n\n"
                             "Похоже, мы уже знакомы!"
                             "\nВведи /help что бы ознакомится со списком доступных комманд")
    except:
        await message.answer("Привет! \n\n"
                             "Извини, похоже, наши сервера сейчас на обслуживании. Пожалуйста, "
                             "повтори попытку позже")



@dp.message_handler(Command("add"))
async def add_metric(message: types.Message):
    await message.answer("Как будет называться новая метрика?")
    await BotState.AddMetric.set()

@dp.message_handler(state=BotState.AddMetric)
async def submit_metric(message: types.Message, state: FSMContext):
    answer = message.text
    try:
        await database.add_metric(message.from_user.id, answer, loop)
        await message.answer("Отлично! Метрика " + answer + " добавлена!")
        await state.reset_state()
    except:
        await message.answer("Привет! \n\n"
                             "Извини, похоже, произошла оишбка. Пожалуйста, "
                             "повтори попытку позже")

@dp.message_handler(Command("delete"))
async def delete_metric(message: types.Message):
    try:
        metrics = await database.get_metrics(message.from_user.id, loop)
        for metric in metrics:
            logging.info(metric)
        await message.answer("Какая метрика будет удалена?")
        await BotState.DeleteMetric.set()
    except:
        await message.answer("Привет! \n\n"
                             "Извини, похоже, произошла оишбка. Пожалуйста, "
                             "повтори попытку позже")