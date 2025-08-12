import os
import requests
import argparse
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()
API_KEY = os.getenv("API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def format_city(city: str) -> str:
    if "," not in city:
        city = city.strip() + ",UA"
    return city


def get_current_weather_text(city: str) -> str:
    """Return formatted current weather text."""
    if not API_KEY:
        return "❌ API_KEY is missing! Please set it in your .env file."
    city = format_city(city)
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    try:
        response = requests.get(CURRENT_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.HTTPError as e:
        # Check if city not found
        if response.status_code == 404:
            return f"❌ City '{city}' does not exist or was not found."
        else:
            raise e  # re-raise for other HTTP errors

    return (
        f"🌤 Current weather in {city}:\n"
        f"🌡 Temperature: {data['main']['temp']} °C\n"
        f"💧 Humidity: {data['main']['humidity']} %\n"
        f"💨 Wind speed: {data['wind']['speed']} m/s"
    )


def get_forecast_text(city: str) -> str:
    """Return formatted forecast text."""
    if not API_KEY:
        return "❌ API_KEY is missing! Please set it in your .env file."
    city = format_city(city)
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    try:
        response = requests.get(FORECAST_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.HTTPError as e:
        if response.status_code == 404:
            return f"❌ City '{city}' does not exist or was not found."
        else:
            raise e

    forecast_lines = [f"📅 5-day / 3-hour forecast for {city}:"]
    for entry in data["list"][:5]:
        dt_txt = entry["dt_txt"]
        temp = entry["main"]["temp"]
        description = entry["weather"][0]["description"]
        forecast_lines.append(f"{dt_txt} — {temp} °C — {description}")
    return "\n".join(forecast_lines)


def run_cli(command: str, city: str):
    try:
        if command == "current":
            print(get_current_weather_text(city))
        elif command == "forecast":
            print(get_forecast_text(city))
    except requests.HTTPError as e:
        print(f"Error fetching data: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Welcome to the Weather Bot!\n\n"
        "You can get current weather and forecast info.\n\n"
        "Use these commands:\n"
        "/current <city> - Get current weather for the city\n"
        "/forecast <city> - Get 5-day forecast for the city\n"
        "/help - Show this help message again"
    )
    await update.message.reply_text(welcome_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 Weather Bot Help\n\n"
        "Commands:\n"
        "/current <city> - Get current weather. Example: /current Kyiv\n"
        "/forecast <city> - Get 5-day forecast. Example: /forecast Lviv\n"
        "/start - Welcome message\n"
        "/help - This help message"
    )
    await update.message.reply_text(help_text)


async def current_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /current <city>")
        return
    city = " ".join(context.args)
    try:
        await update.message.reply_text(get_current_weather_text(city))
    except requests.HTTPError as e:
        await update.message.reply_text(f"Error fetching data: {e}")


async def forecast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /forecast <city>")
        return
    city = " ".join(context.args)
    try:
        await update.message.reply_text(get_forecast_text(city))
    except requests.HTTPError as e:
        await update.message.reply_text(f"Error fetching data: {e}")


def run_telegram():
    if not TELEGRAM_TOKEN:
        raise ValueError("❌ TELEGRAM_TOKEN is missing! Please set it in your .env file.")
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("current", current_command))
    app.add_handler(CommandHandler("forecast", forecast_command))

    print("✅ Telegram bot is running...")
    app.run_polling()


def main():
    parser = argparse.ArgumentParser(description="Weather CLI & Telegram bot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # CLI commands
    parser_current = subparsers.add_parser("current", help="Get current weather for a city")
    parser_current.add_argument("city", type=str, help="City name, e.g. Kyiv")

    parser_forecast = subparsers.add_parser("forecast", help="Get 5-day forecast for a city")
    parser_forecast.add_argument("city", type=str, help="City name, e.g. Lviv")

    # Telegram bot command
    subparsers.add_parser("telegram", help="Run the Telegram bot")

    args = parser.parse_args()

    if args.command == "telegram":
        run_telegram()
    else:
        run_cli(args.command, args.city)


if __name__ == "__main__":
    main()