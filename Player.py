from algorithm0 import *
from common import *
from time import time


class Player:
    def __init__(self):
        self.handCards = []
        self.pos = -1

        self.wildcard = ""

        self.history = []
        # [[pos, action], ...]

        self.tribute = []
        # [[from, to, card], [...], ...]

        self.anti = []
        # [pos1, ...]

    def set_basic_info(self, handcards: list, pos: int, rank: str):
        self.handCards = sorted(handcards, key=lambda c: suit2index[c[0]] + symbol2index[c[1]] * 4)
        self.pos = pos
        set_wildcard('H' + rank)
        set_rank_symbol(rank)
        set_symbol2value(rank)

    def update_history(self, pos: int, action: list):
        pos = (pos - self.pos) % 4
        self.history.append([pos, action])

    def update_tribute(self, tribute_result):
        for i in tribute_result:
            self.tribute.append(i)

    def update_info_anti(self, anti_pos):
        for pos in anti_pos:
            pos = (pos - self.pos) % 4
            self.anti.append(pos)

    def get_action(self) -> list:
        record = (self.history, self.tribute, self.anti)
        if self.__is_active():
            return active(self.handCards, record)
        else:
            return passive(self.handCards, record)

    def __is_active(self):
        if len(self.history) == 0:
            return True
        for i in range(-1, -len(self.history) - 1, -1):
            pos = self.history[i][0]
            action = self.history[i][1]
            if action == pass_action:
                pass
            else:
                if pos == 0:
                    return True
                else:
                    return False

    def finished(self):
        return len(self.handCards) == 0


if __name__ == "__main__":
    cards = [
        'DA', 'S2', 'H6', 'SJ', 'SA', 'DT', 'C8', 'S3', 'SQ',
        'H7', 'C3', 'HJ', 'CQ', 'DT', 'H9', 'S4', 'H3', 'SJ',
        'S4', 'H4', 'C4', 'D4', 'D4', 'DJ', 'HT', 'HQ', 'HK'
        ]

    p = Player()
    p.set_basic_info(cards, 0, '2')
    t_begin = time()
    print(time() - t_begin, end="")
    print("s")