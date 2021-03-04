from random import shuffle, choice, randint
from Player import *
from common import *
from utils import *


def gen_cards():
    cards = []
    for suit in AllSuits:
        for symbol in AllSymbolsExcludingJokers:
            cards.append(suit + symbol)
            cards.append(suit + symbol)
    cards.append('SB')
    cards.append('SB')
    cards.append('HR')
    cards.append('HR')
    shuffle(cards)  # shuffle
    return cards


if __name__ == '__main__':
    cards = gen_cards()

    rank = choice(AllSymbolsExcludingJokers)  # choose a random RANK
    set_symbol2value(rank)

    players = [Player(), Player(), Player(), Player()]

    players[0].set_basic_info(cards[0: 27], 0, rank),
    players[1].set_basic_info(cards[27: 54], 1, rank),
    players[2].set_basic_info(cards[54: 81], 2, rank),
    players[3].set_basic_info(cards[81: 108], 3, rank)

    cur_pos = None
    cur_action = None
    i = 0
    if True:
        while True:
            cur_action = players[i].get_action()
            cur_pos = i
            print_action(cur_pos, cur_action)
            for j in range(4):
                players[j].update_history(cur_pos, cur_action)
            if not players[i].finished():
                i = (i + 1) % 4
            else:
                print("Player " + str(i) + " finished.")
                break

