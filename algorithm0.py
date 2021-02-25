from common import *
from utils import *
from copy import deepcopy
from random import shuffle


def active(handcards: list, record) -> list:
    # TODO
    history, tribute, anti = record

    all_combi = __combine_phase_1(handcards)
    candidates = []
    for combi in all_combi:
        optimal_action, rate = __rate_combi(combi, record)
        candidates.append([optimal_action, rate])
    candidates.sort(key=lambda i: i[1])
    action = candidates[-1][0]
    # update handcards:
    for card in action[2]:
        handcards.remove(card)
    return action


def passive(handcards, record) -> list:
    # TODO
    history, tribute, anti = record
    return pass_action


def __rate_combi(combi, record):
    history, tribute, anti = record
    candidates = []

    all_actions = __get_all_actions(combi)
    if len(all_actions) == 1:
        action = all_actions[0]
        return [action, __rate_active_action(action)]

    for action in all_actions:
        rest_combi = exclude(combi, action[2])
        action_rate = __rate_active_action(action, record)
        combi_rate = __rate_combi(rest_combi, record)[1]
        rate = action_rate + combi_rate
        candidates.append([action, rate])
    candidates.sort(key=lambda i: i[1])
    action = candidates[-1][0]
    rate = candidates[-1][1]
    return [action, rate]


def __get_all_actions_w0(combi: list) -> list:
    all_actions = []
    straight_flushes, straights, bombs, trips, pairs, singles, wildcard_cnt = deepcopy(combi)
    for bomb in bombs:
        all_actions.append(["Bomb", bomb[0][1], bomb])
        if bomb != joker_bomb:
            trips.append([bomb[0], bomb[1], bomb[2]])
    for triple in trips:
        all_actions.append(["Trips", triple[0][1], triple])
        pairs.append([triple[0], triple[1]])
    for pair in pairs:
        all_actions.append(["Pair", pair[0][1], pair])
        singles.append([pair[0]])
    for single in singles:
        all_actions.append(["Single", single[0][1], single])
    # 3+2：
    for triple in trips:
        for pair in pairs:
            if triple[0][1] != pair[0][1] and pair[0] not in AllJokers:
                all_actions.append(["ThreeWithTwo", triple[0][1], triple + pair])
    # 3x2:
    for i in range(len(pairs) - 2):
        start_symbol = pairs[i][0][1]
        end_symbol = pairs[i + 2][0][1]
        if symbol2index[start_symbol] % 13 == (symbol2index[end_symbol] - 2) % 13 and symbol2index[start_symbol] <= 11:
            all_actions.append(["ThreePair", start_symbol, pairs[i] + pairs[i + 1] + pairs[i + 2]])
    # 2x3:
    for i in range(len(trips) - 1):
        start_symbol = trips[i][0][1]
        end_symbol = trips[i + 1][0][1]
        if symbol2index[start_symbol] % 13 == (symbol2index[end_symbol] - 1) % 13 and symbol2index[start_symbol] <= 11:
            all_actions.append(["TwoTrips", start_symbol, trips[i] + trips[i + 1]])

    return all_actions


def __get_all_actions_w1(combi: list) -> list:
    wildcard = get_wildcard()
    all_actions = []
    straight_flushes, straights, bombs, trips, pairs, singles, wildcard_cnt = deepcopy(combi)
    extented_trips = []
    extented_pairs = []
    extented_singles = []
    for bomb in bombs:
        if bomb != joker_bomb:
            extented_trips.append([bomb[0], bomb[1], bomb[2]])
    for triple in trips:
        extented_pairs.append([triple[0], triple[1]])
    for pair in pairs:
        extented_singles.append([pair[0]])

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
        for pair2 in pairs + extented_pairs:
            if pair1 != pair2 and pair1[0] not in AllJokers and pair2[0] not in AllJokers:
                all_actions.append(["ThreeWIthPair", pair1[0][1], pair1 + [wildcard] + pair2])
    for triple in trips + extented_trips:
        for single in singles:
            if single[0][1] != triple[0][1] and single[0] not in AllJokers:
                all_actions.append(["ThreeWithTwo", triple[0][1], triple + single + [wildcard]])
    # MUST use one wildcard
    #
    # single -> x
    # pair -> x + 1
    # triple -> x + 2
    # bomb -> x + 3
    #   -> x + 4+
    # ThreeWithTwo -> x + 2 + 2
    #   -> 3 + x + 1
    # TODO:
    # ThreePairs -> x + 1 + 2 + 2
    #   -> 2 + x + 1 + 2
    #   -> 2 + 2 + x + 1
    # TwoTrips -> x + 2 + 3
    #   -> 3 + x + 2
    return all_actions


def __get_all_actions_w2(combi: list) -> list:
    wildcard = get_wildcard()
    all_actions = []
    straight_flushes, straights, bombs, trips, pairs, singles, wildcard_cnt = deepcopy(combi)
    extented_trips = []
    extented_pairs = []
    extented_singles = []
    for bomb in bombs:
        if bomb != joker_bomb:
            extented_trips.append([bomb[0], bomb[1], bomb[2]])
    for triple in trips:
        extented_pairs.append([triple[0], triple[1]])
    for pair in pairs:
        extented_singles.append([pair[0]])
    # MUST use 2 wildcards
    # TODO
    # pair -> 2x
    # triples -> 2x + 1
    # bomb -> 2x + 2
    #   -> 2x + 3
    #   -> 2x + 4+
    # ThreeWithTwo -> 2x + 3
    #   -> 2x + 1 + 2
    #   -> x + 2 + x + 1
    # ThreePairs -> 2x + 2 + 2
    #   -> 2 + 2x + 2
    #   -> 2 + 2 + 2x
    #   -> x + 1 + x + 1 + 2
    #   -> x + 1 + 2 + x + 1
    #   -> 2 + x + 1 + x + 1
    # TwoTrips -> 2x + 1 + 3
    #   -> x + 2 + x + 2
    #   -> 3 + 2x + 1
    return []


def __get_all_actions(combi: list) -> list:
    wc_cnt = combi[-1]
    all_actions = []
    straight_flushes, straights, bombs, trips, pairs, singles, wildcard_cnt = deepcopy(combi)

    for st in straights:
        min_symbol = __get_st_min_symbol(st)
        all_actions.append(["Straight", min_symbol, st])
    for sf in straight_flushes:
        min_symbol = __get_st_min_symbol(sf)
        all_actions.append(["StraightFlush", min_symbol, sf])

    all_actions += __get_all_actions_w0(combi)
    if wc_cnt >= 1:
        all_actions += __get_all_actions_w1(combi)
        if wc_cnt == 2:
            all_actions += __get_all_actions_w2(combi)
    wildcard = get_wildcard()
    return all_actions


def __rate_active_action(action, record) -> int:
    # TODO
    history, tribute, anti = record
    return 0


def __combine_phase_1(handcards: list) -> list:
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


def __get_st_min_symbol(st: list) -> str:
    wildcard = get_wildcard()
    for i in range(5):
        if st[i] != wildcard:
            return AllSymbolsExcludingJokers[symbol2index[st[i][1]] - i]

