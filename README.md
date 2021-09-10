# Strava Telegram Bot

## How to run Telegram bot

1. Install Python [.python-version](bot/.python-version).
3. Download packages:
```shell
pip install -r requirements.txt
```
4. Define environment variables:
   - `PORT` - HTTP port;
   - `BOT_API_KEY` - Telegram bot API key;
   - `STRAVA_USERS_CONFIG` - Strava users info in JSON format:
```json
{
    "names": {
        "11111222": {
            "name": "John Doe"
        }
    },
    "members": [
        11111222
    ]
}
```
5. Run:
```shell
python bot/auto_uploader.py
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
