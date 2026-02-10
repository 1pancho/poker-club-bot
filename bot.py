import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.constants import ParseMode
from dotenv import load_dotenv
from database import Database
from poker_engine import PokerGame, Player as PokerPlayer

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

# Активные игры (в памяти)
active_games = {}


def format_chips(amount):
    """Красивое форматирование фишек"""
    if amount >= 1000000:
        return f"{amount/1000000:.1f}M"
    elif amount >= 1000:
        return f"{amount/1000:.1f}K"
    return str(amount)


def get_progress_bar(current, max_val, length=10):
    """Создает прогресс-бар"""
    filled = int((current / max_val) * length) if max_val > 0 else 0
    bar = "█" * filled + "░" * (length - filled)
    return bar


def format_player_card(player_profile):
    """Красивая карточка игрока"""
    win_rate = (player_profile.games_won / player_profile.total_games * 100) if player_profile.total_games > 0 else 0

    card = f"""
╭─────────────────────╮
│ 👤 <b>{player_profile.full_name}</b>
│
│ 💰 Фишки: <code>{format_chips(player_profile.chips)}</code>
│ 🏆 Рейтинг: <code>{player_profile.rating}</code>
│
│ 📊 Статистика:
│   Игр: {player_profile.total_games}
│   Побед: {player_profile.games_won} ({win_rate:.1f}%)
│   Выигрыш: {format_chips(player_profile.total_winnings)}
╰─────────────────────╯
"""
    return card


def format_game_table(game: PokerGame, current_player_id=None):
    """Красивое отображение игрового стола"""
    stage_emoji = {
        "waiting": "⏳",
        "preflop": "🎴",
        "flop": "🃏",
        "turn": "🎯",
        "river": "🌊",
        "showdown": "🏆"
    }

    stage_name = {
        "waiting": "Ожидание",
        "preflop": "Префлоп",
        "flop": "Флоп",
        "turn": "Терн",
        "river": "Ривер",
        "showdown": "Вскрытие"
    }

    message = f"""
╔══════════════════════════╗
║   🎰 <b>TEXAS HOLD'EM</b> 🎰   ║
╚══════════════════════════╝

{stage_emoji.get(game.stage, '🎲')} <b>Стадия:</b> {stage_name.get(game.stage, game.stage)}
💰 <b>Банк:</b> <code>{format_chips(game.pot)}</code>

"""

    # Общие карты
    if game.community_cards:
        cards_str = " ".join([str(card) for card in game.community_cards])
        message += f"🎴 <b>Стол:</b> {cards_str}\n\n"
    else:
        message += f"🎴 <b>Стол:</b> [ - - - - - ]\n\n"

    # Игроки
    message += "👥 <b>Игроки:</b>\n"
    for i, player in enumerate(game.players):
        if player.folded:
            status = "❌ Fold"
        elif player.all_in:
            status = "🔥 All-in"
        else:
            status = "✅"

        is_current = "➤ " if (game.get_current_player() and player.user_id == game.get_current_player().user_id) else "  "
        is_dealer = "🔴 " if i == game.dealer_position else ""

        chips_bar = get_progress_bar(player.chips, 2000, 8)

        message += f"{is_current}{is_dealer}<b>{player.name}</b>\n"
        message += f"   {chips_bar} <code>{format_chips(player.chips)}</code> {status}\n"

        if player.current_bet > 0:
            message += f"   💵 Ставка: <code>{format_chips(player.current_bet)}</code>\n"
        message += "\n"

    # Текущий ход
    current = game.get_current_player()
    if current:
        message += f"⏱ <b>Ход игрока:</b> {current.name}\n"
        message += f"💵 <b>Текущая ставка:</b> <code>{format_chips(game.current_bet)}</code>\n"

    return message


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    player = db.get_or_create_player(user.id, user.username, user.full_name)

    welcome_msg = f"""
🎰 <b>Добро пожаловать в Poker Club!</b> 🎰

Привет, {user.first_name}! Готов сыграть в Texas Hold'em?

{format_player_card(player)}

<b>🎮 Команды:</b>
/play - Создать или присоединиться к игре
/balance - Мой баланс и статистика
/bonus - Получить ежедневный бонус
/top - Таблица лидеров
/help - Помощь

<i>Удачи за столами! 🍀</i>
"""

    await update.message.reply_text(welcome_msg, parse_mode=ParseMode.HTML)


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать баланс и статистику"""
    user = update.effective_user
    player = db.get_or_create_player(user.id, user.username, user.full_name)

    message = format_player_card(player)

    keyboard = [
        [
            InlineKeyboardButton("🎁 Получить бонус", callback_data="daily_bonus"),
            InlineKeyboardButton("🎮 Играть", callback_data="create_game")
        ],
        [InlineKeyboardButton("🏆 Рейтинг", callback_data="leaderboard")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ежедневный бонус"""
    user = update.effective_user
    bonus = db.get_daily_bonus(user.id)

    if bonus:
        player = db.get_or_create_player(user.id, user.username, user.full_name)
        message = f"""
🎁 <b>Ежедневный бонус получен!</b>

Вы получили: <code>+{bonus}</code> фишек 💰

Ваш баланс: <code>{format_chips(player.chips)}</code>

<i>Возвращайтесь завтра за новым бонусом! ⏰</i>
"""
    else:
        message = """
⏰ <b>Бонус уже получен</b>

Вы уже получили бонус сегодня!
Возвращайтесь через 24 часа 🕐
"""

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Таблица лидеров"""
    leaders = db.get_leaderboard(10)

    message = """
╔═══════════════════════════╗
║   🏆 <b>ТАБЛИЦА ЛИДЕРОВ</b> 🏆   ║
╚═══════════════════════════╝

"""

    medals = ["🥇", "🥈", "🥉"]

    for i, player in enumerate(leaders, 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        win_rate = (player.games_won / player.total_games * 100) if player.total_games > 0 else 0

        message += f"{medal} <b>{player.full_name}</b>\n"
        message += f"   ⭐️ Рейтинг: <code>{player.rating}</code>\n"
        message += f"   💰 Фишки: <code>{format_chips(player.chips)}</code>\n"
        message += f"   🎯 Винрейт: <code>{win_rate:.1f}%</code> ({player.games_won}/{player.total_games})\n\n"

    keyboard = [[InlineKeyboardButton("🔄 Обновить", callback_data="leaderboard")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создать или присоединиться к игре"""
    chat_id = update.effective_chat.id
    user = update.effective_user
    player = db.get_or_create_player(user.id, user.username, user.full_name)

    # Проверяем, есть ли активная игра в этом чате
    if chat_id in active_games:
        game = active_games[chat_id]
        if game.stage == "waiting":
            # Можно присоединиться
            message = f"""
🎰 <b>Активная игра найдена!</b>

Игроков за столом: {len(game.players)}/{game.max_players}
Блайнды: {game.small_blind}/{game.big_blind}

💰 Ваш баланс: <code>{format_chips(player.chips)}</code>
"""
            keyboard = [
                [InlineKeyboardButton(f"💰 Сесть за стол (100 фишек)", callback_data=f"join_game_{chat_id}_100")],
                [InlineKeyboardButton(f"💵 Сесть за стол (500 фишек)", callback_data=f"join_game_{chat_id}_500")],
                [InlineKeyboardButton(f"💸 Сесть за стол (1000 фишек)", callback_data=f"join_game_{chat_id}_1000")],
                [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
            ]
        else:
            # Игра уже идет
            message = "⏳ Игра уже идет. Дождитесь окончания раунда."
            keyboard = [[InlineKeyboardButton("👀 Посмотреть", callback_data=f"view_game_{chat_id}")]]
    else:
        # Создаем новую игру
        message = f"""
🎰 <b>Создание нового стола</b>

Выберите параметры игры:

💰 Ваш баланс: <code>{format_chips(player.chips)}</code>
"""
        keyboard = [
            [InlineKeyboardButton("🎲 Быстрая игра (10/20)", callback_data="create_quick")],
            [InlineKeyboardButton("💎 Стандарт (50/100)", callback_data="create_standard")],
            [InlineKeyboardButton("👑 Хайроллер (100/200)", callback_data="create_high")],
            [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь"""
    help_text = """
📚 <b>Как играть в Texas Hold'em?</b>

<b>🎯 Цель игры:</b>
Собрать лучшую комбинацию из 5 карт, используя свои 2 карты и 5 общих карт на столе.

<b>🎴 Комбинации (от слабой к сильной):</b>
1. Старшая карта
2. Пара
3. Две пары
4. Тройка (Сет)
5. Стрит
6. Флеш
7. Фулл хаус
8. Каре
9. Стрит флеш
10. Роял флеш

<b>💡 Действия в игре:</b>
• <b>Check</b> - пропустить ход (если нет ставки)
• <b>Call</b> - уравнять ставку
• <b>Raise</b> - повысить ставку
• <b>Fold</b> - сбросить карты
• <b>All-in</b> - поставить все фишки

<b>🎮 Команды бота:</b>
/play - Начать игру
/balance - Баланс и статистика
/bonus - Ежедневный бонус
/top - Таблица лидеров

<b>💰 Фишки:</b>
• Стартовые: 1000 фишек
• Ежедневный бонус: 100 фишек
• Играйте и выигрывайте больше!

<i>Удачи за столами! 🍀</i>
"""

    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    data = query.data
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Ежедневный бонус
    if data == "daily_bonus":
        bonus = db.get_daily_bonus(user.id)
        if bonus:
            player = db.get_or_create_player(user.id, user.username, user.full_name)
            message = f"""
🎁 <b>Бонус получен!</b>

+{bonus} фишек 💰
Баланс: <code>{format_chips(player.chips)}</code>
"""
        else:
            message = "⏰ Бонус уже получен сегодня!"

        await query.edit_message_text(message, parse_mode=ParseMode.HTML)

    # Таблица лидеров
    elif data == "leaderboard":
        leaders = db.get_leaderboard(10)
        message = """
╔═══════════════════════════╗
║   🏆 <b>ТАБЛИЦА ЛИДЕРОВ</b> 🏆   ║
╚═══════════════════════════╝

"""
        medals = ["🥇", "🥈", "🥉"]
        for i, player in enumerate(leaders, 1):
            medal = medals[i-1] if i <= 3 else f"{i}."
            win_rate = (player.games_won / player.total_games * 100) if player.total_games > 0 else 0
            message += f"{medal} <b>{player.full_name}</b>\n"
            message += f"   ⭐️ {player.rating} | 💰 {format_chips(player.chips)} | 🎯 {win_rate:.1f}%\n\n"

        keyboard = [[InlineKeyboardButton("🔄 Обновить", callback_data="leaderboard")]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

    # Создание игры
    elif data.startswith("create_"):
        game_type = data.split("_")[1]
        blinds = {"quick": (10, 20), "standard": (50, 100), "high": (100, 200)}
        sb, bb = blinds.get(game_type, (10, 20))

        # Создаем игру
        game = PokerGame(game_id=str(chat_id), small_blind=sb, big_blind=bb)
        active_games[chat_id] = game

        message = f"""
✅ <b>Стол создан!</b>

💰 Блайнды: {sb}/{bb}
👥 Игроков: 0/{game.max_players}

Выберите бай-ин:
"""
        keyboard = [
            [InlineKeyboardButton(f"💰 {format_chips(bb*5)}", callback_data=f"join_game_{chat_id}_{bb*5}")],
            [InlineKeyboardButton(f"💵 {format_chips(bb*10)}", callback_data=f"join_game_{chat_id}_{bb*10}")],
            [InlineKeyboardButton(f"💸 {format_chips(bb*20)}", callback_data=f"join_game_{chat_id}_{bb*20}")],
        ]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

    # Присоединение к игре
    elif data.startswith("join_game_"):
        parts = data.split("_")
        game_chat_id = int(parts[2])
        buy_in = int(parts[3])

        if game_chat_id not in active_games:
            await query.edit_message_text("❌ Игра не найдена")
            return

        game = active_games[game_chat_id]
        player = db.get_or_create_player(user.id, user.username, user.full_name)

        # Проверяем баланс
        if player.chips < buy_in:
            await query.answer(f"❌ Недостаточно фишек! Нужно {buy_in}, у вас {player.chips}", show_alert=True)
            return

        # Добавляем в игру
        if game.add_player(user.id, user.full_name, buy_in):
            # Списываем фишки
            db.update_player_chips(user.id, player.chips - buy_in)

            await query.answer("✅ Вы сели за стол!", show_alert=True)

            # Обновляем сообщение
            message = format_game_table(game)
            message += "\n⏳ <i>Ожидание игроков...</i>\n"

            keyboard = []
            if len(game.players) >= game.min_players:
                keyboard.append([InlineKeyboardButton("🎮 Начать игру", callback_data=f"start_game_{game_chat_id}")])
            keyboard.append([InlineKeyboardButton("➕ Пригласить друзей", switch_inline_query="Присоединяйся к покеру!")])

            await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
        else:
            await query.answer("❌ Не удалось присоединиться", show_alert=True)

    # Начало игры
    elif data.startswith("start_game_"):
        game_chat_id = int(data.split("_")[2])

        if game_chat_id not in active_games:
            await query.edit_message_text("❌ Игра не найдена")
            return

        game = active_games[game_chat_id]

        if game.start_game():
            message = format_game_table(game)

            current_player = game.get_current_player()
            keyboard = []

            if current_player and current_player.user_id == user.id:
                # Кнопки действий для текущего игрока
                keyboard = [
                    [
                        InlineKeyboardButton("✅ Check", callback_data=f"action_{game_chat_id}_check"),
                        InlineKeyboardButton("📞 Call", callback_data=f"action_{game_chat_id}_call")
                    ],
                    [
                        InlineKeyboardButton("⬆️ Raise", callback_data=f"action_{game_chat_id}_raise"),
                        InlineKeyboardButton("❌ Fold", callback_data=f"action_{game_chat_id}_fold")
                    ],
                    [InlineKeyboardButton("🔥 All-in", callback_data=f"action_{game_chat_id}_all_in")]
                ]

            await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
        else:
            await query.answer("❌ Недостаточно игроков для старта", show_alert=True)

    # Игровые действия
    elif data.startswith("action_"):
        parts = data.split("_")
        game_chat_id = int(parts[1])
        action = parts[2]

        if game_chat_id not in active_games:
            await query.answer("❌ Игра не найдена", show_alert=True)
            return

        game = active_games[game_chat_id]
        current_player = game.get_current_player()

        if not current_player or current_player.user_id != user.id:
            await query.answer("❌ Сейчас не ваш ход!", show_alert=True)
            return

        # Выполняем действие
        if game.player_action(user.id, action):
            message = format_game_table(game)

            # Проверяем, закончилась ли игра
            if game.stage == "showdown":
                # Показываем результаты
                winners, hands, best_cards = game._go_to_showdown()

                message += "\n🏆 <b>РЕЗУЛЬТАТЫ:</b>\n\n"
                for i, winner in enumerate(winners):
                    message += f"👑 <b>{winner.name}</b>\n"
                    message += f"   Комбинация: {hands[i].name_ru}\n"
                    message += f"   Карты: {' '.join([str(c) for c in best_cards[i]])}\n"
                    message += f"   Выигрыш: 💰 <code>{format_chips(game.pot // len(winners))}</code>\n\n"

                # Обновляем статистику
                for winner in winners:
                    db.update_player_stats(winner.user_id, won=True, winnings=game.pot // len(winners))
                    player_profile = db.get_or_create_player(winner.user_id, "", winner.name)
                    db.add_chips(winner.user_id, game.pot // len(winners))

                # Удаляем игру
                del active_games[game_chat_id]

                keyboard = [[InlineKeyboardButton("🔄 Новая игра", callback_data="create_game")]]
                await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
            else:
                # Продолжаем игру
                next_player = game.get_current_player()
                keyboard = []

                if next_player and next_player.user_id == user.id:
                    keyboard = [
                        [
                            InlineKeyboardButton("✅ Check", callback_data=f"action_{game_chat_id}_check"),
                            InlineKeyboardButton("📞 Call", callback_data=f"action_{game_chat_id}_call")
                        ],
                        [
                            InlineKeyboardButton("⬆️ Raise", callback_data=f"action_{game_chat_id}_raise"),
                            InlineKeyboardButton("❌ Fold", callback_data=f"action_{game_chat_id}_fold")
                        ],
                        [InlineKeyboardButton("🔥 All-in", callback_data=f"action_{game_chat_id}_all_in")]
                    ]

                await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
        else:
            await query.answer("❌ Невозможное действие", show_alert=True)

    elif data == "cancel":
        await query.edit_message_text("❌ Отменено")


def main():
    """Запуск бота"""
    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("Не найден BOT_TOKEN в переменных окружения!")
        return

    application = Application.builder().token(token).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("bonus", daily_bonus))
    application.add_handler(CommandHandler("top", leaderboard))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    logger.info("🎰 Poker Bot запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
