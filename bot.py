"""
Telegram-бот обменника CASHEX.
Кнопки: О нас, Курсы, Связаться с нами, Как нас найти.
"""

import os
import logging
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode

import config
import rates

load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Клавиатура главного меню
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["🏦 О нас", "📊 Курсы"],
        ["🛠️ Связаться с нами", "🔎 Как нас найти"],
    ],
    resize_keyboard=True,
)


def get_welcome_text() -> str:
    return (
        "Добро пожаловать в <b>CASHEX</b>!\n\n"
        f"📍 <b>Адрес:</b> {config.ADDRESS}\n"
        "🗓️ Мы работаем для вас <b>24/7</b>. Без обеда и выходных.\n"
        "💵 Работаем только за <b>наличные рубли</b>.\n"
        "💹 Выгодный курс на покупку и продажу USDT.\n"
        "🤩 Без комиссий на покупку и продажу USDT.\n\n"
        'Для обмена нажмите кнопку <b>"Обмен"</b> или напишите /exchange.'
    )


def get_about_text() -> str:
    return (
        "🤖 <b>О нас</b>\n\n"
        "Добро пожаловать в наш бот для обмена криптовалюты!\n\n"
        f"💰 Мы занимаемся обменом криптовалют более {config.ABOUT_YEARS} лет.\n"
        "🗓 Мы работаем для вас 24/7.\n"
        "💵 Мы работаем только за наличные рубли.\n"
        "💹 У нас вы можете купить и продать USDT без комиссии по выгодному курсу.\n\n"
        f"📍 <b>Наш адрес:</b> {config.ADDRESS}\n\n"
        "Для покупки или продажи USDT создайте заявку через кнопку «Обмен» или команду /exchange."
    )


def get_rates_text() -> str:
    pair = rates.fetch_usdt_rub_rates()
    if pair:
        buy, sell = pair
        buy_str = f"{buy:.2f} ₽"
        sell_str = f"{sell:.2f} ₽"
    else:
        buy_str = config.RATE_BUY_USDT_FALLBACK
        sell_str = config.RATE_SELL_USDT_FALLBACK
    return (
        "📊 <b>Курсы</b>\n\n"
        "Курс USDT/RUB (источник: Rapira, покупка +0.5%, продажа −0.5%):\n\n"
        f"🟢 Покупка USDT: {buy_str}\n"
        f"🔴 Продажа USDT: {sell_str}\n\n"
        "Для точного курса на вашу сумму создайте заявку через «Обмен» или /exchange."
    )


def get_contact_text() -> str:
    return (
        "🛠️ <b>Связаться с нами</b>\n\n"
        "По любым вопросам:\n\n"
        f"📞 Телефон: {config.CONTACT_PHONE}\n"
        f"✉️ Email: {config.CONTACT_EMAIL}\n"
        f"💬 Telegram: {config.CONTACT_TELEGRAM}\n\n"
        "Мы на связи 24/7."
    )


def get_location_text() -> str:
    return (
        "🔎 <b>Как нас найти</b>\n\n"
        f"📍 {config.ADDRESS}\n\n"
        "Мы работаем 24/7, без обеда и выходных.\n"
        "Ждём вас в офисе!"
    )


async def start(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        get_welcome_text(),
        reply_markup=MAIN_KEYBOARD,
        parse_mode=ParseMode.HTML,
    )


async def exchange(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🔄 <b>Обмен</b>\n\n"
        "Создание заявки на обмен скоро будет доступно.\n"
        "Пока вы можете связаться с нами через кнопку «Связаться с нами» или по телефону.",
        parse_mode=ParseMode.HTML,
    )


async def handle_menu(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (update.message.text or "").strip()
    if text == "🏦 О нас":
        await update.message.reply_text(get_about_text(), parse_mode=ParseMode.HTML)
    elif text == "📊 Курсы":
        await update.message.reply_text(get_rates_text(), parse_mode=ParseMode.HTML)
    elif text == "🛠️ Связаться с нами":
        await update.message.reply_text(get_contact_text(), parse_mode=ParseMode.HTML)
    elif text == "🔎 Как нас найти":
        await update.message.reply_text(get_location_text(), parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(
            "Выберите пункт меню кнопками ниже 👇",
            reply_markup=MAIN_KEYBOARD,
        )


def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("Задайте BOT_TOKEN в .env или переменных окружения.")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("exchange", exchange))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    logger.info("Бот CASHEX запущен.")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
