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
   - `STRAVA_USERS_CONFIG` - Strava club members in JSON format:
```json
{
   "members": {
      "11111222": {
         "name": "John Doe"
      },
      "11111333": {
         "name": "Jane Doe"
      }
    }
}
```
5. Run:
```shell
python bot/auto_uploader.py
```

## How to run athletes stats updater

1. Install Perl.
2. Download perl modules via cpan.
3. Define environment variables:
   - `STRAVA_EMAIL` - Strava user email;
   - `STRAVA_PASSWORD` - Strava user password.
4. Run:
```shell
cd perl
perl readathletestats.pl <list of Strava ids separated by whitespace>
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
