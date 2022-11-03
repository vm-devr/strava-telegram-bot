from bot.leaderboard import LeaderBoard


def test_get_table():
    athletes = [{"name": "Вася Пупкін", "distance": 60}, {"name": "John Doe", "distance": 55}]

    table = LeaderBoard().get_table(athletes)

    assert table == ["1 Вася Пупкін 60km", "2    John Doe 55km"]
