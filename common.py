__wildcard = str()
__rankSymbol = str()
max5BombValue = 76.5
AllSymbols = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'B', 'R']
AllSymbolsExcludingJokers = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
AllJokers = ["SB", "HR"]
AllJokerSymbols = ['B', 'R']
AllSuits = ['S', 'H', 'C', 'D']

pass_action = ["PASS", "PASS", "PASS"]
joker_bomb = ["SB", "SB", "HR", "HR"]

symbol2index = {
    # key: 'A', '2', ..., 'K', 'B', 'R'
    # value: 0, 1, 2, ..., 14
    'A': 0,
    '2': 1,
    '3': 2,
    '4': 3,
    '5': 4,
    '6': 5,
    '7': 6,
    '8': 7,
    '9': 8,
    'T': 9,
    'J': 10,
    'Q': 11,
    'K': 12,
    'B': 13,
    'R': 14
}

suit2index = {
    'S': 0,
    'H': 1,
    'C': 2,
    'D': 3
}

suit2graphic = {
    'S': '♠',
    'H': '♥',
    'C': '♣',
    'D': '♦'
}

symbol2value = {
    'A': 12,
    '2': 0,
    '3': 1,
    '4': 2,
    '5': 3,
    '6': 4,
    '7': 5,
    '8': 6,
    '9': 7,
    'T': 8,
    'J': 9,
    'Q': 10,
    'K': 11,
    # value 13 is reserved for <rank>
    'B': 14,
    'R': 15
}


def set_symbol2value(rank: str):
    # this function should be called manually
    global symbol2value
    symbol2value[rank] = 13


def get_wildcard():
    return __wildcard


def set_wildcard(v):
    global __wildcard
    __wildcard = v


def get_rank_symbol():
    return __rankSymbol


def set_rank_symbol(v):
    global __rankSymbol
    __rankSymbol = v
