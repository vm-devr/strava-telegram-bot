class LeaderBoard(object):
    def get_table(self, athletes, dist_num=3):
        for rank, ath in enumerate(athletes, start=1):
            ath["rank"] = rank
        self._stringify_field(athletes, "rank", 2, True)
        self._stringify_field(athletes, "name", 21 - dist_num, True)
        self._stringify_field(athletes, "distance", dist_num, False)

        return list(map(lambda ath: ath["rank"] + " " + ath["name"] + " " + ath["distance"] + "km", athletes))

    @staticmethod
    def _stringify_field(data, field, max_symb, left):
        max_item = 0
        for el in data:
            el[field] = str(el[field])
            if len(el[field]) > max_item:
                max_item = len(el[field])

        if max_item > max_symb:
            max_item = max_symb

        for el in data:
            while len(el[field]) < max_item:
                el[field] = f" {el[field]}" if left else f"{el[field]} "

            if len(el[field]) > max_item:
                if max_item == 1:
                    el[field] = "."
                elif max_item == 2:
                    el[field] = f"{el[field][0]}."
                elif max_item == 3:
                    el[field] = f"{el[field][0]}.."
                else:
                    el[field] = f"{el[field][: max_item - 1]}."

        return data
