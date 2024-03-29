from bot.storage import Storage

users_config = """111222 : John Doe;1111333: Jane Doe;11111444: Вася Пупкін"""


def test_get_name():
    storage = Storage(users_config)

    assert storage.get_name(1234) == ""
    assert storage.get_name(111222) == "John Doe"
    assert storage.get_name(1111333) == "Jane Doe"
    assert storage.get_name(11111444) == "Вася Пупкін"


def test_get_members():
    storage = Storage(users_config)

    assert storage.get_members() == [111222, 1111333, 11111444]
