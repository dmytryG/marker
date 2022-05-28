from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from loader import dp
from states.test import BotState

## await state.reset_state()

@dp.message_handler(Command("start"), state=None)
async def say_hello(message: types.Message):
    await message.answer("Привет! \n\n"
                         "Это бот-дневник, в нем ты сможешь отмечать как прошел твой день "
                         "или насколько продуктивно ты сегодня учился, а потом смотреть свою статистику "
                         "и делиться ей с дригими! Не переживай, что пропустишь день, вечером я напомню "
                         "о себе! \n"
                         "Что бы начать использовать бот, добавь метрику коммандой /add\n"
                         "Ты можешь удалить метрику командой /delete\n"
                         "Или можешь посмотреть свою статистику /show")

@dp.message_handler(Command("add"))
async def enter_test(message: types.Message):
    await message.answer("Как будет называться новая метрика?")
    await BotState.AddMetric.set()

@dp.message_handler(state=BotState.AddMetric)
async def enter_test(message: types.Message, state: FSMContext):
    answer = message.text
    await message.answer("Отлично! Метрика " + answer + " добавлена!")
    await state.reset_state()
