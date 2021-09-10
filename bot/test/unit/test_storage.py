from bot.storage import Storage


class TestStorage:
    users_config = '{ \
        "names": { \
            "11111222": { \
                "name": "John Doe" \
            }, \
            "11111333": { \
                "name": "Jane Doe" \
            } \
        }, \
        "members": [ \
            11111222, \
            11111333 \
        ] \
    }'

    def test_get_name(self):
        storage = Storage(self.users_config)

        assert "John Doe" == storage.get_name("11111222")
        assert "Jane Doe" == storage.get_name("11111333")

    def test_get_members(self):
        storage = Storage(self.users_config)

        assert [11111222, 11111333] == storage.get_members()
