from rate import *
from common import *
from utils import *
from copy import deepcopy
from random import shuffle, randint


def active(handcards: list, record) -> list:
    all_combi = __get_all_combi_1(handcards)

    rated_actions = []

    for combi in all_combi:
        action, rate = __get_optimal_action_active(combi, record)
        rated_actions.append([action, rate])

    rated_actions.sort(key=lambda i: i[1])
    action = rated_actions[-1][0]
    # update handcards:
    for card in action[2]:
        handcards.remove(card)
    return action


def passive(handcards, record) -> list:
    history, tribute, anti = record

    all_combi = __get_all_combi_1(handcards)

    rated_actions = []
    for combi in all_combi:
        action, rate = __get_optimal_action_passive(combi, record)
        rated_actions.append([action, rate])

    rated_actions.sort(key=lambda i: i[1])
    action = rated_actions[-1][0]
    # update handcards:
    if action != pass_action:
        for card in action[2]:
            handcards.remove(card)
    return action


def __get_optimal_action_active(combi, record) -> list:
    all_actions = __get_all_actions(combi, pass_action)

    rated = []
    for action in all_actions:
        rest_combi = exclude(combi, action)
        rate = __rate_active(action, rest_combi, record)
        rated.append([action, rate])
    rated.sort(key=lambda t: t[1])
    return rated[-1]


def __get_optimal_action_passive(combi, record) -> list:
    history, tribute, anti = record

    greater_action = None
    for pos, action in reversed(history):
        if action != pass_action:
            greater_action = action
            break

    all_actions = __get_all_actions(combi, greater_action)
    rated = []
    for action in all_actions:
        rest_combi = exclude(combi, action)
        rate = __rate_passive(action, rest_combi, record)
        rated.append([action, rate])
    rated.sort(key=lambda t: t[1])
    if len(rated) == 0:
        return [pass_action, __rate_passive(pass_action, combi, record)]
    return rated[-1]


def __rate_active(action: list, rest_combi: list, record: list) -> int:
    straight_flushes, straights, bombs, trips, pairs, singles, wildcard_cnt = rest_combi
    history, tribute, anti = record
    action_type, action_symbol, action_cards = action
    is_pass = (action == pass_action)

    rate = 0

    small = []
    middle = []
    large = []
    bombs_ex = []

    for s in singles:
        value = symbol2value[s[0][1]]
        if value <= 7:
            small.append(s)
        elif value <= 10:
            middle.append(s)
        else:
            large.append(s)

    for x in pairs + trips:
        value = symbol2value[x[0][1]]
        if value <= 5:
            small.append(x)
        elif value <= 9:
            middle.append(x)
        else:
            large.append(x)

    for st in straights:
        index = symbol2index[__get_straight_min_symbol(st)]
        if index <= 5:
            small.append(st)
        elif index <= 7:
            middle.append(st)
        elif index <= 9:
            large.append(st)
        else:
            print(st)
            exit("in rate active: wrong return value of __get_straight_min_symbol")

    #for bomb in bombs + straight_flushes:
    #    bombs_ex.append(bomb)

    rate += -100 * len(small)

    if len(middle) <= 2:
        pass
    else:
        rate += (2 - len(middle)) * 100

    if len(large) <= 2:
        rate += 30 * len(large)
    elif len(large) <= 3:
        rate += 60
    else:
        rate += 150 - 30 * len(large)

    for b in bombs:
        rate += 100

    for sf in straight_flushes:
        rate += 120

    for a in bombs + trips + pairs + singles:
        rate += symbol2value[a[0][1]]

    for s in straights + straight_flushes:
        rate += symbol2index[__get_straight_min_symbol(s)]

    if wildcard_cnt == 1:
        rate += 30
    elif wildcard_cnt == 2:
        rate += 70

    rate += len(action[2]) * 10

    return rate


def __rate_passive(action: list, rest_combi: list, record: list) -> int:
    straight_flushes, straights, bombs, trips, pairs, singles, wildcard_cnt = rest_combi
    history, tribute, anti = record
    action_type, action_symbol, action_cards = action

    return __rate_active(action, rest_combi, record)


def __get_all_actions_w0(combi: list) -> list:
    all_actions = []
    straight_flushes, straights, bombs, trips, pairs, singles, wildcard_cnt = deepcopy(combi)
    for bomb in bombs:
        all_actions.append(["Bomb", bomb[0][1], bomb])
        if bomb != joker_bomb:
            trips.append([bomb[0], bomb[1], bomb[2]])
    trips.sort(key=lambda t: symbol2index[t[0][1]])
    for triple in trips:
        all_actions.append(["Trips", triple[0][1], triple])
        pairs.append([triple[0], triple[1]])
    pairs.sort(key=lambda t: symbol2index[t[0][1]])
    for pair in pairs:
        all_actions.append(["Pair", pair[0][1], pair])
        singles.append([pair[0]])
    singles.sort(key=lambda t: symbol2index[t[0][1]])
    for single in singles:
        all_actions.append(["Single", single[0][1], single])
    # 3+2：
    for triple in trips:
        for pair in pairs:
            if triple[0][1] != pair[0][1] and pair[0] not in AllJokers:
                all_actions.append(["ThreeWithTwo", triple[0][1], triple + pair])
    # 3x2:
    for i in range(len(pairs) - 2):
        symbol_start = pairs[i][0][1]
        symbol_end = pairs[i + 2][0][1]
        if symbol2index[symbol_start] == symbol2index[symbol_end] - 2 and symbol2index[symbol_end] <= 12:
            all_actions.append(["ThreePair", symbol_start, pairs[i] + pairs[i + 1] + pairs[i + 2]])
    if len(pairs) >= 3 and pairs[0][0][1] == 'A' and pairs[-2][0][1] == 'Q' and pairs[-1][0][1] == 'K':
        all_actions.append(["ThreePair", 'Q', pairs[-2] + pairs[-1] + pairs[0]])
    # 2x3:
    for i in range(len(trips) - 1):
        symbol_start = trips[i][0][1]
        symbol_end = trips[i + 1][0][1]
        if symbol2index[symbol_start] == symbol2index[symbol_end] - 1 and symbol2index[symbol_end] <= 12:
            all_actions.append(["TwoTrips", symbol_start, trips[i] + trips[i + 1]])
    if len(trips) >= 2 and trips[0][0][1] == 'A' and trips[-1][0][1] == 'K':
        all_actions.append(["TwoTrips", 'K', pairs[-1] + pairs[0]])
    return all_actions


def __get_all_actions_w1(combi: list) -> list:
    wildcard = get_wildcard()
    all_actions = []
    straight_flushes, straights, bombs, trips, pairs, singles, wildcard_cnt = deepcopy(combi)
    ex_trips = []
    ex_pairs = []
    ex_singles = []
    for bomb in bombs:
        if bomb != joker_bomb:
            ex_trips.append([bomb[0], bomb[1], bomb[2]])
    for triple in trips:
        ex_pairs.append([triple[0], triple[1]])
    for pair in pairs:
        ex_singles.append([pair[0]])

    all_actions.append(["Single", wildcard[1], [wildcard]])
    for single in singles:
        if single[0] not in AllJokers:
            all_actions.append(["Pair", single[0][1], single + [wildcard]])
    for pair in pairs:
        if pair[0] not in AllJokers:
            all_actions.append(["Trips", pair[0][1], pair + [wildcard]])
    for triple in trips:
        all_actions.append(["Bomb", triple[0][1], triple + [wildcard]])
    for bomb in bombs:
        if bomb != joker_bomb:
            all_actions.append(["Bomb", bomb[0][1], bomb + [wildcard]])
    for pair1 in pairs:
        for pair2 in pairs + ex_pairs:
            if pair1 != pair2 and pair1[0] not in AllJokers and pair2[0] not in AllJokers:
                all_actions.append(["ThreeWithTwo", pair1[0][1], pair1 + [wildcard] + pair2])
    for triple in trips + ex_trips:
        for single in singles:
            if single[0][1] != triple[0][1] and single[0] not in AllJokers:
                all_actions.append(["ThreeWithTwo", triple[0][1], triple + single + [wildcard]])

    all_pairs = sorted(pairs + ex_pairs, key=lambda p: symbol2index[p[0][1]])
    # to find 3x2 (ThreePairs) with one wildcard:
    for single in singles:
        symbol = single[0][1]
        # axbbcc
        # aabxcc
        # aabbcx
        index1 = symbol2index[symbol]
        if 0 <= index1 <= 11: # A-Q, for x + 1 + 2 + 2
            if index1 == 11: # if QX, try to find KKAA
                if len(all_pairs) > 0 and all_pairs[0][0][1] == 'A': # if found AA
                    for i in range(-1, -len(all_pairs), -1): # try to find KK
                        if all_pairs[i][0][1] == 'K': # if find KK, add QXKKAA
                            all_actions.append(["ThreePair", 'Q', single + [wildcard] + all_pairs[i] + all_pairs[0]])
                            break
            else: # if A-J
                min_symbol = symbol
                for i in range(len(all_pairs) - 1):
                    symbol_index_mid = symbol2index[all_pairs[i][0][1]]
                    symbol_index_max = symbol2index[all_pairs[i + 1][0][1]]
                    if index1 == symbol_index_mid - 1 and index1 == symbol_index_max - 2:
                        all_actions.append(["ThreePair", min_symbol, single + [wildcard] + all_pairs[i] + all_pairs[i + 1]])
        if 1 <= index1 <= 12: # 2-K, for 2 + x + 1 + 2
            if index1 == 12: # if KX, try to find QQ AA
                if len(all_pairs) > 0 and all_pairs[0][0][1] == 'A': # if found AA
                    for i in range(-1, -len(all_pairs), -1): # try to find QQ
                        if all_pairs[i][0][1] == 'Q': # if find KK, add QQKXAA
                            all_actions.append(["ThreePair", 'Q', all_pairs[i] + single + [wildcard] + all_pairs[0]])
                            break
            else: # if 2-Q
                mid_symbol = symbol
                min_symbol_pos = 0
                max_symbol_pos = len(all_pairs) - 1
                while min_symbol_pos < len(all_pairs) and symbol2index[all_pairs[min_symbol_pos][0][1]] != symbol2index[mid_symbol] - 1:
                    min_symbol_pos += 1
                if min_symbol_pos < len(all_pairs):
                    while max_symbol_pos > min_symbol_pos and symbol2index[all_pairs[max_symbol_pos][0][1]] != symbol2index[mid_symbol] + 1:
                        max_symbol_pos -= 1
                    if max_symbol_pos > min_symbol_pos:
                        action_cards = all_pairs[min_symbol_pos] + single + [wildcard] + all_pairs[max_symbol_pos]
                        all_actions.append(["ThreePair", all_pairs[min_symbol_pos][0][1], action_cards])
        if 2 <= index1 <= 12 or index1 == 0: # A & 3-K, for 2 + 2 + x + 1
            if index1 == 0: # if AX, try to find QQKK
                for i in range(-1, -len(all_pairs), -1): # try to find KK
                    if all_pairs[i][0][1] == 'K' and all_pairs[i - 1][0][1] == 'Q': # if find QQKK, add QQKKAX
                        all_actions.append(["ThreePair", 'Q', all_pairs[i - 1] + all_pairs[i] + single + [wildcard]])
                        break
            else: # if 3-K
                min_symbol = symbol
                for i in range(-1, -len(all_pairs), -1):
                    symbol_index_min = symbol2index[all_pairs[i - 1][0][1]]
                    symbol_index_mid = symbol2index[all_pairs[i][0][1]]
                    if index1 == symbol_index_min + 2 and index1 == symbol_index_mid + 1:
                        all_actions.append(["ThreePair", all_pairs[i - 1][0][1], all_pairs[i - 1] + all_pairs[i] + single + [wildcard]])
    all_trips = sorted(trips + ex_trips, key=lambda p: symbol2index[p[0][1]])
    for pair in pairs:
        symbol_p = pair[0][1]
        # AAXBBB
        # AAABBX
        index1 = symbol2index[symbol_p]
        if 0 <= index1 <= 12:
            for triple in all_trips:
                symbol_t = triple[0][1]
                if symbol2index[symbol_t] == (index1 + 1) % 13:
                    all_actions.append(["TwoTrips", symbol_p, pair + [wildcard] + triple])
                elif symbol2index[symbol_t] == index1 - 1:
                    all_actions.append(["TwoTrips", symbol_t, triple + pair + [wildcard]])

    # MUST use one wildcard
    #
    # single -> x
    # pair -> x + 1
    # triple -> x + 2
    # bomb -> x + 3
    #   -> x + 4+
    # ThreeWithTwo -> x + 2 + 2
    #   -> 3 + x + 1
    # ThreePairs -> x + 1 + 2 + 2
    #   -> 2 + x + 1 + 2
    #   -> 2 + 2 + x + 1
    # TwoTrips -> x + 2 + 3
    #   -> 3 + x + 2
    return all_actions


def __get_all_actions_w2(combi: list) -> list:
    wildcard = get_wildcard()
    rank_symbol = get_rank_symbol()
    all_actions = []
    straight_flushes, straights, bombs, trips, pairs, singles, wildcard_cnt = deepcopy(combi)
    ex_trips = []
    ex_pairs = []
    ex_singles = []
    for bomb in bombs:
        if bomb != joker_bomb:
            ex_trips.append([bomb[0], bomb[1], bomb[2]])
    for triple in trips:
        ex_pairs.append([triple[0], triple[1]])
    for pair in pairs:
        ex_singles.append([pair[0]])

    all_actions.append(["Pair", rank_symbol, [wildcard, wildcard]])
    for single in singles:
        all_actions.append(["Trips", single[0][1], single + [wildcard, wildcard]])
    for pair in pairs:
        all_actions.append(["Bomb", pair[0][1], pair + [wildcard, wildcard]])
    for triple in trips:
        all_actions.append(["Bomb", triple[0][1], triple + [wildcard, wildcard]])
    for bomb in bombs:
        if bomb != joker_bomb:
            all_actions.append(["Bomb", bomb[0][1], bomb + [wildcard, wildcard]])
    # MUST use 2 wildcards
    # pair -> 2x
    # triples -> 2x + 1
    # bomb -> 2x + 2
    #   -> 2x + 3
    #   -> 2x + 4+
    # TODO -
    # X ThreeWithTwo -> 2x + 3
    #   -> 2x + 1 + 2
    #   -> x + 2 + x + 1
    # X ThreePairs -> 2x + 2 + 2
    #   -> 2 + 2x + 2
    #   -> 2 + 2 + 2x
    #   -> x + 1 + x + 1 + 2
    #   -> x + 1 + 2 + x + 1
    #   -> 2 + x + 1 + x + 1
    # TwoTrips -> 2x + 1 + 3
    #   -> x + 2 + x + 2
    #   -> 3 + 2x + 1
    return all_actions


def __get_all_actions(combi: list, prev_action: list = pass_action) -> list:
    atype = prev_action[0]
    avalue = ""
    aindex = -1
    if prev_action != pass_action:
        avalue = symbol2value[prev_action[1]]
        aindex = symbol2index[prev_action[1]]

    wc_cnt = combi[-1]
    all_actions = []
    straight_flushes, straights, bombs, trips, pairs, singles, wildcard_cnt = deepcopy(combi)

    for st in straights:
        min_symbol = __get_straight_min_symbol(st)
        all_actions.append(["Straight", min_symbol, st])
    for sf in straight_flushes:
        min_symbol = __get_straight_min_symbol(sf)
        all_actions.append(["StraightFlush", min_symbol, sf])

    all_actions += __get_all_actions_w0(combi)
    if wc_cnt >= 1:
        all_actions += __get_all_actions_w1(combi)
        if wc_cnt == 2:
            all_actions += __get_all_actions_w2(combi)

    if prev_action == pass_action:
        return all_actions
    legal_actions = []
    for a in all_actions:
        if (a[0] == "Bomb" or a[0] == "StraightFlush") and (atype == "Bomb" or atype == "StraightFlush"):
            if cmp2bombs(prev_action, a):
                legal_actions.append(a)
        elif (a[0] == "Bomb" or a[0] == "StraightFlush") and not (atype == "Bomb" or atype == "StraightFlush"):
            legal_actions.append(a)
        elif not (a[0] == "Bomb" or a[0] == "StraightFlush") and not (atype == "Bomb" or atype == "StraightFlush"):
            if a[0] == atype and atype != "StraightFlush" and symbol2value[a[1]] > avalue:
                legal_actions.append(a)
            elif a[0] == atype == "StraightFlush" and symbol2index[a[1]] > aindex:
                legal_actions.append(a)
        else:
            pass
    return legal_actions


def __get_all_combi_1(handcards: list) -> list:
    """
    Return  [[StraightFlushes, Straights, Bombs, Trips, Pairs, Singles, rest_wildcard_cnt], ...]
    """
    wildcard = get_wildcard()
    # cnt by card (suit + symbol):
    cards_cnt = get_cards_cnt(handcards)
    original_wc_cnt = handcards.count(wildcard)

    # get sfgc including empty sfg:
    sfgc = [[]]
    __find_sfgc(cards_cnt, original_wc_cnt, [], sfgc, 'A')

    combi_options = []
    for sfg in sfgc:
        cards_cnt_excluding_sfg = deepcopy(cards_cnt)
        rest_wc_cnt = original_wc_cnt
        # get cards_cnt_excluding_sfg & update wildcard_cnt
        for sf in sfg:
            rest_wc_cnt -= len(sf[1])
            for c in sf[0]:
                if c != wildcard:
                    cards_cnt_excluding_sfg[c[0]][c[1]] -= 1
        # get sgc:
        sgc = [[]]
        __find_sgc(cards_cnt_excluding_sfg, rest_wc_cnt, [], sgc, 'A')

        for sg in sgc:
            # for each straight, get cards_cnt_excluding_sfg_and_sg & new wildcard_cnt
            rest_cards_cnt = deepcopy(cards_cnt_excluding_sfg)
            rest_wc_cnt_2 = rest_wc_cnt
            for s in sg:
                rest_wc_cnt_2 -= len(s[1])
                for c in s[0]:
                    if c != wildcard:
                        rest_cards_cnt[c[0]][c[1]] -= 1

            # for each sgf x sg, get a combination"
            bombs = []
            triples = []
            pairs = []
            singles = []
            # check SB & HR:
            if rest_cards_cnt['S']['B'] == 2 and rest_cards_cnt['H']['R'] == 2:
                bombs.append(["SB", "SB", "HR", "HR"])
            else:
                if rest_cards_cnt['S']['B'] == 2:
                    pairs.append(["SB", "SB"])
                elif rest_cards_cnt['S']['B'] == 1:
                    singles.append(["SB"])
                if rest_cards_cnt['H']['R'] == 2:
                    pairs.append(["HR", "HR"])
                elif rest_cards_cnt['H']['R'] == 1:
                    singles.append(["HR"])
            rest_cards_cnt['S']['B'] = 0
            rest_cards_cnt['H']['R'] = 0
            # check other cards
            for symbol in AllSymbolsExcludingJokers:
                cards = []
                symbol_cnt = 0
                for suit in AllSuits:
                    symbol_cnt += rest_cards_cnt[suit][symbol]
                    for i in range(rest_cards_cnt[suit][symbol]):
                        cards.append(suit + symbol)

                if symbol_cnt == 1:
                    singles.append(cards)
                elif symbol_cnt == 2:
                    pairs.append(cards)
                elif symbol_cnt == 3:
                    triples.append(cards)
                elif symbol_cnt >= 4:
                    bombs.append(cards)
            straight_flushes = [sf[0] for sf in sfg]
            straights = [st[0] for st in sg]

            tmp_combi = [straight_flushes, straights, bombs, triples, pairs, singles, rest_wc_cnt_2]
            combi_options.append(tmp_combi)
    return combi_options


def __find_sfgc(cards_cnt: dict, wc_cnt: int, sfg: list, sfgc: list, min_symbol: str):
    wildcard = get_wildcard()
    # find all potential SFs:
    potential_sf = []
    for suit in AllSuits:
        for symbol_index in range(symbol2index[min_symbol], 10):
            exist_cnt = 0
            for i in range(5):
                if cards_cnt[suit][AllSymbols[(symbol_index + i) % 13]] > 0:
                    exist_cnt += 1
            if exist_cnt >= 5 - wc_cnt:
                tmp_sf = []
                used_wildcard = []
                for i in range(5):
                    c = suit + AllSymbols[(symbol_index + i) % 13]
                    if cards_cnt[suit][AllSymbols[(symbol_index + i) % 13]] == 0:
                        used_wildcard.append(c)
                        tmp_sf.append(wildcard)
                    else:
                        tmp_sf.append(c)
                potential_sf.append([tmp_sf, used_wildcard])
    # if none, do nothing and return
    if len(potential_sf) == 0:
        return
    # if any, for each sf, recursively search:
    for sf in potential_sf:
        # add sfg to sfgc
        new_sfg = sfg + [sf]
        sfgc.append(new_sfg)

        # update card cnt (for recurse)
        rest_cards_cnt = deepcopy(cards_cnt)
        for c in sf[0]:
            if c != wildcard:
                rest_cards_cnt[c[0]][c[1]] -= 1
        # update min_symbol
        if sf[0][0] != wildcard:
            new_min_symbol = sf[0][0][1]
        else:
            new_min_symbol = sf[1][0][1]
        __find_sfgc(rest_cards_cnt, wc_cnt - len(sf[1]), new_sfg, sfgc, new_min_symbol)


def __find_sgc(cards_cnt: dict, wc_cnt: int, sg: list, sgc: list, min_symbol: str):
    wildcard = get_wildcard()
    # find all potential Straights:
    potential_straights = []
    for symbol_index in range(symbol2index[min_symbol], 10):
        this_symbol_cnt = 0
        for i in range(5):
            for suit in AllSuits:
                if cards_cnt[suit][AllSymbols[(symbol_index + i) % 13]] > 0:
                    this_symbol_cnt += 1
                    break
        if this_symbol_cnt >= 5 - wc_cnt:
            used_wildcard = []
            tmp_straight = []
            for i in range(5):
                symbol_exist = False
                card = ""
                for suit in AllSuits:
                    if cards_cnt[suit][AllSymbols[(symbol_index + i) % 13]] > 0:
                        symbol_exist = True
                        card = suit + AllSymbols[(symbol_index + i) % 13]
                        break
                if not symbol_exist:
                    used_wildcard.append('S' + AllSymbols[(symbol_index + i) % 13])
                    tmp_straight.append(wildcard)
                else:
                    tmp_straight.append(card)
            potential_straights.append([tmp_straight, used_wildcard])
    # if none, do nothing and return
    if len(potential_straights) == 0:
        return
    # if any, for each sf, recursively search:
    for s in potential_straights:
        # add straight to sg & add sg to sgc
        new_sg = sg + [s]
        sgc.append(new_sg)
        # update card cnt & min_symbol (for recurse)
        cards_cnt_updated = deepcopy(cards_cnt)
        for c in s[0]:
            if c != wildcard:
                cards_cnt_updated[c[0]][c[1]] -= 1
        if s[0][0] != wildcard:
            new_min_symbol = s[0][0][1]
        else:
            new_min_symbol = s[1][0][1]
        __find_sgc(cards_cnt_updated, wc_cnt - len(s[1]), new_sg, sgc, new_min_symbol)


def __get_straight_min_symbol(st: list) -> str:
    """
    There may be wildcard(s) in a straight or straight-flush like XX345 whose min-symbol is A.
    """
    wildcard = get_wildcard()
    for i in range(5):
        if st[i] != wildcard:
            return AllSymbolsExcludingJokers[symbol2index[st[i][1]] - i]


def __is_empty_combi(combi) -> bool:
    straight_flushes, straights, bombs, trips, pairs, singles, wildcard_cnt = combi
    return len(straight_flushes) == len(straights) == len(bombs) == len(trips) == len(pairs) == len(singles) == 0 and wildcard_cnt == 0

