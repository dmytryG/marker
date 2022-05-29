import asyncio
import logging
import threading

import aioschedule
import schedule
import time

import aiomysql
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

import config
import database
import keyboards
from loader import dp, database_con, loop, bot
from states.test import BotState
from keyboards import select_metric_callback



@dp.message_handler(Command("help"))
async def show_help(message: types.Message):
    await message.answer("Привет! \n\n"
                         "Это бот-дневник, в нем ты сможешь отмечать как прошел твой день "
                         "или насколько продуктивно ты сегодня учился, а потом смотреть свою статистику "
                         "и делиться ей с дригими! Не переживай, что пропустишь день, вечером я напомню "
                         "о себе! \n"
                         "Что бы начать использовать бот, добавь метрику коммандой /add\n"
                         "Ты можешь удалить метрику командой /delete\n"
                         "Командой /metrics можно оценить метрику в любой момент времени\n"
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
        await message.answer("Какая метрика будет удалена?",
                             reply_markup = keyboards.select_metric(metrics))
        await BotState.DeleteMetric.set()
    except:
        await message.answer("Привет! \n\n"
                             "Извини, похоже, произошла оишбка. Пожалуйста, "
                             "повтори попытку позже")

@dp.callback_query_handler(select_metric_callback.filter(), state=BotState.DeleteMetric, text_contains = "select_metric")
async def submit_delete_metric(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    try:
        await call.answer(cache_time=1)
        logging.info("Got callback " + str(callback_data))
        if callback_data["action"] == "none":
            await database.delete_metric(callback_data["id"], loop)
            await call.message.answer("Метрика была успешно удалена")
        if callback_data["action"] == "cancel":
            await call.message.answer("Оки доки, отменяю")
    except:
        await call.message.answer("Привет! \n\n"
                             "Извини, похоже, произошла оишбка. Пожалуйста, "
                             "повтори попытку позже")
    try:
        await state.reset_state()
    except:
        logging.warn("Internal error, can't drom FSM")


@dp.message_handler(Command("metrics"))
async def get_metrics_deprecated(message: types.Message):
    all_metrics = await database.get_users(loop)
    for user_id in all_metrics.keys(): #Для каждого пользователя
        for metric in all_metrics[user_id]: # Для каждой метрики
            await bot.send_message(chat_id=user_id, text="Оцени " + metric.name + " по шкале от 1 до 5",
                                   reply_markup=keyboards.rate_metric(metric))

@dp.callback_query_handler(keyboards.rate_metric_callback.filter(), text_contains ="rate_metric")
async def rate_metric(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    try:
        await call.answer(cache_time=1)
        logging.info("Got callback " + str(callback_data))
        logging.info("Set rating for metric " + callback_data["id"] + " as " + callback_data["rating"])
        await database.rate_metric(callback_data["id"], callback_data["rating"], loop)
        # send callback (callback_data["id"], callback_data["rating"])
    except:
        await call.message.answer("Привет! \n\n"
                             "Извини, похоже, произошла оишбка. Пожалуйста, "
                             "повтори попытку позже")

@dp.message_handler(Command("metrics"))
async def get_metrics_for_each_user():
    all_metrics = await database.get_users(loop)
    for user_id in all_metrics.keys(): #Для каждого пользователя
        for metric in all_metrics[user_id]: # Для каждой метрики
            await bot.send_message(chat_id=user_id, text="Оцени " + metric.name + " по шкале от 1 до 5",
                                   reply_markup=keyboards.rate_metric(metric))

@dp.message_handler(Command("show"))
async def show_statistic(message: types.Message):
    try:
        metrics = await database.get_metrics(message.from_user.id, loop)
        cnt = await database.get_contributions(message.from_user.id, loop)
        await message.answer("Приветик! Ты сделал уже " + str(cnt) + " отметок! Поздравляю! Ты можешь просмотреть "
                                                                "подробную статистику, выбрав интересующую тебя "
                                                                "метрику",
                             reply_markup = keyboards.select_metric(metrics))
        await BotState.ShowMetric.set()
    except:
        await message.answer("Привет! \n\n"
                             "Извини, похоже, произошла оишбка. Пожалуйста, "
                             "повтори попытку позже")

@dp.callback_query_handler(select_metric_callback.filter(), state=BotState.ShowMetric, text_contains = "select_metric")
async def submit_show_metric_statistic(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    try:
        await call.answer(cache_time=1)
        logging.info("Got callback " + str(callback_data))
        if callback_data["action"] == "none":
            #Сгенерировать статистику по метрикам
            pass
        if callback_data["action"] == "cancel":
            await call.message.answer("Оки доки, отменяю")
    except:
        await call.message.answer("Привет! \n\n"
                             "Извини, похоже, произошла оишбка. Пожалуйста, "
                             "повтори попытку позже")
    try:
        await state.reset_state()
    except:
        logging.warn("Internal error, can't drom FSM")


async def noon_print():
    await get_metrics_for_each_user()

async def scheduler():
    aioschedule.every().day.at(config.NOON_METRICS_ALERT).do(noon_print)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    asyncio.create_task(scheduler())