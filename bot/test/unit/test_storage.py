from bot.storage import Storage


class TestStorage:
    users_config = '{ \
        "members": { \
            "11111222": { \
                "name": "John Doe" \
            }, \
            "11111333": { \
                "name": "Jane Doe" \
            } \
        } \
    }'

    def test_get_name(self):
        storage = Storage(self.users_config)

        assert storage.get_name("1234") == ""
        assert storage.get_name("11111222") == "John Doe"
        assert storage.get_name("11111333") == "Jane Doe"

    def test_get_members(self):
        storage = Storage(self.users_config)

        assert storage.get_members() == [11111222, 11111333]
