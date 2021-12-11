from bot.member_list import Member, MemberList


class TestMemberList:
    def test_printable(self):
        members = [Member(1, "Вася Пупкін"), Member(2, "John Doe")]

        assert MemberList.printable(members) == [
            'Бігуни <a href="https://gutsulrunning.club/images/2021/08/05/header_large.jpeg">GRC:</a>',
            ' 1. <a href="https://www.strava.com/athletes/2">John Doe</a>',
            ' 2. <a href="https://www.strava.com/athletes/1">Вася Пупкін</a>',
        ]
