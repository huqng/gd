from common import *
from copy import deepcopy


def exclude(combi: list, action: list):
    wildcard = get_wildcard()
    straight_flushes, straights, bombs, trips, pairs, singles, wildcard_cnt = deepcopy(combi)
    cards = deepcopy(action[2])

    if action[0] == "StraightFlush":
        straight_flushes.remove(cards)
    elif action[0] == "Straight":
        straights.remove(cards)
    else:
        for card in cards:
            if card == wildcard:
                wildcard_cnt -= 1
            else:
                removed = False
                for bomb in bombs:
                    if card in bomb:
                        bomb.remove(card)
                        if len(bomb) == 3:
                            bombs.remove(bomb)
                            trips.append(bomb)
                        removed = True
                        break
                if removed:
                    continue
                for trip in trips:
                    if card in trip:
                        trip.remove(card)
                        trips.remove(trip)
                        pairs.append(trip)
                        removed = True
                        break
                if removed:
                    continue
                for pair in pairs:
                    if card in pair:
                        pair.remove(card)
                        pairs.remove(pair)
                        singles.append(pair)
                        removed = True
                        break
                if removed:
                    continue
                for single in singles:
                    if card in single:
                        singles.remove(single)
                        removed = True
                        break
                if removed:
                    continue
                else:
                    print(combi, action)
                    exit(-2)
    return [straight_flushes, straights, bombs, trips, pairs, singles, wildcard_cnt]


def get_cards_cnt(handcards: list) -> dict:
    wildcard = get_wildcard()
    ret = dict()
    for suit in AllSuits:
        ret[suit] = dict()
        for symbol in AllSymbols:
            ret[suit][symbol] = 0
    ret['S']['B'] = 0
    ret['H']['R'] = 0
    for c in handcards:
        if c != wildcard:
            ret[c[0]][c[1]] += 1
    return ret


def calc_bomb_value(action: list) -> float:
    type = action[0]
    if type == "StraightFlush":
        return 5.5 * 14 + symbol2value[action[1]]
    elif action[2] == joker_bomb:
        return 11 * 14
    else:
        return len(action[2]) * 14 + symbol2value[action[1]]
