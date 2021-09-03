# strava-telegram-bot

## How to run

1. Install Python [.python-version](.python-version).
2. Download packages: 
```shell
pip install -r requirements.txt
```
3. Define environment variables:
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
4. Run:
```shell
python AutoUploader.py
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
