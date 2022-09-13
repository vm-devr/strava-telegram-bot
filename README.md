# Strava Telegram Bot

## Live

[Render](https://gutsul-bot.onrender.com)

[Cronhub](https://cronhub.io/schedulers/619/overview)

## How to run Telegram bot

1. Install Python [.python-version](bot/.python-version).
3. Download packages:
```shell
pip install -r requirements.txt
```
4. Define environment variables:
   - `PORT` - HTTP port;
   - `BOT_API_KEY` - Telegram bot API key;
   - `STRAVA_GROUP` - Strava club id;
   - `STRAVA_USERS_CONFIG` - Strava club members in the format `StravaId: Name Surname` separated by `;`:
```
111222: John Doe;1111333: Jane Doe;11111444: Вася Пупкін
```

5. Run:
```shell
python bot/bot.py
```

## How to develop

1. Create and activate virtual environment.
2. Download dev packages:
```shell
pip install -r requirements-dev.txt
```

2. Install pre-commit hook:
```shell
pre-commit install
```

3. Run python unit tests:
```shell
python -m pytest bot/test/unit
```
