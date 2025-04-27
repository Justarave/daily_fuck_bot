import logging
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode

TOKEN = "7576891927:AAFG_PZfzyV93lOtjLTmOPfludJGZmkrmZI"

# Список действий на день
day_steps = [
    "Прими утренние БАДы",
    "Позавтракай",
    "Прогулка 15 минут",
    "Прими душ",
    "Медитация, чтение, визуализация",
    "Работа",
    "Второй завтрак",
    "Тренажерный зал (если нужно)",
    "Работа",
    "Полдник",
    "Работа",
    "Ужин (и вечерние БАДы)",
    "Работа",
    "Душ перед сном",
    "Сон"
]

# Прогресс пользователя
user_steps = {}
progress = {}
training_progress = {}

bot = Bot(TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# Клавиатуры
start_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Я проснулся")]
], resize_keyboard=True)

action_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Сделал"), KeyboardButton(text="Пропустил")]
], resize_keyboard=True)

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привет! Нажми 'Я проснулся', чтобы начать день!", reply_markup=start_kb)

@dp.message(lambda message: message.text == "Я проснулся")
async def wake_up(message: types.Message):
    user_steps[message.from_user.id] = 0
    progress[message.from_user.id] = {"done": 0, "skipped": 0}
    await check_new_week(message.from_user.id)
    await morning_motivation(message.from_user.id)
    await send_next_step(message.from_user.id)

async def send_next_step(user_id):
    if user_id not in user_steps:
        return
    step = user_steps[user_id]
    if step < len(day_steps):
        await bot.send_message(user_id, f"Следующее задание: *{day_steps[step]}*", parse_mode=ParseMode.MARKDOWN, reply_markup=action_kb)
        asyncio.create_task(reminder_loop(user_id, step))
    else:
        await show_day_summary(user_id)
        await bot.send_message(user_id, "Красавчик, отдыхай (: ", reply_markup=start_kb)
        del user_steps[user_id]

@dp.message(lambda message: message.text in ["Сделал", "Пропустил"])
async def completed_step(message: types.Message):
    if message.from_user.id in user_steps:
        if message.text == "Сделал":
            progress[message.from_user.id]["done"] += 1
            # Если этап тренажёрка
            if "Тренажерный зал" in day_steps[user_steps[message.from_user.id]]:
                await increment_training(message.from_user.id)
        else:
            progress[message.from_user.id]["skipped"] += 1
        user_steps[message.from_user.id] += 1
        await send_next_step(message.from_user.id)

async def reminder_loop(user_id, step):
    for _ in range(4):
        await asyncio.sleep(900)  # 15 минут
        if user_steps.get(user_id) == step:
            await bot.send_message(user_id, f"Напоминание! Ты ещё не сделал: *{day_steps[step]}*", parse_mode=ParseMode.MARKDOWN, reply_markup=action_kb)
        else:
            break

async def show_day_summary(user_id):
    done = progress.get(user_id, {}).get("done", 0)
    skipped = progress.get(user_id, {}).get("skipped", 0)
    total = done + skipped
    percent = (done / total) * 100 if total > 0 else 0
    await bot.send_message(user_id, f"*Итоги дня:*\nСделано: {done}\nПропущено: {skipped}\nЭффективность: {percent:.0f}%", parse_mode=ParseMode.MARKDOWN)

async def increment_training(user_id):
    today = datetime.now()
    week = today.isocalendar().week
    if user_id not in training_progress or training_progress[user_id]["week"] != week:
        training_progress[user_id] = {"week": week, "done": 0}
    training_progress[user_id]["done"] += 1

@dp.message(Command("статус"))
async def training_status(message: types.Message):
    user_id = message.from_user.id
    today = datetime.now()
    week = today.isocalendar().week
    if user_id not in training_progress or training_progress[user_id]["week"] != week:
        training_progress[user_id] = {"week": week, "done": 0}
    done = training_progress[user_id]["done"]
    if done >= 3:
        await message.answer("Красавчик :3")
    else:
        await message.answer(f"Ещё чутка, заебал )\nСделано тренировок: {done}/3")

async def morning_motivation(user_id):
    today = datetime.now()
    if today.weekday() == 0:  # Понедельник
        await bot.send_message(user_id, "Эта неделя должна быть лучше предыдущей! Ебашь, скоро 26 :с")

async def check_new_week(user_id):
    today = datetime.now()
    week = today.isocalendar().week
    if user_id not in training_progress or training_progress[user_id]["week"] != week:
        training_progress[user_id] = {"week": week, "done": 0}
    if today.weekday() == 6:  # Воскресенье
        done = training_progress[user_id]["done"]
        if done >= 3:
            await bot.send_message(user_id, "Красавчик :3")
        else:
            await bot.send_message(user_id, "Хули ленимся? Без оправданий!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
