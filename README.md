# Weather CLI & Telegram Bot

A Python application that provides current weather and 5-day weather forecasts using the OpenWeatherMap API.  
It can be used either as a command-line interface (CLI) tool or as a Telegram bot.

---

## Features

- Get current weather by city
- Get 5-day / 3-hour weather forecast by city
- Run a Telegram bot to interactively get weather info

---

## Setup

### Prerequisites

- Python 3.7+
- An OpenWeatherMap API key (https://openweathermap.org/api)
- A Telegram bot token from BotFather (https://t.me/BotFather)

### Installation

1. Clone the repository or copy the script.

2. Create a `.env` file in the project directory with the following content:

```env
API_KEY=your_openweathermap_api_key
TELEGRAM_TOKEN=your_telegram_bot_token
```

3. Install required Python packages:

- pip install python-dotenv requests python-telegram-bot --upgrade

4. Command-Line Interface (CLI)

- python main.py current Kyiv

- python main.py forecast Lviv

5. Telegram Bot 
- python main.py telegram