class LeaderBoard(object):
    def printable(self, data, dist_num=3):
        rank = 1
        for ath in data:
            ath["rank"] = rank
            rank += 1
        self.__stringifyField(data, "rank", 2, True)
        self.__stringifyField(data, "name", 21 - dist_num, True)
        self.__stringifyField(data, "distance", dist_num, False)

        return list(map(lambda ath: ath["rank"] + " " + ath["name"] + " " + ath["distance"] + "km", data))

    def __stringifyField(self, data, field, max_symb, left):
        max_item = 0
        for el in data:
            el[field] = str(el[field])
            if len(el[field]) > max_item:
                max_item = len(el[field])

        if max_item > max_symb:
            max_item = max_symb

        for el in data:
            while len(el[field]) < max_item:
                if left:
                    el[field] = " " + el[field]
                else:
                    el[field] = el[field] + " "

            if len(el[field]) > max_item:
                if max_item == 1:
                    el[field] = "."
                elif max_item == 2:
                    el[field] = el[field][0] + "."
                elif max_item == 3:
                    el[field] = el[field][0] + ".."
                else:
                    el[field] = el[field][: max_item - 1] + "."

        return data
