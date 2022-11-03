from datetime import date

from bot.date import last_sunday


def test_last_sunday():
    assert last_sunday(date(2022, 1, 1)) == date(2021, 12, 26)
    assert last_sunday(date(2022, 11, 3)) == date(2022, 10, 30)
    assert last_sunday(date(2022, 10, 25)) == date(2022, 10, 23)
