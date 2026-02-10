import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
from dotenv import load_dotenv
from database import Database

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных
db = Database()

# Состояния для ConversationHandler
ROOM_NAME, MAX_PLAYERS, BUY_IN, DATE_TIME, LOCATION = range(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "🃏 Привет! Я бот для организации покерных комнат.\n\n"
        "Доступные команды:\n"
        "/create - Создать новую покерную комнату\n"
        "/rooms - Показать активные комнаты\n"
        "/help - Помощь"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text(
        "📚 Инструкция по использованию бота:\n\n"
        "1️⃣ /create - Создать новую покерную комнату\n"
        "   Вы сможете указать название, количество игроков, бай-ин и др.\n\n"
        "2️⃣ /rooms - Посмотреть все активные комнаты\n"
        "   Здесь можно записаться в комнату или выйти из нее\n\n"
        "3️⃣ Создатель комнаты может закрыть её через меню комнаты\n\n"
        "По вопросам пишите @your_username"
    )


async def create_room_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало создания комнаты"""
    await update.message.reply_text(
        "🎰 Создание новой покерной комнаты\n\n"
        "Введите название комнаты:"
    )
    return ROOM_NAME


async def room_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение названия комнаты"""
    context.user_data['room_name'] = update.message.text
    await update.message.reply_text(
        "Отлично! Теперь укажите максимальное количество игроков (или отправьте '-' для пропуска, по умолчанию 9):"
    )
    return MAX_PLAYERS


async def max_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение максимального количества игроков"""
    text = update.message.text
    if text == '-':
        context.user_data['max_players'] = 9
    else:
        try:
            count = int(text)
            if count < 2 or count > 23:
                await update.message.reply_text(
                    "❌ Количество игроков должно быть от 2 до 23. Попробуйте снова:"
                )
                return MAX_PLAYERS
            context.user_data['max_players'] = count
        except ValueError:
            await update.message.reply_text(
                "❌ Пожалуйста, введите число или '-' для пропуска:"
            )
            return MAX_PLAYERS

    await update.message.reply_text(
        "Укажите бай-ин (например: '100$' или 'Фрироллы') или '-' для пропуска:"
    )
    return BUY_IN


async def buy_in(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение бай-ина"""
    text = update.message.text
    context.user_data['buy_in'] = "Не указан" if text == '-' else text

    await update.message.reply_text(
        "Укажите дату и время игры (например: '15.02 в 19:00') или '-' для пропуска:"
    )
    return DATE_TIME


async def date_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение даты и времени"""
    text = update.message.text
    context.user_data['date_time'] = None if text == '-' else text

    await update.message.reply_text(
        "Укажите место проведения или '-' для пропуска:"
    )
    return LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение локации и создание комнаты"""
    text = update.message.text
    context.user_data['location'] = "Не указана" if text == '-' else text

    # Создаем комнату в базе данных
    user = update.effective_user
    room = db.create_room(
        chat_id=update.effective_chat.id,
        creator_id=user.id,
        creator_name=user.full_name,
        room_name=context.user_data['room_name'],
        max_players=context.user_data['max_players'],
        buy_in=context.user_data['buy_in'],
        date_time=context.user_data['date_time'],
        location=context.user_data['location']
    )

    # Автоматически добавляем создателя в список игроков
    db.add_player(room.id, user.id, user.username, user.full_name)

    # Формируем сообщение о созданной комнате
    message = format_room_message(room)

    keyboard = [
        [InlineKeyboardButton("➕ Записаться", callback_data=f"join_{room.id}")],
        [InlineKeyboardButton("➖ Выйти", callback_data=f"leave_{room.id}")],
        [InlineKeyboardButton("🗑 Закрыть комнату", callback_data=f"close_{room.id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, reply_markup=reply_markup)

    # Очищаем данные пользователя
    context.user_data.clear()

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена создания комнаты"""
    context.user_data.clear()
    await update.message.reply_text("❌ Создание комнаты отменено.")
    return ConversationHandler.END


def format_room_message(room):
    """Форматирование сообщения о комнате"""
    players = room.players
    players_count = len(players)

    message = f"🎰 <b>{room.room_name}</b>\n\n"
    message += f"👤 Организатор: {room.creator_name}\n"
    message += f"👥 Игроков: {players_count}/{room.max_players}\n"
    message += f"💰 Бай-ин: {room.buy_in}\n"

    if room.date_time:
        message += f"📅 Время: {room.date_time}\n"

    if room.location != "Не указана":
        message += f"📍 Место: {room.location}\n"

    message += "\n<b>Список игроков:</b>\n"
    for i, player in enumerate(players, 1):
        username = f"@{player.username}" if player.username else player.full_name
        message += f"{i}. {username}\n"

    return message


async def show_rooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать все активные комнаты"""
    rooms = db.get_active_rooms(update.effective_chat.id)

    if not rooms:
        await update.message.reply_text(
            "📭 Нет активных комнат.\n\n"
            "Создайте новую комнату командой /create"
        )
        return

    await update.message.reply_text(f"📋 Найдено активных комнат: {len(rooms)}\n")

    for room in rooms:
        message = format_room_message(room)

        keyboard = [
            [InlineKeyboardButton("➕ Записаться", callback_data=f"join_{room.id}")],
            [InlineKeyboardButton("➖ Выйти", callback_data=f"leave_{room.id}")],
        ]

        # Только создатель может закрыть комнату
        if update.effective_user.id == room.creator_id:
            keyboard.append([InlineKeyboardButton("🗑 Закрыть комнату", callback_data=f"close_{room.id}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='HTML')


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    data = query.data
    action, room_id = data.split('_')
    room_id = int(room_id)

    user = update.effective_user
    room = db.get_room(room_id)

    if not room or not room.is_active:
        await query.edit_message_text("❌ Комната не найдена или уже закрыта.")
        return

    if action == "join":
        # Проверяем, не заполнена ли комната
        players_count = db.get_room_players_count(room_id)
        if players_count >= room.max_players:
            await query.answer("❌ Комната заполнена!", show_alert=True)
            return

        player = db.add_player(room_id, user.id, user.username, user.full_name)
        if player:
            # Обновляем сообщение
            room = db.get_room(room_id)
            message = format_room_message(room)

            keyboard = [
                [InlineKeyboardButton("➕ Записаться", callback_data=f"join_{room.id}")],
                [InlineKeyboardButton("➖ Выйти", callback_data=f"leave_{room.id}")],
            ]

            if user.id == room.creator_id:
                keyboard.append([InlineKeyboardButton("🗑 Закрыть комнату", callback_data=f"close_{room.id}")])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
            await query.answer("✅ Вы записаны в комнату!")
        else:
            await query.answer("ℹ️ Вы уже записаны в эту комнату", show_alert=True)

    elif action == "leave":
        success = db.remove_player(room_id, user.id)
        if success:
            # Обновляем сообщение
            room = db.get_room(room_id)
            message = format_room_message(room)

            keyboard = [
                [InlineKeyboardButton("➕ Записаться", callback_data=f"join_{room.id}")],
                [InlineKeyboardButton("➖ Выйти", callback_data=f"leave_{room.id}")],
            ]

            if user.id == room.creator_id:
                keyboard.append([InlineKeyboardButton("🗑 Закрыть комнату", callback_data=f"close_{room.id}")])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
            await query.answer("✅ Вы вышли из комнаты")
        else:
            await query.answer("❌ Вы не записаны в эту комнату", show_alert=True)

    elif action == "close":
        # Проверяем, что закрывает создатель
        if user.id != room.creator_id:
            await query.answer("❌ Только создатель может закрыть комнату!", show_alert=True)
            return

        db.close_room(room_id)
        await query.edit_message_text(
            f"🔒 Комната '{room.room_name}' закрыта.\n\n"
            f"Участвовало игроков: {len(room.players)}"
        )
        await query.answer("✅ Комната закрыта")


def main():
    """Запуск бота"""
    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("Не найден BOT_TOKEN в переменных окружения!")
        return

    # Создаем приложение
    application = Application.builder().token(token).build()

    # Обработчик создания комнаты
    create_room_handler = ConversationHandler(
        entry_points=[CommandHandler('create', create_room_start)],
        states={
            ROOM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, room_name)],
            MAX_PLAYERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, max_players)],
            BUY_IN: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_in)],
            DATE_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_time)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, location)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(create_room_handler)
    application.add_handler(CommandHandler("rooms", show_rooms))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Запускаем бота
    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
