from common import *

def exclude(combi: list, action: list):
    # TODO - exclude action from a combi
    pass

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
