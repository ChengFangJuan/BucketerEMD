# -*- coding:utf-8 -*-
from __future__ import division
import math
import BucketerEMD.settings as game_settings
import copy
from itertools import combinations,permutations
from BucketerEMD.card_to_string_conversion import CARD_TO_STRING




def get_all_cards():
    card_to_string = CARD_TO_STRING()
    index_card = dict()
    card = card_to_string.rank_table[:game_settings.rank_count]
    flower = card_to_string.suit_table[:game_settings.suit_count]
    cards = []
    index = 0
    for i in card:
        for j in flower:
            cards.append(i + j)
            index += 1
            index_card[index] = i + j
    return cards, index_card

def _suit_cat_flop(s1,s2,s3,s4,s5):

    ret = -1
    if s1 != 0:
        return -1

    if s2 == 0:
        if s3 == 0:
            ret = s4 * 2 + s5
        if s3 == 1:
            ret = 5 + s4 * 3 + s5
    elif s2 == 1:
        if s3 == 0:
            ret = 15 + s4 * 3 + s5
        elif s3 == 1:
            ret = 25 + s4 * 3 + s5
        elif s3 == 2:
            ret = 35 + s4 * 4 + s5

    return ret

def flopID(h,b):
    hold = copy.deepcopy(h)
    board = copy.deepcopy(b)
    board.sort()
    os = {}
    MM = 0
    s = {}
    suit = []

    # 计算牌的花色
    for i in range(5):
        if i <= 1:
            os[i] = (hold[i] - 1) % game_settings.suit_count
        else:
            os[i] = (board[i-2] - 1) % game_settings.suit_count

    # 归一化牌的花色，第一张手牌的花色设置为0，第二张手牌的花色设置为1，以此类推
    for i in range(5):
        j = 0
        while j < i:
            if os[j] == os[i]:
                s[i] = s[j]
                break
            j = j + 1
        if j == i:
            s[i] = MM
            MM = MM + 1

        if i <= 1:
            suit_diff = s[i] - ((hold[i] - 1) % game_settings.suit_count)
            hold[i] = hold[i] + suit_diff
        else:
            suit_diff = s[i] - ((board[i-2] - 1) % game_settings.suit_count)
            board[i-2] = board[i-2] + suit_diff

    board.sort()
    base = ((hold[0] - 1) // game_settings.suit_count) * math.pow(game_settings.rank_count, 4) + \
           ((hold[1] - 1) // game_settings.suit_count) * math.pow(game_settings.rank_count, 3) + \
           ((board[0] - 1) // game_settings.suit_count) * math.pow(game_settings.rank_count, 2) + \
           ((board[1] - 1) // game_settings.suit_count) * game_settings.rank_count + \
           ((board[2] - 1) // game_settings.suit_count)

    for i in range(5):
        if i <= 1:
            s[i] = (hold[i] - 1) % game_settings.suit_count
        else:
            s[i] = (board[i-2] - 1) % game_settings.suit_count

    cat = _suit_cat_flop(s[0],s[1],s[2],s[3],s[4])

    if cat == -1:
        print("error suit cat")

    cat = cat * math.pow(game_settings.rank_count,5) + base

    for key, value in s.items():
        suit.append(value)
    suit_ret = _suit_cat_flop(suit[0],suit[1],suit[2], suit[3],suit[4])

    return cat, suit, suit_ret

def computer_flop_buckets():

    possible_board_card_list = list(range(1,game_settings.card_count+1))
    possible_flop_board_card_comb = list(combinations(possible_board_card_list, 3))
    hand_card = [0] * game_settings.hold_card_count
    card, index_card = get_all_cards()

    code_data = dict()
    for board in possible_flop_board_card_comb:
        print("------- board-------:", board)
        temp_board = list(board)
        print(temp_board)
        used = [0] * game_settings.card_count
        for i in range(len(board)):
            used[board[i]-1] = 1
        for card1 in range(1, game_settings.card_count + 1):
            if used[card1-1] == 0:
                used[card1-1] = 1
                hand_card[0] = card1
                for card2 in range(card1+1, game_settings.card_count + 1):
                    if used[card2-1] == 0:
                        used[card2-1] = 1
                        hand_card[1] = card2
                        code, suit, suit_ret = flopID(hand_card,temp_board)
                        # file.write(str(suit) + '-------' + str(suit_ret) + '\n')
                        if code not in code_data:
                            code_data[code] = []
                        temp = [temp_board[0],temp_board[1],temp_board[2],hand_card[0],hand_card[1]]
                        temp.sort()
                        card_string = index_card[temp[0]] + index_card[temp[1]] + index_card[temp[2]] \
                                      + index_card[temp[3]] + index_card[temp[3]]
                        code_data[code].append(card_string)
                        used[card2-1] = 0
                used[card1-1] = 0

    print("----------code data count-------------")
    for id, value in code_data.items():
        print("Index: {0}, --- Card: {1}".format(id, value))
    print(len(code_data))

    return code_data

def computer_pre_flop_buckets():
    code_data = dict()
    card, index_card = get_all_cards()

    for card1 in range(1, game_settings.card_count + 1):
        for card2 in range(card1+1, game_settings.card_count + 1):
            rank1 = (card1 - 1) // game_settings.suit_count
            rank2 = (card2 - 1) // game_settings.suit_count
            if card1 % game_settings.suit_count == card2 % game_settings.suit_count:
                code = rank1 * game_settings.rank_count + rank2 + 1
                if code not in code_data:
                    code_data[code] = []
                code_data[code].append(index_card[card1] + index_card[card2])
            else:
                code = rank2 * game_settings.rank_count + rank1 + 1
                if code not in code_data:
                    code_data[code] = []
                code_data[code].append(index_card[card1] + index_card[card2])

    print("----------code data count-------------:", len(code_data))
    for id, value in code_data.items():
        print("Index: {0}, --- Card: {1}".format(id, value))
    return code_data



if __name__ == '__main__':
    # computer_pre_flop_buckets()
    computer_flop_buckets()