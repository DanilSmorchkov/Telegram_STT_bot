# Telegram STT Bot

A Python-based Telegram bot for speech-to-text conversion, supporting easy model integration.

## Features

- Simple model addition.
- Modular architecture for API and bot components.
- Docker support for easy deployment.

## Getting Started

### Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/Telegram_STT_bot.git
cd Telegram_STT_bot
pip install -r requirements.txt
```
## Adding a New Model
If you implement a new model class, add it to src/model/ and register it in src/model/factory.py.

## Running the Project

To run the bot, you need to provide a Telegram Bot Token. Obtain the token from [BotFather](https://t.me/BotFather)
and set it as the environment variable `TELEGRAM_BOT_TOKEN` or add it to your configuration file if your project uses one.

#### Using Docker
```bash
docker-compose up --build
```
#### Running API Manually
```bash
python src/api/main.py
```
#### Running Bot Manually
```bash
python src/bot/main.py
```
