import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode

TOKEN = "7576891927:AAFG_PZfzyV93lOtjLTmOPfludJGZmkrmZI"

day_steps = [
    "Прими утренние БАДы",
    "Позавтракай",
    "Прогулка 15 минут",
    "Прими душ",
    "Медитация, чтение, визуализация",
    "Работа",
    "Второй завтрак",
    "Тренажерный зал (прими L-карнитин перед этим)",
    "Работа",
    "Полдник",
    "Работа",
    "Ужин (можно напомнить о вечерних БАДах)",
    "Работа",
    "Душ перед сном",
    "Сон"
]

bot = Bot(TOKEN)
dp = Dispatcher()
user_steps = {}
logging.basicConfig(level=logging.INFO)

start_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Я проснулся")]
], resize_keyboard=True)

action_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Сделал")]
], resize_keyboard=True)

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привет! Нажми 'Я проснулся', чтобы начать день!", reply_markup=start_kb)

@dp.message(lambda message: message.text == "Я проснулся")
async def wake_up(message: types.Message):
    user_steps[message.from_user.id] = 0
    await send_next_step(message.from_user.id)

async def send_next_step(user_id):
    if user_id not in user_steps:
        return
    step = user_steps[user_id]
    if step < len(day_steps):
        await bot.send_message(user_id, f"Следующее задание: *{day_steps[step]}*", parse_mode=ParseMode.MARKDOWN, reply_markup=action_kb)
        asyncio.create_task(reminder_loop(user_id, step))
    else:
        await bot.send_message(user_id, "Красавчик, отдыхай (:", reply_markup=start_kb)
        del user_steps[user_id]

@dp.message(lambda message: message.text == "Сделал")
async def completed_step(message: types.Message):
    if message.from_user.id in user_steps:
        user_steps[message.from_user.id] += 1
        await send_next_step(message.from_user.id)

async def reminder_loop(user_id, step):
    for _ in range(4):
        await asyncio.sleep(900)  # 15 минут
        if user_steps.get(user_id) == step:
            await bot.send_message(user_id, f"Напоминание! Ты ещё не сделал: *{day_steps[step]}*", parse_mode=ParseMode.MARKDOWN, reply_markup=action_kb)
        else:
            break

async def main():
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
