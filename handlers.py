from aiogram import types, F
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from quiz_data import quiz_data
from database import save_result, get_result

user_state = {}  # user_id -> {'index': int, 'score': int}
bot = None  # будет назначен в register_handlers

# Команда /start
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот для проведения квиза. Введите /quiz, чтобы начать.")

# Команда /quiz
async def cmd_quiz(message: types.Message):
    user_id = message.from_user.id
    user_state[user_id] = {'index': 0, 'score': 0}
    await send_question(message.chat.id, user_id)

# Команда /stats
async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    score = await get_result(user_id)
    if score is not None:
        await message.answer(f"📊 Последний результат: {score} / {len(quiz_data)} правильных ответов.")
    else:
        await message.answer("Вы ещё не проходили квиз.")

# Отправка текущего вопроса
async def send_question(chat_id, user_id):
    state = user_state.get(user_id, {'index': 0, 'score': 0})
    index = state['index']

    if index >= len(quiz_data):
        score = state['score']
        await save_result(user_id, score)
        await bot.send_message(chat_id, f"Квиз завершён! 🎉\nВаш результат: {score} / {len(quiz_data)}")
        user_state.pop(user_id, None)
        return

    question = quiz_data[index]
    text = f"{question['question']}\n\n" + "\n".join(
        [f"{i+1}. {opt}" for i, opt in enumerate(question['options'])]
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=opt, callback_data=f"answer:{i}")]
            for i, opt in enumerate(question['options'])
        ]
    )

    await bot.send_message(chat_id, text, reply_markup=keyboard)

# Обработка ответов
async def handle_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    state = user_state.get(user_id)

    if not state:
        await callback.answer("Начните сначала с команды /quiz")
        return

    index = state['index']
    question = quiz_data[index]
    selected_option = int(callback.data.split(":")[1])
    selected_text = question["options"][selected_option]

    # Проверка правильности
    if selected_option == question["correct_option"]:
        state['score'] += 1

    # Удалим кнопки и покажем выбор
    await callback.message.edit_reply_markup()
    await callback.message.answer(f"Вы выбрали: {selected_text}")

    # Следующий вопрос
    state['index'] += 1
    await send_question(callback.message.chat.id, user_id)

    await callback.answer()

# Регистрация
def register_handlers(dp, bot_instance):
    global bot
    bot = bot_instance

    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_quiz, Command("quiz"))
    dp.message.register(cmd_stats, Command("stats"))  # ⬅ новая команда
    dp.callback_query.register(handle_answer, F.data.startswith("answer:"))