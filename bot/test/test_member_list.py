from bot.member_list import Member, MemberList


def test_get_table():
    members = [Member(1, "Вася Пупкін"), Member(2, "John Doe")]

    assert MemberList.get_table(members) == [
        'Бігуни <a href="https://gutsulrunning.club/images/2021/08/05/header_large.jpeg">GRC:</a>',
        ' 1. <a href="https://www.strava.com/athletes/2">John Doe</a>',
        ' 2. <a href="https://www.strava.com/athletes/1">Вася Пупкін</a>',
    ]
